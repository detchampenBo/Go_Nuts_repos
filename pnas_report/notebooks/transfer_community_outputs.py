"""Save and render community analysis outputs from verified results."""

import argparse
from collections import Counter
from html import escape
import json
import math
from pathlib import Path
import re
import shutil
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors, font_manager, patheffects
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import networkx as nx
import pandas as pd
from pyvis.network import Network

from transfer_community_inputs import (
    SHARED, TOL, WEIGHT, checksum, load_graph, modularity, partition_key, require, write_json,
)

PALETTE = ["#372107", "#895211", "#DC831B", "#F9AB50", "#FBC382"]
ORANGE, BLUE = "#DC831B", "#0072B2"
REFERENCES = {
    "leiden": "[Traag, Waltman and Van Eck (2019)](https://arxiv.org/abs/1810.08473) and "
              "[leidenalg API](https://leidenalg.readthedocs.io/en/latest/reference.html)",
    "louvain": "[Blondel et al. (2008)](https://doi.org/10.1088/1742-5468/2008/10/P10008), "
               "[Dugué and Perez (2015)](https://hal.science/hal-01231784) and "
               "[NetworkX Louvain API](https://networkx.org/documentation/networkx-3.6.1/reference/"
               "algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html)",
}


def community_colors(count):
    extra = [colors.to_hex(c).upper() for c in matplotlib.colormaps["tab20"].colors
             if colors.to_hex(c).upper() != BLUE]
    # Spread additional swatches across hue families before using lighter variants.
    palette = PALETTE + extra[::2] + extra[1::2]
    for index in range(max(0, count - len(palette))):
        palette.append(colors.to_hex(colors.hsv_to_rgb(((index * .61803398875) % 1, .55, .6))).upper())
    chosen = palette[:count]
    require(len(set(chosen)) == count and BLUE not in chosen, "Community colours are not unique")
    return chosen


def communities_tables(graph, groups, layout):
    ordered = sorted(partition_key(groups), key=lambda group: (-len(group), group))
    representatives = [min(group, key=lambda club: (-graph.degree(club), club)) for group in ordered]
    labels = nx.get_node_attributes(graph, "label")
    name_counts = Counter(labels[club] for club in representatives)
    in_strength, out_strength = dict(graph.in_degree(weight=WEIGHT)), dict(graph.out_degree(weight=WEIGHT))
    clubs, summary = [], []
    m = graph.size(weight=WEIGHT)
    for community, (group, rep, color) in enumerate(zip(
            ordered, representatives, community_colors(len(ordered))), start=1):
        name = labels[rep] if name_counts[labels[rep]] == 1 else f"{labels[rep]} ({rep})"
        inside = graph.subgraph(group).size(weight=WEIGHT)
        contribution = inside / m - sum(in_strength[c] for c in group) * sum(
            out_strength[c] for c in group) / m**2
        summary.append(dict(community_id=community, community_name=name, color=color,
                            community_size=len(group), representative_id=rep, representative_name=labels[rep],
                            representative_degree=graph.degree(rep), q_contribution=contribution))
        for club in group:
            clubs.append(dict(club_id=club, club_name=labels[club], community_id=community,
                              community_name=name, representative=club == rep, in_degree=graph.in_degree(club),
                              out_degree=graph.out_degree(club), total_degree=graph.degree(club),
                              in_strength=in_strength[club], out_strength=out_strength[club], color=color,
                              **layout.loc[club].to_dict()))
    require(len(clubs) == len(graph) and {row["club_id"] for row in clubs} == set(graph),
            "Observed community table does not cover each club once")
    require(abs(sum(row["q_contribution"] for row in summary) - modularity(graph, groups)) <= TOL,
            "Community contributions do not sum to final Q")
    return pd.DataFrame(clubs).sort_values("club_id"), pd.DataFrame(summary)


