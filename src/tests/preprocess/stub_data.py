# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict

import pandas as pd

from chalet.common.constants import TIME_DISTANCE_MAP, TRANSIT_TIME_KEY
from chalet.model.hash_map import Hashmap
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.processed_od_pairs import OdPairs
from chalet.model.transit_time import TransitTime

TRUCK_RANGE = 300
FUEL_TIME_BOUND = 75
NUM_PROC = 1


def get_stub_data() -> Dict:
    """Returns graph stub data."""
    od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3, 3, 5],
            OdPairs.destination_id: [2, 3, 4, 4, 5],
            OdPairs.demand: [10.0, 20.0, 30.0, 40.0, 0.0],
        }
    )

    tail_id = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 2, 3, 4]
    head_id = [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3, 1, 2, 3, 4]
    arcs = pd.DataFrame(
        {
            Arcs.tail_id: tail_id,
            Arcs.head_id: head_id,
            Arcs.time: [
                10.0,
                20.0,
                30.0,
                10.0,
                40.0,
                50.0,
                20.0,
                40.0,
                60.0,
                30.0,
                50.0,
                60.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            Arcs.distance: [
                10.0,
                20.0,
                30.0,
                10.0,
                40.0,
                50.0,
                20.0,
                40.0,
                60.0,
                30.0,
                50.0,
                60.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            Arcs.fuel_time: 16 * [0.0],
            Arcs.break_time: 16 * [0.0],
        }
    )

    node_ids = [1, 2, 3, 4]
    nodes = pd.DataFrame(
        data={
            Nodes.id: node_ids,
            Nodes.type: ["SITE"],
            Nodes.cost: 4 * [0.0],
            Nodes.latitude: [0.0, 10.0, 0.0, 10.0],
            Nodes.longitude: [0.0, 0.0, 10.0, 10.0],
            Nodes.name: ["node" + str(i) for i in range(1, 5)],
            Nodes.real: 4 * [True],
        },
        index=node_ids,
    )

    older_arcs = pd.DataFrame(
        {
            Arc.tail_id: tail_id,
            Arc.head_id: head_id,
            Arc.time: 16 * [10.0],
            Arc.distance: 16 * [10.0],
        }
    )

    key_type = (older_arcs[[Arc.tail_id, Arc.head_id]].values.dtype, 2)
    value_type = (older_arcs[[Arc.time, Arc.distance]].values.dtype, 2)

    time_dist_map = Hashmap(
        older_arcs[[Arc.tail_id, Arc.head_id]].values,
        older_arcs[[Arc.time, Arc.distance]].values,
        key_type,
        value_type,
        [100, 100],
    )

    parameters = Parameters({"dev_factor": 2})
    transit_time_provider = TransitTime(parameters.max_road_time_once, parameters.legal_break_time)

    data = {
        Node.get_file_name(): nodes,
        Parameters.get_file_name(): parameters,
        OdPair.get_file_name(): od_pairs,
        Arc.get_file_name(): arcs,
        TIME_DISTANCE_MAP: time_dist_map,
        TRANSIT_TIME_KEY: transit_time_provider,
    }

    return data


def get_stub_nodes() -> pd.DataFrame:
    """Returns stub nodes."""
    node_ids = [1, 2, 3, 4]
    nodes = pd.DataFrame(
        data={
            Nodes.id: node_ids,
            Nodes.type: ["TEST_NODE"],
            Nodes.cost: 4 * [0.0],
            Nodes.latitude: [0.0, 10.0, 0.0, 10.0],
            Nodes.longitude: [0.0, 0.0, 10.0, 10.0],
            Nodes.name: ["node" + str(i) for i in range(1, 5)],
            Nodes.real: 4 * [True],
        },
        index=node_ids,
    )
    return nodes


def get_stub_od_pairs() -> pd.DataFrame:
    """Returns stub od pairs."""
    od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3],
            OdPairs.destination_id: [2, 3, 4],
            OdPairs.demand: [10.0, 20.0, 30.0],
        }
    )

    return od_pairs


def get_stub_od_coverage() -> pd.DataFrame:
    """Returns stub od coverage."""
    od_coverage = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3],
            OdPairs.destination_id: [2, 3, 4],
            OdPairs.demand: [10.0, 20.0, 30.0],
            OdPairs.distance: 3 * [10],
        }
    )

    return od_coverage


def get_stub_processed_od_pairs() -> pd.DataFrame:
    """Returns stub processed od pairs."""
    od_pairs = pd.DataFrame(
        {
            OdPairs.origin_id: [1, 2, 3],
            OdPairs.destination_id: [2, 3, 4],
            OdPairs.demand: [10.0, 20.0, 30.0],
            OdPairs.distance: 3 * [10.0],
            OdPairs.legs: 3 * [1],
            OdPairs.max_time: 3 * [float("inf")],
            OdPairs.max_road_time: 3 * [float("inf")],
        }
    )

    return od_pairs


def get_stub_parameters() -> Parameters:
    """Returns stub od parameters."""
    return Parameters({"dev_factor": 2})


def get_stub_arcs() -> pd.DataFrame:
    """Returns stub arcs."""
    tail_id = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 2, 3, 4]
    head_id = [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3, 1, 2, 3, 4]
    arcs = pd.DataFrame(
        {
            Arcs.tail_id: tail_id,
            Arcs.head_id: head_id,
            Arcs.time: [
                10.0,
                20.0,
                30.0,
                10.0,
                40.0,
                50.0,
                20.0,
                40.0,
                60.0,
                30.0,
                50.0,
                60.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            Arcs.distance: [
                10.0,
                20.0,
                30.0,
                10.0,
                40.0,
                50.0,
                20.0,
                40.0,
                60.0,
                30.0,
                50.0,
                60.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            Arcs.fuel_time: 16 * [0.0],
            Arcs.break_time: 16 * [0.0],
        }
    )

    return arcs


def get_stub_time_dist_map() -> Hashmap:
    """Returns stub time dist map."""
    tail_id = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 2, 3, 4]
    head_id = [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3, 1, 2, 3, 4]

    older_arcs = pd.DataFrame(
        {
            Arc.tail_id: tail_id,
            Arc.head_id: head_id,
            Arc.time: 16 * [10.0],
            Arc.distance: 16 * [10.0],
        }
    )

    key_type = (older_arcs[[Arc.tail_id, Arc.head_id]].values.dtype, 2)
    value_type = (older_arcs[[Arc.time, Arc.distance]].values.dtype, 2)

    time_dist_map = Hashmap(
        older_arcs[[Arc.tail_id, Arc.head_id]].values,
        older_arcs[[Arc.time, Arc.distance]].values,
        key_type,
        value_type,
        [100, 100],
    )

    return time_dist_map
