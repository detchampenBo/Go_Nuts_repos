import concurrent.futures
import io
import json
from pathlib import Path

import pandas as pd
import requests


LEAGUES = {'GB1': 'E0', 'L1': 'D1', 'IT1': 'I1', 'ES1': 'SP1', 'FR1': 'F1'}


def fetch(item):
    year, competition_id, division = item
    season_code = f'{year % 100:02d}{(year + 1) % 100:02d}'
    url = f'https://www.football-data.co.uk/mmz4281/{season_code}/{division}.csv'
    response = requests.get(url, timeout=40)
    response.raise_for_status()
    try:
        content = response.content.decode('utf-8-sig')
    except UnicodeDecodeError:
        content = response.content.decode('cp1252')
    frame = pd.read_csv(io.StringIO(content), usecols=['HomeTeam', 'AwayTeam'])
    names = sorted(set(frame['HomeTeam'].dropna()) | set(frame['AwayTeam'].dropna()))
    return {'season_start_year': year, 'transfer_season': f'{year % 100:02d}/{(year + 1) % 100:02d}', 'competition_id': competition_id, 'source_url': url, 'club_names': names, 'match_rows': len(frame)}


if __name__ == '__main__':
    tasks = [(year, competition_id, division) for year in [*range(1993, 2012), 2026] for competition_id, division in LEAGUES.items()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        records = sorted(pool.map(fetch, tasks), key=lambda r: (r['season_start_year'], r['competition_id']))
    path = Path('tmp/research_top_five_historical.json')
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {len(records)} league-season membership lists to {path}')
    for competition_id in LEAGUES:
        subset = [r for r in records if r['competition_id'] == competition_id]
        print(competition_id, json.dumps(sorted({name for r in subset for name in r['club_names']}), ensure_ascii=False))
        print('season counts:', [(r['season_start_year'], len(r['club_names'])) for r in subset])
