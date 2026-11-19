"""Verify directed Louvain candidate scores, aggregation and NetworkX parity."""

from collections import defaultdict
import unittest

import networkx as nx

from louvain_transfer_communities import THRESHOLD, optimize_louvain
from test_leiden_transfer_communities import weighted_fixture
from transfer_community_inputs import WEIGHT, modularity, partition_key


def multilevel_fixture():
    graph = nx.DiGraph()
    edges = [(i, (i+1) % 12, 9) for i in range(12)]
    edges += [(i+1, i, 7) for i in range(0, 12, 2)]
    graph.add_weighted_edges_from(edges, weight=WEIGHT)
    return graph


class LouvainTests(unittest.TestCase):
    def public_parity(self, graph, result, seed=2026):
        expected = nx.community.louvain_communities(graph, weight=WEIGHT, resolution=1.0,
                                                    threshold=THRESHOLD, seed=seed)
        self.assertEqual(partition_key(result[0]), partition_key(expected))
        self.assertAlmostEqual(result[-1]["final_q"], modularity(graph, expected), places=12)

    def verify_every_candidate(self, graph, result):
        _, progress, evaluations, mapping, _, stats = result
        self.assertEqual([r["evaluation_id"] for r in evaluations], list(range(1, len(evaluations)+1)))
        members = defaultdict(set)
        initial_owner = {}
        for level, node, community, club in mapping:
            members[level, node].add(club)
            initial_owner[level, club] = community
        assignments = {}
        level, rejected_changing = 0, 0

        def groups(owner):
            groups = defaultdict(set)
            for club, community in owner.items():
                groups[community].add(club)
            self.assertCountEqual([c for group in groups.values() for c in group], graph)
            return list(groups.values())

        for row in evaluations:
            kind = row["evaluation_type"]
            if kind not in ("candidate", "accepted"):
                continue
            if level != row["level"]:
                level = row["level"]
                assignments = {club: initial_owner[level, club] for club in graph}
            moved = members[level, row["moved_node"]]
            source, target = row["source_community"], row["target_community"]
            before = modularity(graph, groups(assignments))
            self.assertAlmostEqual(row["q_before"], before, places=12)
            self.assertTrue(all(assignments[club] == source for club in moved))
            proposed = dict(assignments)
            proposed.update(dict.fromkeys(moved, target))
            proposed_q = modularity(graph, groups(proposed))
            self.assertAlmostEqual(row["q_candidate"], proposed_q, places=12)
            self.assertAlmostEqual(row["delta_q"], proposed_q-before, places=12)
            if kind == "accepted":
                assignments = proposed
                state = progress[row["move"]]
                self.assertAlmostEqual(state["q"], proposed_q, places=12)
                self.assertEqual(state["represented_clubs"], len(moved))
                self.assertEqual(state["community_count"], len(groups(assignments)))
            elif not row["accepted"] and source != target:
                rejected_changing += 1
        self.assertGreater(rejected_changing, 0)
        self.assertEqual(sum(r["evaluation_type"] == "candidate" for r in evaluations),
                         stats["candidate_evaluations"])

    def test_asymmetric_unequal_weight_candidates_and_rejections(self):
        graph = weighted_fixture()
        result = optimize_louvain(graph, 2026)
        self.verify_every_candidate(graph, result)
        self.public_parity(graph, result)
        singleton = [{n} for n in graph]
        q = result[1][0]["q"]
        self.assertAlmostEqual(q, modularity(graph, singleton), places=12)
        self.assertNotAlmostEqual(q, nx.community.modularity(graph, singleton, weight=None))
        self.assertNotAlmostEqual(q, nx.community.modularity(graph.to_undirected(), singleton, weight=WEIGHT))

    def test_continuous_multilevel_trace_and_repeatability(self):
        graph = multilevel_fixture()
        result = optimize_louvain(graph, 2026)
        self.assertEqual(result, optimize_louvain(graph, 2026))
        self.public_parity(graph, result)
        self.verify_every_candidate(graph, result)
        _, progress, evaluations, mapping, sweeps, stats = result
        self.assertGreater(len({r["level"] for r in progress[1:]}), 1)
        self.assertTrue(any(r["represented_clubs"] > 1 for r in progress))
        self.assertEqual([r["move"] for r in progress], list(range(stats["accepted_moves"]+1)))
        for level in range(1, stats["attempted_levels"]+1):
            self.assertCountEqual([club for l, _, _, club in mapping if l == level], graph)
            self.assertEqual([r for r in sweeps if r["level"] == level][-1]["accepted_moves"], 0)
        aggregates = [r for r in evaluations if r["evaluation_type"] == "aggregation_verification"]
        self.assertTrue(aggregates)
        for row in aggregates:
            self.assertAlmostEqual(row["q_before"], row["q_candidate"], places=12)
            self.assertAlmostEqual(row["q_candidate"], progress[row["move"]]["q"], places=12)
        self.assertEqual(progress[-1]["q"], stats["final_q"])


if __name__ == "__main__":
    unittest.main()
