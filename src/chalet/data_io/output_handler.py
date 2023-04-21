# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Module for writing output data."""
import logging
import os
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def export_data(path: str, context: Dict[str, pd.DataFrame]):
    """Export given context to csv files in the provided path directory."""
    if not os.path.exists(path):
        os.makedirs(path)
    for file_name, df in context.items():
        logger.info(f"========== Running export of file {file_name}  ==========")
        df.to_csv(os.path.join(r"", path, file_name), index=False)
