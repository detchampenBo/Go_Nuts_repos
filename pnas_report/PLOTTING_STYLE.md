# Scientific plotting style

Use this guide when creating analysis plots or changing their presentation in this project. It records the agreed style from the Premier League feeder figures. Explicit user instructions and the target report template take precedence over these defaults.

## Workflow

1. Define what each observation represents, the selected sample, the comparison groups and the question. Verify counts against the saved analysis before drawing. Presentation changes preserve those inputs and classifications.
2. Choose an encoding that answers the question. Use bars and reference markers for observed-versus-expected comparisons; use normalised distributions to compare groups of unequal size. Record the denominator, threshold convention and any display subset.
3. Design at the final physical publication size. Apply the typography, colours, axes and legend conventions below. Move methods, caveats and detailed statistics into the findings recap.
4. Export the combined and standalone views, then inspect the actual PDFs at publication size. Finish when values, layout, fonts and orientation pass the checks below.

## Colour

Default palette, in the user's specified order:

```python
plot_colors = ["#372107", "#895211", "#DC831B", "#F9AB50", "#FBC382"]
```

Use these colours for new analyses unless another palette or semantic colour assignment is requested. Keep each meaning consistent across panels, standalone exports, labels and legends. Colour alone should not carry the full explanation: use clear labels and, where suitable, different marker shapes or luminance.

The feeder figures have explicit assignments that override the default cycle:

| Meaning | Colour | Encoding |
| --- | --- | --- |
| Observed transfers | `#DC831B` | Filled bars, regardless of ownership |
| Null-model expectation | `#0072B2` | Blue diamond and matching numerical label |
| Joint ownership | `#C43C39` | Solid red curve; filled red annotation dots |
| Remaining routes | `#372107` | Solid dark-brown curve |
| Text and axes | `#333333` | Charcoal |
| Distribution grid | `#B0B0B0` | Major gridlines, 0.65 pt |
| Bar-row guides | `#E4E4E4` | Horizontal guides, 0.45 pt |

The final feeder curves are both solid. Keep the matching legend samples solid too. Earlier dashed curves and brown square matrices were superseded by the current exceedance plot.

## Typography and page size

| Element | Default |
| --- | --- |
| Typeface | Arial throughout; verify the actual exported fonts |
| Axis labels and main annotation text | 9.5 pt |
| Tick labels and compact numerical annotations | 9 pt |
| Combined-panel titles | 10 pt, left aligned, prefixed `(a)`, `(b)`, etc. |
| Legend text | 8 pt |
| Background | White |
| Combined figure width | 7.16 inches, unless the report template specifies otherwise |
| Standalone figure width | 3.58 inches, unless the report template specifies otherwise |
| Current reference height | 4.6 inches; adjust height to suit the next analysis |

Combined figures have short panel titles. Standalone plots have **no plot title or subfigure letter**; their titles belong in the report. Axis labels and legends remain on standalone plots. Keep large overall titles, explanatory subtitles and methodological footers in the report or findings recap.

Size text for the final printed width, rather than shrinking a large figure after export. Allocate panel widths and margins according to the content; the layout coordinates in the reference script are examples, not universal dimensions.

## Axes and gridlines

- Use a linear axis by default, with equally spaced major tick values and positions. In the current figures, transfer-count ticks advance by 5 for bars and by 2 for exceedance curves.
- Start quantitative bars at zero. The current exceedance x-axis also starts at zero. Use a logarithmic scale only when explicitly justified and labelled; zero cannot appear on a log axis.
- Include descriptive axis labels and units. Let category names identify rows or groups without a redundant axis title.
- Distribution plots use visible horizontal and vertical major gridlines behind the data. Bar comparisons use light horizontal row guides; vertical grids are optional when they help numerical reading without competing with annotations.
- Hide top and right spines. Use 0.6 pt for the remaining spines; use short, restrained ticks (reference: 2.5 pt length, 0.6 pt width).
- Give the plotting area enough clearance for endpoints and labels. The feeder percentage axis extends slightly above 100% so its initial plateau stays visible.

## Legends and annotations

Use only entries needed to interpret the marks. Group entries vertically in a single column by default, with sample sizes beside group names for distribution comparisons. Use a white box, slightly rounded corners, a thin light-grey border (`#BBBBBB`, 0.6 pt) and enough internal spacing for clear reading.

Place legends inside an empty part of the plotting area: lower right for the current bar panel, upper right for the exceedance panel. Adjust space or wrap a long entry before reducing the font below 8 pt. Inspect the legend against text, bars and complete curve segments, not only against data endpoints.

For observed-versus-expected comparisons:

