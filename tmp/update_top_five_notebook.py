import json
from pathlib import Path


path = Path('pnas_report/notebooks/dataclean.ipynb')
original = path.read_bytes()
notebook = json.loads(original)
assert ''.join(notebook['cells'][16]['source']).strip() == 'reduced_transfers_with_players = cleaned_transfers_with_players.copy()'
assert not ''.join(notebook['cells'][17]['source']).strip()

markdown = """### Keep transfers involving a top-five league club

Keep a row when **either** `from_club_id` **or** `to_club_id` belongs to the Premier League, Serie A, Bundesliga, Ligue 1, or LaLiga in that row's `transfer_season`. Both endpoints may qualify; the other endpoint may be outside those leagues. This reduces transfer rows and club nodes while retaining transfers into and out of the five leagues.

The lookup is `../data/top_five_league_clubs.csv`: one row per season, league, and senior club ID, covering **1993/94–2026/27**. Club names are included for inspection; matching uses IDs to avoid spelling differences. Membership comes from the local league match records for 2012/13–2025/26 and Football-Data's season archives for the remaining covered seasons. See [sources and historical club ID checks](../notes/top_five_league_membership_sources.md).

Use the recorded football season, rather than the calendar year of `transfer_date`: January 2015 belongs to 2014/15. A club's current league or membership in another season does not qualify it.

Membership for **2027/28** is not yet confirmed. Rows outside lookup coverage are excluded from the result, retained separately in `outside_lookup_transfers`, and counted explicitly below. In this snapshot, those 13 rows involve Danish/Korean clubs or the `Retired`/`Without Club` labels; none establishes a top-five league endpoint.
"""
code = """top_five_league_clubs = pd.read_csv(data_dir.parent / 'top_five_league_clubs.csv')
top_five_club_lookup = pd.MultiIndex.from_frame(
    top_five_league_clubs[['transfer_season', 'club_id']]
)

outside_lookup_transfers = reduced_transfers_with_players[
    ~reduced_transfers_with_players['transfer_season'].isin(top_five_league_clubs['transfer_season'])
].copy()

from_top_five = pd.MultiIndex.from_frame(
    reduced_transfers_with_players[['transfer_season', 'from_club_id']]
).isin(top_five_club_lookup)
to_top_five = pd.MultiIndex.from_frame(
    reduced_transfers_with_players[['transfer_season', 'to_club_id']]
).isin(top_five_club_lookup)

top_five_filter_summary = pd.DataFrame({
    'Transfer rows': [len(reduced_transfers_with_players)],
    'Club nodes': [pd.unique(reduced_transfers_with_players[['from_club_id', 'to_club_id']].values.ravel()).size],
}, index=['Before'])

reduced_transfers_with_players = reduced_transfers_with_players[from_top_five | to_top_five].copy()

top_five_filter_summary.loc['After'] = [
    len(reduced_transfers_with_players),
    pd.unique(reduced_transfers_with_players[['from_club_id', 'to_club_id']].values.ravel()).size,
]
display(top_five_filter_summary)
print(f'Rows outside lookup coverage (excluded): {len(outside_lookup_transfers):,}')
if not outside_lookup_transfers.empty:
    display(outside_lookup_transfers.groupby('transfer_season').size().rename('Transfer rows'))
"""
notebook['cells'].insert(17, {
    'cell_type': 'markdown',
    'id': 'top-five-league-membership',
    'metadata': {},
    'source': markdown.splitlines(keepends=True),
})
notebook['cells'][18]['source'] = code.splitlines(keepends=True)
notebook['cells'][18]['execution_count'] = None
notebook['cells'][18]['outputs'] = []
Path('tmp/dataclean_before_top_five.ipynb').write_bytes(original)
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('Added top-five season lookup and OR filter after reduced_transfers_with_players')
