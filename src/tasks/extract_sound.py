from pathlib import Path
import subprocess
import json
from argparse import Namespace

NAME = "Extract Sound"


def main(config: dict, usr_args: Namespace) -> None:
    SOURCE = config["source-video"]
    TARGET = f"{config['cache']}/sound.wav"

    if Path(TARGET).exists():
        print("The result of this step is cached. Skipping the task")
        return
    else:
        print("No cache found. Running the task")

    if not Path(SOURCE).exists():
        raise FileNotFoundError(f"The source file could not be found at '{SOURCE}'")

    res = subprocess.run(
        ['ffmpeg', '-i', SOURCE, '-vn', '-c:a', 'pcm_s16le', TARGET],
        capture_output=True
    )
    if res.returncode == 1:
        raise ValueError(f"ffmpeg call failed: \n{res.stdout.decode('UTF-8')}")
