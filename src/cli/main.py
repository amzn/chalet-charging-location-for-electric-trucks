#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Main."""
import argparse

from chalet.execute import Executor
from chalet.log_config.config import get_logger

parser = argparse.ArgumentParser(description="Charging Location Tool execution engine")
parser.add_argument("-i", "--inputs", help="inputs folder")
parser.add_argument("-o", "--outputs", help="outputs folder")
args, unknown = parser.parse_known_args()

INPUT_PATH = args.inputs or "data/"
OUTPUT_PATH = args.outputs or "output/"


def main():
    """Run the main script for the optimization model."""
    logger = get_logger(OUTPUT_PATH)
    executor = Executor(INPUT_PATH, OUTPUT_PATH)
    executor.execute()
    logger.info("Execution completed for charging location tool.")


if __name__ == "__main__":
    main()
