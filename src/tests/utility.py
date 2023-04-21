# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Util methods for tests."""


def get_path_module(module):
    """This is for refactoring purposes."""
    return module.__module__ + "." + module.__name__