def save_results(method, output, shared, info, observed, layout, partitions, stats, settings, dependencies):
    clubs, summary = communities_tables(observed, partitions["observed"], layout)
    clubs.to_csv(output / "communities.csv", index=False)
    summary.to_csv(output / "community_summary.csv", index=False)
    shutil.copyfile(shared / "shuffled_routes.csv", output / "shuffled_routes.csv")
    require(checksum(output / "shuffled_routes.csv") == info["files_sha256"]["shuffled_routes.csv"],
            "Method shuffle copy differs from shared input")
    final_rows = [(run, community, club) for run, groups in partitions.items()
                  for community, group in enumerate(partition_key(groups), start=1) for club in group]
    pd.DataFrame(final_rows, columns=["run", "community_id", "club_id"]).to_csv(
        output / "final_partitions.csv", index=False)
    result = {name: info[name] for name in ("input_sha256", "counts", "directed", "weight",
              "resolution", "seeds", "shuffle", "club_name_conflicts")}
    result.update(method=method, weighting="eligible transfer records per directed route",
                  shared_inputs_sha256=checksum(shared / "shared_inputs.json"),
                  shared_files_sha256=info["files_sha256"], settings=settings,
                  tolerance=TOL, versions=dependencies, runs=stats,
                  q_observed=stats["observed"]["final_q"], q_shuffled=stats["shuffled"]["final_q"],
                  observed_community_sizes=summary.community_size.tolist(),
                  verification={"all_states_partition_original_clubs": True,
                                "all_saved_q_checks_pass": True,
                                "shuffled_in_out_degrees_and_weight_multiset_preserved": True,
                                "representative_and_contribution_checks_pass": True})
    result["delta_q"] = result["q_observed"] - result["q_shuffled"]
    write_json(output / f"{method}_results.json", result)
    return result


def configure_plotting():
    require(any(font.name == "Arial" for font in font_manager.fontManager.ttflist),
            "Arial is required for the publication exports")
    plt.rcParams.update({
        "font.family": "Arial", "font.size": 9, "axes.labelsize": 9.5, "axes.titlesize": 10,
        "text.color": "#333333", "axes.labelcolor": "#333333", "axes.edgecolor": "#333333",
        "xtick.color": "#333333", "ytick.color": "#333333", "axes.linewidth": .6,
        "axes.spines.top": False, "axes.spines.right": False,
        "xtick.major.width": .6, "ytick.major.width": .6, "xtick.major.size": 2.5,
        "ytick.major.size": 2.5, "legend.fontsize": 9, "legend.edgecolor": "#BBBBBB",
        "legend.facecolor": "white", "legend.framealpha": 1,
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })


def read_community_view(output, shared):
    info = json.loads((shared / "shared_inputs.json").read_text(encoding="utf-8"))
    require(checksum(shared / "observed_routes.csv") == info["files_sha256"]["observed_routes.csv"]
            and checksum(shared / "layout.csv") == info["files_sha256"]["layout.csv"],
            "Shared inputs changed before plotting")
    graph = load_graph(shared / "observed_routes.csv", info["node_order"])
    clubs = pd.read_csv(output / "communities.csv", float_precision="round_trip").set_index("club_id").loc[list(graph)]
    summary = pd.read_csv(output / "community_summary.csv", float_precision="round_trip")
    layout = pd.read_csv(shared / "layout.csv", float_precision="round_trip").set_index("club_id")
    require(clubs[["x", "y", "node_size"]].equals(layout), "Saved assignments use a different layout")
    return graph, clubs, summary


def legend(axis, handles, *, columns=1, location="lower left", anchor=None):
    box = axis.legend(handles=handles, ncols=columns, loc=location, bbox_to_anchor=anchor,
                      handletextpad=.4, columnspacing=1.0, borderpad=.45, labelspacing=.42)
    box.get_frame().set_linewidth(.6)
    return box


def network_legend_height(summary):
    return .25 + .19 * math.ceil(len(summary) / 2)


