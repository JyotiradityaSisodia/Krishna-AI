import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = r"D:\krishna\vosk_model"
MIC_DEVICE_INDEX = None 

audio_queue = queue.Queue()


def _audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(bytes(indata))


def listen_once(seconds: int = 5) -> str:
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)

    result = ""

    stream_kwargs = {
        "samplerate": 16000,
        "blocksize": 8000,
        "dtype": "int16",
        "channels": 1,
        "callback": _audio_callback,
    }

    if MIC_DEVICE_INDEX is not None:
        stream_kwargs["device"] = MIC_DEVICE_INDEX

    with sd.RawInputStream(**stream_kwargs):
        print("Speak now...")
        for _ in range(int(seconds * 2)):
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                if res.get("text"):
                    result += " " + res["text"]

        final_res = json.loads(recognizer.FinalResult())
        if final_res.get("text"):
            result += " " + final_res["text"]

    return result.strip()