# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import pandas as pd

from chalet.data_io.output_handler import export_data

TEST_FILE_NAME = "file_name1"

TEST_DF = pd.DataFrame(data={"col": [1, 2, 3]})


class TestOutputHandler:
    """Test output handler."""

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_export_data_with_new_path(self, mock_os_path, mock_os_makedirs):
        """Test export data if path does not exist."""
        context = {TEST_FILE_NAME: TEST_DF}
        with patch.object(TEST_DF, "to_csv") as to_csv_mock:
            export_data("output", context)
            to_csv_mock.assert_called_with("output/" + TEST_FILE_NAME, index=False)
            mock_os_makedirs.assert_called_once()

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    def test_export_data_with_existing_path(self, mock_os_path, mock_os_makedirs):
        """Test export data if path already exists."""
        context = {TEST_FILE_NAME: TEST_DF}
        with patch.object(TEST_DF, "to_csv") as to_csv_mock:
            export_data("", context)
            to_csv_mock.assert_called_with(TEST_FILE_NAME, index=False)
            mock_os_makedirs.assert_not_called()
