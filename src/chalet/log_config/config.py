# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Logging settings."""
import logging
import os

from chalet.log_config.formatter import CustomFormatter


def get_logger(log_dir=""):
    """Init Logger handlers and formatters."""
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("chalet")
    logger.setLevel(logging.DEBUG)

    formatter = CustomFormatter()
    file_handler = logging.FileHandler(os.path.join(log_dir, "chalet.log"), mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def set_mip_log_file(xpress_model, log_dir):
    """
    Initializes clean log file of Xpress model in given directory.
    """
    mip_log_file = os.path.join(log_dir, "mip.log")
    if os.path.exists(mip_log_file):
        os.remove(mip_log_file)
    xpress_model.setlogfile(mip_log_file)
