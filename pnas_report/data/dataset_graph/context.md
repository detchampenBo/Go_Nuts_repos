# Dataset 1 transfer network

`cleaned_transfers_with_players.csv.gz` contains 105,644 Transfermarkt transfer records joined with player details for 18,985 players. Each row records a player's move and includes the transfer date, season, and age at the time of the move when available.

## Graph terminology

- **Club node** — A club identified by its Transfermarkt ID. The fields `from_club_id` and `to_club_id` identify the clubs at either end of a transfer.
- **Transfer link** — A directed, weighted link from the club identified by `from_club_id` to the club identified by `to_club_id`.
- **Club label** — For readable graph visuals, map `from_club_id` to `from_club_name` and `to_club_id` to `to_club_name`. Use the club ID to identify the node and the club name as its display label.