def draw_network(axis, legend_axis, view):
    graph, clubs, summary = view
    positions = {club: (row.x, row.y) for club, row in clubs.iterrows()}
    nx.draw_networkx_edges(graph, positions, ax=axis, arrows=False, edge_color="#60564C",
                           width=.18, alpha=.12)
    nx.draw_networkx_nodes(graph, positions, ax=axis, nodelist=list(clubs.index),
                           node_size=clubs.node_size, node_color=clubs.color, linewidths=0)
    axis.set(xlim=(-1.08, 1.08), ylim=(-1.08, 1.08), aspect="equal")
    axis.set_axis_off()
    handles = []
    occupied = []
    axis.apply_aspect()
    for row in summary.itertuples():
        x, y = positions[row.representative_id]
        # Numbered representative labels key directly to complete names below.
        offsets = [(0, 9), (9, 5), (-9, 5), (8, -8), (-8, -8), (0, -13), (14, 1), (-14, 1)]
        px, py = axis.transData.transform((x, y))
        scale = axis.figure.dpi / 72
        for offset in offsets:
            label = (px + offset[0] * scale, py + offset[1] * scale)
            if all(math.dist(label, other) > 12 * scale for other in occupied):
                break
        occupied.append(label)
        axis.annotate(str(row.community_id), (x, y), xytext=offset, textcoords="offset points",
                      ha="center", va="center", size=9, weight="bold", zorder=5, annotation_clip=False,
                      path_effects=[patheffects.withStroke(linewidth=2.5, foreground="white")],
                      arrowprops=dict(arrowstyle="-", lw=.55, color="#333333", shrinkA=0, shrinkB=0))
        name = f"{row.community_id}  {row.community_name} ({row.community_size})"
        handles.append(Line2D([], [], ls="", marker="o", markersize=5.1, color=row.color,
                              label=textwrap.fill(name, 28, break_long_words=False)))
    legend_axis.set_axis_off()
    legend(legend_axis, handles, columns=2, location="upper center", anchor=(.5, 1))


def draw_progress(axis, method, data, result):
    x_col, y_col, x_name = (
        ("iteration", "networkx_q", "Completed Leiden iterations") if method == "leiden"
        else ("move", "q", "Accepted Louvain moves")
    )
    observed = data.loc[data.run == "observed"]
    x = observed[x_col]
    q, null = result["q_observed"], result["q_shuffled"]
    observed_line, = axis.plot(x, observed[y_col], color=ORANGE, lw=1.25, marker="o",
                               markersize=3.2 if method == "leiden" else 1.1,
                               label=f"Observed ({x.iloc[-1]:,} {'iterations' if method == 'leiden' else 'moves'})\n"
                                     f"Q = {q:.4f}")
    null_line, = axis.plot([0, x.iloc[-1]], [null, null], color=BLUE, lw=1.15,
                           label=f"Degree-preserving shuffle\n(one graph), Q = {null:.4f}")
    axis.set(xlabel=x_name, ylabel="Directed weighted modularity, Q",
             xlim=(-.025 * max(x.iloc[-1], 1), 1.025 * max(x.iloc[-1], 1)))
    axis.margins(y=.10)
    axis.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    axis.yaxis.set_major_locator(MaxNLocator(nbins=5))
    axis.grid(color="#B0B0B0", alpha=.6, lw=.65)
    axis.set_axisbelow(True)
    legend(axis, [observed_line, null_line], location="lower right" if method == "leiden" else "upper left")


def export(fig, output, stem):
    for ext in ("pdf", "png", "svg"):
        fig.savefig(output / f"{stem}.{ext}", dpi=600 if ext == "png" else None)
    plt.close(fig)


def draw_network_panel(fig, rect, view, title=None, *, legend_height=None):
    left, bottom, width, height = rect
    legend_fraction = (legend_height or network_legend_height(view[2])) / fig.get_figheight()
    axis = fig.add_axes([left, bottom + legend_fraction, width, height - legend_fraction])
    if title:
        fig.text(left + .02, bottom + height, title, size=10, va="bottom")
    draw_network(axis, fig.add_axes([left, bottom, width, legend_fraction]), view)


