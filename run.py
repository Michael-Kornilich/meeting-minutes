import os
import shutil
from datetime import datetime
import sys
import json

from tasks import extract_sound
from tasks import diarize
from tasks import slice_audio
from tasks import stt
from tasks import package


class TaskSuccess:
    def __init__(self):
        self.success: bool = False


class Task:
    def __init__(
            self,
            name: str,
            stdout_path: str,
            verbose: bool = False,
            reroute_stdout: bool = False
    ):
        self.name: str = name
        self.stdout_path: str = stdout_path
        self.verbose: bool = verbose
        self.reroute_stdout = reroute_stdout
        self.task_success = TaskSuccess()

        self._start: datetime | None = None
        self._end: datetime | None = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._separator: str = "-" * 70

    def __enter__(self):
        if self.reroute_stdout:
            f = open(self.stdout_path, mode="a")
            sys.stdout = f
            sys.stderr = f

        self._start = datetime.now()
        print(f"\tStarted task '{self.name}' on {self._start}")
        print(self._separator, end="\n\n")
        return self.task_success

    def __exit__(self, err, value, traceback):
        self._end = datetime.now()
        length_in_sec = (self._end - self._start).total_seconds()
        m, s = divmod(length_in_sec, 60)

        print("\n" + self._separator)
        if err:
            self.task_success.success = False
            print(f"\tThe task '{self.name}' failed after {m:.0f} minutes and {s:.1f} seconds on {self._end.isoformat(sep=' ')}")
            print(f"\tReason: {err.__name__} - {value}", end="\n" * 3)
        else:
            self.task_success.success = True
            print(
                f"\tSuccessfully ended task '{self.name}' on {self._end.isoformat(sep=' ')}."
                f"It took {m:.0f} minutes and {s:.1f} seconds",
                end="\n" * 3
            )

        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        return True


tasks = [
    {"name": "Extract Sound", "callable": extract_sound.main},
    {"name": "Diarize", "callable": diarize.main},
    {"name": "Slice Audio", "callable": slice_audio.main},
    {"name": "Speech-To-Text", "callable": stt.main},
    {"name": "Package result", "callable": package.main},
]

with open("config.json") as f:
    config = json.load(f)

shutil.rmtree(config["data-dir"])
os.mkdir(config["data-dir"])

for task in tasks:
    name = task["name"]
    func = task["callable"]
    with Task(name, "logs.txt") as task_status:
        func()

    if not task_status.success:
        break
