# Shared ownership among the 239 selected recurring Premier League feeder routes

Ownership research completed 11 November 2026; route selection updated 18 November 2026. The current selection requires **at least 2 recorded transfers per directed route and unadjusted upper-tail p < 0.05**, using **999 within-season shuffles, seed 2026**. The p-value threshold is the statistical criterion; the recurrence requirement is a design choice to study repeated movement. Apply both after testing the full arrival sample. Of 328 routes with p < 0.05, 239 meet the recurrence requirement; they contain 721 records. The earlier inclusive p <= 0.05 rule had 241 recurring routes; strict p < 0.05 excludes two at exactly 0.05. Counts include loans, returns and repeated players, not necessarily distinct players or permanent sales.

## Joint-ownership analysis group

On 18 November 2026, the user directed inclusion of **Vitesse → Chelsea** and **Grasshoppers → Wolves** in the joint-ownership group. The plotted group now contains **17 of 239 routes (7.11%)**, comprising the 15 routes with verified transfer overlap plus Vitesse–Chelsea and Grasshoppers–Wolves. It contains **97 pooled records**, including all **8 Vitesse → Chelsea** and **10 Grasshoppers → Wolves** records. The remaining **222 routes** contain **624 records**. Group medians are **4 versus 2**, and means are **5.71 versus 2.81**.

This is an explicit analysis decision, recorded in `manual_joint_ownership_pairs` in the evidence JSON and `manual_joint_ownership_inclusion` / `joint_ownership_group` in the audit CSV. Vitesse–Chelsea and Grasshoppers–Wolves remain unverified in the source audit: no common-equity dates or event-level confirmation are inferred from the inclusion. The documented counts below remain 17 historical pairs, 15 transfer-concurrent pairs and 73 verified concurrent records.

## Source-verified answer

**At least 17 of the 239 unique club pairs (7.11%) had a documented common direct or indirect equity investor at some point in the modelling interval.**

**15 of the 239 pairs (6.28%) have at least one selected transfer record during the documented ownership overlap.** This second count is the more relevant one when asking whether shared ownership could explain the transfers actually observed. Granada–Watford and Hearts–Liverpool account for the difference between 17 and 15.

These are **confirmed minimum counts**, not a claim that the other 222 pairs had no common investor. Historical minority holdings and beneficial-owner chains are incompletely disclosed. Two prominent relationships—Vitesse–Chelsea and Grasshoppers–Wolves—remain outside the confirmed count for the reasons below.

The 239 routes contain **721 recorded transfers**. The 17 documented pairs account for **85** of those records; **73** occur within the coded common-ownership intervals. Records can include loan returns and repeated players. They are not necessarily purchases, sales, or cash payments.

## Definition and denominator

The user chose **any common equity owner, including minority interests**. We include named investors holding club equity directly or through disclosed club-investment holding chains. An explicit common-control disclosure in audited accounts, corroborated by a club ownership statement, also supports inclusion. Ownership is distinct from operational control.

The Hearts–Liverpool case therefore counts: a named broadcaster owned Liverpool shares and held an equity stake in a company that owned Hearts shares. By contrast, a common sponsor, lender, agent, loan partner, friendship, or marriage does not on its own establish common club equity. Unidentified passive fund investors and remote shareholders in unrelated listed corporations have not been reconstructed.

Club identity is matched by ID. The 239 directed routes are also 239 distinct unordered pairs; there is no double counting of reverse routes. They involve 190 supplying clubs and 35 receiving clubs. In particular, Newcastle Jets [5551] is distinct from Newcastle United [762], and New York Red Bulls [623] is distinct from New York City [40058].

The modelling input retains recorded seasons **00/01–26/27**, with input dates **2001-01-01 to 2027-06-30**. The selected routes' 721 records range from **2005-12-31 to 2026-07-01**; none postdates the research date. Ownership after the research date is not assumed to be known.

