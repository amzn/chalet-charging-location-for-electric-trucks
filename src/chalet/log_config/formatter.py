# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Custom Formatters."""
import datetime
import logging


class CustomFormatter(logging.Formatter):
    """Base Formatter."""

    def format(self, record) -> str:
        """Format LogRecord."""
        data = None
        if record.args:
            data = record.args[0]
        time = datetime.datetime.utcfromtimestamp(record.created)
        formatted_record = f"{time} - [{record.name}] - {record.levelname} - {record.msg}"
        if data is not None:
            return formatted_record + f" - {data}"
        return formatted_record
