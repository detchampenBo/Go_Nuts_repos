"""Verify graph semantics, null-model constraints, and the checked-in puzzle data."""
import hashlib
import json
import random
import unittest

from prepare_data import HERE, SOURCE, average_clustering, load_graph, neighborhood, shuffle_graph


class GraphTests(unittest.TestCase):
    def test_two_neighbors_do_not_necessarily_close_a_triangle(self):
        square = {"a": {"b", "d"}, "b": {"a", "c"}, "c": {"b", "d"}, "d": {"a", "c"}}
        self.assertEqual(neighborhood(square, "a")["clustering"], 0)
        square["b"].add("d")
        square["d"].add("b")
        self.assertEqual(neighborhood(square, "a")["clustering"], 1)

    def test_isolates_and_leaves_contribute_zero_to_the_average(self):
        graph = {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}, "d": set(), "e": {"f"}, "f": {"e"}}
        self.assertEqual(average_clustering(graph), 0.5)

    def test_shuffle_preserves_each_degree_with_no_loops_or_duplicates(self):
        _, original, _ = load_graph()
        shuffled = shuffle_graph(original, random.Random(42))
        self.assertNotEqual(shuffled, original)
        for node in original:
            self.assertEqual(len(shuffled[node]), len(original[node]))
            self.assertNotIn(node, shuffled[node])
            for neighbor in shuffled[node]:
                self.assertIn(node, shuffled[neighbor])
        self.assertEqual(shuffled, shuffle_graph(original, random.Random(42)))

    def test_frozen_data_matches_source_and_all_puzzles_have_distinct_values(self):
        nodes, graph, directed = load_graph()
        data = json.loads((HERE / "puzzle-data.json").read_text(encoding="utf-8"))
        self.assertEqual(len(nodes), 303)
        self.assertEqual(directed, 1784)
        self.assertEqual(sum(map(len, graph.values())) // 2, 1434)
        self.assertEqual(sum(not ns for ns in graph.values()), 17)
        self.assertAlmostEqual(data["clustering"], average_clustering(graph))
        digest = hashlib.sha256((SOURCE / "week1_nodes.tsv").read_bytes() + (SOURCE / "week1_edges.tsv").read_bytes()).hexdigest()
        self.assertEqual(data["sourceSha256"], digest)
        for key, hero in data["heroes"].items():
            measured = neighborhood(graph, key)
            for metric in ("degree", "links", "clustering"):
                self.assertEqual(hero[metric], measured[metric])
            self.assertEqual(hero["degree"], hero["shuffled"]["degree"])
        for puzzle in data["puzzles"]:
            for metric in ("degree", "clustering"):
                values = [data["heroes"][n][metric] for n in puzzle[metric]]
                self.assertEqual(len(values), 5)
                self.assertEqual(len(set(values)), 5)
        samples = data["shuffleSamples"]
        self.assertEqual(len(samples), 100)
        self.assertTrue(all(0 <= v <= 1 for v in samples))
        self.assertAlmostEqual(data["shuffleMean"], sum(samples) / 100)
        self.assertAlmostEqual(data["empiricalP"], (1 + sum(v >= data["clustering"] for v in samples)) / 101)
        self.assertGreater(data["empiricalP"], 0)


if __name__ == "__main__":
    unittest.main()
