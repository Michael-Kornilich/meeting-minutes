# Audio processing from a preliminary seminar meeting at 17.04

This project provides a modular, local-first pipeline to diarize and transcribe audio and / or video.

Use cases:

* Meeting minutes
* Summarization
* NLP (parts of the pipeline can be turned on / off)

## Usage

### Setup

1. Install external dependencies
    * `python` 3.14.3 (but any 3.14.x should do)
    * `poetry` 2.3.2 (but any 2.x.x should do)
    * `ffmpeg` (full) 8.x

2. Create a `.env` file in the project root. It should have the following content

```
export HF_TOKEN="hf_xxxxxx"
```

3. Move to the project's directory: `cd path/to/project`
4. Install dependencies (some are redundant WIP): `poetry install --with full-core,stat-modelling`
5. Change the default config
   The config file should have the following structure.

```json
{
  "cache": "path/to/cache/directory"
}
```

Ensure that the given path exists.

Done!

### Run

**Minimal usage example**: `poetry run python src/run.py -i /Users/Jake/Desktop/my-meeting.mp4 meeting.jsonl`

Generally: `poetry run python src/run.py <args>`

### CLI reference

**Flags**

* `--help` (`-h`) - get the CLI reference
* `-i` - path to the input file. It can either be a video or directly a sound file.
  Any file format is supported as long as it's supported by `ffmpeg`
* `--with` - a comma separated list of what steps of the pipeline to *include*. All are included by default
* `--without` - a comma separated list of what steps of the pipeline to *exclude*. None are included by default
* `--init-cache` - if given, deletes everything from the cache directory.
  You can specify the directory in the config.
  If the flag is not given and the cache is not empty, the user will be prompted to proceed at their own risk

**Arguments**

* The first argument without a flag is the path to output the result in. Supported format is `.jsonl`

**Logic**

* `--with` and `--without` flags cannot be used in a single command
* `--help` cannot be used in a combination with any other flag / argument

## The pipeline

**1. Screen records the entire meeting - audio (+ video)**

* Tool for Mac: [BetterCapture](https://github.com/jsattler/BetterCapture?tab=readme-ov-file)
* Records video, system audio, and microphone
* Save the data

**2. Diarize the meeting**

* Tool for sound extraction: `ffmpeg` + thin python wrapper
* Diarizer + runtime: `pyannotate.audio`
* Save all the results (most importantly speaker_id + segments) as `meeting-diary.jsonl` in the `/Volumes/Index/Cache`

**3. Slice the meeting audio into pieces according to the diarizer**

* Tool for slicing: `ffmpeg` + thin python wrapper
* Slice according to `meeting-diary.jsonl`
* Save each segment in `/Volumes/Index/slices` in the following format: `<speaker_id>-<start SS.ms>-<stop SS.ms>.wav`

**4. Run an STT model on each piece**

* STT model: Whisper
* Local runtime: PyTorch (?)
* Save each text piece in `/Volumes/Index/text-slices` as `<speaker_id>-<start HH:MM:SS.sss>-<stop HH:MM:SS.sss>.txt`

**5. Package speaker + interval + text into a `meeting.jsonl` file**

* Tool: python
* Manually listen to speakers
* Map ID's to names / titles.
* For each entry in `meeting-diary.jsonl` format the speaker ID and time boundaries into the format of the text files
* Create the final meeting transcript as `meeting.jsonl` with the structure from above in `/Volumes/Index/Cache`

---

### Details

The output file has the following structure:

```jsonl
{"speaker":"SPEAKER_00", "start": "0:00.000", "stop": "1:00:00.000", "utterance": "My fellow Americans!..."}
{"speaker":"SPEAKER_00", "start": "1:01.000", "stop": "1:03:00.000", "utterance": "I have a question..."}
{...}
```

### Future features

* More flexible speaker mapping
* Support for `.txt` and `.md` output file formats 
