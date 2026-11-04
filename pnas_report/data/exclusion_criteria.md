# Club ID exclusion criteria

Source: `transfermarkt-datasets/unique_transfers.csv` (110,316 unique transfer pairs).

The complete, sorted ID list is in `exclusion_criteria.csv`. Each row gives the club ID, the matching term, the observed club name that triggered exclusion, and any other names observed for the same ID.

An ID is excluded when **any** observed `from_club_name` or `to_club_name` for that ID meets a rule below, ignoring case. A transfer pair is removed if either `from_club_id` or `to_club_id` is on the list. This uses IDs rather than names at filter time, so name variants for a listed ID are also removed.

| Category | Name rule | Examples |
| --- | --- | --- |
| Ages 15–23 | Separate `U`, `Y`, or `S` plus age, or `Sub-` plus age | `AKA Admira U15`, `Sacavenense S17`, `CD Maipú U20`, `Newcastle U21`, `Vizela U23` |
| Bare youth ages | Final standalone `15`, `17`, or `19` | `Portimonense 15`, `Vilaverdense 17` |
| Youth | Separate `Youth`, `Yth`, `Yt`, `Jgd`, or `Jugend` term, or a final `Y`/`Y.` | `Willem II Youth`, `Portimonense Yt`, `1.FC Mül. Jgd.`, `1 Dezembro Y.` |
| Academy | Separate `Academy`, `Akademia`, or `Akad.` term | `Arsenal Academy`, `Akademia Rostov` |
| Junior | Separate `Junior`, `Juniors`, or `Jun.` term | `Altach Juniors`, `Amkar-Junior` |
| B team | Final `B`, `B Team`, `B-Team`, or `(B)` | `AC Ajaccio B` |
| II team | Final `II`, `II Team`, `II-Team`, or `(II)` | `07 Vestur II` |
| 2 team | Final `2` or `-2` | `ATL UTD 2`, `Akron-2` |
| Reserve | Separate `Reserve`, `Reserves`, or `Res.` term | `Al-Ain Reserve`, `Arsenal Res.` |

| Measure | Count |
| --- | ---: |
| Distinct club IDs in source | 17,553 |
| IDs excluded | 7,763 |
| Transfer pairs removed | 35,313 |
| Transfer pairs retained | 75,003 |
| Full transfer rows removed | 69,521 |
| Full transfer rows retained | 105,644 |
| Excluded IDs with another observed name lacking a matching term | 105 |

The 105 IDs with other observed names are retained in the exclusion list because the requested rule is ID based. For example, ID `40421` appears as both `Rayo Vallecano` and `Rayo Youth`. Review `other_observed_names` in the CSV if those aliases should be treated differently. `Newcastle U21` occurs under two IDs (`9253` and `26208`); both are listed.

`Junior`/`Juniors` is a literal name rule, so it also excludes senior clubs whose proper names contain that word (for example, `Boca Juniors`). Bare `18` and `20` endings are not excluded by themselves because some are part of senior club names (for example, `Bourges Foot 18` and `Frechen 20`).
