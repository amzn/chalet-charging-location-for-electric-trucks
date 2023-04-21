# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test input_handler."""
import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

import chalet.data_io.input_handler as input_handler
from chalet.model.parameters import Parameters

TEST_DICT_KEY = "dev_factor"
TEST_DICT_VALUE = 69
TEST_FILE_NAME = Parameters.get_file_name()
FIRST_FILE_NAME = input_handler.files_to_load[0].get_file_name()
LAST_FILE_NAME = input_handler.files_to_load[-1].get_file_name()
TEST_JSON = json.dumps({TEST_DICT_KEY: TEST_DICT_VALUE}, separators=(",", ":"))
TEST_INVALID_JSON = "{"
DATA_FRAME_MOCK = [pd.DataFrame(data={"col": [i + 1], "ID": [i]}) for i in range(len(input_handler.files_to_load))]
EXPECTED_FIRST_DATA_FRAME = DATA_FRAME_MOCK[0]
EXPECTED_LAST_DATAFRAME = DATA_FRAME_MOCK[-1]


class TestLoadData:
    @patch("builtins.open", mock_open(read_data=TEST_JSON))
    @patch.object(input_handler, "_get_file", side_effect=DATA_FRAME_MOCK)
    def test_load_data(self, patch_load_file):
        result = input_handler.get_all_inputs("fake_path")

        assert TEST_FILE_NAME in result
        assert FIRST_FILE_NAME in result
        assert LAST_FILE_NAME in result


class TestLoadFiles:
    @patch.object(input_handler, "_get_file", side_effect=DATA_FRAME_MOCK)
    def test_load_files(self, patch_load_file):
        actual: dict = {}

        input_handler.load_files("", actual)

        assert_frame_equal(EXPECTED_FIRST_DATA_FRAME, actual[FIRST_FILE_NAME])
        assert_frame_equal(EXPECTED_LAST_DATAFRAME, actual[LAST_FILE_NAME])

    def test_load_invalid_files(self):
        with pytest.raises(Exception):
            input_handler.load_files("", {})


class TestLoadParameters:
    @patch("builtins.open", mock_open(read_data=TEST_INVALID_JSON))
    @patch.object(Parameters, "get_file_name", return_value=TEST_FILE_NAME)
    def test_invalid_json(self, patch_get_file_name):
        with pytest.raises(Exception):
            # Parameters.get_file_name = Mock(return_value=TEST_FILE_NAME)
            result: dict = {}

            input_handler.load_parameters("test", result)

    @patch("builtins.open", mock_open(read_data=TEST_JSON))
    def test_load_parameters(self):
        context: dict = {}
        expected = TEST_DICT_VALUE

        input_handler.load_parameters("test", context)
        actual = context[TEST_FILE_NAME].dev_factor

        assert expected == actual
