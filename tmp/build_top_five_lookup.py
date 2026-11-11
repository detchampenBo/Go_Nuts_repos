import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'pnas_report/data'
RAW = DATA / 'transfermarkt-datasets'
history = json.loads((ROOT / 'tmp/research_top_five_historical.json').read_text())
aliases = pd.read_csv(ROOT / 'tmp/top_five_club_aliases.csv')
clubs = pd.read_csv(RAW / 'clubs.csv.gz')


def normalize(name):
    ascii_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    return re.sub('[^a-z0-9]', '', ascii_name.lower())


aliases['key'] = aliases.club_name.map(normalize)
overrides = {
    'GB1': {
        'Hull': 3008, 'Man United': 985, 'Newcastle': 762, 'Oldham': 1078,
        'Sheffield Weds': 1035, 'Stoke': 512, 'Swindon': 352, 'Wimbledon': 114309,
    },
    'IT1': {'Chievo': 862, 'Inter': 46, 'Milan': 5, 'Verona': 276},
    'L1': {
        'Aachen': 8, 'Bielefeld': 10, 'Bochum': 80, 'Cottbus': 25,
        'Dresden': 129, 'Duisburg': 52, 'Dusseldorf': 38, 'Ein Frankfurt': 24,
        'Elversberg': 64, 'FC Koln': 3, 'Hannover': 42, 'Hertha': 44,
        'Kaiserslautern': 2, 'Karlsruhe': 48, 'Leipzig': 497,
        "M'Gladbach": 18, "M'gladbach": 18, 'Munich 1860': 72,
        'Nurnberg': 4, 'Paderborn': 127, 'Schalke 04': 33,
        'Uerdingen': 95, 'Ulm': 69, 'Wattenscheid': 97,
    },
    'FR1': {
        'Ajaccio': 1147, 'Angers': 1420, 'Arles': 11300, 'Auxerre': 290,
        'Bastia': 595, 'Bordeaux': 40, 'Boulogne': 7042, 'Brest': 3911,
        'Caen': 1162, 'Chateauroux': 1175, 'Evian Thonon Gaillard': 14171,
        'Gueugnon': 1397, 'Istres': 2580, 'Le Havre': 738, 'Le Mans': 1164,
        'Lorient': 1158, 'Martigues': 1165, 'Metz': 347, 'Nancy': 1159,
        'Nantes': 995, 'Rennes': 273, 'Sedan': 1081, 'Sochaux': 750,
        'St Etienne': 618, 'Strasbourg': 667, 'Valenciennes': 1423,
    },
    'ES1': {
        'Almeria': 3302, 'Ath Bilbao': 621, 'Ath Madrid': 13, 'Betis': 150,
        'Cadiz': 2687, 'Celta': 940, 'Compostela': 2855, 'Elche': 1531,
        'Espanol': 714, 'Extremadura': 811, 'Granada': 16795, 'Hercules': 7971,
        'La Coruna': 897, 'Las Palmas': 472, 'Lerida': 3239, 'Logrones': 236, 'Malaga': 1084,
        'Mallorca': 237, 'Merida': 38011, 'Murcia': 171, 'Numancia': 2296,
        'Osasuna': 331, 'Oviedo': 2497, 'Recreativo': 2867, 'Salamanca': 1087,
        'Santander': 630, 'Sevilla': 368, 'Sociedad': 681, 'Sp Gijon': 2448,
        'Tenerife': 648, 'Valladolid': 366, 'Vallecano': 367,
        'Villareal': 1050, 'Xerez': 134, 'Zaragoza': 142,
    },
}
league_names = {
    'GB1': 'Premier League', 'IT1': 'Serie A', 'L1': 'Bundesliga',
    'FR1': 'Ligue 1', 'ES1': 'LaLiga',
}
canonical_names = dict(aliases[['club_id', 'club_name']].drop_duplicates('club_id').values)
canonical_names.update(dict(clubs[['club_id', 'name']].values))
canonical_names.update({
    114309: 'Wimbledon FC (-2004)', 811: 'CF Extremadura (-2010)',
    38011: 'CP Merida (-2000)', 236: 'CD Logrones (-2009)',
})
rows = []
for record in history:
    league = record['competition_id']
    for name in record['club_names']:
        club_id = overrides.get(league, {}).get(name)
        if club_id is None:
            candidates = aliases.loc[aliases.key == normalize(name), 'club_id'].unique()
            assert len(candidates) == 1, (league, name, candidates)
            club_id = int(candidates[0])
        rows.append({
            'season_start_year': record['season_start_year'],
            'transfer_season': record['transfer_season'],
            'competition_id': league,
            'league_name': league_names[league],
            'club_id': club_id,
            'club_name': 'VfB Leipzig' if league == 'L1' and name == 'Leipzig' else canonical_names[club_id],
            'source_club_name': name,
            'source_url': record['source_url'],
        })

games = pd.read_csv(RAW / 'games.csv.gz')
games = games[games.competition_id.isin(league_names)]
members = pd.concat([
    games[['season', 'competition_id', f'{side}_club_id', f'{side}_club_name']]
    .set_axis(['season_start_year', 'competition_id', 'club_id', 'source_club_name'], axis=1)
    for side in ['home', 'away']
]).drop_duplicates(['season_start_year', 'competition_id', 'club_id'])
for record in members.to_dict('records'):
    year, league, club_id = record['season_start_year'], record['competition_id'], record['club_id']
    record.update({
        'transfer_season': f'{year % 100:02d}/{(year + 1) % 100:02d}',
        'league_name': league_names[league],
        'club_name': canonical_names[club_id],
        'source_url': f'https://www.transfermarkt.co.uk/{league_names[league].lower().replace(" ", "-")}/gesamtspielplan/wettbewerb/{league}/saison_id/{year}',
    })
    rows.append(record)

lookup = pd.DataFrame(rows).sort_values(['season_start_year', 'competition_id', 'club_name'])
assert not lookup.duplicated(['transfer_season', 'club_id']).any()
counts = lookup.groupby(['season_start_year', 'competition_id']).size()
for (year, league), count in counts.items():
    expected = {
        'GB1': 22 if year <= 1994 else 20,
        'IT1': 18 if year <= 2003 else 20,
        'L1': 18,
        'FR1': 18 if 1997 <= year <= 2001 or year >= 2023 else 20,
        'ES1': 22 if 1995 <= year <= 1996 else 20,
    }[league]
    assert count == expected, (year, league, count, expected)
assert len(counts) == 34 * 5
lookup.to_csv(DATA / 'top_five_league_clubs.csv', index=False)
print(f'Saved {len(lookup):,} memberships, {lookup.club_id.nunique()} clubs, {len(counts)} league-seasons')
