import pickle
import jsonl
import json

with open("config.json") as f:
    config = json.load(f)


def main() -> None:
    with open(f"{config['data-dir']}/transcript.pkl", mode="rb") as f:
        transcript = pickle.load(f)

    speaker_mapping = config["speaker-mapping"]

    clean_transcript = []
    for i in transcript:
        j = i.copy()
        j["speaker"] = speaker_mapping.get(j["speaker"], j["speaker"])
        clean_transcript.append(j)

    jsonl.dump(clean_transcript, f"{config['target-dir']}/meeting.jsonl")
