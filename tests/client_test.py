from __future__ import annotations

import unittest.mock

from py_nextbus.client import NextBusClient
from tests.helpers.mock_responses import MOCK_PREDICTIONS_RESPONSE_NO_ROUTE
from tests.helpers.mock_responses import MOCK_PREDICTIONS_RESPONSE_WITH_ROUTE
from tests.helpers.mock_responses import TEST_AGENCY_ID
from tests.helpers.mock_responses import TEST_DIRECTION_ID
from tests.helpers.mock_responses import TEST_ROUTE_ID
from tests.helpers.mock_responses import TEST_STOP_ID


class TestNextBusClient(unittest.TestCase):

    def setUp(self):
        self.client = NextBusClient()

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_predictions_for_stop_no_route(self, mock_get):
        mock_get.return_value = MOCK_PREDICTIONS_RESPONSE_NO_ROUTE

        result = self.client.predictions_for_stop(
            TEST_STOP_ID, agency_id=TEST_AGENCY_ID
        )

        self.assertEqual({r["stop"]["id"] for r in result}, {TEST_STOP_ID})
        self.assertEqual(len(result), 3)  # Results include all routes

        mock_get.assert_called_once()
        mock_get.assert_called_with(
            f"agencies/{TEST_AGENCY_ID}/stops/{TEST_STOP_ID}/predictions",
            {"coincident": True},
        )

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_predictions_for_stop_with_route(self, mock_get):
        mock_get.return_value = MOCK_PREDICTIONS_RESPONSE_WITH_ROUTE

        result = self.client.predictions_for_stop(
            TEST_STOP_ID,
            TEST_ROUTE_ID,
            agency_id=TEST_AGENCY_ID,
            direction_id=TEST_DIRECTION_ID,
        )

        # Assert all predictions are for the correct stop
        self.assertEqual({r["stop"]["id"] for r in result}, {TEST_STOP_ID})
        self.assertEqual({r["route"]["id"] for r in result}, {TEST_ROUTE_ID})
        self.assertEqual(
            {p["direction"]["id"] for r in result for p in r["values"]},
            {TEST_DIRECTION_ID},
        )

        mock_get.assert_called_once()
        mock_get.assert_called_with(
            f"agencies/{TEST_AGENCY_ID}/routes/{TEST_ROUTE_ID}/stops/{TEST_STOP_ID}/predictions",
            {"coincident": True, "direction": TEST_DIRECTION_ID},
        )


if __name__ == "__main__":
    unittest.main()
