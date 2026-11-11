from __future__ import annotations

import queue
import time

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
BLOCK_DURATION = 0.05
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

# Tuned for your mic based on your debug output
CLAP_THRESHOLD = 0.035
MIN_CLAP_GAP = 0.08
MAX_DOUBLE_CLAP_GAP = 0.90


def _rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    audio = audio.astype(np.float32).flatten()
    return float(np.sqrt(np.mean(np.square(audio))))


def wait_for_double_clap(timeout_sec: float = 6.0, verbose: bool = False) -> bool:
    q: queue.Queue[np.ndarray] = queue.Queue()
    clap_times: list[float] = []

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    start = time.time()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=callback,
    ):
        while time.time() - start < timeout_sec:
            try:
                data = q.get(timeout=0.2)
            except queue.Empty:
                continue

            level = _rms(data)
            now = time.time()

            if verbose:
                print(f"[CLAP] level={level:.3f}")

            if level >= CLAP_THRESHOLD:
                if not clap_times or (now - clap_times[-1]) >= MIN_CLAP_GAP:
                    clap_times.append(now)
                    if verbose:
                        print(f"[CLAP] clap detected at {now:.2f}")

                clap_times = clap_times[-3:]

                if len(clap_times) >= 2:
                    gap = clap_times[-1] - clap_times[-2]
                    if MIN_CLAP_GAP <= gap <= MAX_DOUBLE_CLAP_GAP:
                        if verbose:
                            print(f"[CLAP] double clap detected, gap={gap:.3f}")
                        return True

    return False