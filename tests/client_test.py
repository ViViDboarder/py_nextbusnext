from __future__ import annotations

import unittest.mock
from unittest.mock import MagicMock

from py_nextbus.client import NextBusClient
from tests.helpers.mock_responses import MOCK_AGENCY_LIST_RESPONSE
from tests.helpers.mock_responses import MOCK_PREDICTIONS_RESPONSE_NO_ROUTE
from tests.helpers.mock_responses import MOCK_PREDICTIONS_RESPONSE_WITH_ROUTE
from tests.helpers.mock_responses import MOCK_ROUTE_DETAILS_RESPONSE
from tests.helpers.mock_responses import MOCK_ROUTE_LIST_RESPONSE
from tests.helpers.mock_responses import TEST_AGENCY_ID
from tests.helpers.mock_responses import TEST_DIRECTION_ID
from tests.helpers.mock_responses import TEST_ROUTE_ID
from tests.helpers.mock_responses import TEST_STOP_ID


class TestNextBusClient(unittest.TestCase):
    def setUp(self):
        self.client = NextBusClient()

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_list_agencies(self, mock_get: MagicMock):
        mock_get.return_value = MOCK_AGENCY_LIST_RESPONSE

        agencies = self.client.agencies()

        # Check critical agency keys
        for agency in agencies:
            self.assertIsNotNone(agency["id"])
            self.assertIsNotNone(agency["name"])

        # Check test agency name
        self.assertIn(TEST_AGENCY_ID, [agency["id"] for agency in agencies])

        mock_get.assert_called_once_with("agencies")

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_list_routes(self, mock_get: MagicMock):
        mock_get.return_value = MOCK_ROUTE_LIST_RESPONSE

        routes = self.client.routes(TEST_AGENCY_ID)

        # Check critical route keys
        for route in routes:
            self.assertIsNotNone(route["id"])
            self.assertIsNotNone(route["title"])

        # Check test route id
        self.assertIn(TEST_ROUTE_ID, [route["id"] for route in routes])

        mock_get.assert_called_once_with(f"agencies/{TEST_AGENCY_ID}/routes")

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_route_details(self, mock_get: MagicMock):
        mock_get.return_value = MOCK_ROUTE_DETAILS_RESPONSE

        route_details = self.client.route_details(
            TEST_ROUTE_ID, agency_id=TEST_AGENCY_ID
        )

        # Check critical route detail keys
        for stop in route_details["stops"]:
            self.assertIsNotNone(stop["id"])
            self.assertIsNotNone(stop["name"])

        for direction in route_details["directions"]:
            self.assertIsNotNone(direction["name"])
            self.assertIsNotNone(direction["useForUi"])
            self.assertIsNotNone(direction["stops"])

        self.assertIn(TEST_STOP_ID, [stop["id"] for stop in route_details["stops"]])

        mock_get.assert_called_once_with(
            f"agencies/{TEST_AGENCY_ID}/routes/{TEST_ROUTE_ID}"
        )

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_predictions_for_stop_no_route(self, mock_get: MagicMock):
        mock_get.return_value = MOCK_PREDICTIONS_RESPONSE_NO_ROUTE

        result = self.client.predictions_for_stop(
            TEST_STOP_ID, agency_id=TEST_AGENCY_ID
        )

        self.assertEqual({r["stop"]["id"] for r in result}, {TEST_STOP_ID})
        self.assertEqual(len(result), 3)  # Results include all routes

        mock_get.assert_called_once_with(
            f"agencies/{TEST_AGENCY_ID}/stops/{TEST_STOP_ID}/predictions",
        )

    @unittest.mock.patch("py_nextbus.client.NextBusClient._get")
    def test_predictions_for_stop_with_route(self, mock_get: MagicMock):
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
        # Assert all predictions are for the correct direction
        self.assertEqual(
            {p["direction"]["id"] for r in result for p in r["values"]},
            {TEST_DIRECTION_ID},
        )
        # Assert we only have the one prediction for the stop and route
        self.assertEqual(len(result), 1)

        mock_get.assert_called_once_with(
            f"agencies/{TEST_AGENCY_ID}/nstops/{TEST_ROUTE_ID}:{TEST_STOP_ID}/predictions",
        )


if __name__ == "__main__":
    unittest.main()
