"""Export the monthly numbers behind fig_h2_arc_sentiment.png (raw arcs, all four models) to a CSV,
using the same functions and seed as Pilot/a1_age30_arc_sentiment.py (monthly(), arc() from
a1_age30_arc.py; one rng seeded 2805, models in the same order).

Usage: python export_h2_arc_4models.py <dir with a1_age30_arc.py> <data dir> <out csv>
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, sys.argv[1])
from a1_age30_arc import monthly, arc  # noqa: E402

D, OUT = Path(sys.argv[2]), Path(sys.argv[3])
MODELS = [("roberta", "RoBERTa (main)"), ("vader", "VADER"), ("bing", "Bing"),
          ("bing_nofootball", "Bing, no football words")]
days = pd.read_csv(D / "sentences.csv", usecols=["days_from_transfer"]).days_from_transfer
rng = np.random.default_rng(2805)
out = []
for m, title in MODELS:
    a = arc(monthly(D, m, days), rng)
    a["model"] = title
    out.append(a)
res = pd.concat(out)[["model", "group", "month", "signings", "mean", "lo", "hi", "mean_smooth", "lo_smooth", "hi_smooth"]]
res.to_csv(OUT, index=False, float_format="%.4f")
print(res.groupby("model").size())
