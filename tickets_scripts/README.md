# Music Bingo Tickets — Step-by-Step Guide

This app generates Music Bingo tickets from an Excel playlist and turns them into printable HTML/PDF using a background template.

---

## What you need

- **Python 3** (with `venv` and `pip`)
- **Node.js** (for PDF generation)
- An **Excel file** with your song list
- A **background image** for the tickets (optional; e.g. in `sources/template/`)

---

## Step 1: Prepare the Excel playlist

1. Put your Excel file here:
   ```
   tickets_scripts/sources/source_tickets.xlsx
   ```
2. In the workbook, use **one sheet per round**. The script uses **sheet index 0** by default (the 1st sheet). You can change this in `index_real.py` (see `sheet_index=4`).
3. Sheet format:
   - **Column A:** Track ID (numbers: 1, 2, 3, …)
   - **Column B:** Song name
   - **Column C:** Artist(s) — optional
   - Row 1 can be a header.

Example:

| A (ID) | B (Song name)     | C (Artist)   |
|--------|-------------------|--------------|
| 1      | Song Title One    | Artist Name  |
| 2      | Song Title Two    | Another One  |

You need **at least 9 songs** in the sheet to generate tickets.

---

## Step 2: Set up Python and generate tickets (JSON)

1. Open a terminal and go to the app folder:
   ```bash
   cd path/to/music_bingo_scripts/tickets_scripts
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   On Windows: `venv\Scripts\activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Adjust settings in `index_real.py`:
   - `sheet_index=0` — which sheet to use (0 = first sheet)
   - `num_tickets=500` — how many tickets to generate

5. Run the ticket generator:
   ```bash
   python3 index_real.py
   ```

6. You should see something like:
   - `Loaded N tracks from sheet '...'`
   - `All tickets unique: True`
   - `Exported 500 tickets to /output/tickets folder.`

7. Result:
   - **JSON tickets:** `output/tickets/ticket_1.json`, `ticket_2.json`, …
   - **CSV (round stats):** `exported_data/<round_name>.csv`

---

## Step 3: Add a background template (optional)

1. Put your background image in:
   ```
   tickets_scripts/sources/template/
   ```
2. Use the **exact name** you will pass to the PDF script, e.g.:
   - `audience_choice.png` or `audience_choice.jpg`

If the file is missing, the script will still run and use a blank background.

---

## Step 4: Generate HTML or PDF

1. Stay in the same folder (with JSON tickets already in `output/tickets`):
   ```bash
   cd path/to/music_bingo_scripts/tickets_scripts
   ```

2. Install Node dependencies (first time only):
   ```bash
   npm install
   ```

3. Generate **HTML** (to preview or print from the browser):
   ```bash
   node generate-pdf.js audience_choice.png -html -o audience_choice
   ```
   Or with the default template name:
   ```bash
   node generate-pdf.js -html
   ```

4. Generate **PDF** directly:
   ```bash
   node generate-pdf.js audience_choice.png -pdf -o audience_choice
   ```

5. Arguments:
   - First non-option argument = template name (e.g. `audience_choice.png` or `audience_choice`). The script looks for `sources/template/<name>.png` or `.jpg`.
   - `-html` — output HTML only
   - `-pdf` — output PDF (needs a supported environment like Chronium(easiest); otherwise use HTML and “Print to PDF” from the browser)
   - `-o <name>` — output file name without extension (default: `tickets`)

6. Output is written to:
   ```
   output/tickets_final/<name>.html
   output/tickets_final/<name>.pdf
   ```

---

## Quick reference

| Step | Command / location |
|------|---------------------|
| Excel file | `sources/source_tickets.xlsx` |
| Template image | `sources/template/<name>.png` or `.jpg` |
| Generate tickets | `python3 index_real.py` (from `tickets_scripts`, with venv active) |
| JSON tickets | `output/tickets/ticket_*.json` |
| HTML/PDF | `node generate-pdf.js <template> -pdf -o <name>` |
| Final files | `output/tickets_final/<name>.html` and `<name>.pdf` |

---

## Troubleshooting

- **“Excel file not found”** — Ensure `sources/source_tickets.xlsx` exists and you run `index_real.py` from `tickets_scripts`.
- **“Not enough tracks”** — The chosen sheet must have at least 9 rows with valid ID (column A) and song name (column B).
- **“Background not found”** — Put the image in `sources/template/` with the same name you pass to `generate-pdf.js` (e.g. `audience_choice.png`).
- **“No such file or directory: exported_data”** — Create the folder `exported_data` in the same directory as `index_real.py` (or the script can be updated to create it automatically).
- **PDF generation fails** — Open the generated HTML in a browser and use **Print → Save as PDF**.

---

**Author:** Mintoiu Marius - Flaviu  
**LinkedIn:** www.linkedin.com/in/marius-mintoiu  
**GitHub:** https://github.com/MintoiuM  
**Email Rotaract:** marius.mintoiu@rotaract.ro  
**Email Personal:** mintoiu.marius3012@gmail.com  

No copyright, free to use for any rotaract club. If help is needed contact me!
