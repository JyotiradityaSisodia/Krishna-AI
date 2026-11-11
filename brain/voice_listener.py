from __future__ import annotations

import queue
from typing import Optional

import noisereduce as nr
import numpy as np
import sounddevice as sd
import torch
from faster_whisper import WhisperModel
from scipy.signal import butter, lfilter
from silero_vad import get_speech_timestamps, load_silero_vad

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
MODEL_SIZE = "medium"

GAIN_MULTIPLIER = 2.0
NOISE_SAMPLE_SECONDS = 0.25
MAX_RECORD_SECONDS = 4
SILENCE_BLOCK_LIMIT = 4

WAKE_WORDS = [
    "hey krishna",
    "hi krishna",
    "hare krishna",
    "krishna",
]

audio_queue: queue.Queue[np.ndarray] = queue.Queue()

print("🧠 Loading Whisper model...")
whisper_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

print("🧠 Loading Silero VAD...")
vad_model = load_silero_vad()


def audio_callback(indata, frames, time_info, status):
    if status:
        pass
    audio_queue.put(indata.copy())


def _normalize_text(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _highpass_filter(audio: np.ndarray, cutoff: float = 120.0, sr: int = SAMPLE_RATE) -> np.ndarray:
    if len(audio) < 10:
        return audio
    nyquist = 0.5 * sr
    norm_cutoff = cutoff / nyquist
    b, a = butter(2, norm_cutoff, btype="high", analog=False)
    return lfilter(b, a, audio).astype(np.float32)


def _normalize_gain(audio: np.ndarray, gain: float = GAIN_MULTIPLIER) -> np.ndarray:
    if audio.size == 0:
        return audio
    boosted = audio * gain
    peak = np.max(np.abs(boosted)) if boosted.size else 0.0
    if peak > 0.98:
        boosted = boosted / peak * 0.98
    return boosted.astype(np.float32)


def _trim_silence_edges(audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
    if audio.size == 0:
        return audio
    abs_audio = np.abs(audio)
    idx = np.where(abs_audio > threshold)[0]
    if idx.size == 0:
        return np.array([], dtype=np.float32)
    start = max(0, int(idx[0]) - 400)
    end = min(len(audio), int(idx[-1]) + 400)
    return audio[start:end].astype(np.float32)


def _clean_audio(audio: np.ndarray, noise_sample: Optional[np.ndarray]) -> np.ndarray:
    cleaned = audio.astype(np.float32)
    cleaned = _highpass_filter(cleaned)
    cleaned = _normalize_gain(cleaned)

    if noise_sample is not None and noise_sample.size > 0:
        try:
            cleaned = nr.reduce_noise(
                y=cleaned,
                sr=SAMPLE_RATE,
                y_noise=noise_sample.astype(np.float32),
                stationary=True,
                prop_decrease=0.80,
            ).astype(np.float32)
        except Exception:
            pass

    cleaned = _normalize_gain(cleaned)
    cleaned = _trim_silence_edges(cleaned)
    return cleaned.astype(np.float32)


def _looks_low_confidence(text: str) -> bool:
    text = _normalize_text(text)

    if not text:
        return True

    bad_patterns = {
        "the",
        "a",
        "uh",
        "um",
        "hmm",
        "huh",
        "ok",
        "okay",
        "hey",
        "hi",
    }
    if text in bad_patterns:
        return True

    words = text.split()
    if len(words) == 1 and words[0] not in {"krishna"}:
        return True

    if len(words) >= 2 and len(set(words)) == 1:
        return True

    return False


def _correct_command(text: str) -> str:
    text = _normalize_text(text)
    if not text:
        return text

    # Exact/safe corrections only
    exact_map = {
        "the best one": "test voice recognition",
        "best one": "test voice recognition",
        "voice test": "test voice recognition",
        "test voice": "test voice recognition",
        "voice recognition": "test voice recognition",
        "stop listing": "stop listening",
        "stop listen": "stop listening",
        "stop listening": "stop listening",
        "shutdown continuous mode": "shutdown continuous mode",
    }

    if text in exact_map:
        return exact_map[text]

    return text


def _record_noise_profile() -> np.ndarray:
    frames_needed = max(1, int(NOISE_SAMPLE_SECONDS / 0.5))
    chunks = []

    for _ in range(frames_needed):
        try:
            chunk = audio_queue.get(timeout=0.5)
            chunks.append(chunk)
        except queue.Empty:
            break

    if not chunks:
        return np.array([], dtype=np.float32)

    return np.concatenate(chunks, axis=0).flatten().astype(np.float32)


def record_until_silence(timeout: int = MAX_RECORD_SECONDS) -> tuple[np.ndarray, bool]:
    collected = []
    saw_speech = False

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=audio_callback,
    ):
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except queue.Empty:
                break

        noise_profile = _record_noise_profile()
        silence_counter = 0

        while True:
            try:
                data = audio_queue.get(timeout=0.8)
            except queue.Empty:
                break

            collected.append(data)

            audio_chunk = np.concatenate(collected, axis=0).flatten().astype(np.float32)
            audio_for_vad = torch.from_numpy(audio_chunk)

            speech = get_speech_timestamps(
                audio_for_vad,
                vad_model,
                sampling_rate=SAMPLE_RATE,
            )

            if len(speech) > 0:
                saw_speech = True
                silence_counter = 0
            else:
                silence_counter += 1

            if saw_speech and silence_counter > SILENCE_BLOCK_LIMIT:
                break

            if len(collected) * 0.5 > timeout:
                break

    if not collected:
        return np.array([], dtype=np.float32), False

    full_audio = np.concatenate(collected, axis=0).flatten().astype(np.float32)
    cleaned = _clean_audio(full_audio, noise_profile)
    return cleaned, saw_speech


def transcribe_audio(audio: np.ndarray) -> str:
    if audio.size == 0:
        return ""

    segments, _ = whisper_model.transcribe(
        audio,
        beam_size=3,
        language="en",
        vad_filter=True,
        condition_on_previous_text=False,
        temperature=0.0,
    )
    return " ".join(seg.text for seg in segments).strip()


def listen_debug(verbose: bool = False) -> dict:
    audio, saw_speech = record_until_silence()

    if not saw_speech or audio.size == 0:
        return {
            "raw_transcript": "",
            "corrected_transcript": "",
            "low_confidence": True,
            "success": False,
        }

    raw_text = _normalize_text(transcribe_audio(audio))
    corrected = _correct_command(raw_text) if raw_text else ""
    low_confidence = _looks_low_confidence(raw_text)

    if verbose and raw_text:
        print(f"🧠 Raw Heard: {raw_text}")
        print(f"✅ Corrected: {corrected}")
        print(f"⚠️ Low confidence: {low_confidence}")

    return {
        "raw_transcript": raw_text,
        "corrected_transcript": corrected,
        "low_confidence": low_confidence,
        "success": bool(raw_text) and not low_confidence,
    }


def listen() -> str | None:
    debug = listen_debug()
    if not debug["success"]:
        return None
    return debug["corrected_transcript"]


def contains_wake_word(text: str) -> bool:
    text = _normalize_text(text)
    if "krishna" in text:
        return True
    fuzzy_triggers = ["krish", "krisna", "krushna"]
    return any(trigger in text for trigger in fuzzy_triggers)


def strip_wake_word(text: str) -> str:
    text = _normalize_text(text)

    for trigger in ["hey krishna", "hi krishna", "hare krishna", "krishna"]:
        while trigger in text:
            text = text.replace(trigger, " ").strip()
            text = _normalize_text(text)

    leftovers = {"hey", "hi", "hare"}
    words = [w for w in text.split() if w not in leftovers]
    return _normalize_text(" ".join(words))


def _is_wake_only(text: str) -> bool:
    text = _normalize_text(text)
    if not text:
        return True
    return strip_wake_word(text) == ""


def listen_for_wake_and_command() -> dict:
    wake_debug = listen_debug()

    if not wake_debug["raw_transcript"]:
        return {
            "success": False,
            "stage": "wake",
            "message": "No speech detected for wake word.",
            "wake_raw": "",
            "wake_corrected": "",
        }

    wake_raw = wake_debug["raw_transcript"]
    wake_corrected = wake_debug["corrected_transcript"]

    if not contains_wake_word(wake_raw) and not contains_wake_word(wake_corrected):
        return {
            "success": False,
            "stage": "wake",
            "message": "Wake word not detected.",
            "wake_raw": wake_raw,
            "wake_corrected": wake_corrected,
        }

    if _is_wake_only(wake_raw) or _is_wake_only(wake_corrected):
        command_debug = listen_debug()

        if not command_debug["raw_transcript"]:
            return {
                "success": True,
                "stage": "wake_only",
                "wake_raw": wake_raw,
                "wake_corrected": wake_corrected,
                "command_raw": "",
                "command_corrected": "",
                "message": "Wake word detected. No command heard yet.",
            }

        if command_debug["low_confidence"]:
            return {
                "success": False,
                "stage": "command",
                "wake_raw": wake_raw,
                "wake_corrected": wake_corrected,
                "command_raw": command_debug["raw_transcript"],
                "command_corrected": command_debug["corrected_transcript"],
                "message": "Wake word detected, but command confidence was too low.",
            }

        return {
            "success": True,
            "stage": "command",
            "wake_raw": wake_raw,
            "wake_corrected": wake_corrected,
            "command_raw": command_debug["raw_transcript"],
            "command_corrected": command_debug["corrected_transcript"],
            "message": "Wake word and command detected successfully.",
        }

    inline_command = strip_wake_word(wake_raw)
    corrected_inline = _correct_command(inline_command)

    return {
        "success": True,
        "stage": "inline_command",
        "wake_raw": wake_raw,
        "wake_corrected": wake_corrected,
        "command_raw": inline_command,
        "command_corrected": corrected_inline,
        "message": "Wake word and inline command detected.",
    }