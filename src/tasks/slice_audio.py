import jsonl
from pathlib import Path
import os
import subprocess
import json

NAME = "Slice Audio"

with open("config.json") as f:
    config = json.load(f)


def main() -> None:
    diary = list(jsonl.load(f"{config['cache']}/meeting-diary.jsonl"))
    if not Path(f"{config['cache']}/slices/").exists():
        os.mkdir(f"{config['cache']}/slices")
    else:
        os.rmdir(f"{config['cache']}/slices")

    print("Splitting audio...")
    num_errs = 0
    for i in diary:
        speaker = str(i["speaker_id"])
        start = str(i["start"])
        end = str(i["stop"])

        filename = f'{speaker}-{start.replace(".", "_")}-{end.replace(".", "_")}.wav'

        res = subprocess.run(
            ["ffmpeg", "-ss", start, "-to", end, "-i", f"{config['cache']}/sound.wav",
             "-c:a", "pcm_s16le", f"{config['cache']}/slices/" + filename],
            capture_output=True
        )
        if res.returncode != 0:
            print(f"An error occurred while slicing segment {i}")
            num_errs += 1

    if num_errs / len(diary) > 0.1:
        raise RuntimeError(f"Failure rate is over allowed limit: {num_errs / len(diary):.0%}")

    return
