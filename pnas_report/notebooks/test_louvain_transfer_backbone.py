"""Focused fixtures and independent checks of the exported observed backbone."""

import json
import unittest
from collections import defaultdict

import networkx as nx

import louvain_transfer_backbone as backbone


def fixture(*edges, nodes=()):
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_weighted_edges_from(edges)
    return backbone.score_scope(graph)


class DirectedFilterTest(unittest.TestCase):
    def setUp(self):
        # A=10, B=20, C=30, D=40, E=50, F=60. Nonconsecutive IDs exercise the R vertex map.
        self.scope = fixture((10, 20, 15), (10, 30, 1), (40, 20, 3), (50, 60, 9))
        self.routes = {route.pair: route for route in self.scope.routes}

    def test_directional_scores_strict_cutoff_and_one_weight(self):
        route = self.routes[10, 20]
        self.assertEqual((route.source_out_degree, route.source_out_strength), (2, 16))
        self.assertEqual((route.destination_in_degree, route.destination_in_strength), (2, 18))
        self.assertEqual(route.source_out_score, 0.0625)
        self.assertAlmostEqual(route.destination_in_score, 1 / 6)
        self.assertFalse(route.passes(0.0625))
        self.assertLess(route.source_out_score, 0.10)
        self.assertGreater(route.destination_in_score, 0.10)
        self.assertLess(route.destination_in_score, 0.20)
        self.assertEqual([(r.pair, r.transfer_count) for r in self.scope.retained(0.20)], [((10, 20), 15)])
        self.assertIsNone(self.routes[10, 30].destination_in_score)
        self.assertIsNone(self.routes[40, 20].source_out_score)

    def test_degree_one_dyad_and_empty_active_graph(self):
        dyad = self.routes[50, 60]
        self.assertIsNone(dyad.source_out_score)
        self.assertIsNone(dyad.destination_in_score)
        self.assertIsNone(dyad.min_score)
        self.assertFalse(dyad.structural_exception)
        self.assertNotIn(dyad, self.scope.retained(1.00))
        self.assertIn(dyad, self.scope.retained(None))
        clubs = {i: backbone.Club(str(i), "1", False) for i in self.scope.graph}
        metrics = backbone.retention_metrics(self.scope, clubs, 0.0625)
        for key in ("retained_routes", "retained_transfers", "active_clubs", "largest_weak_component",
                    "weak_components", "strong_components"):
            self.assertEqual(metrics[key], 0)
        self.assertEqual(metrics["isolates"], 6)

    def test_exact_decimal_endpoint_tie_is_excluded(self):
        scope = fixture((1, 2, 4), (1, 3, 1))
        tied = next(route for route in scope.routes if route.pair == (1, 2))
        self.assertEqual(tied.source_out_score, 0.20)
        self.assertNotIn(tied, scope.retained(0.20))
        self.assertIn(tied, scope.retained(0.21))

    def test_paper_exception_separate_from_package_and_empty_scope(self):
        # G -> H, I -> H, H -> J, J -> K, J -> L.
        exception = fixture((7, 8, 1), (9, 8, 1), (8, 10, 1), (10, 11, 1), (10, 12, 1))
        route = next(r for r in exception.routes if r.pair == (8, 10))
        self.assertTrue(route.structural_exception)
        self.assertIsNone(route.source_out_score)
        self.assertIsNone(route.destination_in_score)
        self.assertTrue(all(route in exception.retained(alpha) for alpha in backbone.SLIDER_ALPHAS))
        empty = fixture(nodes=(123, 456))
        self.assertEqual(empty.retained(None), [])
        self.assertEqual([row["club_id"] for row in backbone.fixed_layout(empty)], [123, 456])
        _, diagnostics = backbone.reference_check(
            {"fixture": self.scope, "exception": exception, "empty": empty}, (0.0625, 0.10, 0.20)
        )
        self.assertEqual([(r["r_raw_rows"], r["r_unique_routes"]) for r in diagnostics[:3]],
                         [(0, 0), (1, 1), (2, 1)])
        self.assertTrue(all(r["r_unique_routes"] == 0 and r["paper_routes"] == 1 for r in diagnostics[3:6]))
        self.assertTrue(all(r["r_raw_rows"] == 0 and r["paper_routes"] == 0 for r in diagnostics[6:]))

    def test_reciprocal_weights_and_scope_specific_denominators(self):
        full = fixture((1, 2, 7), (2, 1, 3), (1, 3, 1), (1, 4, 20), (5, 2, 4))
        internal = backbone.score_scope(full.graph.subgraph([1, 2, 3]))
        internal_routes = {r.pair: r for r in internal.routes}
        full_routes = {r.pair: r for r in full.routes}
        self.assertEqual(internal_routes[1, 2].transfer_count, 7)
        self.assertEqual(internal_routes[2, 1].transfer_count, 3)
        self.assertEqual(internal_routes[1, 2].source_out_score, 0.125)
        self.assertEqual(full_routes[1, 2].source_out_score, 0.5625)
        self.assertIsNone(internal_routes[1, 2].destination_in_score)
        self.assertAlmostEqual(full_routes[1, 2].destination_in_score, 4 / 11)
        self.assertIn((1, 2), {r.pair for r in internal.retained(0.20)})
        self.assertNotIn((1, 2), {r.pair for r in full.retained(0.20)})
        backbone.reference_check({"reciprocal": full, "induced": internal})


