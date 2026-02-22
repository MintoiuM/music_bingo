import random
from src.track_extractor.ExcelTracks import ExcelTracks

import csv
class BingoManager:
    def __init__(self, num_tickets, playlist_store="gsheets", playlist_id=None, gsheets_url=None, sheet_index=2, min_bingo_threshold=None):
        """
        Initialize the BingoTicketsGenerator with a dictionary of tracks and the number of tickets.

        Parameters:
        - tracks: Dictionary of tracks to choose from.
        - num_tickets: The number of unique tickets to generate.
        - min_bingo_threshold: Require first bingo only after this many songs (default: 30, or len(tracks)//2 for small playlists).
        """
        self.tracks = dict()
        if playlist_store == "excel":
            excel_tracks_extractor = ExcelTracks(gsheets_url, sheet_index)
            self.tracks = excel_tracks_extractor.tracks
            self.round_name = excel_tracks_extractor.round_name

        self.num_tickets = num_tickets
        self.tickets = []  # To store generated tickets
        n = len(self.tracks)
        self.min_bingo_threshold = min_bingo_threshold if min_bingo_threshold is not None else (min(30, n // 2) if n < 80 else 30)
        self._check_tracks_count()

    def _check_tracks_count(self):
        """Each ticket needs 9 unique songs; ensure we have at least 9 tracks."""
        n = len(self.tracks)
        if n < 9:
            raise ValueError(
                f"Not enough tracks to generate bingo tickets: found {n}, need at least 9. "
                "Add more songs to your Excel source (Source.xlsx, sheet index 0) with columns: ID | Song Name | Artist(s)."
            )

    def generate_ticket(self):
        """
        Generate a single ticket with 9 unique songs chosen at random.

        Returns:
        - A list of 9 unique songs.
        """
        ticket = random.sample(list(self.tracks.keys()), 9)
        return ticket

    def generate_tickets(self, iteration=0):
        """
        Generate the specified number of unique tickets.

        Returns:
        - A list of unique tickets (each ticket is a list of 9 songs).
        """
        generated_tickets = set()
        while len(generated_tickets) < self.num_tickets:
            ticket = tuple(sorted(self.generate_ticket()))
            generated_tickets.add(ticket)
        
        min_bingo_song_index = len(self.tracks.keys())
        min_line_song_index = len(self.tracks.keys())
        for i, ticket in enumerate(generated_tickets):
            bingo_min_song_index = max(ticket)+1
            line_min_song_index = min([max([ticket[0], ticket[1], ticket[2]]), max([ticket[3], ticket[4], ticket[5]]), max([ticket[6], ticket[7], ticket[8]]), max([ticket[0], ticket[3], ticket[6]]), max([ticket[1], ticket[4], ticket[7]]), max([ticket[2], ticket[5], ticket[8]])])
            if bingo_min_song_index < min_bingo_song_index:
                min_bingo_song_index = bingo_min_song_index
            if line_min_song_index < min_line_song_index:
                min_line_song_index = line_min_song_index
        print(f"Generating tickets... iteration {iteration} min_line_song_index: {min_line_song_index} min_bingo_song_index: {min_bingo_song_index}")

        max_iterations = 100  # stop after this many tries to avoid running forever
        if min_bingo_song_index <= self.min_bingo_threshold:
            if iteration >= max_iterations:
                print(f"⚠️ Stopping after {max_iterations} attempts (min_bingo_song_index={min_bingo_song_index}, threshold={self.min_bingo_threshold}). Using these tickets anyway.")
            else:
                self.generate_tickets(iteration + 1)
                return
        
        shuffled_tickets=[]
        for ticket in generated_tickets:
            shuffled_ticket = list(ticket)
            random.shuffle(shuffled_ticket)
            shuffled_tickets.append(shuffled_ticket)
        self.tickets = shuffled_tickets

        with open(f'./exported_data/{self.round_name}.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["Ticket #ID","Începând de la a câta piesa este linie?", "Începând de la a câta piesă este Bingo?", "Song 1", "Song 2", "Song 3", "Song 4", "Song 5", "Song 6", "Song 7", "Song 8", "Song 9"])
            for i, ticket in enumerate(self.tickets):
                bingo_min_song_index = max(ticket)
                line_min_song_index = min([max([ticket[0], ticket[1], ticket[2]]), max([ticket[3], ticket[4], ticket[5]]), max([ticket[6], ticket[7], ticket[8]]), max([ticket[0], ticket[3], ticket[6]]), max([ticket[1], ticket[4], ticket[7]]), max([ticket[2], ticket[5], ticket[8]])])
                writer.writerow([f"{i+1}"]+ [line_min_song_index] + [bingo_min_song_index] + [f"{song}. {self.tracks[song]['name']}" for song in ticket])

        return self.tickets

    def find_bingo_rounds(self):
        tracks_order = list(self.tracks.keys())
        bingo_rounds = []
        line_rounds = []
        for i in range(len(tracks_order)):
            bingo_tickets_count = 0
            for (ticket_index, ticket) in enumerate(self.tickets):
                is_ticket_bingo = True
                is_line_ticket = True
                for ticket_item in ticket:
                    if ticket_item not in tracks_order[:i+1]:
                        is_ticket_bingo = False
                        break
                line_min_song_index = min([max([ticket[0], ticket[1], ticket[2]]), max([ticket[3], ticket[4], ticket[5]]), max([ticket[6], ticket[7], ticket[8]]), max([ticket[0], ticket[3], ticket[6]]), max([ticket[1], ticket[4], ticket[7]]), max([ticket[2], ticket[5], ticket[8]])])
                if line_min_song_index > i+1:
                    is_line_ticket = False
                if is_line_ticket:
                    line_rounds.append(i)
                    if len(line_rounds) == 1:
                        print(f"First Line: Starting with the song {i+1} with the ticket #{ticket_index+1}")
                        print(f"The ticket is: {ticket}")
                if is_ticket_bingo:
                    bingo_tickets_count += 1
                    if bingo_tickets_count == 1 and len(bingo_rounds) == 0:
                        print(f"First Bingo: Starting with song {i+1} with the ticket #{ticket_index+1}")
                        print(f"The ticket is: {ticket}")
                        # for element in ticket:
                        #     print(self.tracks[element]['name'])
            if bingo_tickets_count > 0:
                bingo_rounds.append(i)
                # print(f"Bingo! Round {i+1} with {bingo_tickets_count} tickets")
