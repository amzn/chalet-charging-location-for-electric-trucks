# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test transit time."""
from chalet.model.transit_time import TransitTime

transit_time = TransitTime(300, 30)


class TestTransitTime:
    def test_break_time(self):
        break_time = transit_time.break_time(1413.2)

        assert break_time == 120.0

    def test_full_time(self):
        full_time = transit_time.full_time(1413.2)

        assert full_time == 1533.2

    def test_road_time(self):
        road_time = transit_time.road_time(300.0)

        assert road_time == 300.0
