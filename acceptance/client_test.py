import unittest

from py_nextbus import NextBusClient

TEST_AGENCY = "sfmta-cis"
TEST_ROUTE = "F"
TEST_STOP = "4513"


class ClientTest(unittest.TestCase):
    client: NextBusClient

    def setUp(self):
        self.client = NextBusClient()

    def test_list_agencies(self):
        agencies = self.client.agencies()

        # Check critical agency keys
        for agency in agencies:
            self.assertIsNotNone(agency["id"])
            self.assertIsNotNone(agency["name"])

        # Check test agency name
        self.assertIn(TEST_AGENCY, [agency["id"] for agency in agencies])

        self.assertGreater(self.client.rate_limit, 0)
        self.assertGreater(self.client.rate_limit_remaining, 0)
        self.assertGreater(self.client.rate_limit_percent, 0)

    def test_list_routes(self):
        routes = self.client.routes(TEST_AGENCY)

        # Check critical route keys
        for route in routes:
            self.assertIsNotNone(route["id"])
            self.assertIsNotNone(route["title"])

        # Check test route id
        self.assertIn(TEST_ROUTE, [route["id"] for route in routes])

    def test_route_details(self):
        route_details = self.client.route_details(TEST_ROUTE, agency_id=TEST_AGENCY)

        # Check critical route detail keys
        for stop in route_details["stops"]:
            self.assertIsNotNone(stop["id"])
            self.assertIsNotNone(stop["name"])

        for direction in route_details["directions"]:
            self.assertIsNotNone(direction["name"])
            self.assertIsNotNone(direction["useForUi"])
            self.assertIsNotNone(direction["stops"])

        self.assertIn(TEST_STOP, [stop["id"] for stop in route_details["stops"]])

    def test_predictions_for_stop(self):
        predictions = self.client.predictions_for_stop(
            TEST_STOP, TEST_ROUTE, agency_id=TEST_AGENCY
        )

        # Check critical prediction keys
        for prediction in predictions:
            self.assertIsNotNone(prediction["stop"]["id"])
            self.assertIsNotNone(prediction["stop"]["name"])
            self.assertIsNotNone(prediction["route"]["id"])
            self.assertIsNotNone(prediction["route"]["title"])

            for value in prediction["values"]:
                self.assertIsNotNone(value["minutes"])
                self.assertIsNotNone(value["timestamp"])
