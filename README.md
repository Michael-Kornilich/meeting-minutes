# Audio processing from a preliminary seminar meeting at 17.04
The goal of the mini-project is to efficiently capture, process and summarize information shared at the preliminary meeting about my seminar work.

## Usage
**External requirements**
* `python` 3.14.3 (but any 3.14.x should do)
* `poetry` 2.3.2 (but any 2.x.x should do)
* `ffmpeg` (full) 8.x

**Setup:** 
* Create a `.env` file in the project root
* `cd path/to/project/src`
* `poetry install --with full-core,stat-modelling`

**Config:** 
* Config file: `config.json`
* The config file should have the following structure:
```json
{
  "data-dir": "path/to/cache/directory",
  "source-video": "path/to/source/video.mp4",
  "target-dir": "directory/to/save/the/output/in",
  "speaker-mapping": {
    "SPEAKER_00": "Jack",
    "SPEAKER_01": "Jodi",
    "SPEAKER_02": "Max"
  }
}
```

* The speaker mapping does not properly work right now

**Run:** `cd path/to/project/src && clear && poetry run python run.py`

**WARNING:** The `data-dir` directory will be emptied as soon as the script starts. So the best practice would be to create a new directory for the project

### Input 
A `.mp4` (or a `.wav`) file

### Output
A `meeting.jsonl` file with the following contents:
```jsonl
{"speaker":"Francis Wong", "start": "0:00.000", "stop": "1:00:00.000", "utterance": "My fellow Americans!..."}
{"speaker":"Student 1", "start": "1:01.000", "stop": "1:03:00.000", "utterance": "I have a question..."}
{...}
```

## The pipeline
**1. Screen record the entire meeting - audio + video**
* Tool: [BetterCapture](https://github.com/jsattler/BetterCapture?tab=readme-ov-file)
* Records video, system audio, and microphone

**2. Save the data on the `Index` drive**
* Save as `.mp4` in the `/Volumes/Index/BetterCapture` as `meeting.mp4`

**3. Diarize the meeting**
* Tool for sound extraction: `ffmpeg` + thin python wrapper
* Diarizer + runtime: `pyannotate.audio`
* Save all the results (most importantly speaker_id + segments) as `meeting-diary.jsonl` in the `/Volumes/Index/Cache`

**4. Slice the meeting audio into pieces according to the diarizer**
* Tool for slicing: `ffmpeg` + thin python wrapper
* Slice according to `meeting-diary.jsonl`
* Save each segment in `/Volumes/Index/slices` in the following format: `<speaker_id>-<start SS.ms>-<stop SS.ms>.wav`

**5. Run an STT model on each piece**
* STT model: TBA
* Local runtime: TBA
* Save each text piece in `/Volumes/Index/text-slices` as `<speaker_id>-<start HH:MM:SS.sss>-<stop HH:MM:SS.sss>.txt`

**6. Package speaker + interval + text into a `meeting.jsonl` file**
* Tool: python
* Listen to speakers, find Francis Wong
* Map his ID to his name. Map others are student-n (n = 1, 2,...)
* For each entry in `meeting-diary.jsonl` format the speaker ID and time boundaries into the format of the text files
* Create the final meeting transcript as `meeting.jsonl` with the structure from above in `/Volumes/Index/Cache`

**7. Upload files into an LLM**
* Use the final `meeting.jsonl` and ChatGPT to summarize information into a clean `summary.md` file. Store it in `/Volumes/Index/Cache`

---
* Use git for versioning, ignore binaries. They will be backed up separately
* Test the pipeline on a test-meeting and on a youtube video
