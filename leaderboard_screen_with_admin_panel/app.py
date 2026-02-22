#!/usr/bin/env python3
"""
Music Bingo Leaderboard Application
Tracks tickets bought per team with live updates
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Path to JSON data file
DATA_FILE = 'leaderboard.json'
NUM_ROUNDS = 5


def get_lan_ip() -> str | None:
    """
    Best-effort LAN IP detection for printing a usable URL.
    Returns None if we can't determine it.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable; no packets are sent.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _coerce_non_negative_int(value, default: int = 0) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return n if n >= 0 else 0


def normalize_team(team: dict) -> tuple[dict, bool]:
    """
    Ensure a team has the round-based schema:
      { "name": str, "rounds": [int, int, int, int, int] }

    Returns (team, changed).
    """
    changed = False

    # Name normalization
    name = str(team.get("name", "")).strip()
    if not name:
        name = "Unknown"
    if team.get("name") != name:
        team["name"] = name
        changed = True

    rounds = team.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != NUM_ROUNDS:
        # Migrate old schema: { tickets: <int> }
        old_total = _coerce_non_negative_int(team.get("tickets"), default=0)
        rounds = [0] * NUM_ROUNDS
        rounds[0] = old_total
        team["rounds"] = rounds
        changed = True
    else:
        coerced = [_coerce_non_negative_int(x, default=0) for x in rounds]
        if coerced != rounds:
            team["rounds"] = coerced
            changed = True

    # Remove legacy field if present
    if "tickets" in team:
        del team["tickets"]
        changed = True

    return team, changed

def load_data():
    """Load leaderboard data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {'teams': []}

        teams = data.get("teams", [])
        if not isinstance(teams, list):
            return {'teams': []}

        any_changed = False
        normalized = []
        for t in teams:
            if not isinstance(t, dict):
                any_changed = True
                continue
            t2, changed = normalize_team(t)
            normalized.append(t2)
            any_changed = any_changed or changed

        data["teams"] = normalized
        if any_changed:
            save_data(data)
        return data
    return {'teams': []}

def save_data(data):
    """Save leaderboard data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_teams_with_totals() -> list[dict]:
    """Return teams with normalized schema + computed `total_tickets`."""
    data = load_data()
    teams = data.get('teams', [])
    computed: list[dict] = []
    for t in teams:
        t2, _ = normalize_team(dict(t))
        total = sum(_coerce_non_negative_int(x, default=0) for x in t2.get("rounds", [0] * NUM_ROUNDS))
        t2["total_tickets"] = total
        computed.append(t2)
    return computed


def get_leaderboard_teams() -> list[dict]:
    """Teams sorted by total tickets (desc), then name (asc)."""
    teams = get_teams_with_totals()
    return sorted(
        teams,
        key=lambda x: (-_coerce_non_negative_int(x.get("total_tickets"), default=0), str(x.get("name", "")).lower()),
    )


def get_admin_teams() -> list[dict]:
    """Teams sorted alphabetically by name (asc)."""
    teams = get_teams_with_totals()
    return sorted(teams, key=lambda x: str(x.get("name", "")).lower())

@app.route('/')
def leaderboard():
    """Display the leaderboard"""
    teams = get_leaderboard_teams()
    return render_template('leaderboard.html', teams=teams)

@app.route('/admin')
def admin():
    """Admin interface for editing teams"""
    teams = get_admin_teams()
    return render_template('admin.html', teams=teams, num_rounds=NUM_ROUNDS)

@app.route('/api/teams', methods=['GET'])
def api_get_teams():
    """API endpoint to get current teams (for live updates)"""
    teams = get_leaderboard_teams()
    return jsonify({'teams': teams})

