"""Directed disparity backbones of the saved observed Louvain transfer network."""

import csv
import hashlib
import json
import math
import platform
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx


REPORT = Path(__file__).resolve().parents[1]
OUTPUT = REPORT / "output"
DESTINATION = OUTPUT / "louvain_transfer_backbone_findings"
SHARED = OUTPUT / "transfer_community_comparison"
LOUVAIN = OUTPUT / "louvain_transfer_communities_findings"
REFERENCE = Path(__file__).with_name("disparityfilter_reference.R")
REFERENCE_ALPHA = 0.50
LAYOUT_SEED = 2029
PARITY_ALPHAS = (0.05, 0.10, 0.20, 0.30, 0.50)
SNAPSHOT_ALPHAS = (0.10, 0.20, 0.30)
SLIDER_ALPHAS = tuple(i / 100 for i in range(1, 101))
OBSERVED_Q = json.loads((LOUVAIN / "louvain_results.json").read_text())["q_observed"]
COMMUNITY_SUMMARY = {row["community_id"]: row for row in csv.DictReader(
    (LOUVAIN / "community_summary.csv").open(encoding="utf-8"))}



@dataclass(frozen=True)
class Club:
    name: str
    community: str
    representative: bool


@dataclass(frozen=True)
class Route:
    from_club_id: int
    to_club_id: int
    transfer_count: int
    source_out_degree: int
    source_out_strength: int
    source_out_score: float | None
    destination_in_degree: int
    destination_in_strength: int
    destination_in_score: float | None
    min_score: float | None
    structural_exception: bool

    @property
    def pair(self):
        return self.from_club_id, self.to_club_id

    def passes(self, alpha):
        return self.min_score is not None and self.min_score < alpha


