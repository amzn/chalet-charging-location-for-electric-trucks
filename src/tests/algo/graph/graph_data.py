# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pandas as pd

from chalet.common.constants import TIME_DISTANCE_MAP, TRANSIT_TIME_KEY
from chalet.model.hash_map import Hashmap
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters
from chalet.model.processed_arcs import Arcs
from chalet.model.processed_nodes import Nodes
from chalet.model.transit_time import TransitTime

NODE_ATTR_COST_ONE = {Nodes.cost: 1.0}
NODE_ATTR_COST_ZERO = {Nodes.cost: 0.0}
EDGE_ATTR_ALL_TIMES_ONE = {Arcs.time: 1.0, Arcs.fuel_time: 1.0, Arcs.break_time: 1.0}


def get_stub_od_pairs():
    """Returns stub od_pairs."""
    return pd.DataFrame(
        {
            "ORIGIN_ID": [1, 2, 3],
            "DESTINATION_ID": [2, 3, 4],
            "DEMAND": [10.0, 20.0, 30.0],
            "LEGS": 3 * [1],
            "MAX_TIME": [40.0, 80.0, 120.0],
            "MAX_ROAD_TIME": [40.0, 80.0, 120.0],
        }
    )


TAIL_ID = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 2, 3, 4]
HEAD_ID = [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3, 1, 2, 3, 4]


def get_stub_arcs():
    """Returns stub arcs."""
    return pd.DataFrame(
        {
            "TAIL_ID": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 2, 3, 4],
            "HEAD_ID": [2, 3, 4, 1, 3, 4, 1, 2, 4, 1, 2, 3, 1, 2, 3, 4],
            "ROAD_TIME": [
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
            "DISTANCE": [
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
            "FUEL_TIME": 16 * [0.0],
            "BREAK_TIME": 16 * [0.0],
        }
    )


NODE_IDS = [1, 2, 3, 4]


def get_stub_nodes():
    """Returns stub nodes."""
    return pd.DataFrame(
        data={
            "ID": NODE_IDS,
            "TYPE": ["TEST_NODE"],
            "COST": 4 * [1.0],
            "LATITUDE": [0.0, 10.0, 0.0, 10.0],
            "LONGITUDE": [0.0, 0.0, 10.0, 10.0],
            "NAME": ["node" + str(i) for i in range(1, 5)],
            "REAL": 4 * [True],
        },
        index=NODE_IDS,
    )


OLDER_ARCS = pd.DataFrame({"TAIL_ID": TAIL_ID, "HEAD_ID": HEAD_ID, "TIME": 16 * [10], "DISTANCE": 16 * [10]})

KEY_TYPE = (OLDER_ARCS[[Arc.tail_id, Arc.head_id]].values.dtype, 2)
VALUE_TYPE = (OLDER_ARCS[["TIME", Arc.distance]].values.dtype, 2)


def get_stub_time_dist_map():
    """Returns stub time_dist_map."""
    return Hashmap(
        OLDER_ARCS[[Arc.tail_id, Arc.head_id]].values,
        OLDER_ARCS[[Arc.time, Arc.distance]].values,
        KEY_TYPE,
        VALUE_TYPE,
        [100, 100],
    )


def get_stub_parameters():
    """Returns stub parameters."""
    return Parameters({"dev_factor": 2})


def get_stub_transit_time_provider():
    """Returns stub transit_time_provider."""
    return TransitTime(get_stub_parameters().max_road_time_once, get_stub_parameters().legal_break_time)


def get_stub_data():
    """Returns stub data."""
    return {
        Node.get_file_name(): get_stub_nodes(),
        Parameters.get_file_name(): get_stub_parameters(),
        OdPair.get_file_name(): get_stub_od_pairs(),
        Arc.get_file_name(): get_stub_arcs(),
        TIME_DISTANCE_MAP: get_stub_time_dist_map(),
        TRANSIT_TIME_KEY: get_stub_transit_time_provider(),
    }
