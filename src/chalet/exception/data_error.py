# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data related exceptions."""


class DataError(Exception):
    """Base class for other data related exceptions."""

    pass


class NegativeValueError(DataError):
    """Raised when value is negative."""

    pass


class ValueOutOfThresholdError(DataError):
    """Raised when value is less or more than the expected threshold."""

    pass