@app.route('/api/teams', methods=['POST'])
def api_add_team():
    """API endpoint to add a new team"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Team name is required'}), 400
    
    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])
    
    # Check if team already exists
    for team in teams:
        if team['name'].lower() == name.lower():
            return jsonify({'error': 'Team already exists'}), 400
    
    # Add new team
    teams.append({
        'name': name,
        'rounds': [0] * NUM_ROUNDS
    })
    
    leaderboard_data['teams'] = teams
    save_data(leaderboard_data)
    
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})

@app.route('/api/teams/<team_name>/add-tickets', methods=['POST'])
def api_add_tickets(team_name):
    """API endpoint to add tickets to a team (defaults to Round 1)."""
    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])
    data = request.get_json() or {}

    round_number = _coerce_non_negative_int(data.get("round"), default=1)
    if round_number < 1 or round_number > NUM_ROUNDS:
        round_number = 1
    
    tickets_to_add = data.get('tickets', 1)
    try:
        tickets_to_add = int(tickets_to_add)
        if tickets_to_add < 1:
            return jsonify({'error': 'Number of tickets must be at least 1'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid number of tickets'}), 400
    
    found = False
    for team in teams:
        if team['name'].lower() == team_name.lower():
            team, _ = normalize_team(team)
            idx = round_number - 1
            team["rounds"][idx] = _coerce_non_negative_int(team["rounds"][idx], default=0) + tickets_to_add
            found = True
            break
    
    if not found:
        return jsonify({'error': 'Team not found'}), 404
    
    save_data(leaderboard_data)
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})


@app.route('/api/teams/<team_name>/round/<int:round_number>', methods=['PUT'])
def api_set_round_tickets(team_name, round_number: int):
    """Set the ticket count for a specific round (absolute value)."""
    if round_number < 1 or round_number > NUM_ROUNDS:
        return jsonify({'error': f'Round must be between 1 and {NUM_ROUNDS}'}), 400

    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])
    data = request.get_json() or {}

    try:
        tickets_value = int(data.get("tickets"))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid number of tickets'}), 400

    if tickets_value < 0:
        return jsonify({'error': 'Tickets cannot be negative'}), 400

    found = False
    for team in teams:
        if team['name'].lower() == team_name.lower():
            team, _ = normalize_team(team)
            team["rounds"][round_number - 1] = tickets_value
            found = True
            break

    if not found:
        return jsonify({'error': 'Team not found'}), 404

    save_data(leaderboard_data)
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})


@app.route('/api/round/<int:round_number>', methods=['PUT'])
def api_bulk_set_round_tickets(round_number: int):
    """Set ticket counts for a specific round for multiple teams at once."""
    if round_number < 1 or round_number > NUM_ROUNDS:
        return jsonify({'error': f'Round must be between 1 and {NUM_ROUNDS}'}), 400

    payload = request.get_json() or {}
    tickets_by_team = payload.get("ticketsByTeam") or payload.get("tickets_by_team")
    if not isinstance(tickets_by_team, dict):
        return jsonify({'error': 'Expected JSON body: { "ticketsByTeam": { "Team": 0, ... } }'}), 400

    # Validate first (avoid partial saves)
    normalized_updates: dict[str, int] = {}
    for raw_name, raw_tickets in tickets_by_team.items():
        name = str(raw_name).strip()
        if not name:
            continue
        try:
            tickets_value = int(raw_tickets)
        except (TypeError, ValueError):
            return jsonify({'error': f'Invalid tickets value for "{name}"'}), 400
        if tickets_value < 0:
            return jsonify({'error': f'Tickets cannot be negative for "{name}"'}), 400
        normalized_updates[name.lower()] = tickets_value

    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])

    # Apply updates
    missing = []
    for name_lc, tickets_value in normalized_updates.items():
        matched = False
        for team in teams:
            if str(team.get('name', '')).strip().lower() == name_lc:
                team, _ = normalize_team(team)
                team["rounds"][round_number - 1] = tickets_value
                matched = True
                break
        if not matched:
            missing.append(name_lc)

    if missing:
        return jsonify({'error': f'Unknown team(s): {", ".join(missing)}'}), 400

    save_data(leaderboard_data)
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})

@app.route('/api/teams/<team_name>', methods=['PUT'])
def api_update_team(team_name):
    """API endpoint to update team name or rounds"""
    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])
    data = request.get_json() or {}
    
    found = False
    for team in teams:
        if team['name'].lower() == team_name.lower():
            team, _ = normalize_team(team)
            if 'new_name' in data:
                team['name'] = data['new_name'].strip()
            if 'rounds' in data and isinstance(data['rounds'], list) and len(data['rounds']) == NUM_ROUNDS:
                team['rounds'] = [_coerce_non_negative_int(x, default=0) for x in data['rounds']]
            found = True
            break
    
    if not found:
        return jsonify({'error': 'Team not found'}), 404
    
    save_data(leaderboard_data)
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})

@app.route('/api/teams/<team_name>', methods=['DELETE'])
def api_delete_team(team_name):
    """API endpoint to delete a team"""
    leaderboard_data = load_data()
    teams = leaderboard_data.get('teams', [])
    
    teams = [t for t in teams if t['name'].lower() != team_name.lower()]
    
    if len(teams) == len(leaderboard_data.get('teams', [])):
        return jsonify({'error': 'Team not found'}), 404
    
    leaderboard_data['teams'] = teams
    save_data(leaderboard_data)
    return jsonify({'success': True, 'teams': get_leaderboard_teams()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Initialize data file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        save_data({'teams': []})
    
    host = '0.0.0.0'
    port = 5000
    debug = True

    # Avoid printing twice with Flask's debug reloader
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    if (not debug) or is_reloader_child:
        lan_ip = get_lan_ip()

        print("Starting Music Bingo Leaderboard...")
        print(f"Leaderboard: http://localhost:{port}/")
        print(f"Admin Panel: http://localhost:{port}/admin")
        print(f"Leaderboard: http://127.0.0.1:{port}/")
        print(f"Admin Panel: http://127.0.0.1:{port}/admin")
        if lan_ip:
            print(f"Leaderboard (LAN): http://{lan_ip}:{port}/")
            print(f"Admin Panel (LAN): http://{lan_ip}:{port}/admin")

    app.run(debug=debug, host=host, port=port)
