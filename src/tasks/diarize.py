from pathlib import Path
import pickle
from dotenv import load_dotenv
import os
import jsonl
import json

NAME = "Diarize"

with open("config.json") as f:
    config = json.load(f)


def main() -> None:
    print("Importing runtime...")
    import pyannote
    from pyannote.audio import Pipeline

    if Path(f"{config['cache']}/meeting-diary.jsonl").exists():
        print("Diary jsonl exists. Skipping the task")
        return

    if Path(f"{config['cache']}/diarization.pkl").exists():
        with open(f"{config['cache']}/diarization.pkl", mode="rb") as file:
            output = pickle.load(file)
    else:
        print("No cache found. Running the task")

        load_dotenv(".env")

        print("Importing the model...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-community-1",
            token=os.environ["HF_TOKEN"]
        )

        # Tune hyperparams to have a less aggressive diarization
        print("Running the model. This will take a while...")
        output = pipeline(f"{config['cache']}/sound.wav")

        for turn, speaker in output.speaker_diarization:
            print(f"{speaker} speaks between t={turn.start:.3f}s and t={turn.end:.3f}s")

        with open(f"{config['cache']}/diarization.pkl", mode="wb") as file:
            pickle.dump(output, file)

    segments = [i for i in output.exclusive_speaker_diarization if i[0].end - i[0].start > 1]
    json_lines = [{"speaker_id": i[1], "start": i[0].start, "stop": i[0].end} for i in segments]
    jsonl.dump(json_lines, f"{config['cache']}/meeting-diary.jsonl")
    return
