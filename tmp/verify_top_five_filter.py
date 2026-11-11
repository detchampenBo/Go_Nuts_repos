import contextlib
import io
import json
import os
from pathlib import Path

os.environ['MPLBACKEND'] = 'Agg'
import nbformat
import pandas as pd


path = Path('pnas_report/notebooks/dataclean.ipynb')
notebook = nbformat.read(path, as_version=4)
nbformat.validate(notebook)
before_notebook = json.loads(Path('tmp/dataclean_before_top_five.ipynb').read_text(encoding='utf-8'))
saved_notebook = json.loads(path.read_text(encoding='utf-8'))
assert saved_notebook['cells'][:17] == before_notebook['cells'][:17]
assert saved_notebook['cells'][19:] == before_notebook['cells'][18:]

namespace = {'display': lambda *args: None}
with contextlib.redirect_stdout(io.StringIO()):
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == 'code':
            exec(compile(cell.source, f'{path}:cell-{i}', 'exec'), namespace)

original = namespace['cleaned_transfers_with_players']
result = namespace['reduced_transfers_with_players']
lookup = namespace['top_five_league_clubs']
pairs = set(zip(lookup.transfer_season, lookup.club_id))
from_member = pd.Series([
    (season, club_id) in pairs
    for season, club_id in zip(original.transfer_season, original.from_club_id)
], index=original.index)
to_member = pd.Series([
    (season, club_id) in pairs
    for season, club_id in zip(original.transfer_season, original.to_club_id)
], index=original.index)
pd.testing.assert_frame_equal(result, original.loc[from_member | to_member])
assert result.columns.equals(original.columns)
assert not lookup.duplicated(['transfer_season', 'club_id']).any()
assert lookup.groupby(['transfer_season', 'competition_id']).ngroups == 170

# Promotion/relegation and historical names must change the answer by season.
assert ('05/06', 506) in pairs and ('06/07', 506) not in pairs and ('07/08', 506) in pairs
assert ('19/20', 399) not in pairs and ('20/21', 399) in pairs
assert ('23/24', 399) not in pairs and ('25/26', 399) in pairs
assert ('93/94', 497) in pairs and ('93/94', 23826) not in pairs
assert ('93/94', 114309) in pairs and ('93/94', 3884) not in pairs
assert ('96/97', 811) in pairs and ('96/97', 29095) not in pairs
assert ('10/11', 7971) in pairs and ('10/11', 34156) not in pairs

print(namespace['top_five_filter_summary'].to_string())
print('Truth table:', {
    'from only (keep)': int((from_member & ~to_member).sum()),
    'to only (keep)': int((~from_member & to_member).sum()),
    'both (keep)': int((from_member & to_member).sum()),
    'neither (remove)': int((~from_member & ~to_member).sum()),
})
print('Outside coverage:', namespace['outside_lookup_transfers'].groupby('transfer_season').size().to_dict())
print('Validated notebook structure, executed every code cell, preserved existing cells,')
print('checked exact retained rows and columns, all four OR cases, and historical membership changes.')
