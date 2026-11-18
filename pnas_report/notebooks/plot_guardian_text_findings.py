"""Plot the saved Guardian text-part findings (H2, H2b, coverage) in the group style.

Run from any directory (PowerShell):  python -B <repo>/pnas_report/notebooks/plot_guardian_text_findings.py

Style: pnas_report/PLOTTING_STYLE.md (Arial, default palette, 7.16 in combined / 3.58 in standalone).
Data: the saved CSVs in pnas_report/figures/plotting/data/ (nothing is recomputed; the asserts below
check that the inputs are the ones behind the paper's numbers).
Output: pnas_report/output/guardian_text_findings/ (combined + standalone, PDF/PNG/SVG) and two
compatibility PDFs in pnas_report/paper/figures/ that main.tex already includes.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FixedLocator, MultipleLocator, NullLocator  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parents[1]          # pnas_report/
DATA = PROJECT_DIR / "figures" / "plotting" / "data"
OUT = PROJECT_DIR / "output" / "guardian_text_findings"
PAPER_FIG = PROJECT_DIR / "paper" / "figures"

# ---- style (PLOTTING_STYLE.md) -------------------------------------------------------------
WIDTH_IN, HALF_IN = 7.16, 3.58          # combined / standalone width
PALETTE = ["#372107", "#895211", "#DC831B", "#F9AB50", "#FBC382"]
OLD, YOUNG = PALETTE[2], PALETTE[0]     # 30+ = orange, under 30 = dark brown (both figures)
SPEC = PALETTE[1]                       # gap figure: no controls (hollow circle) vs controls (filled diamond)
CHARCOAL, DIST_GRID, ROW_GUIDE, LEGEND_EDGE = "#333333", "#B0B0B0", "#E4E4E4", "#BBBBBB"
LINE_W = 1.5

FONT = "Arial"
if not any(f.name == FONT for f in font_manager.fontManager.ttflist):
    # Liberation Sans has Arial's metrics; used only for previews on machines without Arial.
    print("WARNING: Arial not found, preview font Liberation Sans used. Final exports must be made with Arial.")
    FONT = "Liberation Sans"

plt.rcParams.update({
    "font.family": FONT, "font.size": 9.5, "text.color": CHARCOAL,
    "axes.labelcolor": CHARCOAL, "axes.edgecolor": CHARCOAL, "axes.linewidth": 0.6,
    "xtick.color": CHARCOAL, "ytick.color": CHARCOAL,
    "axes.labelsize": 9.5, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.pad": 2, "ytick.major.pad": 2,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.fontsize": 8, "axes.unicode_minus": True,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})

MODELS = ["RoBERTa (main)", "VADER", "Bing", "Bing, no football words"]
CTRL_KEY = {"RoBERTa (main)": "RoBERTa", "VADER": "VADER", "Bing": "Bing",
            "Bing, no football words": "Bing, no football words"}
TONE_COL = {"RoBERTa (main)": "roberta", "VADER": "vader", "Bing": "bing",
            "Bing, no football words": "bing_nofootball"}
STEM = {"RoBERTa (main)": "roberta", "VADER": "vader", "Bing": "bing", "Bing, no football words": "bing_nofootball"}
S0, S1 = "1 no controls (as 11 Nov)", "7 all: no quotes, type adjusted, fame + value"


# ---- data + checks ------------------------------------------------------------------------
def read_and_verify():
    raw = pd.read_csv(DATA / "a1_h2_arc_4models.csv", encoding="utf-8-sig")
    adj = pd.read_csv(DATA / "a1_h2b_arc.csv", encoding="utf-8-sig")
    ctl = pd.read_csv(DATA / "a1_h2b_controls.csv", encoding="utf-8-sig")
    cov = pd.read_csv(DATA / "a1_coverage_age.csv", encoding="utf-8-sig")
    st = pd.read_csv(DATA / "signing_tone.csv", encoding="utf-8-sig")

    assert len(st) == 1332 and st.age30plus.sum() == 88
    main = st[st.in_main_sample]
    n_old, n_young = int(main.age30plus.sum()), int((~main.age30plus).sum())
    assert (n_old, n_young) == (67, 753)
    old, young = main[main.age30plus], main[~main.age30plus]
    assert [round(x, 4) for x in (old.roberta_before.mean(), old.roberta_after.mean(),
                                  young.roberta_before.mean(), young.roberta_after.mean())] \
        == [0.0914, 0.0838, 0.1253, 0.1117]
    for d in (raw, adj):
        assert sorted(d.model.unique()) == sorted(MODELS)
        assert sorted(d.month.unique()) == list(range(-12, 12))
        assert len(d) == 4 * 2 * 24
    r = ctl.set_index(["model", "spec", "period"]).gap_30plus_minus_under30
    assert round(r["RoBERTa", S1, "after"], 4) == -0.0349 and round(r["RoBERTa", S1, "before"], 4) == -0.0153
    n_adj = ctl[(ctl.spec == S1) & (ctl.model == "RoBERTa")].iloc[0]
    assert (n_adj.n_30plus, n_adj.n_under30) == (65, 728)
    c = cov[cov.articles == "all article types"].set_index(["spec", "period"]).ratio_30plus_vs_under30
    assert [round(c["season only", p], 2) for p in ("before", "after", "change")] == [2.24, 1.44, 0.65]
    return raw, adj, ctl, cov, main, (n_old, n_young), (int(n_adj.n_30plus), int(n_adj.n_under30))


# ---- shared helpers -------------------------------------------------------------------------
def legend(ax, handles, loc, **kw):
    leg = ax.legend(handles=handles, loc=loc, frameon=True, fancybox=True, borderpad=0.6,
                    handlelength=2.0, labelspacing=0.45, borderaxespad=0.5, **kw)
    frame = leg.get_frame()
    frame.set_facecolor("white"), frame.set_edgecolor(LEGEND_EDGE), frame.set_linewidth(0.6)
    frame.set_boxstyle("round,pad=0,rounding_size=0.25")
    return leg


def save(fig, stem, folder=OUT, formats=("pdf", "png", "svg")):
    folder.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        # fixed page size (no tight cropping), PNG at 600 dpi
        fig.savefig(folder / f"{stem}.{ext}", dpi=600 if ext == "png" else None)


# ---- arcs (H2 raw, H2b adjusted) -------------------------------------------------------------
def draw_arc(ax, d, ycol, ylabel, counts, show_x=True, show_y=True, legend_loc=None, headroom=False):
    ax.set_axisbelow(True)
    ax.grid(True, color=DIST_GRID, linewidth=0.65)
    ax.axvline(0, color=CHARCOAL, linewidth=0.8, linestyle=(0, (3, 2)), zorder=1)
    for g, col in (("Under 30", YOUNG), ("30+", OLD)):
        for after in (False, True):           # before and after drawn apart: smoothing never bridges the move
            s = d[(d.group == g) & ((d.month >= 0) == after)].sort_values("month")
            ax.plot(s.month + 0.5, s[ycol], color=col, linewidth=LINE_W, solid_capstyle="butt", zorder=3)
    ax.set_xlim(-12.5, 12.5)
    ax.xaxis.set_major_locator(MultipleLocator(3))
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    if show_x:
        ax.set_xlabel("Months from the transfer")
    if show_y:
        ax.set_ylabel(ylabel)
    if legend_loc:
        if headroom:                           # free band above the curves for the legend
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo, hi + 0.5 * (hi - lo))
        legend(ax, [Line2D([], [], color=OLD, lw=LINE_W, label=f"30+ (n = {counts[0]})"),
                    Line2D([], [], color=YOUNG, lw=LINE_W, label=f"Under 30 (n = {counts[1]})")], legend_loc)


def arc_figures(data, ycol, ylabel, counts, stem):
    # common y-range per model is set by the data; ticks stay equally spaced (0.05)
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_IN, 4.6))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.935, bottom=0.1, hspace=0.45, wspace=0.2)
    for i, (ax, m, letter) in enumerate(zip(axes.ravel(), MODELS, "abcd")):
        draw_arc(ax, data[data.model == m], ycol, ylabel, counts, show_x=i >= 2, show_y=i % 2 == 0,
                 legend_loc="upper right" if i == 0 else None, headroom=i == 0)
        ax.set_title(f"({letter}) {m}", loc="left", fontsize=10, pad=6)
    save(fig, f"{stem}_combined")
    combined = fig
    for m in MODELS:
        f, ax = plt.subplots(figsize=(HALF_IN, 2.75))
        f.subplots_adjust(left=0.2, right=0.97, top=0.97, bottom=0.17)
        draw_arc(ax, data[data.model == m], ycol, ylabel, counts, legend_loc="upper right", headroom=True)
        save(f, f"{stem}_{STEM[m]}")
        plt.close(f)
    return combined


# ---- tone gaps + coverage ------------------------------------------------------------------
def point(ax, y, x, lo, hi, filled):
    ax.plot([lo, hi], [y, y], color=SPEC, linewidth=1.3, solid_capstyle="butt", zorder=2)
    if filled:
        ax.plot(x, y, "D", ms=5.2, mfc=SPEC, mec="none", zorder=3)
    else:
        ax.plot(x, y, "o", ms=5.6, mfc="white", mec=SPEC, mew=1.3, zorder=3)


def spec_handles(labels):
    return [Line2D([], [], color=SPEC, lw=1.3, marker="o", ms=5.6, mfc="white", mec=SPEC, mew=1.3, label=labels[0]),
            Line2D([], [], color=SPEC, lw=1.3, marker="D", ms=5.2, mfc=SPEC, mec="none", label=labels[1])]


OFF = 0.17
YLAB = {"RoBERTa (main)": "RoBERTa\n(main)", "VADER": "VADER", "Bing": "Bing",
        "Bing, no football words": "Bing, no\nfootball words"}


def draw_gap(ax, ctl, period, show_labels=True, show_legend=False, xlabel=True, headroom=False):
    ys = np.arange(len(MODELS))[::-1]
    ax.set_axisbelow(True)
    for y in ys:
        ax.axhline(y, color=ROW_GUIDE, linewidth=0.45, zorder=0)
    ax.axvline(0, color=CHARCOAL, linewidth=0.6, zorder=1)
    for y, m in zip(ys, MODELS):
        for spec, dy, filled in ((S0, OFF, False), (S1, -OFF, True)):
            r = ctl[(ctl.model == CTRL_KEY[m]) & (ctl.spec == spec) & (ctl.period == period)].iloc[0]
            point(ax, y + dy, r.gap_30plus_minus_under30, r.ci_lo, r.ci_hi, filled)
    ax.set_xlim(-0.16, 0.08)
    ax.xaxis.set_major_locator(MultipleLocator(0.05))
    ax.set_ylim(-0.6, len(MODELS) - 0.4 + (0.95 if show_legend or headroom else 0))
    ax.set_yticks(ys)
    ax.set_yticklabels([YLAB[m] for m in MODELS] if show_labels else [])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    if xlabel:
        ax.set_xlabel("Tone gap, 30+ minus under 30")
    if show_legend:
        legend(ax, spec_handles(["No controls", "All controls"]), "upper right")


COV_ROWS = [("before", "Before"), ("after", "After"), ("change", "Growth,\nafter/before")]


def draw_coverage(ax, cov, show_legend=True):
    ys = np.arange(len(COV_ROWS))[::-1]
    c = cov[cov.articles == "all article types"]
    ax.set_axisbelow(True)
    for y in ys:
        ax.axhline(y, color=ROW_GUIDE, linewidth=0.45, zorder=0)
    ax.axvline(1, color=CHARCOAL, linewidth=0.6, zorder=1)
    for y, (period, _) in zip(ys, COV_ROWS):
        for spec, dy, filled in (("season only", OFF, False), ("+ market value", -OFF, True)):
            r = c[(c.spec == spec) & (c.period == period)].iloc[0]
            point(ax, y + dy, r.ratio_30plus_vs_under30, r.ratio_lo, r.ratio_hi, filled)
    ax.set_xscale("log")
    ax.set_xlim(0.4, 8)
    ax.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4]))     # equal steps on the log axis
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels(["0.5", "1", "2", "4"])
    ax.set_ylim(-0.6, len(COV_ROWS) - 0.4 + 0.3)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in COV_ROWS])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Articles, 30+ / under 30\n(ratio, log scale)")
    if show_legend:
        legend(ax, spec_handles(["Season only", "+ market value"]), "lower right")


def gap_figures(ctl, cov):
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH_IN, 3.1), gridspec_kw={"width_ratios": [1, 1, 1.1]})
    fig.subplots_adjust(left=0.115, right=0.985, top=0.9, bottom=0.21, wspace=0.42)
    draw_gap(axes[0], ctl, "before", headroom=True)   # same rows as (b)
    draw_gap(axes[1], ctl, "after", show_labels=False, show_legend=True)
    draw_coverage(axes[2], cov)
    for ax, t in zip(axes, ["(a) Tone, year before", "(b) Tone, year after", "(c) Coverage volume"]):
        ax.set_title(t, loc="left", fontsize=10, pad=6)
    save(fig, "h2b_tone_gap_coverage_combined")
    for period, stem in (("before", "h2b_tone_gap_before"), ("after", "h2b_tone_gap_after")):
        f, ax = plt.subplots(figsize=(HALF_IN, 2.75))
        f.subplots_adjust(left=0.27, right=0.96, top=0.97, bottom=0.17)
        draw_gap(ax, ctl, period, show_legend=True)
        save(f, stem)
        plt.close(f)
    f, ax = plt.subplots(figsize=(HALF_IN, 2.75))
    f.subplots_adjust(left=0.27, right=0.96, top=0.97, bottom=0.22)
    draw_coverage(ax, cov)
    save(f, "coverage_ratio")
    plt.close(f)
    return fig


def main():
    raw, adj, ctl, cov, main_sample, n_raw, n_adj = read_and_verify()
    f1 = arc_figures(raw, "mean_smooth", "Sentiment (−1 to 1)", n_raw, "h2_raw_tone_arc")
    f2 = arc_figures(adj, "smooth", "Adjusted sentiment (−1 to 1)", n_adj, "h2b_adjusted_tone_arc")
    f3 = gap_figures(ctl, cov)
    # compatibility exports: the filenames main.tex already includes
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    f2.savefig(PAPER_FIG / "fig_h2b_arc_paper.pdf")
    f3.savefig(PAPER_FIG / "fig_h2b_tone_coverage.pdf")
    print(f"font: {FONT}; wrote {len(list(OUT.glob('*')))} files to {OUT} and 2 PDFs to {PAPER_FIG}")


if __name__ == "__main__":
    main()
