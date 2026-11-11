from __future__ import annotations

import asyncio
import os
import random
import tempfile
import time
from datetime import datetime

import requests

from brain.clap_detector import wait_for_double_clap
from brain.voice_listener import (
    contains_wake_word,
    listen_debug,
    strip_wake_word,
)

try:
    import edge_tts
except Exception:
    edge_tts = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    from playsound import playsound
except Exception:
    playsound = None


BACKEND_URL = "http://127.0.0.1:8000/chat"
EDGE_VOICE = "en-IN-NeerjaNeural"


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def is_wake_only_text(text: str) -> bool:
    text = normalize(text)
    if not text:
        return True
    return strip_wake_word(text) == ""


def build_startup_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning, sir. Krishna is online and listening."
    if 12 <= hour < 17:
        return "Good afternoon, sir. Krishna is online and listening."
    if 17 <= hour < 22:
        return "Good evening, sir. Krishna is online and listening."
    return "Hello, sir. Krishna is online and listening."


async def _edge_tts_to_file(text: str, filepath: str) -> None:
    communicate = edge_tts.Communicate(text=text, voice=EDGE_VOICE, rate="-10%")
    await communicate.save(filepath)


def _speak_edge(text: str) -> bool:
    if edge_tts is None or playsound is None:
        return False

    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)

    try:
        asyncio.run(_edge_tts_to_file(text, path))
        playsound(path)
        return True
    except Exception:
        return False
    finally:
        try:
            os.remove(path)
        except Exception:
            pass


def _speak_pyttsx3(text: str) -> None:
    import pyttsx3

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 140)
        engine.setProperty("volume", 1.0)

        voices = engine.getProperty("voices")

        preferred = None
        for v in voices:
            name = (getattr(v, "name", "") or "").lower()
            if "david" in name or "mark" in name:
                preferred = v.id
                break

        if preferred:
            engine.setProperty("voice", preferred)

        engine.say(text)
        engine.runAndWait()

    except Exception:
        pass


def send_to_backend(command: str) -> str:
    command = command.strip()
    if not command:
        return "I did not catch the command clearly, sir."

    try:
        response = requests.post(
            BACKEND_URL,
            json={"message": command},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        payload = data.get("response", "")

        if isinstance(payload, str):
            return payload

        if isinstance(payload, dict):
            if "assistant_reply" in payload and payload["assistant_reply"]:
                return str(payload["assistant_reply"])
            if "reply" in payload and payload["reply"]:
                return str(payload["reply"])
            if "message" in payload and payload["message"]:
                return str(payload["message"])
            return str(payload)

        return str(data)

    except Exception as e:
        return f"I ran into a backend issue, sir. {e}"


def process_command(command: str) -> str | None:
    normalized = normalize(command)

    if not normalized:
        return None

    if normalized in {"krishna", "hey krishna", "hi krishna", "hare krishna", "hey", "hi", "hare"}:
        speak("Yes, sir.")
        return "active"

    if normalized in {"exit continuous mode", "shutdown continuous mode"}:
        speak("Understood, sir. Stopping continuous mode.")
        raise SystemExit

    if normalized == "stop listening":
        speak("Understood, sir. Entering sleep mode. Say hey krishna to wake me.")
        return "sleep"

    reply = send_to_backend(command)
    speak(reply)
    return "active"


def active_loop() -> str:
    wake_responses = [
        "Yes, sir.",
        "At your service, sir.",
        "Go ahead, sir.",
        "I'm listening, sir.",
    ]

    silence_streak = 0

    while True:
        print("\n[Wake phase]")
        wake = listen_debug(verbose=True)

        raw = normalize(wake.get("raw_transcript", ""))
        corrected = normalize(wake.get("corrected_transcript", ""))

        if raw == "stop listening" or corrected == "stop listening":
            print("[DEBUG] stop listening detected")
            speak("Understood, sir. Entering sleep mode. Say hey krishna to wake me.")
            return "sleep"

        if raw in {"shutdown continuous mode", "exit continuous mode"} or corrected in {
            "shutdown continuous mode",
            "exit continuous mode",
        }:
            print("[DEBUG] shutdown detected")
            speak("Understood, sir. Stopping continuous mode.")
            raise SystemExit

        if not raw:
            silence_streak += 1
            time.sleep(0.35 if silence_streak < 3 else 0.8)
            continue

        silence_streak = 0

        if wake.get("low_confidence", False):
            time.sleep(0.4)
            continue

        if not contains_wake_word(raw) and not contains_wake_word(corrected):
            time.sleep(0.4)
            continue

        if is_wake_only_text(raw) or is_wake_only_text(corrected):
            speak(random.choice(wake_responses))

            print("[Command phase]")
            command = listen_debug(verbose=True)
            cmd_raw = normalize(command.get("raw_transcript", ""))
            cmd_corrected = normalize(command.get("corrected_transcript", ""))

            if cmd_raw == "stop listening" or cmd_corrected == "stop listening":
                print("[DEBUG] stop listening detected in command phase")
                speak("Understood, sir. Entering sleep mode. Say hey krishna to wake me.")
                return "sleep"

            if not cmd_raw:
                speak("I did not hear a command, sir.")
                time.sleep(0.4)
                continue

            if command.get("low_confidence", False):
                speak("Please repeat the command clearly, sir.")
                time.sleep(0.4)
                continue

            final_command = cmd_corrected or cmd_raw
            state = process_command(final_command)
            if state == "sleep":
                return "sleep"
            time.sleep(0.2)
            continue

        inline_command = strip_wake_word(raw)
        if not inline_command:
            inline_command = strip_wake_word(corrected)

        if inline_command:
            if inline_command == "stop listening":
                print("[DEBUG] inline stop listening detected")
                speak("Understood, sir. Entering sleep mode. Say hey krishna to wake me.")
                return "sleep"

            state = process_command(inline_command)
            if state == "sleep":
                return "sleep"

        time.sleep(0.25)


def sleep_loop() -> str:
    print("Krishna is in sleep mode. Wake with hey krishna.")

    while True:
        print("[Sleep phase: voice]")
        wake = listen_debug(verbose=True)
        raw = normalize(wake.get("raw_transcript", ""))
        corrected = normalize(wake.get("corrected_transcript", ""))

        if raw and not wake.get("low_confidence", False):
            if contains_wake_word(raw) or contains_wake_word(corrected):
                speak("I'm awake, sir.")
                return "active"

        print("[Sleep phase: clap]")
        if wait_for_double_clap(timeout_sec=6.0, verbose=True):
            speak("Double clap detected. I'm awake, sir.")
            return "active"

        time.sleep(0.25)


def main() -> None:
    print("========================================")
    print("Krishna continuous mode started")
    print("Say: 'Hey Krishna'")
    print("Say: 'stop listening' to sleep")
    print("Wake from sleep with: 'hey krishna'")
    print("To fully stop: say 'shutdown continuous mode'")
    print("========================================")

    speak(build_startup_greeting())

    mode = "active"

    while True:
        try:
            if mode == "active":
                mode = active_loop()
            else:
                mode = sleep_loop()
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except SystemExit:
            break
        except Exception as e:
            print(f"[Loop error] {e}")
            time.sleep(0.5)
            
def speak(text: str) -> None:
    print(f"Krishna: {text}")

    # small natural delay
    import time
    time.sleep(0.15)

    _speak_pyttsx3(text)


if __name__ == "__main__":
    main()