@dataclass
class Scope:
    graph: nx.DiGraph
    routes: list[Route]

    def retained(self, alpha):
        if alpha is None:
            return self.routes
        return [route for route in self.routes if route.structural_exception or route.passes(alpha)]


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_checksums():
    return {
        path.relative_to(REPORT).as_posix(): sha256(path)
        for directory in (SHARED, LOUVAIN)
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_inputs():
    shared_path = SHARED / "shared_inputs.json"
    shared = json.loads(shared_path.read_text(encoding="utf-8"))
    louvain = json.loads((LOUVAIN / "louvain_results.json").read_text(encoding="utf-8"))
    require(sha256(shared_path) == louvain["shared_inputs_sha256"], "Shared metadata checksum differs")
    require(shared["files_sha256"] == louvain["shared_files_sha256"], "Shared file manifests differ")
    for name, digest in shared["files_sha256"].items():
        require(sha256(SHARED / name) == digest, f"Checksum differs for {name}")
    for key in ("input_sha256", "counts", "directed", "weight", "resolution", "seeds"):
        require(shared[key] == louvain[key], f"Shared and Louvain metadata differ for {key}")
    require(shared["directed"] and shared["weight"] == "transfer_count", "Unexpected graph metadata")
    require(louvain["q_observed"] == OBSERVED_Q, "Unexpected observed Louvain Q")

    clubs = {}
    groups = {}
    representatives = Counter()
    for row in read_csv(LOUVAIN / "communities.csv"):
        club_id, group = int(row["club_id"]), row["community_id"]
        require(club_id not in clubs, f"Duplicate membership for {club_id}")
        club = Club(row["club_name"], group, row["representative"] == "True")
        clubs[club_id] = club
        display = {"name": row["community_name"], "color": row["color"]}
        require(groups.setdefault(group, display) == display, f"Inconsistent display data for {group}")
        if club.representative:
            representatives[group] += 1
    require(set(groups) == COMMUNITY_SUMMARY.keys(), "Display communities differ from saved summary")
    require(representatives == {group: 1 for group in groups}, "Expected one representative per community")
    groups = {key: groups[key] for key in COMMUNITY_SUMMARY}

    saved_groups = defaultdict(set)
    saved_clubs = set()
    for row in read_csv(LOUVAIN / "final_partitions.csv"):
        if row["run"] == "observed":
            club_id = int(row["club_id"])
            require(club_id not in saved_clubs, "Duplicate observed partition assignment")
            saved_clubs.add(club_id)
            saved_groups[row["community_id"]].add(club_id)
    display_groups = {group: {i for i in clubs if clubs[i].community == group} for group in groups}
    require(
        {frozenset(nodes) for nodes in display_groups.values()}
        == {frozenset(nodes) for nodes in saved_groups.values()},
        "Observed membership differs from the saved partition",
    )

    edges = {}
    for row in read_csv(SHARED / "observed_routes.csv"):
        u, v, weight = (int(row[k]) for k in ("from_club_id", "to_club_id", "transfer_count"))
        require(u != v and weight > 0 and (u, v) not in edges, f"Invalid observed route {u} -> {v}")
        edges[u, v] = weight
    endpoints = {club for pair in edges for club in pair}
    require(endpoints == set(clubs) == set(shared["node_order"]), "Observed club coverage differs")
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(clubs))
    graph.add_weighted_edges_from((u, v, weight) for (u, v), weight in sorted(edges.items()))
    require(nx.get_edge_attributes(graph, "weight") == edges, "Directed routes changed during graph construction")
    require((len(clubs), len(edges), sum(edges.values())) == (shared["counts"]["nodes"], shared["counts"]["edges"], shared["counts"]["records"]), "Full checkpoint differs")

    graphs = {"whole": graph}
    for group, checkpoint in COMMUNITY_SUMMARY.items():
        subgraph = graph.subgraph(display_groups[group]).copy()
        actual = (groups[group]["name"], len(subgraph), subgraph.number_of_edges(), subgraph.size(weight="weight"))
        require(actual[0] == checkpoint["community_name"] and actual[1] == int(checkpoint["community_size"]),
                f"Community {group} checkpoint differs: {actual}")
        graphs[group] = subgraph
    internal_routes = sum(g.number_of_edges() for key, g in graphs.items() if key != "whole")
    internal_weight = sum(g.size(weight="weight") for key, g in graphs.items() if key != "whole")
    require(internal_routes == sum(clubs[u].community == clubs[v].community for u, v in edges),
            "Internal route totals disagree")
    require(internal_weight == sum(w for (u, v), w in edges.items() if clubs[u].community == clubs[v].community),
            "Internal transfer totals disagree")
    require(abs(nx.community.modularity(graph, list(display_groups.values()), weight="weight") - OBSERVED_Q) <= 1e-10,
            "Observed partition Q differs from new saved optimizer result")
    return clubs, groups, graphs, sum((v, u) in edges for u, v in edges) // 2


def endpoint_score(weight, strength, degree):
    if degree <= 1:
        return None
    # Evaluate the rational power before rounding so an exact cutoff tie stays equal.
    return (strength - weight) ** (degree - 1) / strength ** (degree - 1)


def score_scope(graph):
    require(graph.is_directed(), "Disparity scoring requires a directed graph")
    out_degree, in_degree = dict(graph.out_degree()), dict(graph.in_degree())
    out_strength = dict(graph.out_degree(weight="weight"))
    in_strength = dict(graph.in_degree(weight="weight"))
    routes = []
    for u, v, weight in sorted(graph.edges(data="weight")):
        ko, ki = out_degree[u], in_degree[v]
        so, si = out_strength[u], in_strength[v]
        source = endpoint_score(weight, so, ko)
        destination = endpoint_score(weight, si, ki)
        minimum = min((score for score in (source, destination) if score is not None), default=None)
        exception = ko == ki == 1 and in_degree[u] > 1 and out_degree[v] > 1
        routes.append(Route(u, v, weight, ko, so, source, ki, si, destination, minimum, exception))
    return Scope(graph, routes)


