# Season-specific top-five league membership

Researched 2026-11-04 for `notebooks/dataclean.ipynb`.

The finished lookup is [`../data/top_five_league_clubs.csv`](../data/top_five_league_clubs.csv):
3,300 memberships across 170 league-seasons (1993/94–2026/27), covering 243
distinct club IDs. It includes the season, competition, league name, club ID,
club name, original source name, and source URL. Each `(transfer_season, club_id)`
key is unique.

## Selection rule and season convention

Keep a transfer when `(transfer_season, from_club_id)` **or**
`(transfer_season, to_club_id)` occurs in the membership lookup. Both endpoints may
qualify. The other endpoint may belong to another league. This therefore retains
some clubs outside the five leagues as transfer counterparties.

Use the recorded football season, rather than the transfer date's calendar year:
for example, `14/15` means the season beginning in 2014. League membership changes
with promotion and relegation; a club's present league or its historical inclusion
in `clubs.csv.gz` is insufficient to identify its league in a particular season.

## Sources

The local Transfermarkt match dataset supplies historical club IDs directly for
2012/13–2025/26. Select only the five competition IDs below and union the unique
home and away club IDs within each `(season, competition_id)` group. The local
`competitions.csv.gz` gives the competition identifiers and their source pages.

| League | Transfermarkt ID | Football-Data division | Source archive |
| --- | --- | --- | --- |
| Premier League | `GB1` | `E0` | [England](https://www.football-data.co.uk/englandm.php) |
| Serie A | `IT1` | `I1` | [Italy](https://www.football-data.co.uk/italym.php) |
| Bundesliga | `L1` | `D1` | [Germany](https://www.football-data.co.uk/germanym.php) |
| Ligue 1 / historical Division 1 | `FR1` | `F1` | [France](https://www.football-data.co.uk/francem.php) |
| LaLiga / Primera Division | `ES1` | `SP1` | [Spain](https://www.football-data.co.uk/spainm.php) |

For 1993/94–2011/12 and 2026/27, download each league's original match CSV from
Football-Data and union its `HomeTeam` and `AwayTeam` values. The publisher defines
those fields in its [data dictionary](https://www.football-data.co.uk/notes.txt).
This is an inference of membership from observed league matches, rather than a
list of current clubs reused across historical seasons.

CSV URL pattern:

```text
https://www.football-data.co.uk/mmz4281/{start_yy}{end_yy}/{division}.csv
```

For example, the five 1993/94 source files are
[Premier League](https://www.football-data.co.uk/mmz4281/9394/E0.csv),
[Bundesliga](https://www.football-data.co.uk/mmz4281/9394/D1.csv),
[Serie A](https://www.football-data.co.uk/mmz4281/9394/I1.csv),
[LaLiga](https://www.football-data.co.uk/mmz4281/9394/SP1.csv), and
[French Division 1](https://www.football-data.co.uk/mmz4281/9394/F1.csv).
All 100 required external league-season files downloaded successfully.

The publisher's current archive includes 2026/27. Those files already contain
matches for all 20 Premier League, 20 Serie A, 18 Bundesliga, 18 Ligue 1 and 20
LaLiga clubs:
[E0](https://www.football-data.co.uk/mmz4281/2627/E0.csv),
[I1](https://www.football-data.co.uk/mmz4281/2627/I1.csv),
[D1](https://www.football-data.co.uk/mmz4281/2627/D1.csv),
[F1](https://www.football-data.co.uk/mmz4281/2627/F1.csv), and
[SP1](https://www.football-data.co.uk/mmz4281/2627/SP1.csv).

Match Football-Data aliases to the existing Transfermarkt club IDs explicitly.
Keep names in the lookup for inspection, but filter on IDs so abbreviations and
name changes do not alter the result. Important identity distinctions include
historical VfB Leipzig (`Leipzig` in 1993/94) versus RB Leipzig, Wimbledon FC
versus AFC Wimbledon, and Reggiana versus Reggina. Spelling variants such as
`M'Gladbach`/`M'gladbach` and `Villareal`/`Villarreal` identify the same club.
Transfermarkt archived competition pages were also attempted, but returned HTTP
403 in direct fetches; indexed first-party Transfermarkt pages supplied the
identity checks below.

### Historical club identity checks

| Football-Data label | Transfermarkt club ID | Identity and primary evidence |
| --- | --- | --- |
| `Leipzig` in 1993/94 | `497` | VfB Leipzig. Transfermarkt's [1993/94 Bundesliga competition page](https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1/saison_id/1993) explicitly links its VfB Leipzig entry to `/1-fc-lokomotive-leipzig/startseite/verein/497/saison_id/1993`. The current Lokomotive name therefore does not invalidate this historical ID. RB Leipzig is a different club. |
| `Wimbledon` | `114309` | [Wimbledon FC (-2004), 1998/99 profile](https://www.transfermarkt.co.uk/wimbledon-fc-2004-/startseite/verein/114309/saison_id/1998). Do not substitute AFC Wimbledon (`3884`) or MK Dons (`991`). |
| `Extremadura` | `811` | [CF Extremadura (-2010)](https://www.transfermarkt.de/cf-extremadura-2010-/startseite/verein/811), founded 1924; distinct from Extremadura UD (`29095`). |
| `Logrones` | `236` | CD Logroñés (-2009). The first-party [historical competition page](https://www.transfermarkt.mx/segunda-division/startseite/wettbewerb/ES2/saison_id/1952) explicitly links CD Logroñés to `/cd-logrones-aufgel-/startseite/verein/236/saison_id/1952`. UD Logroñés (`24420`) and SD Logroñés (`33303`) are different clubs. |
| `Merida` | `38011` | [CP Mérida (-2000)](https://www.transfermarkt.de/cp-merida-aufgel-/startseite/verein/38011/saison_id/1970), distinct from Mérida AD (`46854`) and Mérida UD (`18662`). |
| `Hercules` | `7971` | Spanish Hércules CF. The [Spanish competition page](https://www.transfermarkt.es/primera-division-r-f-e-f-grupo-ii/startseite/wettbewerb/E3G2/saison_id/2025/spieltag/20) explicitly links to `/hercules-alicante/startseite/verein/7971/saison_id/2025`. Dutch Hercules (`34156`) is a different club. |
| `Lerida` | `3239` | Historical UE Lleida (-2011). The [2004/05 LaLiga2 competition page](https://www.transfermarkt.us/laliga2/startseite/wettbewerb/ES2/saison_id/2004) explicitly links UE Lleida to `/ue-lleida-aufgel-/startseite/verein/3239/saison_id/2004`. |

## Coverage checks

The 2012/13–2025/26 local match records yield 1,366 distinct
`(season, competition_id, club_id)` memberships. Each league-season has the full
expected club count: 20 in England, Italy and Spain; 18 in Germany; 20 in France
until 2022/23 and 18 from 2023/24 onward.

The older downloaded league-season counts reflect historical league sizes:

| League | Historical club counts in downloaded seasons |
| --- | --- |
| Premier League | 22 in 1993/94–1994/95; 20 from 1995/96 |
| Serie A | 18 through 2003/04; 20 from 2004/05 |
| Bundesliga | 18 throughout |
| French Division 1 / Ligue 1 | 20 through 1996/97; 18 in 1997/98–2001/02; 20 in 2002/03–2011/12; 18 in 2026/27 |
| LaLiga | 22 in 1995/96–1996/97; 20 in the other downloaded seasons |

## Unsupported future season

Do not invent 2027/28 top-five membership. The saved transfer data contains 13
cleaned rows labelled `27/28`; inspection found only Korean clubs, Brondby
(Transfermarkt ID `206`), and non-club labels (`Retired`, ID `123`, and
`Without Club`, ID `515`). These rows can be excluded independently of unannounced
2027/28 promotion and relegation because neither endpoint belongs to one of the
five countries' leagues. Any unsupported season involving a potential top-five
club must be surfaced for review instead of silently treated as non-membership.

## Filter verification on the saved data

Every notebook code cell executed successfully. An independent set-of-tuples
membership check produced exactly the same retained rows, indices, order, and
columns as the notebook's vectorized filter.

| Measure | Before | After |
| --- | ---: | ---: |
| Transfer rows | 105,644 | 23,238 |
| Distinct endpoint club IDs | 8,599 | 1,265 |

The retained rows comprise 7,421 with only the source club qualifying, 8,519 with
only the destination club qualifying, and 7,298 with both qualifying. The 82,406
removed rows include the 13 unsupported-season rows, which remain available in
`outside_lookup_transfers`.

Historical spot checks covered Juventus's absence from Serie A in 2006/07,
Leeds's season-specific promotion/relegation, VfB Leipzig versus RB Leipzig,
Wimbledon versus AFC Wimbledon, and the older Extremadura and Spanish Hércules
identities. All 170 league-season club counts matched the expected league sizes.
