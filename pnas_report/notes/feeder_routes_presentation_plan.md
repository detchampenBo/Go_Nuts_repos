# Presentation plan: unusually frequent routes and shared ownership

Prepared 11 November 2026 from the completed feeder-route analysis and ownership audit. Updated 18 November 2026 to include Vitesse–Chelsea and Grasshoppers–Wolves in the joint-ownership group by user decision; their common-equity evidence and ownership dates remain unresolved. The current selection requires at least 2 recorded transfers per directed route and an unadjusted shuffle p-value strictly below 0.05. This is a presentation plan; the proposed figures have not yet been created.

## Execution brief for the next agent

**Implement this plan: first create one full-width, three-panel academic figure using Matplotlib.** The user will start a fresh agent for execution. This handoff contains the agreed data, presentation choices and completion criteria; no further design approval is needed for this first figure.

The panels must communicate the sequence **A: recorded transfers → B: observed versus seasonal-null counts → C: shared ownership and route volume**. The reader should be able to identify the sample, comparison, units and principal findings from the figure itself, without relying on the surrounding report prose. Use readable titles, direct numerical annotations, axis labels and legends where needed.

### Implementation and outputs

- Project root: `C:/Users/victo/Codex/Go_Nuts_repos/pnas_report`. All paths below are relative to this root.
- Read the existing report template under `paper/` to determine its full text width and compatible typography. Fit the figure to that width, and choose enough height for readable labels. Begin with three panels arranged across the page; allow panel B extra width for club names.
- Create `notebooks/plot_premier_league_feeder_findings.py`, with paths resolved relative to `__file__`, using existing Matplotlib, pandas and NumPy dependencies.
- Read the saved analysis outputs listed under Sources. They contain the data needed for this figure. Preserve the completed shuffle analysis and ownership classifications; plotting does not require rerunning permutations or researching new owners.
- Export the combined figure as `output/premier_league_feeder_findings_three_panel.png` at **300 dpi or higher**, plus matching **PDF and SVG** versions. Use embedded fonts or vector text suitable for the report.
- Save its final caption as `output/premier_league_feeder_findings_three_panel_caption.md`. Keep generated files in `output`.

### Required visual style

Use the user's requested colours in this order of meaning:

| Meaning | Colour | Suggested Matplotlib hex |
| --- | --- | --- |
| Recorded transfer activity / observed counts | Orange | `#E69F00` |
| Seasonal-null expected counts | Blue | `#0072B2` |
| Joint-ownership group (including manual Vitesse–Chelsea and Grasshoppers–Wolves inclusions) | Red | `#C43C39` |
| Text, baselines, gridlines and unresolved evidence | Neutral charcoal / grey | `#333333` / `#D9D9D9` |

Use additional colours only if they carry a necessary, clearly explained category. Keep colour meanings consistent across panels, and reinforce important distinctions with marker shape, fill or direct labels so they remain interpretable in greyscale.

Use a white background, restrained styling, consistent fonts and clear panel labels **A**, **B**, **C**. Every quantitative panel needs an informative title and correctly matched **x-axis and y-axis labels**, with units. Include **light horizontal grid/reference lines**, drawn behind the data; panel C also needs clearly distinguished horizontal median markers. A zero baseline and sensible tick spacing should make counts easy to read. For panel B's horizontal bars, add light horizontal row guides and use the count axis ticks to locate expected markers accurately.

Bars must start at zero. Expected counts may be fractional, while observed counts are integers. Avoid decorative effects that compete with the data. Legends should explain symbols and colours without repeating information already directly labelled. Keep the figure-level title short; use panel titles and short annotations to carry the detailed message.

### Panel specification

- **A — Recorded arrivals:** use the season-specific `pl_arrivals` in the results JSON's `season_coverage` to plot an orange seasonal arrival profile. Label x **Transfer season** and y **Recorded Premier League arrivals**. Add a compact, prominent summary of **2,882 arrivals**, **500 origins**, **42 destinations** and **1,988 observed routes**. Put the 19,712 eligible-record context in a short annotation or caption. This quantitative panel replaces the earlier schematic count-diagram suggestion so the axes and horizontal gridlines have a meaningful role. Show a readable subset of season tick labels, preserve missing-season gaps, and label sparse/partial coverage. Present the profile as recorded sample coverage, not a measured population trend.
- **B — Unusually frequent routes:** follow the six-route table in section 2. Draw orange horizontal observed-count bars and blue expected-count markers. Label x **Recorded transfers per route** and y **Origin → Premier League destination**; the legend must clarify that blue markers are seasonal-null expectations. Add observed/expected values directly. Mark verified ownership in red using a separate status symbol or short annotation, preserving orange/blue meanings for count versus expectation. Show unresolved/family-connected cases distinctly from confirmed ownership. For Girona explicitly show **12/17 during shared ownership**; Strasbourg **11/11**; Udinese **9/9**. Include **999 seasonal shuffles; at least 2 transfers and unadjusted p < 0.05** and the **239-route** selection somewhere readable in the combined figure.
- **C — Ownership and volume:** plot all **239 selected routes** as individual points, grouped as **Joint-ownership group (n = 17; includes Vitesse–Chelsea and Grasshoppers–Wolves by user decision)** in red and **Remaining selected routes (n = 222)** in orange. Label x **Ownership classification** and y **Recorded transfers per route (pooled)**. Use deterministic jitter or an equivalent displacement that reveals the discrete count distribution, with clearly labelled horizontal medians **4** and **2**. Mean values **5.71** and **2.81** can be secondary annotations if space permits. State visibly that this is a descriptive comparison. The remaining group includes unresolved cases and two historical-only ownership pairs; it is not a verified independently owned control group.