def reference_check(scopes, alphas=PARITY_ALPHAS):
    with TemporaryDirectory(prefix="louvain_backbone_") as directory:
        folder = Path(directory)
        write_csv(folder / "vertices.csv", (
            {"scope": scope, "vertex_index": index, "club_id": club}
            for scope, data in scopes.items()
            for index, club in enumerate(sorted(data.graph), start=1)
        ), ["scope", "vertex_index", "club_id"])
        write_csv(folder / "routes.csv", (
            {"scope": scope, "from_club_id": route.from_club_id,
             "to_club_id": route.to_club_id, "transfer_count": route.transfer_count}
            for scope, data in scopes.items() for route in data.routes
        ), ["scope", "from_club_id", "to_club_id", "transfer_count"])
        subprocess.run(["conda", "run", "-n", "network_analysis", "--no-capture-output", "Rscript", "--vanilla", str(REFERENCE), str(folder), ",".join(map(str, alphas))],
                       check=True)
        versions = dict(zip(("R", "R_igraph", "disparityfilter"),
                            (folder / "versions.txt").read_text(encoding="utf-8").splitlines(), strict=True))
        package = defaultdict(dict)
        for row in read_csv(folder / "retained.csv"):
            key = row["scope"], float(row["alpha"])
            pair = int(row["from_club_id"]), int(row["to_club_id"])
            require(pair not in package[key], "R wrapper returned duplicate ordered pairs")
            package[key][pair] = int(row["transfer_count"])
        raw_counts = {(row["scope"], float(row["alpha"])): int(row["raw_rows"])
                      for row in read_csv(folder / "diagnostics.csv")}

    diagnostics = []
    for name, scope in scopes.items():
        exceptions = {r.pair: r.transfer_count for r in scope.routes if r.structural_exception}
        for alpha in alphas:
            statistical = {r.pair: r.transfer_count for r in scope.routes if r.passes(alpha)}
            reference = package[name, alpha]
            retained = {r.pair: r.transfer_count for r in scope.retained(alpha)}
            statistical_match = reference == statistical
            paper_match = retained == (reference | exceptions)
            diagnostics.append({
                "scope": name, "alpha": alpha, "r_raw_rows": raw_counts[name, alpha],
                "r_unique_routes": len(reference), "retained_transfer_count": sum(retained.values()),
                "structural_exceptions": len(exceptions), "paper_routes": len(retained),
                "statistical_match": statistical_match, "paper_rule_match": paper_match,
                "r_only": sorted(reference.items() - statistical.items()),
                "python_only": sorted(statistical.items() - reference.items()),
            })
    return versions, diagnostics


def retention_metrics(scope, clubs, alpha):
    routes = scope.retained(alpha)
    active = nx.DiGraph((r.from_club_id, r.to_club_id) for r in routes)
    weak_sizes = [len(component) for component in nx.weakly_connected_components(active)]
    between = [r for r in routes if clubs[r.from_club_id].community != clubs[r.to_club_id].community]
    transfers = sum(r.transfer_count for r in routes)
    between_transfers = sum(r.transfer_count for r in between)
    return {
        "retained_routes": len(routes),
        "retained_transfers": transfers,
        "active_clubs": len(active),
        "isolates": len(scope.graph) - len(active),
        "largest_weak_component": max(weak_sizes, default=0),
        "weak_components": len(weak_sizes),
        "strong_components": nx.number_strongly_connected_components(active),
        "within_routes": len(routes) - len(between),
        "within_transfers": transfers - between_transfers,
        "between_routes": len(between),
        "between_transfers": between_transfers,
    }


def retention_table(scopes, clubs):
    for name, scope in scopes.items():
        baseline = retention_metrics(scope, clubs, None)
        denominators = {
            "original_routes": baseline["retained_routes"],
            "original_transfers": baseline["retained_transfers"],
            "original_clubs": len(scope.graph),
            **{f"original_{key}": baseline[key] for key in (
                "within_routes", "within_transfers", "between_routes", "between_transfers"
            )},
        }
        previous = set()
        original = nx.get_edge_attributes(scope.graph, "weight")
        for alpha in (*SLIDER_ALPHAS, None):
            weights = {route.pair: route.transfer_count for route in scope.retained(alpha)}
            require(previous <= weights.keys(), f"Retention is not nested at {name}/{alpha}")
            require(weights.items() <= original.items(), f"Original route weights differ at {name}/{alpha}")
            previous = weights.keys()
            metrics = retention_metrics(scope, clubs, alpha)
            coverage = {
                f"{metric}_fraction": metrics[metric] / denominators[denominator] if denominators[denominator] else 0
                for metric, denominator in (
                    ("retained_routes", "original_routes"), ("retained_transfers", "original_transfers"),
                    ("active_clubs", "original_clubs"), ("largest_weak_component", "original_clubs"),
                )
            }
            yield {"scope": name, "view": "unfiltered" if alpha is None else "filtered", "alpha": alpha,
                   **denominators, **metrics, **coverage}


