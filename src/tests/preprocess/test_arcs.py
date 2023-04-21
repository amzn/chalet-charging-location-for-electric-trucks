# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from chalet.model.input.node import Node
from chalet.model.input.node_type import NodeType
from chalet.model.parameters import Parameters
from chalet.model.processed_arcs import Arcs
from chalet.model.transit_time import TransitTime
from chalet.preprocess.arcs import PreprocessArcs

nodes_a_ids = [1, 2, 3]
nodes_a = pd.DataFrame(
    data={
        Node.id: nodes_a_ids,
        Node.type: [NodeType.STATION, NodeType.SITE, NodeType.STATION],
    },
    index=nodes_a_ids,
)

nodes_b_ids = [1, 2, 3, 4]
nodes_b = pd.DataFrame(
    data={
        Node.id: nodes_b_ids,
        Node.type: [NodeType.STATION, NodeType.SITE, NodeType.STATION, NodeType.SITE],
    },
    index=nodes_b_ids,
)


class TestPreprocessArcs:
    """Test for PreprocessArcs class"""

    @patch.object(PreprocessArcs, "_create_time_distance_map")
    @patch.object(PreprocessArcs, "_preprocess_arcs")
    def test_preprocess(self, mock_preprocess_arcs, mock_time_distance_map):
        """Test preprocess arcs."""
        tail_id = [1, 1, 2, 2, 3, 3, 1, 2, 3]
        head_id = [2, 3, 1, 3, 1, 2, 1, 2, 3]
        arcs = pd.DataFrame(
            data={
                Arcs.tail_id: tail_id,
                Arcs.head_id: head_id,
                Arcs.time: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                Arcs.distance: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
            },
            index=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        )
        parameters = Parameters({"dev_factor": 2})
        transit_time_provider = TransitTime(parameters.max_road_time_once, parameters.legal_break_time)
        data = {
            "nodes": nodes_a.copy(),
            "arcs": arcs.copy(),
            "parameters": parameters,
            "transit_time": transit_time_provider,
        }

        PreprocessArcs().preprocess(data)

        mock_time_distance_map.assert_called()
        mock_preprocess_arcs.assert_called()

    def test_preprocess_arcs(self):
        """Test arcs preprocessing."""

        params = Parameters({"dev_factor": 2})
        tt_provider = TransitTime(params.max_road_time_once, params.legal_break_time)
        arcs = pd.DataFrame(
            {
                Arcs.tail_id: [1, 1, 1, 1, 2, 2, 2, 3, 3],
                Arcs.head_id: [1, 2, 3, 4, 1, 3, 4, 1, 2],
                Arcs.distance: [11.0, 129.0, 13.0, 1400.0, 210.0, 83.0, 84.0, 131.0, 82.0],
                Arcs.time: [11.0, 129.0, 13.0, 1400.0, 210.0, 83.0, 84.0, 131.0, 82.0],
                "CONDITION": [
                    "SELF_LOOP_REMOVE",
                    "EXCEEDS_FINAL_RANGE_REMOVE",
                    "TOO_CLOSE_REMOVE",
                    "EXCEEDS_RANGE_REMOVE",
                    "EXCEEDS_INITIAL_RANGE_REMOVE",
                    "NOT_EXCEEDS_INITIAL_RANGE",
                    "SITE_TO_SITE_REMOVE",
                    "NOT_TOO_CLOSE",
                    "EXCEEDS_MAX_FUEL_TIME_REMOVE",
                ],
            }
        )
        expected_arcs = arcs[~arcs["CONDITION"].str.contains("REMOVE")].copy()
        expected_arcs[Arcs.fuel_time] = [0.0, 39.3]
        expected_arcs[Arcs.break_time] = [0.0, 0.0]

        PreprocessArcs()._preprocess_arcs(arcs, nodes_b.copy(), tt_provider, params)

        assert_frame_equal(arcs, expected_arcs)

    def test_range_filter_arcs(self):
        """Test arcs filtering based on range."""

        arcs = pd.DataFrame(
            {
                Arcs.tail_id: [1, 1, 1, 1, 2, 2, 2, 3, 3],
                Arcs.head_id: [1, 2, 3, 4, 1, 3, 4, 1, 2],
                Arcs.distance: [11.0, 129.0, 13.0, 1400.0, 210.0, 83.0, 84.0, 131.0, 82.0],
                "CONDITION": [
                    "SELF_LOOP_REMOVE",
                    "EXCEEDS_FINAL_RANGE_REMOVE",
                    "TOO_CLOSE_REMOVE",
                    "EXCEEDS_RANGE_REMOVE",
                    "EXCEEDS_INITIAL_RANGE_REMOVE",
                    "NOT_EXCEEDS_INITIAL_RANGE",
                    "SITE_TO_SITE_REMOVE",
                    "NOT_TOO_CLOSE",
                    "NOT_EXCEEDS_FINAL_RANGE",
                ],
            }
        )
        expected_arcs = arcs[~arcs["CONDITION"].str.contains("REMOVE")].copy()

        PreprocessArcs()._range_filter_arcs(arcs, nodes_b.copy(), 125, 125, 250, 50)

        assert_frame_equal(arcs, expected_arcs)

        with pytest.raises(ValueError):
            PreprocessArcs()._range_filter_arcs(arcs, nodes_b.copy(), 125, 1250, 250, 50)

    def test_add_fuel_time(self):
        """Test addition of fuel time."""

        params = Parameters({"dev_factor": 2})
        arcs = pd.DataFrame(
            {
                Arcs.tail_id: [1, 1, 2, 2, 3, 3, 1, 2, 3],
                Arcs.head_id: [2, 3, 1, 3, 1, 2, 1, 2, 3],
                Arcs.time: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                Arcs.distance: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                "CONDITION": [
                    "STATION_TO_SITE",
                    "STATION_TO_STATION",
                    "SITE_TO_STATION",
                    "SITE_TO_STATION",
                    "STATION_TO_STATION",
                    "STATION_TO_SITE",
                    "STATION_TO_STATION",
                    "SITE_TO_SITE",
                    "STATION_TO_STATION",
                ],
            }
        )
        expected_arcs = arcs.copy()
        expected_arcs[Arcs.fuel_time] = [40.5, 6.0, 0.0, 0.0, 6.0, 49.5, 0.0, 0.0, 0.0]

        PreprocessArcs()._add_fuel_time(arcs, nodes_a.copy(), params)

        assert_frame_equal(arcs, expected_arcs)

    def test_time_filter_arcs(self):
        """Test arc filtering based on fuel time bounds."""

        arcs = pd.DataFrame(
            {
                Arcs.tail_id: [1, 1, 2, 2, 3, 3, 1, 2, 3],
                Arcs.head_id: [2, 3, 1, 3, 1, 2, 1, 2, 3],
                Arcs.time: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                Arcs.distance: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                Arcs.fuel_time: [10.0, 20.0, 10.0, 40.0, 20.0, 40.0, 0.0, 0.0, 0.0],
                "CONDITION": [
                    "TOO_LOW",
                    "WITHIN_BOUNDS",
                    "NOT_STATION",
                    "NOT_STATION",
                    "WITHIN_BOUNDS",
                    "TOO_HIGH",
                    "TOO_LOW",
                    "NOT_STATION",
                    "TOO_LOW",
                ],
            }
        )
        expected_arcs = arcs[arcs["CONDITION"].isin(["WITHIN_BOUNDS", "NOT_STATION"])].copy()

        PreprocessArcs()._time_filter_arcs(arcs, nodes_a.copy(), 15, 30)

        assert_frame_equal(arcs, expected_arcs)
