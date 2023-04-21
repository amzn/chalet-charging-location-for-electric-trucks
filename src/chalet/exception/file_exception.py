# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""File related exceptions."""


class FileException(Exception):
    """Base class for other file related exceptions."""

    pass


class LoadFileError(FileException):
    """Raised when there is an error in reading file."""

    pass
