"""Small, independently checked fixtures for the feeder-route statistical contract."""

from collections import Counter
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from premier_league_feeder_routes import _build_sample, _network, _route_statistics


class FeederRoutesTests(unittest.TestCase):
    def setUp(self):
        self.sample = pd.DataFrame([
            ("01/02", 10, 100, 1),
            ("01/02", 10, 100, 1),
            ("01/02", 20, 200, 2),
            ("02/03", 10, 200, 3),
            ("02/03", 30, 300, 4),
        ], columns=["transfer_season", "from_club_id", "to_club_id", "player_id"])

    def test_expected_family_ties_and_unadjusted_p_values_against_independent_calculation(self):
        permutations, seed = 37, 2026
        table, verification = _route_statistics(self.sample, permutations, seed)
        routes = table.set_index(["from_club_id", "to_club_id"])
        expected = {(10, 100): 4 / 3, (10, 200): 7 / 6, (10, 300): 1 / 2,
                    (20, 100): 2 / 3, (20, 200): 1 / 3,
                    (30, 200): 1 / 2, (30, 300): 1 / 2}
        self.assertEqual(set(routes.index), set(expected))
        for pair, value in expected.items():
            self.assertAlmostEqual(routes.loc[pair, "expected_count"], value)
        rng = np.random.default_rng(seed)
        observed = Counter(zip(self.sample.from_club_id, self.sample.to_club_id))
        ge, ties = Counter(), Counter()
        for _ in range(permutations):
            simulated = Counter()
            for _, season in self.sample.groupby("transfer_season", sort=True):
                shuffled = rng.permutation(season.to_club_id.to_numpy())
                simulated.update(zip(season.from_club_id, shuffled))
            for pair in expected:
                ge[pair] += simulated[pair] >= observed[pair]
                ties[pair] += simulated[pair] == observed[pair]
        raw = np.array([(1 + ge[pair]) / (1 + permutations) for pair in routes.index])
        np.testing.assert_array_equal(routes.p_value, raw)
        np.testing.assert_array_equal(routes.permutations_equal, [ties[pair] for pair in routes.index])
        self.assertGreater(ties[(10, 100)], 0)
        self.assertGreater(ge[(10, 100)], ge[(10, 100)] - ties[(10, 100)])
        np.testing.assert_array_equal(routes.significant, raw < 0.05)
        self.assertNotIn("adjusted_p_value", routes.columns)
        self.assertTrue(routes.loc[routes.observed_count.eq(0), "p_value"].eq(1).all())
        self.assertEqual(routes.loc[(10, 100), "distinct_players"], 1)
        self.assertEqual(routes.loc[(10, 100), "repeat_player_extra_records"], 1)
        self.assertTrue(routes.loc[(10, 100), "repeated_player_flag"])
        self.assertAlmostEqual(routes.loc[(10, 100), "destination_share"], 2 / 3)
        self.assertTrue(verification["all_permutations_preserved_origin_and_destination_totals_within_every_season"])

    def test_unadjusted_threshold_excludes_p_equal_to_point_zero_five(self):
        sample = pd.DataFrame([
            ("01/02", 10, 100, player) for player in range(5)
        ] + [
            ("01/02", 20, 200, player) for player in range(5, 10)
        ], columns=self.sample.columns)
        table, _ = _route_statistics(sample, 19, 2026)
        observed = table.loc[table.observed_count.gt(0)]
        self.assertTrue(observed.p_value.eq(0.05).all())
        self.assertFalse(observed.significant.any())
        self.assertFalse(observed.selected_route.any())
        self.assertFalse(table.loc[table.observed_count.eq(0), "significant"].any())

    def test_selection_requires_recurrence_even_when_single_transfer_is_significant(self):
        sample = pd.DataFrame([
            ("01/02", 10, 100, 1),
        ] + [
            ("01/02", 20, 200, player) for player in range(2, 102)
        ] + [
            ("01/02", 30, 300, 102), ("01/02", 30, 300, 103),
        ], columns=self.sample.columns)
        table, _ = _route_statistics(sample, 999, 2026)
        routes = table.set_index(["from_club_id", "to_club_id"])
        self.assertTrue(routes.loc[(10, 100), "significant"])
        self.assertFalse(routes.loc[(10, 100), "selected_route"])
        self.assertTrue(routes.loc[(30, 300), "selected_route"])
        self.assertFalse(table.loc[table.observed_count.lt(2), "selected_route"].any())

    def test_same_club_has_distinct_supplying_and_receiving_nodes(self):
        table, _ = _route_statistics(self.sample, 5, 2026)
        table["to_club_id"] = table.to_club_id.replace({100: 10})
        graph = _network(table)
        self.assertIn(("origin", 10), graph)
        self.assertIn(("destination", 10), graph)
        self.assertEqual(sum(data["weight"] for _, _, data in graph.edges(data=True)), len(self.sample))

    def test_membership_is_season_specific_and_exclusions_are_audited(self):
        transfers = pd.DataFrame([
            ("01/02", 10, 100, 1), ("02/03", 10, 200, 2),
            ("01/02", 515, 100, 3), ("01/02", 20, 123, 4),
            ("01/02", 20, 300, 5),
        ], columns=self.sample.columns)
        lookup = pd.DataFrame([
            ("01/02", 100, "GB1", "Club 100"),
            ("02/03", 10, "GB1", "Club 10"),
            ("02/03", 200, "GB1", "Club 200"),
        ], columns=["transfer_season", "club_id", "competition_id", "club_name"])
        with tempfile.TemporaryDirectory() as directory:
            transfers_path, lookup_path = Path(directory) / "transfers.csv", Path(directory) / "lookup.csv"
            transfers.to_csv(transfers_path, index=False)
            lookup.to_csv(lookup_path, index=False)
            with self.assertWarns(UserWarning):
                sample, labels, counts, coverage, discrepancies = _build_sample(transfers_path, lookup_path)
            self.assertEqual(sample.player_id.tolist(), [1])
            self.assertNotIn(20, labels)  # Missing names must fall back to IDs, not empty labels.
            for exclusion in ("non_club_origin", "non_club_destination", "premier_league_origin",
                              "non_premier_league_destination"):
                self.assertEqual(counts[f"excluded_{exclusion}_records"], 1)
            self.assertEqual([row["pl_arrivals"] for row in coverage], [1, 0])
            self.assertTrue(discrepancies)
            lookup.iloc[:1].to_csv(lookup_path, index=False)
            with self.assertRaisesRegex(ValueError, "does not cover seasons"):
                _build_sample(transfers_path, lookup_path)


if __name__ == "__main__":
    unittest.main()
