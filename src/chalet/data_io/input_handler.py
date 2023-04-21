# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Module for loading data."""
import json
import logging
import os
from typing import Any, List

import pandas as pd

from chalet.exception.file_exception import LoadFileError
from chalet.model.base_csv_file import BaseCsvFile
from chalet.model.input.arc import Arc
from chalet.model.input.node import Node
from chalet.model.input.od_pair import OdPair
from chalet.model.parameters import Parameters

logger = logging.getLogger(__name__)

# Define list of all csv files that need to be loaded
files_to_load: List[Any] = [Node, Arc, OdPair]

chunk_size = 1000000


def get_all_inputs(path: str) -> dict:
    """Load all input files from a given path and set as context for processing."""
    context: dict = {}
    load_files(path, context)
    load_parameters(path, context)
    return context


def load_files(path: str, context: dict):
    """Load all csv files."""
    for file in files_to_load:
        try:
            data = _get_file(path, file)
            context[file.get_file_name()] = data
            logger.info(f"Loaded file: {file.get_file_name()} successfully.")
        except Exception as exception:
            error_msg = "Loading error in file '{}': {}"
            raise LoadFileError(error_msg.format(file.get_file_name(), str(exception)))
    context[Node.get_file_name()].set_index(Node.id, inplace=True, drop=False)


def load_parameters(path: str, context: dict):
    """Load parameters."""
    params_json = open(os.path.join(path, Parameters.get_file_name() + ".json"))
    try:
        params_data = json.load(params_json)
        param_object = Parameters(params_data)
        context[Parameters.get_file_name()] = param_object
        logger.info(f"Loaded file: {Parameters.get_file_name()} successfully.")
    except Exception as exception:
        error_msg = "Loading error in '{}': {}."
        raise LoadFileError(error_msg.format(Parameters.get_file_name(), str(exception)))
    finally:
        params_json.close()


def _get_file(path: str, file: BaseCsvFile) -> pd.DataFrame:
    """Load a csv file from given path and perform schema validations."""
    csv_filepath = os.path.join(path, file.get_file_name() + ".csv")

    # Read in chunks to support large csv files, e.g., arcs.csv can have thousands of rows
    chunks = pd.read_csv(csv_filepath, chunksize=chunk_size)
    data = pd.concat(chunks)
    validated_data = file.get_schema().validate(data)
    return validated_data
