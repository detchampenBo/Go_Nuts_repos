# Ownership audit checkpoint — archived after completion

Resumed and completed on 11 November 2026. The final result is **at least 17 documented shared-owner pairs in the model interval, with 15 having a transfer during ownership overlap**. A historical indirect minority link, Hearts–Liverpool, was added after this checkpoint. See the [completed audit](premier_league_feeder_ownership_audit.md) and [all 334 classifications](../output/premier_league_feeder_ownership_audit.csv). The remainder below preserves the earlier, provisional checkpoint and is not the current result.

Paused on 11 November 2026. Research is incomplete; counts below are provisional, not a finished result.

## User's question and agreed definition

Of the 334 routes meeting the unadjusted p <= 0.05 threshold in the 999-shuffle feeder-route analysis, how many unique club pairs shared an owner during the modelling interval?

The user confirmed **any shared equity owner, including a minority stake**, rather than only a shared controlling owner. The research should distinguish:

1. Shared ownership at any point within the modelling interval.
2. At least one of the route's actual model-selected transfer records occurring while shared ownership was in place.

Do not infer equity ownership from a loan partnership, sponsorship, common agent, financing, or a family relationship alone. Count disclosed direct club stakes and documented indirect ownership through club-holding companies. Explain the limits of tracking undisclosed small stakes or remote passive investors.

## Data checks already completed

- Input: `../output/premier_league_feeder_significant_routes.csv`; confirm it still matches the significant rows of the complete route table before finishing.
- 334 directed routes; also 334 unique unordered pairs (no reverse-pair duplication).
- 271 distinct origins; 40 distinct PL destination clubs.
- The 334 routes contain 821 model-selected transfer records in total.
- Model input covers recorded seasons 00/01–26/27, with input dates 2001-01-01–2027-06-30. None of the 821 records for these significant routes is later than the research date, 2026-11-11.
- **Important:** Do not simply join route keys against every eligible input row. That includes additional moves from seasons when the destination was outside the PL. Rebuild the exact arrival sample using `_build_sample` in `../notebooks/premier_league_feeder_routes.py`, then join route keys. Its joined event counts must equal the CSV's `observed_count` for every route.

## Provisional findings to finish checking

The working count is **16 pairs with documented shared ownership sometime in the modelling interval**, of which **15 have at least one selected transfer during the shared-ownership interval**. These are confirmed-minimum candidates pending final consolidation and review, not proof that all remaining pairs had no common owner.

| Pair | Working ownership link | Timing note |
| --- | --- | --- |
| Girona → Manchester City | City Football Group | Acquisition August 2017; 12 of 17 selected records are later. Five records predate acquisition. Record the 2024/25 blind trust separately from economic ownership. |
| Melbourne City → Manchester City | City Football Group | Melbourne acquisition effective 23 January 2014; all four selected records later. |
| New York City → Manchester City | City Football Group | Founded under shared ownership 21 May 2013; both records later. |
| Lommel → Manchester City | City Football Group | Acquisition May 2020; both records later. |
| Troyes → Manchester City | City Football Group | Acquisition September 2020; all four records later. |
| Strasbourg → Chelsea | BlueCo | Shared ownership from June 2023; all 11 records later. |
| RWDM → Crystal Palace | John Textor / Eagle | Check acquisition and Palace disposal dates; both recorded moves fall within overlap. |
| Union SG → Brighton | Tony Bloom | Acquisition 2018, minority retained after July 2023; all six records during overlap. |
| Udinese → Watford | Pozzo ownership | Official Watford accounts say Udinese is under common control; Udinese's 2017 statement explicitly calls it the same ownership. More than a surname/family inference. Nine route records. |
| Granada → Watford | Pozzo ownership | Shared ownership existed from Watford acquisition in 2012 until Granada disposal in June 2016, but **all four selected events are after disposal**; count for interval-ever, not transfer-concurrent. |
| Olympiacos → Nottingham Forest | Evangelos Marinakis | Forest acquisition 2017; six records during overlap. Forest control-trust gaps in 2025/2026 do not contain selected event dates. |
| Rio Ave → Nottingham Forest | Evangelos Marinakis | Rio Ave equity acquisition **completed 15 June 2024**, not the November 2023 approval announcement; all four selected events later. |
| OH Leuven → Leicester | King Power | Completion 6 June 2017; four records later. |
| Midtjylland → Brentford | Matthew Benham | Shared ownership 2014–2023; both selected records in 2021/2022. |
| Colorado → Arsenal | Kroenke / KSE | Both selected records are Auston Trusty, 31 January and 14 July 2022. |
| Lorient → Bournemouth | Black Knight | Lorient deal announced 13 January 2023 but **completed 1 February 2023**. Three of four selected records are after completion; Ouattara on 19 January 2023 is before completion. |

Tentative arithmetic from those intervals: 83 recorded transfers on the 16 candidate routes; 73 occur within the working confirmed ownership intervals. Verify computationally before reporting.

## Key exclusions / unresolved cases

