from datetime import time
from pathlib import Path
from dotenv import load_dotenv
import pickle
import json
from argparse import Namespace

NAME = "Speech-To-Text"


def _seconds_to_time(string_time: str) -> time:
    if ":" not in string_time:
        raise ValueError("The separator ':' not found in time")

    s, ms = [int(i) for i in string_time.split(":")]
    h = s // 3600
    s = s % 3600

    m = s // 60
    s = s % 60

    ms = int(float("0." + str(ms)) * 1_000_000)
    return time(h, m, s, ms)


def main(config: dict, usr_args: Namespace) -> None:
    print("Importing the runtime...")
    from faster_whisper import WhisperModel

    for i in Path(f"{config['cache']}/slices").iterdir():
        if i.name.startswith("."):
            continue
        if not i.name.endswith(".wav"):
            raise ValueError(f"An invalid slice: {i.name}")
    print("All slices have valid extension (.wav)")

    load_dotenv()

    transcript = []

    print("Importing the model...")
    model = WhisperModel("small", compute_type="int8")

    for path in Path(f"{config['cache']}/slices").iterdir():
        print(f"Transcribing {path.name}...")
        segments, info = model.transcribe(path.absolute(), language="en")

        speaker, start, end = path.name.split("-")

        start = start.replace("_", ":")
        start = _seconds_to_time(start)

        end = end[:-4].replace("_", ":")
        end = _seconds_to_time(end)

        utteration = "".join(segment.text for segment in segments).strip()

        if not utteration:
            continue

        transcript.append({
            "speaker": speaker,
            "start": start.strftime("%H:%M:%S.%f"),
            "end": end.strftime("%H:%M:%S.%f"),
            "utteration": utteration
        })

    transcript.sort(key=lambda x: time.fromisoformat(x["start"]))

    with open(f"{config['cache']}/transcript.pkl", mode="wb") as f:
        pickle.dump(transcript, f)

    return
