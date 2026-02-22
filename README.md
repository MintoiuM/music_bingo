# Music Bingo Scripts

A set of tools for running **Music Bingo** events: from preparing tickets and song slides to showing a live leaderboard on the day. Everything is designed for Rotaract (or similar) clubs and can be used freely.

---

## What is Music Bingo?

Music Bingo is a game where players have bingo-style tickets with song titles. Songs are played (or shown), and the first team to complete a line (or full card) wins. This project helps you:

1. **Create the tickets** — from your song list to printable PDFs  
2. **Run the show** — slides for each song (with optional audio)  
3. **Display the leaderboard** — rankings on a big screen, updated live

---

## The three parts of this project

| Part | Folder | What it’s for |
|------|--------|----------------|
| **Tickets** | `tickets_scripts/` | Turn an Excel playlist into unique bingo tickets, then into HTML or PDF you can print. |
| **Song slides** | `screens_with_songs_on_event_day/` | Build a PowerPoint (or similar) with one slide per song. You can optionally download and trim audio from YouTube and have slides advance with the music. |
| **Leaderboard** | `leaderboard_screen_with_admin_panel/` | A small web app: a full-screen leaderboard for the projector and an admin page to add teams and enter ticket counts per round. The leaderboard refreshes automatically. |

Each part has its own **README** in that folder with setup and step-by-step instructions.

---

## Typical workflow

1. **Before the event**  
   - Put your song list in Excel (see each folder’s README for the exact format).  
   - **Tickets:** Run the ticket scripts to generate and print your bingo tickets.  
   - **Slides:** Create the PowerPoint from the same (or a similar) Excel file; optionally download audio and create a version with auto-advance.  

2. **On the event day**  
   - **Leaderboard:** Start the leaderboard app, open the leaderboard view on the big screen and the admin panel on a laptop/tablet.  
   - Add teams and enter ticket counts as rounds finish; the screen updates automatically.  
   - Run your song slides (and music) as usual for the game.

---

## What you need (in short)

- **Tickets:** Python, Node.js, and an Excel file with your songs.  
- **Slides:** Python, FFmpeg (if you want to download/trim audio), and an Excel file (and optionally a background image).  
- **Leaderboard:** Python and a browser; no login, best used on a local network.

For details, requirements, and commands, see the README in each folder.

---

**Author:** Mintoiu Marius - Flaviu  
**LinkedIn:** www.linkedin.com/in/marius-mintoiu  
**GitHub:** https://github.com/MintoiuM  
**Email Rotaract:** marius.mintoiu@rotaract.ro  
**Email Personal:** mintoiu.marius3012@gmail.com  

No copyright, free to use for any rotaract club. 
If help is needed contact me!