### Verification and completion criteria

1. Verify the saved tables agree with the numeric checkpoints in this plan before plotting; calculate plotting values from the tables rather than using the prose as hardcoded data. Investigate material discrepancies instead of forcing the checkpoints.
2. Produce the complete combined three-panel figure and its three export formats. Titles, both axis labels, count units, needed legends, horizontal guides, ownership status and key annotations must be present and legible.
3. Inspect the saved full figure and enlarged views of every panel. Check clipping, long club names, overlapping markers/text, legend placement and horizontal-line visibility. Inspect again at its intended printed width and revise spacing or height until readable.
4. Check the figure and caption use the 17/222 comparison, pooled counts and unadjusted significance rule consistently. Ownership symbols must respect the saved evidence, including unresolved cases and Girona's pre-acquisition records. Add no inferential significance stars or error bars to panel C without an additional specified statistical analysis.
5. Finish by linking the PNG, PDF, SVG, caption and plotting script, and report numeric and visual verification. The first deliverable is the full-width combined figure, rather than a slide deck or a set of standalone panels.

## Narrative

Move from **recorded transfer activity**, to **departures from the seasonal shuffle model**, to **shared ownership among higher-volume selected routes**.

Suggested title: **Shared ownership features in the largest unusually frequent routes into the Premier League.**

The supported result is a descriptive association with repeated transfer volume. The audit has not established that most unusually frequent routes share an owner, or that shared ownership caused the concentration.

## 1. Establish the size of the recorded network

Lead with **2,882 recorded Premier League arrivals**, from **500 supplying clubs** into **42 receiving clubs**, forming **1,988 observed origin–destination routes**. The arrivals involve 1,445 distinct players and were selected from 19,712 eligible transfer records. Premier League status is evaluated in the transfer season, not from current membership.

**Visual:** panel A uses the seasonal arrival profile and compact summary counts specified in the execution brief. It establishes both the size and uneven coverage of the recorded network. A detailed club network can be supplementary.

**Caption:** Counts describe recorded movements, including loans and returns, rather than necessarily permanent sales. All recorded seasons are retained, including sparse and partial coverage.

**Verify:** numbers agree with `premier_league_feeder_results.json`; figure labels distinguish records, players and routes.

## 2. Show which routes are unusually frequent

Explain the null model in one sentence: **Randomly reassign Premier League destinations among arrival records within each season, preserving every origin's PL-bound total and every destination's recruitment total in that season.** Origins, players and seasons remain fixed. Repeat 999 times using seed 2026.

Lead with **239 selected recurring routes**, each with **at least 2 recorded transfers and unadjusted upper-tail p < 0.05**. The statistical threshold identifies unusually concentrated movement under the seasonal shuffle; the recurrence cutoff is a design choice to focus on repeated movement. Apply both criteria equally to ownership groups after running the shuffle on the full sample. There are 328 routes with p < 0.05, of which 89 have only one transfer and are excluded. The prior p <= 0.05 rule retained 241 recurring routes; strict p < 0.05 excludes two at the boundary, giving 239.

**Visual:** plot actual counts as bars and seasonal-null expectations as markers for the largest selected routes, ranked by observed count. Use a fixed display rule and include ties at the cutoff. As a compact initial view, show the six routes with at least eight recorded transfers:

| Route | Recorded | Expected | Ownership evidence |
| --- | ---: | ---: | --- |
| Girona → Manchester City | 17 | 1.910 | Confirmed, with 12 records during overlap |
| Strasbourg → Chelsea | 11 | 1.636 | Confirmed, all 11 during overlap |
| Grasshoppers → Wolves | 10 | 0.953 | Joint-ownership group by user decision; common equity unverified |
| Udinese → Watford | 9 | 0.846 | Confirmed, all 9 during overlap |
| Leeds → Tottenham | 8 | 1.771 | No documented common equity found |
| Vitesse → Chelsea | 8 | 1.361 | Joint-ownership group by user decision; ownership dates unresolved |

This is a readability subset of the largest flows, not a new significance test or an ownership-selected sample. A supplementary observed-versus-expected plot can display the full tested set.

