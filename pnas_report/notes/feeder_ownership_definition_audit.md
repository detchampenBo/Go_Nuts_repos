# Ownership-definition and timing audit for feeder routes

Research date: 11 November 2026. This is a supporting source audit for the 334 routes with unadjusted Monte Carlo p-value <= 0.05. It does not supply a separate total for all 334 pairs.

## Operational definition

The user selected **any shared equity owner, including a minority owner**. A conservative, auditable implementation is to count a named person or entity with documented equity in both clubs, directly or through a disclosed club-holding company, during overlapping dates. Treat legal completion, rather than an announcement of an agreement, as the start date when both are available. An owner's equity interest does not necessarily establish operational control.

Record two distinct answers: ownership overlapping the overall modelling interval, and ownership overlapping at least one actual selected transfer record on the route. The first can include ownership acquired after every transfer on the route. Neither requires the clubs to have shared ownership throughout the entire modelling interval.

Pure sponsorship, a player-development agreement, common agents, business friendships, a loan to an owner, and marriage between different owners do not by themselves establish that the same person or entity owns equity in both clubs. Put these links in separate relationship/uncertainty categories. This is a coding definition, not a factual finding that these relationships are irrelevant to transfers.

There is a completeness limitation to a literal zero-threshold interpretation of "any" owner: undisclosed minority interests, fund limited partners, nominee holdings and investors in publicly listed parent companies cannot be exhaustively reconstructed from club announcements. An unconfirmed pair should be labelled **no documented common owner found**, rather than proven independently owned. Disclosed club-investment ownership chains are the practical scope of this source audit.

## A timing correction: FC Lorient -> AFC Bournemouth

This pair is a confirmed shared-equity relationship, but the initial January 2023 announcement predates completion. Cannae's audited filing reports that BKFE agreed to invest on **13 January 2023** and completed acquisition of the Lorient minority interest on **1 February 2023**. It also records the Bournemouth acquisition as completed on **13 December 2022**. Therefore, 1 February 2023 is the common-equity start date. [Cannae SEC filing, subsequent-events note](https://www.sec.gov/Archives/edgar/data/1704720/000170472023000025/R10.htm).

The four selected PL-arrival records on this route are:

| Player | Recorded transfer date | After common-equity completion? |
| --- | --- | --- |
| Dango Ouattara | 19 January 2023 | No |
| Romain Faivre | 31 January 2024 | Yes |
| Junior Kroupi | 3 February 2025 | Yes |
| Junior Kroupi | 30 June 2025 | Yes |

Thus the route qualifies, with **3 of its 4 selected records** occurring after the documented equity acquisition. The agreement-stage connection could be relevant to Ouattara, but equity ownership should not be backdated to the announcement. Record counts come from the project arrival sample returned by `_build_sample`, not an unfiltered join of all eligible rows to route IDs.

