import pickle
import jsonl
import json

NAME = "Package"

with open("config.json") as f:
    config = json.load(f)


def main() -> None:
    with open(f"{config['cache']}/transcript.pkl", mode="rb") as f:
        transcript = pickle.load(f)

    speaker_mapping = config["speaker-mapping"]

    for i in range(len(transcript)):
        transcript[i]["speaker"] = speaker_mapping.get(transcript[i]["speaker"], transcript[i]["speaker"])

    jsonl.dump(transcript, f"{config['target-dir']}/meeting.jsonl")
