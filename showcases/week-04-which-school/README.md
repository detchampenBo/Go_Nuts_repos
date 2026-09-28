# Which School?

## Philosophical Beef

Open `beef.html` for the dispute-led companion: Hegel/Schopenhauer,
Hobbes/Rousseau, and Plato/Aristotle. Read sourced positions, predict whether
the pair shares a community, then inspect 50 exact membership results and
their shared Wikipedia neighbours. Portraits are local public-domain assets
with source credits in the page. Design decisions are in `BEEF-DESIGN.md`.

Rebuild the exact pair results with `python3 prepare_beef.py` after rebuilding
`school-data.json`. It checks the original partitions against the stored
modularity and community counts; aligned display lanes are not used to infer
co-membership. All user state stays in memory.

## The Symposium

Open `symposium.html` for a scroll-told dinner party that teaches the week's
concepts on 24 well-known philosophers: your own seating plan scored by
modularity, Louvain replayed move by move, the degree-preserving null, weights
and strength, the disparity filter against a global cut, k-clique circles, and
finally where the guests sit among all 1,374. Rebuild its data with
`python3 prepare_symposium.py` (after `prepare_data.py`); `node --test` also
runs `symposium.test.mjs`.

## Original explorer

Week 4 explorable on communities. Louvain sorts the course's 1,374 Wikipedia
philosophers into schools of thought, 50 times with 50 seeds. The page shows
who always lands in the same school, and who doesn't.

- **Lanes** are communities from a reference run. That run is the medoid: the
  run with the highest mean NMI to the other 49. Lanes are ordered by median
  birth year. Communities with fewer than 20 members share a grey "splinter" lane.
- **Across** is birth year (Wikidata P569, with a stretched piecewise axis).
- **Within a lane**, distance from the centre line shows how often a
  philosopher is sorted elsewhere. Each dot leans toward its second school.
- **Reroll / Play** switches to a single run. Philosophers outside their usual
  school get an ink ring and sit on the edge that faces home.
- **Tribunal**: one ballot square per run. Click a square to jump to that run.

Visitors can name the lanes. Names are stored in `localStorage` only.

## Rebuild and verify

```sh
python3 prepare_data.py   # ~4 s, stdlib only, deterministic across PYTHONHASHSEED
node --test               # school.test.mjs
python3 -m http.server 8000   # from the repo root, then open /showcases/week-04-which-school/
```

The inputs are in `../../data/week4/`. The node and edge TSVs come from the course
data page. `week4_birth_years.tsv` was fetched from the Wikidata API on
2026-09-24; 50 philosophers have no birth year and are placed at the midpoint of their era.
Louvain, modularity, NMI and the degree-preserving shuffle are written from scratch in
`prepare_data.py`. The run prints its own sanity checks: Q 0.48–0.51 against a null of 0.223 ± 0.002.