def network_html(view):
    graph, clubs, summary = view
    net = Network(height="640px", width="100%", directed=True, cdn_resources="in_line")
    for row in clubs.reset_index().itertuples():
        details = (f"{row.club_name} (ID {row.club_id})\n"
                   f"Community {row.community_id} — {row.community_name}\n"
                   f"In-degree: {row.in_degree} · Out-degree: {row.out_degree}\n"
                   f"Incoming transfers: {row.in_strength} · Outgoing transfers: {row.out_strength}")
        net.add_node(row.club_id, x=row.x * 380, y=-row.y * 380, fixed=True, physics=False,
                     size=1.6 * math.sqrt(row.node_size), color=row.color, title=details)
        # add_node substitutes the club ID for an empty label.
        net.get_node(row.club_id)["label"] = str(row.community_id) if row.representative else ""
    for a, b, weight in graph.edges(data=WEIGHT):
        net.add_edge(a, b, title=f"{clubs.at[a, 'club_name']} → {clubs.at[b, 'club_name']}"
                                f"\nTransfer count: {weight}")
    net.set_options(json.dumps({
        "physics": {"enabled": False}, "interaction": {"hover": True, "tooltipDelay": 120},
        "nodes": {"shape": "dot", "font": {"color": "transparent", "strokeWidth": 0}, "borderWidth": 0},
        "edges": {"smooth": False, "width": .55, "color": {"color": "#5C5148", "opacity": .14,
                  "inherit": False}, "arrows": {"to": {"enabled": True, "scaleFactor": .18}}},
    }))
    html = net.generate_html()
    # PyVis 0.3.2 emits Bootstrap CDN tags even when it embeds vis-network.
    html = re.sub(r'<link\s+href="https://cdn\.jsdelivr\.net/[^>]+>', "", html)
    html = re.sub(r'<script\s+src="https://cdn\.jsdelivr\.net/[^>]+></script>', "", html)
    entries = "".join(f'<li data-community="{r.community_id}"><span style="background:{r.color}"></span>'
                      f'{r.community_id} {escape(r.community_name)} ({r.community_size})</li>'
                      for r in summary.itertuples())
    key = ('<style>body{font:14px Arial,sans-serif;color:#333;margin:0}'
           '#mynetwork{box-sizing:border-box;float:none!important}h1:empty{display:none}'
           '.vis-tooltip{white-space:pre-line!important}'
           '.key{display:flex;flex-wrap:wrap;gap:.5rem 1.4rem;list-style:none;padding:0 1rem}'
           '.key span{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}'
           '</style><ul class="key" aria-label="Communities and club counts">' + entries + '</ul>')
    representatives = summary.representative_id.tolist()
    # Draw the representative labels above the nodes, with room for adjacent representatives.
    labels = f"<script>const representativeIds = {json.dumps(representatives)};\n" + """
    network.on("afterDrawing", ctx => {
        const positions = network.getPositions(representativeIds);
        const scale = network.getScale();
        const offsets = [[0,-13],[14,-7],[-14,-7],[13,12],[-13,12],[0,19],[22,1],[-22,1]];
        const occupied = [];
        ctx.save();
        ctx.font = "bold " + 15/scale + "px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        representativeIds.forEach((id, index) => {
            const p = positions[id];
            const choices = offsets.map(([dx,dy]) => [p.x+dx/scale,p.y+dy/scale]);
            const [x,y] = choices.find(([x,y]) =>
                occupied.every(([a,b]) => Math.hypot(x-a,y-b)*scale >= 17)) ?? choices.at(-1);
            occupied.push([x,y]);
            ctx.beginPath();
            ctx.moveTo(p.x,p.y);
            ctx.lineTo(x,y);
            ctx.lineWidth = .7/scale;
            ctx.strokeStyle = "#333";
            ctx.stroke();
            ctx.lineJoin = "round";
            ctx.lineWidth = 3/scale;
            ctx.strokeStyle = "white";
            ctx.strokeText(String(index+1),x,y);
            ctx.fillStyle = "#333";
            ctx.fillText(String(index+1),x,y);
        });
        ctx.restore();
    });
    network.redraw();
    </script>"""
    return html.replace("</body>", key + labels + "</body>")


