from __future__ import annotations

import json
import os
import queue
import time
from difflib import get_close_matches
from typing import Any

import sounddevice as sd
from vosk import KaldiRecognizer, Model


DEFAULT_MODEL_PATHS = [
    "vosk_model",
    "vosk-model-en-us-0.22-lgraph",
    "vosk-model-en-us-0.22",
    "vosk-model-small-en-us-0.15",
    "models/vosk_model",
]

KNOWN_COMMANDS = [
    "test voice recognition",
    "voice recognition",
    "listen now",
    "voice status",
    "check voice module",
    "what should we do next",
    "open app",
    "learn voice recognition",
    "approve voice recognition",
]


def _find_model_path() -> str | None:
    for path in DEFAULT_MODEL_PATHS:
        if os.path.isdir(path):
            return path
    return None


def voice_module_status() -> dict[str, Any]:
    model_path = _find_model_path()
    return {
        "available": model_path is not None,
        "model_path": model_path,
        "message": "Voice model found." if model_path else "No Vosk model folder found.",
    }


def _normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    return " ".join(text.split())


# 🔥 SMART COMMAND MAPPING (THIS FIXES YOUR ISSUE)
def _closest_command(text: str) -> str:
    normalized = _normalize_text(text)

    if not normalized:
        return normalized

    # Hard intent mapping (important)
    if "voice" in normalized or "cognition" in normalized:
        return "test voice recognition"

    if "test" in normalized:
        return "test voice recognition"

    if "listen" in normalized:
        return "listen now"

    if "status" in normalized:
        return "voice status"

    if "next" in normalized:
        return "what should we do next"

    # fallback fuzzy match
    match = get_close_matches(normalized, KNOWN_COMMANDS, n=1, cutoff=0.5)
    return match[0] if match else normalized


def _looks_low_confidence(text: str) -> bool:
    normalized = _normalize_text(text)
    if not normalized:
        return True

    words = normalized.split()

    if len(words) <= 1:
        return True

    if len(words) == 2:
        maybe = _closest_command(normalized)
        if maybe == normalized:
            return True

    return False


def transcribe_once(
    timeout_sec: int = 10,
    samplerate: int = 16000,
    lead_in_delay_sec: float = 1.0,
) -> dict[str, Any]:
    model_path = _find_model_path()
    if not model_path:
        return {
            "success": False,
            "transcript": "",
            "message": "No Vosk model folder found. Put your model in 'vosk_model'.",
        }

    q: queue.Queue[bytes] = queue.Queue()
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, samplerate)

    def callback(indata, frames, time_info, status):
        q.put(bytes(indata))

    transcript_parts: list[str] = []

    try:
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            # 🔥 delay before listening (fixes noise capture)
            time.sleep(lead_in_delay_sec)

            start = time.time()
            while time.time() - start < timeout_sec:
                try:
                    data = q.get(timeout=1.0)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = _normalize_text(result.get("text", ""))
                    if text:
                        transcript_parts.append(text)

            final_result = json.loads(recognizer.FinalResult())
            final_text = _normalize_text(final_result.get("text", ""))
            if final_text:
                transcript_parts.append(final_text)

    except Exception as e:
        return {
            "success": False,
            "transcript": "",
            "message": f"Voice capture failed: {e}",
        }

    raw_transcript = _normalize_text(
        " ".join(x for x in transcript_parts if x))

    if not raw_transcript:
        return {
            "success": False,
            "transcript": "",
            "message": "No speech detected.",
        }

    corrected = _closest_command(raw_transcript)

    # ✅ IMPORTANT FIX (YOU ASKED THIS)
    if _looks_low_confidence(raw_transcript):
        return {
            "success": False,
            "transcript": raw_transcript,
            "message": "Low confidence voice input. Please repeat clearly.",
        }

    return {
        "success": True,
        "transcript": corrected,
        "raw_transcript": raw_transcript,
        "message": "Voice transcription successful.",
    }