- Use integer observed totals at bar ends and one decimal place for displayed expectations. Keep full precision in calculations.
- Label expectations **Expected transfers (null model)**, wrapping the parenthesis onto a second line if needed. The displayed expectation is pooled over the analysed period; season-specific constraints describe the model, not a single-season plotted total.
- Write directed club pairs with short, straight, filled vector arrows between names. Vector arrows avoid unsupported font glyphs and give a thicker shaft.
- Put ownership dots immediately after the destination name, followed by the relevant count annotation. Use filled markers with no dark outline.
- Keep a marker's physical diameter consistent across panels and legend entries. The current red annotation dots are approximately 5.09 pt in diameter. Matplotlib scatter `s` is an area: a 1.2x increase in marker width and height requires multiplying `s` by `1.2**2`; `Line2D.markersize` is already a length.

Define every fraction in the findings recap and derive its numerator and denominator from the appropriate source. The feeder-specific `8/8` and `10/10` exceptions describe manual inclusion coverage, rather than verified ownership-period overlap; their meanings remain documented in the [findings recap](output/premier_league_feeder_summary.md). Carry that distinction forward when reusing the annotation pattern.

## Comparing transfer-count distributions

The final distribution choice is an **empirical exceedance curve**, replacing the individual dot matrix. At threshold `x`, calculate:

```text
exceedance_percent(x) = 100 * number of group observations with count >= x
                            / total number of observations in that group
```

Normalise each group separately. Use every selected observation in its group, rather than only the prominent cases displayed in another panel. This permits a comparison of distribution shapes when group sample sizes differ.

Evaluate integer thresholds from zero to one above the observed maximum. Draw exact step curves, using `where="pre"` for the inclusive `count >= x` convention. Keep counts discrete: no density smoothing, arbitrary histogram bins or fitted distribution are needed for this view.

The current axis labels are **Recorded transfers per route** and **Routes with at least x transfers (%)**. For another variable, adapt both labels and state the threshold convention explicitly. Include equality when testing the curve: an observation with count 4 contributes at threshold 4 and drops out at threshold 5.

If selection requires counts of at least 2, both curves are 100% at thresholds 0, 1 and 2. This plateau does not imply that observations with counts 0 or 1 are in the sample. Each curve reaches zero one threshold above its group's maximum.

Keep means and medians in the findings recap unless requested in the figure. The final feeder legend contains just the two group names and sample sizes; mean/median lines and statistical legend rows were removed.

These curves describe the selected sample. The plotting style does not determine eligibility rules, significance thresholds, ownership definitions or causal claims for a new analysis. In particular, the feeder selection of at least 2 transfers and unadjusted `p < 0.05` is specific to that analysis, not a universal plotting rule.

## Files and reproduction

Keep plotting code under `notebooks/` and resolve paths relative to `__file__`. Read saved analysis outputs for presentation changes. Derive annotations, distributions and statistics from those inputs.

Put deliverables in a descriptive folder inside `output/`, following this structure:

```text
output/<analysis>_findings/
    README.md
    combined.pdf / .png / .svg
    <descriptive_panel_a_name>.pdf / .png / .svg
    <descriptive_panel_b_name>.pdf / .png / .svg
```

Export all three views from the same data and plotting logic. Standalone plots contain only their own axes, labels and legend; they are vector exports, not screenshot crops. Export PDFs with embedded fonts, PNGs at 600 dpi, and SVGs with editable text. Use `pdf.fonttype = 42` and `svg.fonttype = "none"` in Matplotlib. Preserve intended page dimensions when saving rather than relying on automatic tight cropping. Keep existing filenames as compatibility exports when report references depend on them.

Provide a short folder README linking the formats and stating the reproduction command. Keep a brief, descriptive caption separate from the fuller findings recap, which holds coverage, model, selection, annotation definitions, group statistics and limitations.

## Verification before delivery

- Confirm that cohort counts, eligibility and classifications match the saved analysis. Reformatting must not alter observations or analytical results.
- Check displayed counts and rounded labels against their full-precision inputs; apply display cutoffs consistently and include all ties.
- Check exceedance normalisation, the `>=` boundary, monotonicity, the 0-100% range, the initial plateau and the terminal zero. Verify selected thresholds by direct counting.
- Verify equally spaced ticks on linear axes, zero baselines and explicit scale labels.
- Check that legend colours and marks match the data, that marker outlines follow the requested style, and that every legend fits without covering observations, curves or labels.
- Render and inspect each PDF at its intended publication width, including a grayscale view. Check actual output for clipped labels and legibility.
- Verify embedded fonts, vector content, 0-degree PDF page rotation and upright horizontal titles/text. Check both rotation metadata and the rendered page before treating a rotated viewer preview as a file error.
- Verify that combined titles are present, standalone titles are absent, and all PDF/PNG/SVG files reflect the latest run. Summarise any discrepancies rather than changing cohorts to match expected numbers.

## Reference implementation

- [Plotting and export source](notebooks/plot_premier_league_feeder_findings.py)
- [Current combined and standalone figures](output/premier_league_feeder_findings/README.md)
- [Findings and method recap](output/premier_league_feeder_summary.md)

To apply this style in a later task, ask: **"Use `pnas_report/PLOTTING_STYLE.md` for this analysis, with its default palette unless I specify other colours."**
