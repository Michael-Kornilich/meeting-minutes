import os
import shutil
from datetime import datetime
import sys
import json
import argparse
from pathlib import Path
from importlib import import_module


class TaskSuccess:
    def __init__(self):
        self.success: bool = False


class Task:
    def __init__(
            self,
            name: str,
            stdout_path: str | None = None,
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

        if self.reroute_stdout and self.stdout_path is None:
            raise ValueError("reroute_stdout expects stdout_path to be not None")

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
            print(
                f"\tThe task '{self.name}' failed after {m:.0f} minutes and {s:.1f} seconds on {self._end.isoformat(sep=' ')}")
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


class UniqueCSV(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            return set()

        raw_items = values.split(",")
        items = [i for i in raw_items if i]
        if len(set(items)) != len(items):
            raise ValueError(f"The given list has duplicates in it")
        setattr(namespace, self.dest, set(items))


class EnsureValidPath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        usr_path = Path(values)

        if not usr_path.exists():
            raise FileNotFoundError(f"The given path does not exist: '{usr_path.absolute()}'")
        if not usr_path.is_dir():
            raise ValueError(f"The given path is not a directory: '{usr_path.absolute()}'")

        setattr(namespace, self.dest, usr_path)
        return


parser = argparse.ArgumentParser(
    prog="poetry run python scr/run.py",
    description="This CLI provides a modular, local-first pipeline to diarize and transcribe audio and / or video",
)

parser.add_argument(
    "--init-cache",
    dest="init_cache",
    action="store_true",
    help="specify, whether to remove (possible) contents of the cache directory",
)

parser.add_argument(
    "-i",
    dest="input",
    metavar="input-filepath",
    required=True,
    action=EnsureValidPath,
    help="Filepath to the input file"
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--with",
    dest="with_steps",
    metavar="list",
    action=UniqueCSV,
    default=set(),
    help="Specify, which exacts steps of the pipeline to run",
)
group.add_argument(
    "--without",
    dest="without_steps",
    metavar="list",
    action=UniqueCSV,
    default=set(),
    help="Specify, which exacts steps of the pipeline to exclude"
)

parser.add_argument(
    "output",
    metavar="output-filepath",
    action=EnsureValidPath,
    help="Directory to create the .jsonl file in. If --with or --without flags are used, this argument is ignored"
)

user_input = parser.parse_args()

with Task("Setup") as task_success:
    with open("config.json") as f:
        config = json.load(f)

    available_tasks = ("extract_sound", "diarize", "slice_audio", "stt", "package")
    task_registry = []

    for task_file in available_tasks:
        task = import_module("tasks." + task_file)
        task_registry.append({
            "name": task.NAME, "callable": task.main
        })
    # TODO: freeze better
    task_registry = tuple(task_registry)

    passed_tasks = user_input.with_steps or user_input.without_steps
    if not passed_tasks.issubset(set(available_tasks)):
        raise ValueError(f"Illegal task(s) passed: {', '.join(passed_tasks - set(available_tasks))}")

    if user_input.init_cache:
        if list(Path(config["cache"]).iterdir()):
            inp = (f"The cache directory ({Path(config['cache']).absolute()}) is not empty. "
                   f"Do you want to delete its contents [Y|n]? ")

            if inp == "Y":
                shutil.rmtree(config["cache"])
                os.mkdir(config["cache"])
            elif inp == "n":
                print("WARNING: since the cache directory is not empty, consistency of files cannot be guaranteed")
            else:
                raise ValueError(f"Invalid input '{inp}'")

    if user_input.output.name.split(".")[1] != "jsonl":
        raise ValueError(
            f"The output file extension must be 'jsonl'. '{user_input.output.name.split('.')[1]}' was given"
        )

    if user_input.init_cache is True:
        shutil.rmtree(config["cache"])
        os.mkdir(config["cache"])

if not task_success.success:
    quit()

for task in task_registry:
    name = task["name"]
    func = task["callable"]
    with Task(name) as task_status:
        func(config, user_input)

    if not task_status.success:
        quit()
