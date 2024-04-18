# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test postprocess."""
import unittest
from unittest.mock import DEFAULT, patch

import numpy as np
import pandas as pd

from chalet.model.parameters import Parameters
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs
from chalet.postprocess.post_process_context import PostProcess

od_coverage_filename = "od_coverage.csv"
stations_filename = "stations.csv"
unknown_sites_filename = "unknown_sites.csv"

test_dataframe = pd.DataFrame({"column1": [10], "column2": [20]})


class TestPostProcess(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPostProcess, self).__init__(*args, **kwargs)
        self.dummy_obj_post_process = PostProcess(
            test_dataframe, test_dataframe, [], Parameters({}), test_dataframe, test_dataframe, {}
        )
        nodes = pd.DataFrame(
            {
                Nodes.id: [1, 2, 3],
                Nodes.name: ["a", "b", "c"],
                Nodes.type: ["a", "b", "c"],
                Nodes.real: [0, 0, 1],
                Nodes.latitude: [1, 2, 3],
                Nodes.longitude: [1, 2, 3],
                Nodes.demand: [10, 10, 10],
                Nodes.energy: [100, 100, 100],
            }
        )
        od_pairs = pd.DataFrame(
            {
                OdPairs.origin_id: [10, 20, 30],
                OdPairs.destination_id: [10, 20, 30],
                OdPairs.demand: [1, 1, 1],
                OdPairs.distance: [0, 0, 0],
                OdPairs.feasible: [True, True, True],
                OdPairs.covered: [1, 2, 4],
                OdPairs.stations: ["a", "b", "c"],
                OdPairs.fuel_stops: [1, 2, 3],
                OdPairs.direct_time: [1.0, 1.0, 1.0],
                OdPairs.route_distance: [1.0, 1.0, 1.0],
                OdPairs.route_time: [1.0, 1.0, 1.0],
            }
        )
        od_coverage = pd.DataFrame(
            {
                OdPairs.origin_id: [10, 20, 30],
                OdPairs.destination_id: [10, 20, 30],
                OdPairs.demand: [1, 1, 1],
                OdPairs.distance: [0, 0, 0],
                OdPairs.feasible: [False, False, False],
                OdPairs.stations: ["a", "b", "c"],
                OdPairs.fuel_stops: [1, 2, 3],
            }
        )
        self.valid_obj_post_process = PostProcess(nodes, od_pairs, [], Parameters({}), od_coverage, test_dataframe, {})

    def test_stat_attrs(self):
        """Validate static names."""
        post_pros = self.dummy_obj_post_process
        self.assertEqual(post_pros.od_coverage_file, od_coverage_filename)
        self.assertEqual(post_pros.stations_file, stations_filename)
        self.assertEqual(post_pros.missing_file, unknown_sites_filename)

    def test__process_od_data__missed_od_pairs(self):
        """Validate failure on empty od_pairs data."""
        post_pros = self.dummy_obj_post_process
        with self.assertRaises(KeyError):
            with patch.multiple("chalet.postprocess.post_process_context", calc_station_stats=DEFAULT) as util_mock:
                post_pros._process_od_data()
                util_mock["calc_station_stats"].assert_called()

    def test__process_od_data__invalid_data(self):
        """Validate failure on invalid od_pairs data."""
        test_od_pairs = pd.DataFrame({"ORIGIN_ID": [10, 20], "DESTINATION_ID": [10, 20]})
        post_pros = self.dummy_obj_post_process
        post_pros.od_pairs = test_od_pairs
        with self.assertRaises(KeyError):
            with patch.multiple("chalet.postprocess.post_process_context", calc_station_stats=DEFAULT) as util_mock:
                post_pros._process_od_data()
                util_mock["calc_station_stats"].assert_called()

    def test__process_od_data__valid_data(self):
        """Validate execution on valid data."""
        post_pros = self.valid_obj_post_process
        with patch.multiple("chalet.postprocess.post_process_context", calc_station_stats=DEFAULT) as util_mock:
            util_mock["calc_station_stats"].return_value = {}
            post_pros._process_od_data()
            util_mock["calc_station_stats"].assert_called()

    def test_postprocess(self):
        """Correct execution calls for postprocess call."""
        post_pros = self.valid_obj_post_process
        with patch.object(post_pros, "_process_od_data") as mock:
            post_pros.postprocess()
            mock.assert_called()

    def test_postprocess__validate_outputs(self):
        """Validate expected outputs."""
        post_pros = self.valid_obj_post_process
        expected_nodes = pd.DataFrame({Nodes.id: [], Nodes.type: [], Nodes.demand: [], Nodes.energy: []})
        expected_nodes = expected_nodes.astype(np.int64)
        expected_nodes[Nodes.type] = expected_nodes[Nodes.type].astype(object)

        expected_sites = pd.DataFrame(
            {
                "column1": [10],
                "column2": [20],
            }
        )

        expected_od_coverage = pd.DataFrame(
            {
                OdPairs.origin_id: [10, 20, 30],
                OdPairs.destination_id: [10, 20, 30],
                OdPairs.demand: [1, 1, 1],
                OdPairs.direct_distance: [0, 0, 0],
                OdPairs.direct_time: [1.0, 1.0, 1.0],
                OdPairs.feasible: [True, True, True],
                OdPairs.stations: ["a", "b", "c"],
                OdPairs.fuel_stops: [1, 2, 3],
                OdPairs.route_distance: [1.0, 1.0, 1.0],
                OdPairs.route_time: [1.0, 1.0, 1.0],
            }
        )
        expected_export_context = {
            unknown_sites_filename: expected_sites,
            od_coverage_filename: expected_od_coverage,
            stations_filename: expected_nodes,
        }
        with patch.multiple("chalet.postprocess.post_process_context", calc_station_stats=DEFAULT) as util_mock:
            post_pros.postprocess()
            util_mock["calc_station_stats"].assert_called()
            expected_keys = set(expected_export_context.keys())
            self.assertEqual(set(post_pros.export_context.keys()), expected_keys)
            for key in expected_keys:
                pd.testing.assert_frame_equal(post_pros.export_context[key], expected_export_context[key])