- **Vitesse → Chelsea:** unresolved indirect equity/control. KNVB's 19 April 2024 statement reports indications of Abramovich influence/control and investigation. This is not a confirmed, dated shared-equity interval; do not silently classify it as either a verified positive or proven negative.
- **Grasshoppers → Wolves:** former Grasshoppers owner Jenny Wang is associated by family with Fosun founder Guo Guangchang, but family connection alone does not establish a common equity owner. Keep this distinct from verified common-equity ownership.
- **Salzburg → Leeds:** all three selected moves are July 2022–January 2023, before Red Bull's Leeds minority investment on 30 May 2024. Also, UEFA's 2017 decision and Austrian Bundesliga material describe Salzburg's association ownership and changed Red Bull influence; branding/sponsorship does not establish common equity even for the interval-ever definition.
- **NAC Breda → Manchester City:** official club statement describes a loan/development partnership, not CFG acquisition.
- **Royal Antwerp → Manchester United:** cooperation/loan relationship does not establish equity ownership.
- **Slavia Praha → West Ham:** do not confuse Slavia with Sparta Prague, the club linked to Daniel Kretinsky.
- Club IDs matter: Newcastle → Swansea is Australian Newcastle Jets (5551), not Newcastle United (762). New York → Bolton is NY Red Bulls (623), not NYCFC (40058).

## Sources already located

City-group sources:

- [Girona acquisition](https://www.cityfootballgroup.com/post/girona-fc-acquired-by-new-investors). Website header currently says 13 August 2017, whereas widely cited dates differ; month precision is sufficient because no selected transfer falls near this August boundary.
- [Melbourne acquisition, effective 23 January 2014](https://melbournecityfc.com.au/news/club-statement-0/).
- [NYCFC founding anniversary and ownership](https://www.newyorkcityfc.com/news/nycfc-celebrates-founding-day-anniversary).
- [Lommel acquisition](https://www.cityfootballgroup.com/post/city-football-group-expands-to-belgium-acquiring-lommel-sk) and [club timeline](https://www.cityfootballgroup.com/clubs/lommel-sk).
- [Troyes acquisition](https://www.cityfootballgroup.com/post/city-football-group-add-estac-troyes-as-tenth-club) and [club timeline](https://www.cityfootballgroup.com/clubs/estac-troyes).
- [CFG club ownership roster](https://www.cityfootballgroup.com/clubs).
- [UEFA 2024/25 blind-trust decision](https://www.uefa.com/news-media/news/028f-1b4ba6fcea09-078845f25cbf-1000/).
- [NAC partnership clarification](https://www.nac.nl/nieuws/reactie-nac-op-berichtgeving-telegraaf).

Other important sources returned by research agents:

- [Lorient completion date, Cannae SEC filing](https://www.sec.gov/Archives/edgar/data/1704720/000170472023000025/R10.htm).
- [Rio Ave completed acquisition statement](https://rioavefc.pt/destaque/comunicado-rio-ave-futebol-clube-futebol-sad/) and [earlier approval](https://rioavefc.pt/destaque/maioria-expressiva-dos-socios-aprova-a-sad/).
- [OH Leuven completion statement](https://s3-ap-southeast-1.amazonaws.com/story.kingpower.com/wp-content/uploads/2017/06/13152814/Press_Statement_120617KP_OHL_Takeover_ENG.pdf).
- [Watford 2021 official accounts](https://images.gc.watfordfcservices.co.uk/d30fc840-2d82-11ef-a0be-37a5b1f697a8.pdf) and [2025 official accounts](https://images.gc.watfordfcservices.co.uk/ae753480-2dc5-11f1-bc79-416e9c4833f1.pdf): Udinese company under common control; Gino Pozzo ultimate controller.
- [Udinese same-ownership statement, 2017](https://www.udinese.it/news/squadra/gerolin-lavoreremo-sodo-per-tornare-ad-alti-livelli).
- [Granada ownership exit](https://www.granadacf.es/noticias/la-llegada-de-jiang-lizhang-situa-a-granada-en-el-foco-nacional-e-internacional).
- [Forest holding-company PSC chronology](https://find-and-update.company-information.service.gov.uk/company/10613412/persons-with-significant-control): Marinakis ceased 29 April 2025, restored 6 June 2025; second gap 17 April–10 June 2026.
- [Leeds Red Bull minority stake announcement](https://www.leedsunited.com/en/news/leeds-united-announce-red-bull-as-front-of-shirt-partner).
- [UEFA Salzburg/Leipzig reasoned decision, 2017](https://editorial.uefa.com/resources/0258-0e2dece33fb8-5cc21edafedf-1000/rb_leipzig_fc_salzburg_-_cfcb_adjudicatory_chamber_decision_-_june_2017.pdf).
- [KNVB Vitesse statement, 19 April 2024](https://www.knvb.nl/nieuws/betaald-voetbal/licentiezaken/69055/licentiecommisie-18-wedstrijdpunten-mindering-voor).

## Resume work

1. Read any saved `feeder_ownership_*` supporting notes. Agents were interrupted on pause; some notes may be unfinished or absent.
2. Finish primary-source citations for every included interval, date precision, minority stakes, disposals, and blind trusts. Complete the 40-destination portfolio screen, preserving uncertainty about undisclosed minority stakes.
3. Construct an auditable dated evidence table and classify all 334 pairs. Use the exact model-selected sample for date overlaps; verify route counts and the tentative 16/15 split computationally.
4. Save the final research note under `notes`, with any generated audit CSV/JSON outputs under `output`. Keep the original shuffle implementation and its outputs unchanged.
5. Report confirmed-minimum counts, list the verified pairs, explain the interval-ever versus transfer-concurrent distinction, and name unresolved cases. Shared ownership and excess transfer counts alone do not establish resale income, sell-on clauses, or causation.