The exact PL-arrival sample was rebuilt with the original `_build_sample` function and then joined to the selected route keys. Every resulting route count matches the original `observed_count`. Joining route IDs directly to the whole eligible-transfer input would incorrectly include additional moves from seasons when the receiving club was outside the Premier League.

## Documented pairs

“During overlap” counts selected records, not distinct players. Ownership dates below describe the evidence-supported period; year/month precision is deliberate when an exact completion date was not established. Current portfolio pages are used with historical announcements and accounts, not projected backward as sole evidence.

| Origin → destination | Common investor/group | Ownership timing relevant to this audit | Selected records | During overlap | Primary evidence |
| --- | --- | --- | ---: | ---: | --- |
| Girona → Manchester City | City Football Group | August 2017 onward; minority equity qualifies | 17 | 12 | [Acquisition](https://www.cityfootballgroup.com/post/girona-fc-acquired-by-new-investors), [group portfolio](https://www.cityfootballgroup.com/clubs) |
| Strasbourg → Chelsea | BlueCo / Clearlake-led group | Strasbourg closing July 2023; Chelsea acquired May 2022 | 11 | 11 | [RCSA's acquisition release](https://cdn-s-www.dna.fr/pdf/fabdc231-1a78-4f0a-9c91-c6ba1a8b61c1/document.pdf), [BlueCo accounts filings](https://find-and-update.company-information.service.gov.uk/company/13949552/filing-history), [Chelsea completion](https://www.chelseafc.com/en/news/article/statement-from-board-of-directors-of-chelsea-football-club-limit) |
| Udinese → Watford | Pozzo ownership group | Pozzo era beginning 2012; same ownership and accounting common control explicitly documented | 9 | 9 | [Udinese ownership statement](https://www.udinese.it/news/squadra/gerolin-lavoreremo-sodo-per-tornare-ad-alti-livelli), [Watford 2021 accounts](https://images.gc.watfordfcservices.co.uk/d30fc840-2d82-11ef-a0be-37a5b1f697a8.pdf), [2025 accounts](https://images.gc.watfordfcservices.co.uk/ae753480-2dc5-11f1-bc79-416e9c4833f1.pdf) |
| Olympiacos → Nottingham Forest | Evangelos Marinakis | Shared ownership from Forest's 2017 acquisition | 6 | 6 | [Olympiacos yearbook](https://www.olympiacos.org/sites/default/files/book_en.pdf), [Forest retrospective](https://livepreview.nottinghamforest.co.uk/news/2025/august/29/mr-marinakis---a-proud-day-for-everyone-/), [holding-company register](https://find-and-update.company-information.service.gov.uk/company/10613412/persons-with-significant-control) |
| Union SG → Brighton | Tony Bloom | Union investment in 2018; retained minority after July 2023 change of control | 6 | 6 | [Union ownership statement](https://rusg.brussels/en/news/statement-president-and-owner-alex-muzio-0), [Brighton biography](https://www.brightonandhovealbion.com/media-article/tony-bloom-mbe) |
| Lorient → Bournemouth | Black Knight Football group / Bill Foley | Equity completion **1 February 2023**, following January agreement | 4 | 3 | [Cannae SEC filing](https://www.sec.gov/Archives/edgar/data/1704720/000170472023000025/R10.htm), [Bournemouth accounts](https://images.gc.afcbournemouthservices.co.uk/4213e360-089e-11f0-96ca-3b5257f7e8db.pdf) |
| Rio Ave → Nottingham Forest | Evangelos Marinakis / RAH Sports Investments | Rio Ave 80% acquisition completed **15 June 2024** | 4 | 4 | [Completion](https://rioavefc.pt/destaque/comunicado-rio-ave-futebol-clube-futebol-sad/), [earlier investor identification](https://rioavefc.pt/destaque/maioria-expressiva-dos-socios-aprova-a-sad/), [shareholding](https://rioavefc.pt/sad/governo-da-sociedade/) |
| OH Leuven → Leicester | King Power | OH Leuven 92% acquisition completed **6 June 2017** | 4 | 4 | [Owner's completion release](https://s3-ap-southeast-1.amazonaws.com/story.kingpower.com/wp-content/uploads/2017/06/13152814/Press_Statement_120617KP_OHL_Takeover_ENG.pdf), [Leicester statement](https://www.lcfc.com/media-article/King-Power-To-Unite-Fans-Of-Leicester-City-and-OH-Leuven) |
| Granada CF → Watford | Gino Pozzo / Pozzo ownership group | Shared ownership after Watford takeover in 2012; Granada disposal completed by mid-June 2016 | 4 | **0** | [Granada exit statement](https://www.granadacf.es/noticias/jiang-lizhang-nuevo-maximo-accionista-del-granada-cf), [club-published completion chronology](https://www.granadacf.es/noticias/la-llegada-de-jiang-lizhang-situa-a-granada-en-el-foco-nacional-e-internacional) |
| Melbourne City → Manchester City | City Football Group | Acquisition effective **23 January 2014** | 4 | 4 | [Melbourne completion statement](https://melbournecityfc.com.au/news/club-statement-0/) |
| Troyes → Manchester City | City Football Group | Acquisition September 2020 | 4 | 4 | [Acquisition](https://www.cityfootballgroup.com/post/city-football-group-add-estac-troyes-as-tenth-club), [club timeline](https://www.cityfootballgroup.com/clubs/estac-troyes) |
| RWDM → Crystal Palace | John Textor / Eagle Football | RWDM investment January 2022; Palace stake disposal completed **24 July 2025** | 2 | 2 | [Textor's investment archive](https://www.johntextor.org/press-molenbeek), [Palace investment](https://www.cpfc.co.uk/news/announcement/john-textor-joins-crystal-palace-football-club-board-of-directors/), [Palace disposal completion](https://www.cpfc.co.uk/news/announcement/crystal-palace-welcomes-woody-johnson/) |
| Midtjylland → Brentford | Matthew Benham | FCM acquisition **2 July 2014**; disposal announced August 2023 and confirmed in club history | 2 | 2 | [Acquisition and existing Brentford ownership](https://www.brentfordfc.com/en/news/matthew-benham-takes-majority-shareholding-in-fc-midtjylland_62788), [FCM disposal announcement](https://www.fcm.dk/nyheder/heartland-koeber-fc-midtjylland/), [FCM history](https://www.fcm.dk/klubben/) |
| Colorado Rapids → Arsenal | Stan Kroenke / KSE | Common equity from 2007, initially minority at Arsenal | 2 | 2 | [Arsenal ownership biography](https://www.arsenal.com/the-arsenal-board), [Colorado owner biography](https://www.coloradorapids.com/club/stan-kroenke) |
| New York City → Manchester City | City Football Group | Joint ownership established **21 May 2013** | 2 | 2 | [NYCFC founding statement](https://www.newyorkcityfc.com/news/nycfc-celebrates-founding-day-anniversary) |
| Lommel → Manchester City | City Football Group | Acquisition May 2020 | 2 | 2 | [Acquisition](https://www.cityfootballgroup.com/post/city-football-group-expands-to-belgium-acquiring-lommel-sk), [club timeline](https://www.cityfootballgroup.com/clubs/lommel-sk) |
| Heart of Midlothian → Liverpool | Granada plc, indirectly through SMG for Hearts | Simultaneous holdings documented at September 2001, 2002 and 2003 snapshots; SMG exited Hearts in 2005 | 2 | **0** | [Granada financial table 7.32](https://www.sec.gov/Archives/edgar/data/765245/000089109203003665/e16421_6k.htm), [SMG equity investment](https://www.investegate.co.uk/announcement/rns/stv-group--stvg/strat-alliance-with-heart-mid-/110942), [SMG disposal disclosure](https://www.investegate.co.uk/announcement/rns/stv-group--stvg/final-results/869254) |

## Why the timing changes the answer

- **Girona–City:** five of 17 records precede the August 2017 acquisition. Twelve occur after it. The counts alone do not identify purchases or sell-on arrangements.
- **Granada–Watford:** all four selected events—30 June 2016, 1 July 2016, 25 August 2017 and 20 July 2020—postdate the documented Granada disposal. The route qualifies for ownership sometime in the model interval, but not for a selected transfer while co-owned.
- **Lorient–Bournemouth:** Dango Ouattara's 19 January 2023 record follows the agreement announcement but precedes the 1 February equity closing. Faivre's 2024 record and the two Kroupi records in 2025 follow closing.
- **Hearts–Liverpool:** Granada plc is the broadcaster, not Granada CF. The SEC table documents approximately 16.9% of SMG alongside 9.99% of Liverpool; SMG's disclosed Hearts ordinary-equity stake was 19.9%. This is an indirect minority-investment chain, not common operational control. Both selected transfers are in 2011/2014, after SMG's 2005 exit. The audit does not claim exact entry/exit dates for Granada's own SMG holding.

Acquisition/exit brackets in the evidence JSON record the precision of the retrieved sources. None of the selected events falls within an uncertain boundary bracket. That check does not remove gaps in historical source coverage: in particular, the original exact-day primary completion document for Watford's 2012 takeover was not recovered, and the Pozzo-era coding uses historical continuity corroborated by the subsequent explicit club and audited-account disclosures. The FCM August 2023 announcement was conditional; the later club history confirms exit in 2023 without establishing an exact legal closing day. Neither affects an event close to a boundary.

Girona's 2024/25 blind trust and Forest's registered control interruptions are recorded separately from equity ownership. A sensitivity check excluding those control windows changes none of the 73 transfer-concurrent classifications: no selected event on a verified route falls inside them. Forest's register records the 2025 gap as 29 April–6 June and the 2026 gap as 17 April–10 June. [UEFA Girona decision](https://www.uefa.com/news-media/news/028f-1b4ba6fcea09-078845f25cbf-1000/), [Forest holding-company register](https://find-and-update.company-information.service.gov.uk/company/10613412/persons-with-significant-control).

## Unresolved and excluded network relationships

| Pair | Audit classification | Reason |
| --- | --- | --- |
| Vitesse → Chelsea | Included in joint-ownership group by user decision; source evidence unresolved | KNVB reported indications of Abramovich control/influence and investigation in 2024. Funding/control evidence is material, but this audit did not establish a verified equity interval. Do not classify this as proved independently owned. [KNVB](https://www.knvb.nl/nieuws/betaald-voetbal/licentiezaken/69055/licentiecommisie-18-wedstrijdpunten-mindering-voor). |
| Grasshoppers → Wolves | Included in joint-ownership group by user decision; identical equity holder unverified | Grasshoppers' disclosed owner Jenny Wang and Wolves' Fosun ownership are family-connected, but the retrieved sources do not prove the same beneficial equity investor held both clubs. [GC ownership change](https://www.gcz.ch/news/artikel/27/information-betreffend-verkauf-der-aktien-der-grasshopper-fussball-ag/), [Wolves acquisition](https://www.wolves.co.uk/news/club/2016072016-fosun-group-takes-over-wolves/). |
| Salzburg → Leeds | Branded-network affiliation; common equity unverified | Leeds Red Bull investment announced 30 May 2024, after all three selected arrivals in 2022/January 2023. Salzburg's association-owned company and sponsorship structure do not establish Red Bull GmbH equity ownership. [Leeds announcement](https://www.leedsunited.com/en/news/leeds-united-announce-red-bull-as-front-of-shirt-partner), [Austrian register](https://www.evi.gv.at/f/452749h), [UEFA ownership/governance decision](https://editorial.uefa.com/resources/0258-0e2dece33fb8-5cc21edafedf-1000/rb_leipzig_fc_salzburg_-_cfcb_adjudicatory_chamber_decision_-_june_2017.pdf). |
| NAC Breda → Manchester City | Development partnership; common equity unverified | NAC describes loans, facilities and knowledge sharing, not acquisition by CFG. [NAC clarification](https://www.nac.nl/nieuws/reactie-nac-op-berichtgeving-telegraaf). |
| Royal Antwerp → Manchester United | Cooperation; common equity unverified | The loan relationship does not itself establish an equity link; no common investor was verified in the source screen. |

These five cases and the other 217 unconfirmed pairs total 222. Their negative confirmation flags mean **not established by this research**, not “no common owner existed.”

## Source-screen coverage

The original source screen covered 334 route keys and 40 destinations under the earlier p <= 0.05 rule. The current 239-route selection (35 destinations) is a subset, so its source coverage is retained. The linked research notes below describe the historical 334-route screen, not the current denominator. This is not an exhaustive historical shareholder census. Some destination ownership sources are recent disclosures that establish portfolio context; they cannot prove the absence of every earlier minority investor. The saved classification preserves this distinction.

- [Candidate ownership histories](feeder_ownership_candidate_sources.md): 113 routes into ten destinations—Chelsea, Palace, Brighton, Watford, Forest, Leicester, Brentford, Arsenal, Southampton and Wolves. Ten documented pairs, nine with transfer-concurrent records.
- [Other-destination screen](feeder_ownership_other_destinations.md): 200 routes into 29 destinations, including a complete supplying-club ID inventory. Lorient–Bournemouth is the conventional confirmed match. Historical ownership gaps, including Reading, are explicit.
- [Historical/definition audit](feeder_ownership_definition_audit.md): adds Hearts–Liverpool through the broadcaster equity chain and checks historical BSkyB/NTL and PEAK6 portfolios, loan partnerships, control and minority-investor definitions. Hearts is included in the 200-route denominator above, not an additional route to that denominator.

### City group screen

In the original 334-route source screen, the remaining 21 routes entered Manchester City. Five documented equity matches are Girona, Melbourne City, New York City, Lommel and Troyes. The other supplying clubs are River Plate, FC Twente, NAC Breda, KV Kortrijk, Talleres, KV Mechelen, PEC Zwolle, Valencia, Wolfsburg, Partizan, Vélez Sarsfield, Arminia Bielefeld, Radomiak, Como, Čukarički and Groningen. No additional documented common-equity match was found in the bounded portfolio screen. This is not a complete historical register of every shareholder in those clubs. [CFG ownership portfolio](https://www.cityfootballgroup.com/clubs), [historical 2017 club guide](https://www.mancity.com/-/media/files/media-guide/tour-media-guide---2017.ashx?la=en), [NAC partnership statement](https://www.nac.nl/nieuws/reactie-nac-op-berichtgeving-telegraaf).

## Saved audit and verification

- [All 239 selected pairs and classifications](../output/premier_league_feeder_ownership_audit.csv): preserves original route measures and adds owner, source URLs, date brackets, status and concurrent-record counts.
- [Manually sourced ownership intervals](../output/premier_league_feeder_ownership_evidence.json): the auditable research input, with per-pair citations and precision notes.
- [All 721 selected records with ownership-date flags](../output/premier_league_feeder_ownership_events.csv).
- [Counts by destination](../output/premier_league_feeder_ownership_destinations.csv).
- [Results and verification metadata](../output/premier_league_feeder_ownership_results.json): model settings, denominator, counts, source limits and input SHA-256 hashes.
- [Reproduction script](../notebooks/premier_league_feeder_ownership_audit.py). From any working directory, run `python -B <project>/notebooks/premier_league_feeder_ownership_audit.py` against the saved evidence and current analysis files.

Verification checks the current 239-route selection, unique keys, exact season-filtered event counts, valid ownership bounds, source citations for every positive, absence of future selected events, and consistency of event/pair totals. Counts were independently recalculated from the saved event table. Original feeder-route and age/degree analysis files are not rewritten by this audit.

This result describes the confirmed ownership share **among the selected routes**. It does not establish that ownership-linked routes are overrepresented compared with the full network; that would require an ownership-labelled comparison set. It also does not establish causation, permanent sales, transfer profits or sell-on-clause payments.
