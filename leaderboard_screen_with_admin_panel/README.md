# Music Bingo Leaderboard & Admin Panel

A Flask web app that shows a **leaderboard** for Music Bingo (teams ranked by tickets) and an **admin panel** to manage teams and ticket counts per round. The leaderboard auto-refreshes so you can show it on a big screen while you update data from the admin on another device.

---

## What it does

- **Leaderboard** (`/`): Full-screen view with a vinyl-style podium (top 3) and a list of the rest. Sorted by total tickets (sum of all rounds). Designed for 1920×1080 but scales to fit the window.
- **Admin panel** (`/admin`): Add/delete teams, set ticket counts per round (Round 1–5), search teams, and save round data in bulk.
- **Data**: Stored in `leaderboard.json` in the project folder. Each team has a name and a list of ticket counts per round; total tickets = sum of rounds.

---

## Requirements

- Python 3.x
- Dependencies: `Flask`, `Werkzeug` (see `requirements.txt`)

---

## Setup

1. **Create a virtual environment (recommended):**
   ```bash
   cd leaderboard_screen_with_admin_panel
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # or: venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional – background images:**  
   For the leaderboard and admin styling you can add:
   - `static/leaderboard-bg.png` – tiled background for the leaderboard
   - `static/container-bg.png` – background for admin section panels  
   If these are missing, the app still works; it uses fallback colors.

---

## Running the app

From the project folder (with `venv` activated if you use it):

```bash
python app.py
```

- **Port:** 5000  
- **Host:** `0.0.0.0` (reachable from other devices on the same network)

You’ll see URLs in the console, for example:

- Leaderboard: `http://localhost:5000/` or `http://<your-LAN-IP>:5000/`
- Admin panel: `http://localhost:5000/admin` or `http://<your-LAN-IP>:5000/admin`

**Suggested use:**  
- Open the **leaderboard** on the projector/screen (e.g. `http://<LAN-IP>:5000/`).  
- Open the **admin panel** on a laptop/tablet (e.g. `http://<LAN-IP>:5000/admin`) to add teams and enter tickets.

---

## Using the Leaderboard

- **URL:** `http://<host>:5000/`
- Shows:
  - **Top 3:** Podium with vinyl-style circles (gold / silver / bronze), team name and total tickets.
  - **4th place and below:** Two columns of rows with rank, team name, and total tickets.
- The page **auto-refreshes every 2 seconds** by refetching `/api/teams`, so changes made in the admin appear on the leaderboard shortly after you save.
- No login; anyone who can reach the server can view it. Keep the admin URL for staff only.

---

## Using the Admin Panel

- **URL:** `http://<host>:5000/admin`
- **Link:** “← Back to Leaderboard” goes to `/`.

### Add a team

1. In **“Add New Team”**, type the team name.
2. Click **Add Team**.  
   The new team appears in the list with 0 tickets for all rounds.

### Manage tickets by round

- Use the **Round 1**, **Round 2**, … **Round 5** tabs to switch which round you’re editing.
- For each team you see:
  - Total tickets (sum of all rounds).
  - Current round’s ticket count (e.g. “Round 1: 3”).
  - An input field for that round’s tickets.
- Enter the ticket count in the input (0 or more).
- Click **Save Round** to save **all** teams’ values for the **currently selected round** in one go.  
  The page reloads and the leaderboard (on the other screen) will update on its next refresh.

**Tip:** You can press **Enter** in a ticket input to jump to the next team’s input for fast data entry.

### Search teams

- Use the **“Search teams...”** box to filter the list by team name (case-insensitive).  
- Press **Escape** to clear the search.

### Delete a team

- Click **Delete** next to a team and confirm. The team is removed from the data and from both leaderboard and admin.

---

## Data file: `leaderboard.json`

- Location: same folder as `app.py`.
- Structure:
  ```json
  {
    "teams": [
      { "name": "Team A", "rounds": [2, 1, 0, 0, 0] },
      { "name": "Team B", "rounds": [0, 3, 1, 0, 0] }
    ]
  }
  ```
- `rounds` has exactly 5 numbers (Round 1–5). Total tickets = sum of `rounds`.  
- You can edit this file by hand if needed; the app will normalize and fix invalid values on load.

---

## API (for reference)

- `GET /api/teams` – list teams (leaderboard order, with `total_tickets`).
- `POST /api/teams` – add team; body: `{ "name": "Team Name" }`.
- `PUT /api/round/<1–5>` – set tickets for that round for all teams; body: `{ "ticketsByTeam": { "Team A": 2, "Team B": 0 } }`.
- `DELETE /api/teams/<team_name>` – delete a team.

---

## Summary

| Task              | Where                | Action                                              |
|-------------------|----------------------|-----------------------------------------------------|
| Show rankings     | Leaderboard (`/`)    | Open on big screen; it auto-refreshes every 2 s.    |
| Add teams         | Admin → Add New Team | Enter name, click Add Team.                         |
| Enter tickets     | Admin → Round tabs   | Select round, type numbers, click Save Round.       |
| Find a team       | Admin                | Use the search box.                                 |
| Remove a team     | Admin                | Click Delete next to the team and confirm.          |

---

**Author:** Mintoiu Marius - Flaviu  
**LinkedIn:** www.linkedin.com/in/marius-mintoiu  
**GitHub:** https://github.com/MintoiuM  
**Email Rotaract:** marius.mintoiu@rotaract.ro  
**Email Personal:** mintoiu.marius3012@gmail.com  

No copyright, free to use for any rotaract club. If help is needed contact me!