def plot_saved(method, output, shared):
    """Regenerate figures directly from saved assignments, layout and Q trace."""
    output, shared = Path(output), Path(shared)
    configure_plotting()
    view = read_community_view(output, shared)
    result = json.loads((output / f"{method}_results.json").read_text(encoding="utf-8"))
    require(result["shared_inputs_sha256"] == checksum(shared / "shared_inputs.json"),
            "The selected analysis uses different shared inputs")
    progress = pd.read_csv(output / f"{method}_progress.csv", float_precision="round_trip")
    network = f"{method}_transfer_communities"
    trace = f"{method}_transfer_modularity_progress"
    combined = f"{method}_transfer_communities_and_modularity"
    height = max(3.4, 2.75 + network_legend_height(view[2]))

    fig = plt.figure(figsize=(3.58, height))
    draw_network_panel(fig, (.02, .02, .96, .96), view)
    export(fig, output, network)
    fig = plt.figure(figsize=(3.58, 3.4))
    draw_progress(fig.add_axes([.19, .16, .77, .79]), method, progress, result)
    export(fig, output, trace)
    fig = plt.figure(figsize=(7.16, height))
    draw_network_panel(fig, (.009, .02, .48, .91), view, "(a) Transfer communities")
    draw_progress(fig.add_axes([.59, .16, .386, .77]), method, progress, result)
    fig.text(.59, .93, "(b) Modularity progress", size=10, va="bottom")
    export(fig, output, combined)

    html = network_html(view)
    (output / f"{network}.html").write_text(html, encoding="utf-8")
    svg = (output / f"{trace}.svg").read_text(encoding="utf-8").split("<svg", 1)[1]
    (output / f"{combined}.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Transfer communities and '
        'modularity</title><style>body{margin:0;display:grid;grid-template-columns:minmax(0,3fr) '
        'minmax(17rem,2fr);align-items:start}iframe{border:0;width:100%;height:820px}svg{width:100%;'
        'height:auto}@media(max-width:740px){body{display:block}}</style>'
        f'<iframe title="Interactive network" srcdoc="{escape(html, quote=True)}"></iframe>'
        f'<svg{svg}</html>', encoding="utf-8")
    write_method_notes(method, output, result, (network, trace, combined))


