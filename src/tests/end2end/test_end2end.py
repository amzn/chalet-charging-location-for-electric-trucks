# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import pandas as pd
from pandas import Index
from pandas.testing import assert_frame_equal

from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs
from cli.main import main

OUTPUT_DIR = "src/tests/end2end/output_data/"
INPUT_DIR = "src/tests/end2end/input_data/"


@patch("cli.main.INPUT_PATH", INPUT_DIR)
@patch("cli.main.OUTPUT_PATH", OUTPUT_DIR)
def test_end2end():
    main()

    actual_od_coverage = pd.read_csv(OUTPUT_DIR + "od_coverage.csv")
    actual_stations = pd.read_csv(OUTPUT_DIR + "stations.csv")
    actual_unknown_sites = pd.read_csv(OUTPUT_DIR + "unknown_sites.csv")

    expected_od_coverage = pd.DataFrame(
        {
            OdPairs.origin_id: [3, 2, 0],
            OdPairs.destination_id: [1, 5, 4],
            OdPairs.demand: 1.0,
            OdPairs.direct_distance: [376.11, 349.78, 206.6],
            OdPairs.direct_time: [360.54, 341.50, 186.77],
            OdPairs.feasible: True,
            OdPairs.stations: ["96/22/293", "96/165/36", "205/293"],
            OdPairs.fuel_stops: [3, 3, 2],
            OdPairs.route_distance: [396.31, 350.74, 212.23],
            OdPairs.route_time: [520.12, 471.76, 260.48],
        }
    )
    expected_stations = pd.DataFrame(
        {
            Nodes.id: [22, 36, 96, 165, 205, 293],
            Nodes.type: "STATION",
            Nodes.demand: [1.0, 1.0, 2.0, 1.0, 1.0, 2.0],
            Nodes.energy: [208.3, 225.0, 510.0, 252.0, 183.3, 490.3],
        },
    )
    expected_unknown_sites = pd.DataFrame({0: []}, columns=Index(["0"]))

    assert_frame_equal(actual_od_coverage, expected_od_coverage)
    assert_frame_equal(actual_stations, expected_stations)
    assert_frame_equal(actual_unknown_sites, expected_unknown_sites)
