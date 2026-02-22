import sys
import os
import json
from src.BingoManager import BingoManager

sys.setrecursionlimit(100000)

# Initialize manager (same as before)
bingo_manager = BingoManager(
    playlist_store="excel",
    gsheets_url=os.path.normpath(os.path.join(os.path.dirname(__file__), "sources", "source_tickets.xlsx")),
    sheet_index=0,
    num_tickets=500
)
bingo_manager.generate_tickets()

print(f"✅ All tickets unique: {len(bingo_manager.tickets) == len(set(map(tuple, bingo_manager.tickets)))}")

# Generate round statistics (same)
bingo_manager.find_bingo_rounds()

# Create output folder for JSON
os.makedirs("./output/tickets", exist_ok=True)

# Export each ticket as a JSON file
for i, ticket in enumerate(bingo_manager.tickets):
    songs = []
    for song_id in ticket:
        song_info = bingo_manager.tracks[song_id]
        songs.append({
            "title": song_info["name"],       # song title
            "artists": song_info.get("artists", "Unknown")  # ensure field exists
        })

    ticket_data = {
        "id": i + 1,
        "round_name": bingo_manager.round_name,
        "songs": songs
    }

    # Save one JSON per ticket
    with open(f"./output/tickets/ticket_{i+1}.json", "w", encoding="utf-8") as f:
        json.dump(ticket_data, f, indent=2, ensure_ascii=False)

print(f"🎟️ Exported {len(bingo_manager.tickets)} tickets to /output/tickets folder.")