def fixed_layout(scope):
    graph = scope.graph
    reference = nx.DiGraph()
    reference.add_weighted_edges_from(
        (route.from_club_id, route.to_club_id, route.transfer_count) for route in scope.retained(REFERENCE_ALPHA)
    )
    # A symmetric layout uses the sum of the two weights on reciprocal routes.
    force = nx.Graph()
    for u, v, weight in reference.edges(data="weight"):
        force.add_edge(u, v, weight=weight + force.get_edge_data(u, v, {}).get("weight", 0))
    positions = nx.spring_layout(force, seed=LAYOUT_SEED, weight="weight", method="force", iterations=120)
    # Keep clubs outside the reference graph in a grid below the active layout.
    margin = sorted(set(graph) - set(force))
    columns = min(32, max(1, math.ceil(math.sqrt(len(margin) * 5))))
    for i, club in enumerate(margin):
        positions[club] = (-0.96 + 1.92 * (i % columns) / max(1, columns - 1), -1.14 - 0.064 * (i // columns))
    for index, club in enumerate(sorted(graph), start=1):
        x, y = positions[club]
        strength = graph.degree(club, weight="weight")
        yield {"club_id": club, "vertex_index": index, "x": float(x), "y": float(y),
               "node_size": 2 + 0.72 * math.sqrt(strength), "reference_isolate": club not in force}


def save_explorable(destination, scopes, clubs, groups, layouts, retention):
    from pyvis import __file__ as pyvis_file

    browser_data = {}
    for key, scope in scopes.items():
        graph = scope.graph
        browser_data[key] = {
            "name": groups[key]["name"] if key in groups else "Whole network",
            "nodes": [
                {**row, **asdict(clubs[row["club_id"]]),
                 "in_routes": graph.in_degree(row["club_id"]), "out_routes": graph.out_degree(row["club_id"]),
                 "in_transfers": graph.in_degree(row["club_id"], weight="weight"),
                 "out_transfers": graph.out_degree(row["club_id"], weight="weight")}
                for row in layouts[key]
            ],
            "routes": [
                {"from": r.from_club_id, "to": r.to_club_id, "weight": r.transfer_count,
                 "out_score": r.source_out_score, "in_score": r.destination_in_score,
                 "exception": r.structural_exception, "reciprocal": graph.has_edge(r.to_club_id, r.from_club_id)}
                for r in scope.routes
            ],
            "retention": [row for row in retention if row["scope"] == key],
        }
    data = json.dumps({"groups": groups, "scopes": browser_data}, ensure_ascii=False, separators=(",", ":"))
    template = Path(__file__).with_name("louvain_transfer_backbone_template.html").read_text(encoding="utf-8")
    vis_root = Path(pyvis_file).parent / "templates" / "lib" / "vis-9.1.2"
    js = (vis_root / "vis-network.min.js").read_text(encoding="utf-8")
    # The source map is a developer asset and is unnecessary for the offline document.
    js = js.split("//# sourceMappingURL=")[0]
    css = (vis_root / "vis-network.css").read_text(encoding="utf-8")
    html = (template.replace("/* VIS_CSS */", css).replace("/* VIS_JS */", js)
            .replace("/* NETWORK_DATA */", data.replace("<", r"\u003c")))
    (destination / "louvain_transfer_backbone.html").write_text(html, encoding="utf-8")


def save_publication(destination, scope, clubs, groups, layout):
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import font_manager
    from matplotlib.collections import LineCollection, PolyCollection
    from matplotlib.lines import Line2D

    font_manager.findfont("Arial", fallback_to_default=False)
    positions = {row["club_id"]: (row["x"], row["y"]) for row in layout}
    sizes = {row["club_id"]: row["node_size"] for row in layout}
    frame_clubs = sorted({club for route in scope.retained(max(SNAPSHOT_ALPHAS)) for club in route.pair})
    frame_x, frame_y = zip(*(positions[club] for club in frame_clubs))
    from itertools import cycle
    markers = dict(zip(groups, cycle(("o", "s", "^", "D", "P"))))

    with mpl.rc_context({"font.family": "Arial", "font.size": 9.5, "text.color": "#333333",
                         "pdf.fonttype": 42, "svg.fonttype": "none", "figure.facecolor": "white"}):
        figure, axes = plt.subplots(1, 3, figsize=(7.16, 2.82))
        figure.subplots_adjust(left=0.025, right=0.975, top=0.88, bottom=0.16, wspace=0.09)
        for panel, (ax, alpha) in enumerate(zip(axes, SNAPSHOT_ALPHAS, strict=True)):
            routes = scope.retained(alpha)
            active = sorted({club for route in routes for club in route.pair})
            segments, arrows, widths = [], [], []
            for route in routes:
                u, v = route.pair
                start, end = np.array(positions[u]), np.array(positions[v])
                direction = end - start
                distance = np.linalg.norm(direction)
                if distance == 0:
                    continue
                unit = direction / distance
                normal = np.array([-unit[1], unit[0]])
                shift = normal * 0.008 if scope.graph.has_edge(v, u) else 0
                tip = end - unit * min(0.037 + 0.002 * sizes[v], distance * 0.28) + shift
                base = tip - unit * min(0.025, distance * 0.22)
                segments.append([start + shift, tip])
                arrows.append([tip, base + 0.008 * normal, base - 0.008 * normal])
                widths.append(0.14 + 0.11 * math.sqrt(route.transfer_count))
            ax.add_collection(LineCollection(segments, linewidths=widths, colors="#555555", alpha=0.28))
            ax.add_collection(PolyCollection(arrows, facecolors="#555555", edgecolors="none", alpha=0.38))
            for group, display in groups.items():
                nodes = [i for i in active if clubs[i].community == group]
                if nodes:
                    x, y = zip(*(positions[i] for i in nodes))
                    ax.scatter(x, y, s=[sizes[i] * 0.9 for i in nodes], marker=markers[group],
                               color=display["color"], linewidths=0.2, edgecolors="#333333", zorder=3)
            ax.set(xlim=(min(frame_x) - 0.06, max(frame_x) + 0.06),
                   ylim=(min(frame_y) - 0.06, max(frame_y) + 0.06), aspect="equal")
            ax.set_axis_off()
            ax.set_title(f"({chr(97 + panel)})  α = {alpha:.2f}", loc="left", fontsize=10, pad=5)
        legend_marks = [
            Line2D([], [], marker=markers[group], linestyle="none", markersize=5.09,
                   markerfacecolor=display["color"], markeredgecolor="#333333", markeredgewidth=0.25,
                   label=display["name"]) for group, display in groups.items()
        ]
        legend = figure.legend(handles=legend_marks, loc="lower center", bbox_to_anchor=(0.5, 0.025),
                               ncol=min(5, len(groups)), fontsize=8, facecolor="white", edgecolor="#BBBBBB", framealpha=1)
        legend.get_frame().set_linewidth(0.6)
        for suffix in ("pdf", "png", "svg"):
            figure.savefig(destination / f"louvain_backbone_alpha_comparison.{suffix}", dpi=600)
        plt.close(figure)


def save_docs(destination, scopes, clubs, groups, retention):
    lookup = {(row["scope"], row["alpha"]): row for row in retention}
    whole = lookup["whole", 0.20]
    lines = [
        "# Louvain transfer backbone", "",
        f"The observed directed network contains {whole['original_clubs']:,} clubs, "
        f"{whole['original_routes']:,} ordered routes and {whole['original_transfers']:,} recorded transfers. "
        f"The saved {len(groups)}-community Louvain partition has modularity Q = {OBSERVED_Q:.6f}.",
        "",
        "## Whole network", "",
        "| α | Routes | Transfers | Active clubs | Largest weak component | Between-community routes | Between-community transfers |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for alpha in SNAPSHOT_ALPHAS:
        row = lookup["whole", alpha]
        lines.append(f"| {alpha:.2f} | {row['retained_routes']:,}/{row['original_routes']:,} "
                     f"| {row['retained_transfers']:,}/{row['original_transfers']:,} "
                     f"| {row['active_clubs']:,}/{row['original_clubs']:,} "
                     f"| {row['largest_weak_component']:,}/{row['original_clubs']:,} "
                     f"| {row['between_routes']:,}/{row['original_between_routes']:,} "
                     f"| {row['between_transfers']:,}/{row['original_between_transfers']:,} |")
    cross = sorted(
        (r for r in scopes["whole"].retained(0.20) if clubs[r.pair[0]].community != clubs[r.pair[1]].community),
        key=lambda r: (-r.transfer_count, r.pair),
    )
    examples = ", ".join(
        f"{clubs[u].name} ({groups[clubs[u].community]['name']}) → "
        f"{clubs[v].name} ({groups[clubs[v].community]['name']}, {route.transfer_count} transfers)"
        for route in cross[:3] for u, v in [route.pair]
    )
    lines += ["", f"At α = 0.20, {whole['within_routes'] / whole['original_within_routes']:.1%} of within-community "
              f"routes survive, compared with {whole['between_routes'] / whole['original_between_routes']:.1%} "
              f"of between-community routes. The three highest-weight surviving cross-community routes "
              f"(with ties ordered by club IDs) are {examples}.",
              "", "## Within the saved communities", "",
              "Each community uses its internal routes to compute endpoint degrees and strengths.", "",
              "| Community | Active clubs at 0.10 | Largest weak component at 0.10 | Active clubs at 0.20 | Largest weak component at 0.20 | Weak components at 0.20 |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for group, display in groups.items():
        strict, start = lookup[group, 0.10], lookup[group, 0.20]
        n = start["original_clubs"]
        lines.append(f"| {display['name']} | {strict['active_clubs']}/{n} | {strict['largest_weak_component']}/{n} "
                     f"| {start['active_clubs']}/{n} | {start['largest_weak_component']}/{n} | {start['weak_components']} |")
    strict_groups = [lookup[group, 0.10] for group in groups]
    smallest_active = min(strict_groups, key=lambda row: row["active_clubs_fraction"])
    smallest_component = min(strict_groups, key=lambda row: row["largest_weak_component_fraction"])
    community_rows = [r for r in retention if r["scope"] in groups and r["alpha"] is not None]
    first_isolate = max((r for r in community_rows if r["isolates"]), key=lambda r: r["alpha"])
    first_split = max((r for r in community_rows if r["weak_components"] > 1), key=lambda r: r["alpha"])
    lines += [
        "",
        f"As the slider moves down from 1.00, {groups[first_isolate['scope']]['name']} loses club coverage first "
        f"at α = {first_isolate['alpha']:.2f} ({first_isolate['active_clubs']}/{first_isolate['original_clubs']} active). "
        f"{groups[first_split['scope']]['name']} is the first to have multiple active weak components, "
        f"at α = {first_split['alpha']:.2f} ({first_split['weak_components']} components, "
        f"largest {first_split['largest_weak_component']}/{first_split['original_clubs']} clubs).",
        "",
        f"At α = 0.10, {groups[smallest_active['scope']]['name']} has the lowest incident-club coverage "
        f"({smallest_active['active_clubs']}/{smallest_active['original_clubs']}) and "
        f"{groups[smallest_component['scope']]['name']} has the smallest largest weak component relative "
        f"to its membership ({smallest_component['largest_weak_component']}/{smallest_component['original_clubs']}). "
        "The per-community retention table records the full slider grid without historical community assumptions.",
        "",
        "## Report cutoff", "",
        f"Use α = 0.20 as the course-derived starting point and a readable report snapshot. The whole-network "
        f"view shows {whole['retained_routes_fraction']:.1%} of routes and {whole['retained_transfers_fraction']:.1%} "
        f"of transfer volume, with {whole['active_clubs']:,} active clubs in {whole['weak_components']} weak components; "
        f"the largest covers {whole['largest_weak_component_fraction']:.1%} of observed clubs. "
        f"At 0.10, the sparser drawing retains {lookup['whole', 0.10]['retained_transfers_fraction']:.1%} "
        f"of volume and has {lookup['whole', 0.10]['weak_components']} active weak components. "
        f"At 0.30, coverage rises to {lookup['whole', 0.30]['retained_transfers_fraction']:.1%} of volume "
        "and the additional routes add visual overlap.",
        "",
        "The directed disparity rule tests each source's outgoing and destination's incoming shares. "
        "A score strictly below α at either eligible endpoint retains the route. The directed connectivity "
        "exception is tested separately. Eligible exception routes by scope are "
        + ", ".join(f"{groups.get(key, {'name': 'Whole network'})['name']} ({sum(r.structural_exception for r in scope.routes)})"
                    for key, scope in scopes.items()) + ".",
        "",
        "Coverage uses original scope totals. Active clubs touch at least one retained route. Weak and "
        "strong component counts use only active clubs, with isolates counted separately. Weak connectivity "
        "ignores arrow direction. All colours and group labels come from the saved pre-filter partition.",
        "",
        "Alpha is an exploratory local cutoff. A network-wide false-positive rate would require a separate "
        "inferential procedure. The transfer weights count records in the observed sample, and retention "
        "describes locally concentrated volume under the null. Explaining why a route exists requires "
        "evidence beyond these transfer counts.",
        "",
        "The original LaTeX subsection reports the broad-period analysis. Its bibliography entry for "
        "Serrano, Boguñá and Vespignani is reusable in the restricted paper. "
        "[Historical LaTeX subsection](../../../../paper/transfer_backbone.tex) · "
        "[BibTeX file](../../../../paper/transfer_backbone_references.bib)",
        "",
    ]
    (destination / "backbone_summary.md").write_text("\n".join(lines), encoding="utf-8")

    caption_counts = " ".join(
        f"At α = {alpha:.2f}, the backbone contains {lookup['whole', alpha]['retained_routes']:,} routes, "
        f"{lookup['whole', alpha]['retained_transfers']:,} transfers and {lookup['whole', alpha]['active_clubs']:,} active clubs."
        for alpha in SNAPSHOT_ALPHAS
    )
    readme = [
        "# Louvain transfer backbone outputs", "",
        "Open the [offline explorable](louvain_transfer_backbone.html) in a browser. Use the community selector "
        "to switch directional denominators. The slider starts at 0.20, and the unfiltered control restores every route.",
        "",
        "- [Publication PDF](louvain_backbone_alpha_comparison.pdf) · [600 dpi PNG](louvain_backbone_alpha_comparison.png) "
        "· [Editable-text SVG](louvain_backbone_alpha_comparison.svg)",
        "- [Scoped route scores](backbone_route_scores.csv) · [Retention and fragmentation](backbone_retention.csv) "
        "· [Fixed layouts and R vertex indices](backbone_layout.csv)",
        "- [Checksums, versions and R parity](backbone_results.json) · [Findings and interpretation](backbone_summary.md)",
        "",
        "## Figure caption", "",
        f"Directed transfer backbones of the same observed network at three local disparity cutoffs. {caption_counts} "
        f"Panels use fixed positions and node sizes, with colours and symbols identifying the {len(groups)} saved Louvain "
        "communities. Arrows run from origin to destination and their shafts widen with transfer count.",
        "",
        "## Reproduce from the workspace root", "", "```powershell",
        "conda activate network_analysis",
        "conda run -n machine-learning python pnas_report/reruns/h1_2012_13-2024_25/notebooks/louvain_transfer_backbone.py",
        "python -m unittest discover -s pnas_report/notebooks -p test_louvain_transfer_backbone.py",
        "```", "",
        f"The analysis runs R package parity on all {len(scopes)} views at five cutoffs before exporting. The retention table "
        "includes each slider value and the unfiltered baseline. Missing endpoint scores and unfiltered alpha are "
        "blank in the CSV. The layout defines the contiguous one-based R vertex index within each scope.", "",
    ]
    (destination / "README.md").write_text("\n".join(readme), encoding="utf-8")


def main():
    destination = DESTINATION
    before = input_checksums()
    clubs, groups, graphs, reciprocal_pairs = load_inputs()
    print("Verified saved checksums, membership, and all route totals.", flush=True)
    scopes = {key: score_scope(graph) for key, graph in graphs.items()}
    versions, parity = reference_check(scopes)
    print(f"Completed {len(parity)} directed R parity comparisons; "
          f"{sum(not row['paper_rule_match'] for row in parity)} paper-rule mismatches. "
          "Failures remain explicit; scoring and strict cutoffs are unchanged.", flush=True)
    retention = list(retention_table(scopes, clubs))
    layouts = {key: list(fixed_layout(scope)) for key, scope in scopes.items()}
    destination.mkdir(parents=True, exist_ok=True)
    write_csv(destination / "backbone_route_scores.csv", (
        {"scope": key, **asdict(route)} for key, scope in scopes.items() for route in scope.routes
    ), ["scope", *Route.__dataclass_fields__])
    write_csv(destination / "backbone_retention.csv", retention, list(retention[0]))
    write_csv(destination / "backbone_layout.csv", (
        {"scope": key, **row} for key, rows in layouts.items() for row in rows
    ), ["scope", *layouts["whole"][0]])
    save_explorable(destination, scopes, clubs, groups, layouts, retention)
    save_publication(destination, scopes["whole"], clubs, groups, layouts["whole"])
    save_docs(destination, scopes, clubs, groups, retention)
    failed = [row for row in parity if not row["statistical_match"] or not row["paper_rule_match"]]
    for document in ("README.md", "backbone_summary.md"):
        with (destination / document).open("a", encoding="utf-8") as handle:
            handle.write(f"\n\nThe R reference agrees in {len(parity) - len(failed)} of {len(parity)} "
                         "scope/cutoff comparisons. Python uses the original integer numerator and strict cutoff. "
                         "[Saved parity results](backbone_results.json) · "
                         "[Boundary diagnosis](../../provenance/backbone_boundary_diagnosis.json)\n")
    require(input_checksums() == before, "A saved Louvain or shared input changed during analysis")
    results = {
        "input_sha256": before, "inputs_unchanged": True,
        "observed_louvain_q": OBSERVED_Q, "observed_reciprocal_pairs": reciprocal_pairs,
        "directed": True, "weight": "transfer_count", "communities": groups,
        "versions": {"Python": platform.python_version(), **versions, **{
            package: metadata.version(package) for package in ("networkx", "numpy", "scipy", "matplotlib", "pyvis")
        }},
        "rules": {
            "statistical": "Keep if either applicable score (1 - weight / strength) ** (degree - 1) is strictly below alpha.",
            "precision": "Compute the integer numerator and denominator of the score before rounding once to a double.",
            "degree_one": "A directional endpoint of degree one has a missing score.",
            "structural_exception": "Keep if source out-degree = destination in-degree = 1 and source in-degree > 1 and destination out-degree > 1.",
            "unfiltered": "All observed routes in the scope.",
            "scope": "Whole graph or directed induced subgraph using the saved display community IDs.",
        },
        "layout": {
            "reference_alpha": REFERENCE_ALPHA, "seed": LAYOUT_SEED,
            "algorithm": "NetworkX weighted spring_layout, force method, 120 iterations. Reciprocal weights are summed for layout only.",
            "networkx_version": nx.__version__, "node_size": "2 + 0.72 * sqrt(original in-strength + out-strength)",
            "reference_isolates": {key: sum(row["reference_isolate"] for row in rows) for key, rows in layouts.items()},
            "vertex_index": "Contiguous one-based index by club ID in backbone_layout.csv.",
        },
        "structural_exceptions": {key: sum(r.structural_exception for r in scope.routes) for key, scope in scopes.items()},
        "parity": parity,
        "r_parity_passed": all(row["statistical_match"] and row["paper_rule_match"] for row in parity),
    }
    (destination / "backbone_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                                                       encoding="utf-8")
    print(f"Wrote backbone deliverables to {destination}", flush=True)


if __name__ == "__main__":
    main()
