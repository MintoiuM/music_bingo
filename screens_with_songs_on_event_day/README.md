# Screens with songs on event day

Create PowerPoint slides for Music Bingo: one slide per song (title, artist, year), with optional audio and auto-advance. Audio can be downloaded from YouTube and trimmed using the same Excel source.

## Prerequisites

- **Python 3** (e.g. 3.10+)
- **FFmpeg** (for downloading/trimming audio): `sudo apt install ffmpeg` (or set `--ffmpeg-location` in download script)
- **Excel source:** `sources/music_bingo_songs.xlsx`
- **Background image:** `sources/background.jpeg` (used on every slide)

## Setup

```bash
cd screens_with_songs_on_event_day
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Excel source format

**File:** `sources/music_bingo_songs.xlsx`

- **First column:** Song line for slides and filenames. Format: `SONG_NAME - ARTIST_NAME (RELEASE_YEAR)` (the first ` - ` separates song from artist; year in parentheses at the end).
- **Download script only** also uses:
  - **Column 2:** Optional time interval(s), e.g. `0:30-1:00` or `30-60` or `0:30-1:00, 1:30-2:00`. Empty = full track.
  - **Column 3:** YouTube URL (`youtube.com` or `youtu.be`). Rows without a URL are skipped for download.
                  Use only the link without any constraints:
                                  ✅ https://www.youtube.com/watch?v=NFXm8PMqCNE 
                                  ✅ https://youtu.be/3LmSjmcUNh8?si=DINEMtmwzhor0WRM
                                  ❎ https://www.youtube.com/watch?v=z-2_OstpR5c&list=RDz-2_OstpR5c&start_radio=1 
                                     `(remove everything after first '&' (&list=RDz-2_OstpR5cstart_radio=1))`

First row is treated as a header and skipped.

---

## Workflow

### 1. List available sheets (optional)

To see sheet IDs and names so you can pick the right `-s` value:

```bash
python download_songs.py --list-sheets
```

Example output: `-s 0  'INTERNATIONAL 1960-1989'`, `-s 1  'INTERNATIONAL 1990 - 2010'`, etc.

### 2. Download audio from YouTube (optional)

Downloads audio for each row that has a YouTube URL, saves as `output/<FOLDER_NAME>/<sanitized_name>.m4a`. Existing files are skipped. Failed downloads are retried up to 3 times.

```bash
python download_songs.py -f <FOLDER_NAME> -s <SHEET_ID>
```

**Examples:**

```bash
python download_songs.py -f RETRO -s 0
python download_songs.py -f february_2025 -s 1
python download_songs.py -f test -s 0 --dry-run   # only print what would be downloaded
```

**Options:**

|      Option         |                             Description                                       |
|---------------------|-------------------------------------------------------------------------------|
| `-f`, `--folder`    | **Required.** Output folder under `output/` (e.g. `RETRO` → `output/RETRO/`). |
| `-s`, `--sheet`     | Sheet index (0-based). Default: 0. Use `--list-sheets` to see IDs.            |
| `--source`          | Path to xlsx (default: `sources/music_bingo_songs.xlsx`).                     |
| `-n`, `--dry-run`   | Do not download; only print what would be done.                               |
| `--ffmpeg-location` | Path to `ffmpeg` (or directory containing it) if not in PATH.                 |

At the end the script prints **Songs downloaded: N** so you can check that everything ran as expected.

### 3. Create the PowerPoint

Builds a presentation from the first column of the chosen sheet. First slide is an intro (“ROUND” / “Starting soon...”); then one slide per song (song name, artist, year) with the background image.

**From Excel (recommended):**

```bash
python create_presentation.py -s <SHEET_ID> -o <OUTPUT_NAME>
```

**With audio and auto-advance:**  
Point `-a` at the folder where the `.m4a` files are (same as the `-f` folder you used for download). Each slide gets that track embedded and is set to advance after the track length.

```bash
python create_presentation.py -s 0 -a output/RETRO -o event
```

Output is saved as `output/event.pptx` (`.pptx` is added if you omit it).

**Options:**

|       Option        |                                                  Description                                                                         |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `-s`, `--sheet`     | Sheet index (0-based). Reads first column only.                                                                                      |
| `-o`, `--output`    | Output path. Default: `output/sample.pptx` or `output/songs_slides.pptx`. If you give only a name, it is saved under `output/`.      |
| `-a`, `--audio-dir` | Folder with `.m4a` files named like the first column (e.g. `output/RETRO`). Embeds audio and sets slide advance to the sound length. |

**Other ways to create slides (without Excel):**

- From a text file (one song per line):  
  `python create_presentation.py songs.txt -o my_slides`
- From command-line titles:  
  `python create_presentation.py "Song One" "Song Two" -o my_slides`
- Sample only (no sheet, no song list):  
  `python create_presentation.py`  
  → `output/sample.pptx`

### 4. Run the slide show

- Open the generated `.pptx` in PowerPoint (or compatible app).
- Start the slide show.
- **Enable “Use Timings”** (or “Advance slides using timings”) so slides advance automatically after each track when you used `-a`.

---

## Full example

```bash
# Activate venv (see Setup)
source venv/bin/activate

# See sheets
python download_songs.py --list-sheets

# Download audio for sheet 0 into output/RETRO
python download_songs.py -f RETRO -s 0
# Check final line: "Songs downloaded: N"

# Create presentation with audio and auto-advance
python create_presentation.py -s 0 -a output/RETRO -o RETRO_event
# Opens as output/RETRO_event.pptx
```

---

## Customization in code

In `create_presentation.py` you can adjust:

- **Content box** (where the song/artist/year text sits):  
  `TEXT_BOX_LEFT`, `TEXT_BOX_TOP`, `TEXT_BOX_WIDTH`, `TEXT_BOX_HEIGHT` (in inches).
- **Debug border:** Set `SHOW_TEXT_BOX_BORDER = True` to draw a red rectangle around that box.

---

## Programmatic use

```python
from create_presentation import (
    create_sample_presentation,
    create_slides_from_songs,
    create_slides_from_song_triples,
    load_songs_from_xlsx,
)

# Sample deck
create_sample_presentation("output/demo.pptx")

# From a list of titles
create_slides_from_songs(["Track 1", "Track 2"], "output/demo.pptx")

# From Excel with optional audio
songs = load_songs_from_xlsx(0)  # 0 = first sheet; returns (song, artist, year, raw_cell)
create_slides_from_song_triples(songs, "output/event.pptx", audio_dir=Path("output/RETRO"))
```

---

## Files in this folder

|            File                  |                                  Purpose                                            |
|----------------------------------|-------------------------------------------------------------------------------------|
| `create_presentation.py`         | Builds the PowerPoint from Excel or a song list; optional audio and advance timing. |
| `download_songs.py`              | Downloads audio from YouTube and trims by intervals; uses same xlsx.                |
| `sources/music_bingo_songs.xlsx` | Source data (songs, optional intervals, YouTube URLs).                              |
| `sources/background.jpeg`        | Background image for every slide.                                                   |
| `output/`                        | Default location for downloaded `.m4a` folders and generated `.pptx` files.         |

---

**Author:** Mintoiu Marius - Flaviu  
**LinkedIn:** www.linkedin.com/in/marius-mintoiu  
**GitHub:** https://github.com/MintoiuM  
**Email Rotaract:** marius.mintoiu@rotaract.ro  
**Email Personal:** mintoiu.marius3012@gmail.com  

No copyright, free to use for any rotaract club. 
If help is needed contact me!