class SavedBackboneTest(unittest.TestCase):
    def test_observed_scopes_and_exported_connectivity(self):
        _, _, graphs, reciprocal = backbone.load_inputs()
        self.assertEqual(reciprocal, 3835)
        self.assertTrue(all(graph.is_directed() for graph in graphs.values()))
        scores = defaultdict(list)
        for row in backbone.read_csv(backbone.DESTINATION / "backbone_route_scores.csv"):
            scores[row["scope"]].append(row)
        retention = {(row["scope"], float(row["alpha"]) if row["alpha"] else None): row
                     for row in backbone.read_csv(backbone.DESTINATION / "backbone_retention.csv")}
        self.assertEqual(len(retention), 6 * 101)
        for scope, graph in graphs.items():
            with self.subTest(scope=scope):
                original = {(int(r["from_club_id"]), int(r["to_club_id"])): int(r["transfer_count"])
                            for r in scores[scope]}
                self.assertEqual(len(original), len(scores[scope]))
                self.assertEqual(original, nx.get_edge_attributes(graph, "weight"))
                self.assertEqual(int(retention[scope, None]["original_clubs"]), len(graph))
                for alpha in backbone.SNAPSHOT_ALPHAS:
                    # Independent undirected traversal on ordered retained pairs.
                    neighbors = defaultdict(set)
                    routes = transfers = 0
                    for row in scores[scope]:
                        if row["structural_exception"] == "True" or any(
                            row[key] and float(row[key]) < alpha
                            for key in ("source_out_score", "destination_in_score")
                        ):
                            u, v = int(row["from_club_id"]), int(row["to_club_id"])
                            neighbors[u].add(v)
                            neighbors[v].add(u)
                            transfers += original[u, v]
                            routes += 1
                    undiscovered = set(neighbors)
                    sizes = []
                    while undiscovered:
                        component = [undiscovered.pop()]
                        for club in component:
                            unseen = neighbors[club] & undiscovered
                            component.extend(unseen)
                            undiscovered.difference_update(unseen)
                        sizes.append(len(component))
                    observed = retention[scope, alpha]
                    for key, count in (("retained_routes", routes), ("retained_transfers", transfers),
                                       ("active_clubs", len(neighbors)), ("weak_components", len(sizes)),
                                       ("largest_weak_component", max(sizes, default=0))):
                        self.assertEqual(int(observed[key]), count, (scope, alpha, key))

    def test_saved_parity_layout_and_checksums(self):
        results = json.loads((backbone.DESTINATION / "backbone_results.json").read_text(encoding="utf-8"))
        self.assertEqual(results["input_sha256"], backbone.input_checksums())
        self.assertTrue(results["inputs_unchanged"])
        self.assertEqual(results["versions"]["disparityfilter"], "2.2.3")
        self.assertEqual(results["layout"]["seed"], 2029)
        self.assertEqual(results["layout"]["reference_alpha"], 0.50)
        self.assertEqual(set(results["structural_exceptions"].values()), {0})
        checks = results["parity"]
        self.assertEqual({(r["scope"], r["alpha"]) for r in checks},
                         {(name, alpha) for name in ("whole", *backbone.CHECKPOINTS) for alpha in backbone.PARITY_ALPHAS})
        self.assertTrue(all(r["r_unique_routes"] == r["paper_routes"] for r in checks))
        mapping = defaultdict(list)
        for row in backbone.read_csv(backbone.DESTINATION / "backbone_layout.csv"):
            mapping[row["scope"]].append((int(row["vertex_index"]), int(row["club_id"])))
        for scope, rows in mapping.items():
            self.assertEqual(rows, list(enumerate(sorted(club for _, club in rows), start=1)), scope)


if __name__ == "__main__":
    unittest.main()