Cannae subsequently announced acquisition of the remaining 60% on **28 January 2026**, bringing BKFC to 100% of Lorient. The announcement identifies Bournemouth as another club in the group. [Cannae completion announcement](https://www.cannaeholdings.com/news-releases/news-release-details/cannae-holdings-inc-announces-black-knight-football-clubs-bkfc).

## Salzburg -> Leeds: later relationship and legal-form caveat

Leeds announced Red Bull's minority equity investment on **30 May 2024**. The three selected Salzburg -> Leeds records are 1 July 2022 (Rasmus Kristensen and Brenden Aaronson) and 3 January 2023 (Maximilian Wöber). They all precede that Leeds investment. This route therefore provides no transfer-concurrent ownership evidence based on that transaction. [Leeds announcement](https://www.leedsunited.com/en/news/leeds-united-announce-red-bull-as-front-of-shirt-partner).

There is a separate equity-versus-influence issue. UEFA's 16 June 2017 reasoned decision identifies FC Red Bull Salzburg GmbH as wholly owned by the Salzburg association and discusses Red Bull's sponsorship, membership and governance influence. Its conclusion followed changes removing the decisive influence that concerned the investigator. That decision does not establish Red Bull GmbH as an equity shareholder in Salzburg. Consequently, branding and conventional descriptions of a Red Bull "network" alone are insufficient to code a strict common-equity ownership link with Leeds. A later Salzburg corporate-register record would be needed to establish equity ownership in the overlapping period. [UEFA reasoned decision, especially paragraphs 11 and 50–55](https://editorial.uefa.com/resources/0258-0e2dece33fb8-5cc21edafedf-1000/rb_leipzig_fc_salzburg_-_cfcb_adjudicatory_chamber_decision_-_june_2017.pdf).

## Grasshoppers -> Wolves: distinguish family relationship from verified common equity

Wolves' acquisition announcement identifies **Fosun** as acquiring 100% on **21 July 2016**. [Wolves announcement](https://www.wolves.co.uk/news/club/2016072016-fosun-group-takes-over-wolves/).

Grasshopper's **17 January 2024** announcement identifies LAFC as its new majority shareholder and names **Jenny Wang** as the former shareholder. These statements establish different disclosed ownership vehicles; they do not themselves establish common equity between Grasshoppers and Wolves. [Grasshopper announcement](https://www.gcz.ch/news/artikel/1/lafc-und-gc-zuerich-gehen-partnerschaft-ein/).

All ten selected Grasshoppers -> Wolves events fall between 8 October 2020 and 30 June 2023. A family or related-party connection may therefore be relevant to the observed pattern, but it should be recorded separately unless evidence traces the same actual beneficial equity owner into both clubs. This audit does **not** conclude that no such ownership exists; it concludes that the primary sources retrieved here do not prove it.

Wolves also announced **PEAK6's minority investment in Fosun Sports on 19 October 2021**, illustrating why minority ownership must be screened rather than treating Fosun as the sole relevant investor. The same announcement describes PEAK6's Roma and Bournemouth stakes as former holdings. Neither ownership overlap nor its dates should be inferred from a list of investments held at different times. [Wolves PEAK6 announcement](https://www.wolves.co.uk/news/club/20211019-peak6-investments-acquire-minority-share-in-fosun-sports/?isNative=true).

## Vitesse -> Chelsea: material financial links are not verified shared equity

Vitesse acknowledged reporting about indirect Abramovich financing in 2010–2016, while referring to prior KNVB findings about its disclosed ownership and control. This establishes that there is a financing allegation requiring attention, not primary proof of Abramovich holding Vitesse equity. [Vitesse response](https://www.vitesse.nl/nieuws/2023/reactie-vitesse-op-publicatie-the-guardian).

Vitesse's later statement identifies the transfer of shares held by PMH/Valeriy Oyf to the independent Vitesse Voor Altijd foundation. It supplies a primary ownership description for that transaction. [Vitesse completion announcement](https://www.vitesse.nl/nieuws/2024/aandelenoverdracht-definitief-afgerond).

The eight selected records span 30 June 2011 to 30 June 2018. For a strict shared-equity count, classify this as **unresolved financing/control-linked, not confirmed common equity**. Do not turn the absence of a retrieved equity document into proof of no relationship.

## Financial-investor checks that do not add a pair

RedBird's investment in Fenway Sports Group is documented on **31 March 2021**, and RedBird completed its AC Milan acquisition on **31 August 2022**. This is a genuine indirect common-investor example, but **AC Milan -> Liverpool is not among the 334 selected routes**. It therefore adds no pair to this denominator. [FSG investment announcement](https://fenwaysportsgroup.com/wp-content/uploads/2021/03/FSG-Announces-Investment-by-RedBird-Capital-LeBron-James-Maverick-Carter-Join-FSG-Ownership.pdf), [AC Milan completion announcement](https://www.acmilan.com/en/news/articles/club/2022-08-31/redbird-capital-partners-completes-acquisition-of-ac-milan).

Aston Villa's Atairos announcement identifies V Sports as the owner and describes Atairos entering as a minority partner. It does not establish ownership of Nice by Atairos or V Sports. Nice's own ownership letter identifies the INEOS sporting family. Accordingly, the retrieved material does not substantiate Nice -> Aston Villa as common equity. [Villa Atairos announcement](https://www.avfc.co.uk/news/2023/december/15/v-sports-announces-investment-from-atairos/), [Nice ownership letter](https://www.ogcnice.com/en/article/121693/letter-from-sir-jim-ratcliffe-to-fans.html).

## Important modelling limitations

Use only season-classified Premier League arrivals to count event overlap. A route-ID match against the entire eligible-transfer input can include moves when that destination was outside the Premier League and inflate the comparison.

The input includes future-dated transfer records extending beyond the research date. Ownership after 11 November 2026 cannot be verified as a historical fact. Separate documented ownership overlap from an assumption that ownership will continue through those future records.

The initial supporting audit found no additional confirmed route beyond the conventional groups researched elsewhere. The follow-up below establishes an additional historical indirect-equity pair.

## Follow-up: a confirmed historical indirect-equity link, Hearts -> Liverpool

**Heart of Midlothian [43] -> Liverpool [31] qualifies for ownership overlapping the modelling interval, but not for ownership concurrent with its recorded transfers.** The common investor is Granada, through its minority holding in Scottish Media Group (SMG) as well as a direct Liverpool holding.

The chain is supported by first-party financial disclosures:

1. SMG's 6 September 1999 regulatory announcement identifies a subscription for **19.9% of Hearts' ordinary share capital**, together with convertible loan stock. The often-repeated 37.4% was the maximum **after hypothetical full conversion**, not the initial equity stake. [SMG announcement](https://www.investegate.co.uk/announcement/rns/stv-group--stvg/strat-alliance-with-heart-mid-/110942).
2. SMG's 2000 interim results confirm that the investment held at **30 June 2000** included ordinary share capital as well as secured convertible loan stock. This confirms the investment was held, rather than merely proposed. [SMG interim results](https://www.investegate.co.uk/announcement/rns/stv-group--stvg/2000-interim-results-/194715).
3. Granada's financial table 7.32 reports both **16.89%, 16.87%, and 16.87% of SMG** and **9.99% of Liverpool** at the respective **30 September 2001, 2002, and 2003** snapshots. Combining the documented holdings establishes Granada's indirect minority economic interest in Hearts while it also held Liverpool equity. This is a named corporate investment chain, not a sponsorship or an inferred fund limited-partner connection. [Granada financial information filed with the SEC](https://www.sec.gov/Archives/edgar/data/765245/000089109203003665/e16421_6k.htm).
4. SMG's 2005 results state that it announced the sale of its **19.9% Hearts stake on 20 October 2005**. [SMG 2005 final results](https://www.investegate.co.uk/announcement/rns/stv-group--stvg/final-results/869254).

The exact entry and exit dates for Granada's SMG holding have not been established here. The three 2001–2003 financial snapshots already prove overlap inside the modelling interval; do not present those snapshots as exact acquisition and disposal boundaries. SMG's Hearts exit by October 2005 is sufficient to distinguish this link from the route's selected records, which occurred on **31 August 2011 and 30 June 2014**. There are **zero transfer-concurrent records** for this documented chain.

### Broader omission checks

- **PEAK6/Hulsizer:** PEAK6's own portfolio lists Bournemouth, AS Roma, and Wolves as exited sports investments. Wolves' 19 October 2021 announcement explicitly calls Roma and Bournemouth former holdings. Screening all three names against the 334 routes produces **no pair between those three clubs**. Therefore this portfolio does not add a selected route merely because it contains several clubs. [PEAK6 portfolio](https://peak6.com/peak6-strategic-capital/), [Wolves investment announcement](https://www.wolves.co.uk/news/club/20211019-peak6-investments-acquire-minority-share-in-fosun-sports/?isNative=true).
- **Bournemouth -> Newcastle:** the selected events are September 2020 and May 2022. Newcastle's own acquisition statement identifies a 100% transfer from St James Holdings to PIF/PCP/RB Sports & Media on 7 October 2021, supplying no PEAK6 shared-equity link. The selected Bournemouth -> Portsmouth events are 2007 and 2009; no common PEAK6 interest was established for that pair either. [Newcastle acquisition announcement](https://www.newcastleunited.com/en/news/pif-pcp-capital-partners-and-rb-sports-media-acquire-newcastle-united-football-club).
- **Historic broadcasters:** an Ofcom-commissioned report documents the broadcaster-equity era, and NTL's own annual report discusses stakes and agreements with Newcastle, Villa, Leicester, Middlesbrough and Rangers. Screening the conventional BSkyB club portfolio (Chelsea, Leeds, Manchester City, Manchester United, Sunderland), the NTL five-club portfolio, and Granada's direct Arsenal/Liverpool holdings produces no within-group pair among the 334. Adding the documented SMG chain produces exactly the Hearts -> Liverpool match above. Shared ownership of a club's television-channel joint venture is not treated as ownership of the club itself. [Ofcom annex](https://www.ofcom.org.uk/siteassets/resources/documents/consultations/uncategorised/8480-market_invest_paytv/associated-documents/annex_10.pdf?v=333290), [NTL 2000 annual report](https://media.corporate-ir.net/media_files/irol/13/135485/reports/ntl2000.pdf).
- **Nice -> Arsenal / Villa:** Nice's 2016 disclosure names Chien Lee, Alex Zheng, Paul Conway and the retained Jean-Pierre Rivere interest; its club history confirms INEOS acquired 100% on 26 August 2019. This does not establish a common club-equity owner with the selected Arsenal or Villa routes. No additional positive was found through these named owners. [Nice 2016 ownership announcement](https://www.ogcnice.com/fr/article/23766/nouveaux-investisseurs-communique-officiel.html), [Nice history](https://www.ogcnice.com/en/the-club/history/a-new-era.html).
- **Genoa/777/Harris–Blitzer:** no source retrieved establishes 777, Dan Sucu, Harris or Blitzer as a common equity owner between Genoa and West Ham or Tottenham, the two Genoa destinations among the 334. West Ham's disclosure identifies its named significant owners; Palace separately discloses Harris and Blitzer, but Genoa -> Palace is not one of these 334 routes. Do not merge distinct US investment firms or investors merely because they share prior employers or credit relationships. [West Ham ownership disclosure](https://www.whufc.com/en/ownership), [Palace company details](https://www.cpfc.co.uk/company-details/).
- **Fulham/Khan:** the official Companies House control record identifies the Khan family trusts and the subsequent Fulham Football Leisure holding chain. The official Premier League directory identifies Shahid Khan as chairman. No documented common club-equity owner was found for any of Fulham's selected origins; the review does not claim to prove every minority investor absent. [Companies House](https://find-and-update.company-information.service.gov.uk/company/02114486/persons-with-significant-control), [Premier League club directory](https://www.premierleague.com/en/news/694769).

This follow-up adds **one verified interval-ever pair and zero transfer-concurrent pairs** to the preceding conventional-group screening. Vitesse -> Chelsea remains an unresolved financing/control-linked case, Grasshoppers -> Wolves remains a separately recorded family-linked case, and neither is promoted into the verified common-equity count by this audit.
