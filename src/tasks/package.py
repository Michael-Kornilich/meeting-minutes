import pickle
import jsonl
from argparse import Namespace

NAME = "Package"


def main(config: dict, usr_args: Namespace) -> None:
    with open(f"{config['cache']}/transcript.pkl", mode="rb") as f:
        transcript = pickle.load(f)

    speaker_mapping = config["speaker-mapping"]

    for i in range(len(transcript)):
        transcript[i]["speaker"] = speaker_mapping.get(transcript[i]["speaker"], transcript[i]["speaker"])

    jsonl.dump(transcript, f"{usr_args.ouput}/meeting.jsonl")
