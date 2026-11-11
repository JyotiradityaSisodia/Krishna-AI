import hashlib
import re
import subprocess
from pathlib import Path
import winsound

PIPER_DIR = Path(r"D:\krishna\piper")
PIPER_EXE = PIPER_DIR / "piper.exe"
VOICE_MODEL = PIPER_DIR / "voices" / "voice.onnx"
CACHE_DIR = PIPER_DIR / "cache"

CACHE_DIR.mkdir(exist_ok=True)


def prepare_text_for_voice(text: str, mode: str = "short") -> str:
    if not text:
        return ""

    clean = " ".join(str(text).strip().split())
    clean = clean.replace("```", "").replace("**", "").replace("`", "")

    if mode == "full":
        return clean

    # short mode
    parts = re.split(r'(?<=[.!?])\s+', clean)
    short_text = " ".join(parts[:2]).strip()

    if len(short_text) > 220:
        short_text = short_text[:220].rsplit(" ", 1)[0] + "."

    return short_text


def _cache_path_for_text(text: str) -> Path:
    key = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{key}.wav"


def speak(text: str, mode: str = "short"):
    try:
        prepared = prepare_text_for_voice(text, mode=mode)
        if not prepared:
            return

        output_wav = _cache_path_for_text(prepared)

        if not output_wav.exists():
            cmd = [
                str(PIPER_EXE),
                "--model",
                str(VOICE_MODEL),
                "--output_file",
                str(output_wav),
            ]

            result = subprocess.run(
                cmd,
                input=prepared,
                text=True,
                capture_output=True
            )

            if result.returncode != 0:
                print("Piper stderr:", result.stderr)
                print("Piper stdout:", result.stdout)
                return

        winsound.PlaySound(str(output_wav), winsound.SND_FILENAME)

    except Exception as e:
        print("Piper voice error:", e)