**Caption:** Significance is the unadjusted per-route Monte Carlo p-value, with ties included and a plus-one correction. The minimum p-value is 0.001. Expected counts are averages under the seasonal null and may be fractional. Merely exceeding the mean is not the significance criterion: 1,821 observed routes exceed expectation, whereas 328 meet the p-value threshold and 239 also meet the recurrence requirement.

**Verify:** bar counts and expectation markers come from the same full route table; all ties at the cutoff are shown; the p-value rule is explicit. Do not describe the null as an unconstrained random graph.

## 3. Reveal the ownership link and compare transfer volume

Reveal ownership categories on the same ranked-route figure: **joint-ownership group**, **unresolved/related**, and **no documented link found**. Label Vitesse–Chelsea and Grasshoppers–Wolves as manual group inclusions. In addition to pooled counts, annotate how many records actually occur during shared ownership. This keeps the two largest routes prominent without implying that every large route is co-owned.

Then show a **dot plot with median markers** for all 239 selected routes, grouped into the joint-ownership group (15 verified-overlap routes plus Vitesse–Chelsea and Grasshoppers–Wolves by user decision) and remaining selected routes. Include the group sizes in the axis labels and display the underlying observations so that the many two- and three-record routes remain visible.

| Descriptive measure | Joint-ownership group | Remaining selected routes |
| --- | ---: | ---: |
| Routes | 17 | 222 |
| Mean pooled transfer count | 5.71 | 2.81 |
| Median pooled transfer count | 4 | 2 |
| Routes containing one transfer | 0 | 0 |

Lead with: **The two highest-count significant routes connect clubs with common investors, and routes in the joint-ownership group have twice the median pooled transfer count of the remaining selected routes.**

Use **17 of 239 (7.11%)** as the joint-ownership group count, including Vitesse–Chelsea and Grasshoppers–Wolves by user decision. The verified ownership-concurrent pair count remains **15 of 239 (6.28%)**. The broader historical audit found 17 pairs with ownership overlap somewhere in the modelling interval, but Granada–Watford and Hearts–Liverpool have no selected transfer during that overlap. Show the broader 17-pair definition in a methods note or appendix.

The group comparison uses pooled counts: the 17 routes contain 97 records in total, of which 73 occurred during verified shared ownership. Five Girona records and one Lorient record precede ownership completion; the eight Vitesse–Chelsea and ten Grasshoppers–Wolves records have unresolved ownership timing. Label the other group as “remaining selected routes,” not “independently owned,” because it contains unresolved cases and two historical-only ownership links.

**Verify:** plot all 239 routes, with 17/222 group sizes; identify Vitesse–Chelsea and Grasshoppers–Wolves as manual group inclusions while preserving unresolved source evidence; reproduce means and medians from the audit CSV; state that this comparison is descriptive and has not tested an ownership effect. Pooled expectations are not estimates specifically for the ownership period.

## Condensed report wording

We analysed **2,882 recorded Premier League arrivals** across **1,988 club-to-club routes**. A seasonal destination-shuffle model identified **239 recurring, unusually frequent routes** using **unadjusted p < 0.05 and at least 2 recorded transfers per route**. The p-value threshold is the statistical criterion; the recurrence cutoff is the design criterion. Together these routes contain **721 recorded transfers**. The two highest-count selected routes—Girona → Manchester City (**17 observed versus 1.91 expected**) and Strasbourg → Chelsea (**11 versus 1.64**)—connect clubs with common investors. Twelve Girona–City records and all eleven Strasbourg–Chelsea records occurred during ownership overlap. Across the selected sample, the **17 routes in the joint-ownership group (including Vitesse–Chelsea and Grasshoppers–Wolves by user decision) had a median of four pooled transfer records**, compared with **two** for the remaining routes. Shared ownership therefore features in some of the largest unusual flows, while the observed association does not establish its cause or financial purpose.

## Deliverable order

1. Create panel A's seasonal arrival profile and summary counts; verify values and labels against the saved results.
2. Create the actual-versus-expected route chart using the stated display rule; verify values and p-value labels.
3. Add ownership evidence and timing annotations; create the full-sample ownership-volume comparison; check group counts and descriptive statistics.
4. Assemble the full-width three-panel Matplotlib figure and export its PNG, PDF and SVG versions with the caption. Inspect the actual saved outputs and their readability at the report's printed width before delivery.

## Sources

- [Transfer analysis summary](../output/premier_league_feeder_summary.md)
- [Complete route table](../output/premier_league_feeder_routes.csv)
- [Transfer analysis results](../output/premier_league_feeder_results.json)
- [Source-linked ownership audit](premier_league_feeder_ownership_audit.md)
- [All 239 ownership classifications](../output/premier_league_feeder_ownership_audit.csv)
- [Ownership event-date flags](../output/premier_league_feeder_ownership_events.csv)

The principal scope is recorded player movement. Ownership histories do not supply transfer-type labels, sell-on clauses, resale proceeds or proof of a financial mechanism. A claim that ownership-linked routes are overrepresented across the whole network would require ownership labels for the comparison network, beyond this selected-route audit.