def write_method_notes(method, output, result, stems):
    name = method.capitalize()
    refs = REFERENCES[method]
    qt = result["q_observed"], result["q_shuffled"], result["delta_q"]
    counter = "completed_iterations" if method == "leiden" else "accepted_moves"
    commands = (f"python -B pnas_report/notebooks/{method}_transfer_communities.py")
    caption, summary = (f"{stems[0]}_{part}.md" for part in ("caption", "summary"))
    links = [f"- [{p.name}]({p.name})" for p in sorted(output.glob("*.csv"))]
    figures = ["- " + " · ".join(f"[{ext.upper()}]({stem}.{ext})"
               for ext in ("pdf", "png", "svg", "html") if (output / f"{stem}.{ext}").exists())
               + f" — {label}" for stem, label in zip(stems, (
                   "Transfer communities", "Modularity progress", "Combined view"))]
    (output / "README.md").write_text(
        f"# {name} transfer communities\n\n" + "\n".join(figures + links) + "\n"
        f"- [Results and versions]({method}_results.json)\n- [Captions]({caption})\n"
        f"- [Findings and method]({summary})\n\n"
        f"From the repository root in the machine-learning environment:\n\n"
        f"```powershell\n{commands}\n{commands} --plot-only\n```\n\nSources: {refs}.\n",
        encoding="utf-8")
    (output / caption).write_text(
        f"# {name} figure captions\n\n"
        f"**Transfer communities.** {name} communities in the directed transfer graph. Node area "
        "increases with total directed degree. Numbered representative clubs are keyed to names "
        "and club counts in the legend. The interactive view shows direction and route weights.\n\n"
        f"**Modularity progress.** Each orange marker is one saved observed state. Final directed "
        f"weighted modularity was {qt[0]:.4f}. The solid blue line shows Q = {qt[1]:.4f} "
        "after optimization on one degree-preserving shuffled graph.\n\n"
        f"**Combined view.** (a) {name} communities on the shared layout. (b) The observed "
        "modularity trace and optimized shuffled-graph reference.\n", encoding="utf-8")
    counts = result["counts"]
    run_lines = []
    for run, stats in result["runs"].items():
        counters = ", ".join(f"{key.replace('_', ' ')} {value:,}" for key, value in stats.items()
                             if isinstance(value, int))
        run_lines.append(f"- {run.capitalize()} Q = {stats['final_q']:.9f}, {counters}. "
                         f"Stopped after {stats['stopping_reason']}.")
    (output / summary).write_text(
        f"# {name} transfer communities\n\n"
        f"How much directed, weighted modularity does {name} find in the eligible transfer "
        f"network and in one randomized realization? The joining-rate analysis supplied "
        f"{counts['records']:,} eligible records from {counts['distinct_players']:,} players. "
        "The network keeps all eligible destinations, including clubs outside the Premier League. "
        f"The graph has {counts['nodes']:,} clubs and {counts['edges']:,} directed routes, "
        "with one positive transfer-count weight per route. Club names follow the notebook's "
        "destination-over-origin convention. Conflicting names are listed in the results. "
        "Representatives maximize original in-degree plus out-degree, with ties resolved by club ID. "
        "This measure counts routes. Transfer strengths sum their weights.\n\n"
        f"{name} starts from singletons and optimizes directed weighted modularity at gamma = 1. "
        f"The optimizer seed is {result['seeds']['optimizer']}. "
        + ("Leiden keeps its refinement phase and records complete iterations. "
           "The original paper motivates the refinement choice. Directed strong connectivity is "
           "measured separately as a diagnostic. " if method == "leiden" else
           "The NetworkX-based instrumented run records candidate evaluations and accepted "
           "moves, including supernode relocations. ") +
        f"NetworkX independently scored every saved accepted state with absolute tolerance {TOL:g}. "
        f"See the [results]({method}_results.json) for settings and versions. {refs}.\n\n"
        + "\n".join(run_lines) + "\n\n"
        f"The shared null used {result['shuffle']['successes']:,} successful directed three-edge swaps "
        f"in {result['shuffle']['attempts']:,} attempts and retained "
        f"{result['shuffle']['fraction_original_routes_retained']:.2%} of observed routes. "
        "A separate seed permuted the observed weight multiset over sorted shuffled routes. "
        "The model preserves each club's topological in/out degrees, total transfer volume "
        "and the global weight distribution. Club-specific strengths, the route-volume association, seasons, "
        "season-specific league eligibility, geography, ownership, reciprocity and player trajectories "
        "can change. The swap budget leaves mixing unquantified.\n\n"
        f"Observed minus shuffled Q = {qt[2]:.9f}. The observed run recorded "
        f"{result['runs']['observed'][counter]:,} steps in its method-specific progress unit. "
        "This comparison describes one seed and one randomized realization. It supplies no null "
        "distribution or significance test. Optimization is heuristic and seed-sensitive. Community "
        "names are display labels.\n",
        encoding="utf-8")


def analysis_cli(method, transfers, output, run):
    parser = argparse.ArgumentParser(description=f"Run directed weighted {method.capitalize()} analysis.")
    parser.add_argument("--transfers-path", type=Path, default=transfers)
    parser.add_argument("--output-dir", type=Path, default=output)
    parser.add_argument("--shared-dir", type=Path, default=SHARED)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()
    if args.plot_only:
        plot_saved(method, args.output_dir, args.shared_dir)
    else:
        result = run(args.transfers_path, args.output_dir, seed=args.seed, shared_dir=args.shared_dir)
        print(f"{method.capitalize()} Q observed={result['q_observed']:.9f}, "
              f"shuffled={result['q_shuffled']:.9f}, delta={result['delta_q']:.9f}")
