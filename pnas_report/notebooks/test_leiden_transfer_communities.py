"""Exercise directed Leiden scoring, convergence, conversion and the common null."""

from collections import Counter
import unittest

import leidenalg as la
import networkx as nx

from leiden_transfer_communities import groups_from_membership, optimize_leiden, to_igraph
from transfer_community_inputs import (
    WEIGHT, modularity, partition_key, routes, shuffle_routes, try_three_edge_swap,
)


def weighted_fixture():
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([
        (10, 20, 7), (20, 10, 3), (20, 30, 2), (30, 40, 11),
        (40, 30, 5), (40, 10, 1), (10, 30, 4), (20, 50, 3),
    ], weight=WEIGHT)
    return graph


class LeidenTests(unittest.TestCase):
    def test_conversion_and_fixed_partition_quality(self):
        graph = weighted_fixture()
        converted, clubs = to_igraph(graph)
        self.assertEqual(converted.vs["club_id"], list(graph))
        self.assertEqual([(clubs[e.source], clubs[e.target], e[WEIGHT]) for e in converted.es],
                         list(graph.edges(data=WEIGHT)))
        for mode, strength in (("in", graph.in_degree), ("out", graph.out_degree)):
            self.assertEqual(converted.strength(mode=mode, weights=WEIGHT),
                             [strength(club, weight=WEIGHT) for club in clubs])
        for membership in (list(range(5)), [0, 0, 1, 1, 0]):
            groups = groups_from_membership(clubs, membership)
            m = sum(w for _, _, w in routes(graph))
            expected = 0
            for group in groups:
                internal = sum(w for a, b, w in routes(graph) if a in group and b in group)
                incoming = sum(w for a, b, w in routes(graph) if b in group)
                outgoing = sum(w for a, b, w in routes(graph) if a in group)
                expected += internal / m - incoming * outgoing / m**2
            partition = la.ModularityVertexPartition(
                converted, initial_membership=membership, weights=WEIGHT)
            self.assertAlmostEqual(partition.quality(), expected, places=12)
            self.assertAlmostEqual(modularity(graph, groups), expected, places=12)
            self.assertNotAlmostEqual(nx.community.modularity(graph, groups, weight=None), expected)
            self.assertNotAlmostEqual(
                nx.community.modularity(graph.to_undirected(), groups, weight=WEIGHT), expected)

    def test_trace_and_public_converged_parity(self):
        graph = weighted_fixture()
        result = optimize_leiden(graph, 2026)
        groups, progress, memberships, stats, settings = result
        self.assertEqual(result, optimize_leiden(graph, 2026))
        converted, clubs = to_igraph(graph)
        expected = la.find_partition(converted, la.ModularityVertexPartition, weights=WEIGHT,
                                     n_iterations=-1, seed=2026)
        self.assertEqual(partition_key(groups),
                         partition_key(groups_from_membership(clubs, expected.membership)))
        self.assertAlmostEqual(stats["final_q"], expected.quality(), places=12)
        self.assertTrue(settings["refine_partition"])
        self.assertEqual(memberships[0], list(range(len(clubs))))
        self.assertLessEqual(progress[-1]["returned_improvement"], 0)
        self.assertTrue(all(row["returned_improvement"] > 0 for row in progress[1:-1]))
        self.assertEqual(stats["completed_iterations"], len(progress)-1)
        self.assertEqual(stats["quality_verification_calls"], len(progress))
        for index, (row, membership) in enumerate(zip(progress, memberships)):
            state = groups_from_membership(clubs, membership)
            self.assertCountEqual([club for group in state for club in group], clubs)
            self.assertEqual(row["iteration"], index)
            self.assertAlmostEqual(row["networkx_q"], modularity(graph, state), places=12)
            self.assertAlmostEqual(row["delta_q"], row["returned_improvement"], places=12)


class ShuffleTests(unittest.TestCase):
    def test_loop_rejection_and_triangle_reversal(self):
        graph = nx.DiGraph([(0, 1), (1, 2), (2, 1)])
        self.assertFalse(try_three_edge_swap(graph, 0, 1, 2, 1))
        self.assertEqual(set(graph.edges), {(0, 1), (1, 2), (2, 1)})
        graph = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
        self.assertTrue(try_three_edge_swap(graph, 0, 1, 2, 0))
        self.assertEqual(set(graph.edges), {(0, 2), (2, 1), (1, 0)})

    def test_shared_shuffle_invariants_and_reproducibility(self):
        graph = weighted_fixture()
        before = routes(graph)
        shuffled, info = shuffle_routes(graph, 2027, 2028, target=7)
        repeated, repeated_info = shuffle_routes(graph, 2027, 2028, target=7)
        self.assertEqual(before, routes(graph))
        self.assertEqual(routes(shuffled), routes(repeated))
        self.assertEqual(info, repeated_info)
        self.assertEqual(info["successes"], 7)
        self.assertEqual(list(shuffled), list(graph))
        self.assertEqual(dict(graph.in_degree()), dict(shuffled.in_degree()))
        self.assertEqual(dict(graph.out_degree()), dict(shuffled.out_degree()))
        self.assertEqual(shuffled.number_of_edges(), graph.number_of_edges())
        self.assertFalse(shuffled.is_multigraph())
        self.assertEqual(nx.number_of_selfloops(shuffled), 0)
        self.assertEqual(Counter(w for _, _, w in before), Counter(w for _, _, w in routes(shuffled)))
        self.assertEqual(graph.size(weight=WEIGHT), shuffled.size(weight=WEIGHT))
        self.assertNotEqual(set(graph.edges), set(shuffled.edges))


if __name__ == "__main__":
    unittest.main()
