from __future__ import annotations

import unittest.mock
from datetime import datetime

import py_nextbus.client as client

"""Unit tests for client.py"""
# pylint: disable=unused-argument, protected-access, no-self-use, invalid-name


class TestInit(unittest.TestCase):
    """Tests for the constructor of the NextBusClient class."""

    def test_type_error_raised_if_output_format_is_not_string(self):
        """Test that a TypeError is raised when the value for the output_format argument is not a
        string."""

        with self.assertRaises(TypeError):
            client.NextBusClient(output_format=None)

        with self.assertRaises(TypeError):
            client.NextBusClient(output_format=1)

        with self.assertRaises(TypeError):
            client.NextBusClient(output_format=True)

        with self.assertRaises(TypeError):
            client.NextBusClient(output_format=["json"])

        with self.assertRaises(TypeError):
            client.NextBusClient(output_format={"output_format": "json"})

    def test_value_error_raised_if_output_format_is_not_json_or_xml(self):
        """Test that a ValueError is raised if the value for the output_format argument is a string
        but is neither "json" nor "xml"."""

        with self.assertRaises(ValueError):
            client.NextBusClient(output_format="foo")

    def test_no_exceptions_raised_if_output_format_is_valid(self):
        """Test that no exceptions are raised if the value for the output_format argument is either
        "json" or "xml"."""

        client.NextBusClient(output_format="json")
        client.NextBusClient(output_format="JSON")
        client.NextBusClient(output_format="Json")
        client.NextBusClient(output_format="xml")
        client.NextBusClient(output_format="XML")
        client.NextBusClient(output_format="Xml")
        client.NextBusClient(output_format=client.ReturnFormat.JSON)
        client.NextBusClient(output_format=client.ReturnFormat.XML)

    def test_no_exceptions_raised_if_use_compression_is_boolean(self):
        """Test that no exceptions are raised if the value for the use_compression argument is a
        boolean."""

        client.NextBusClient(
            output_format=client.ReturnFormat.JSON, use_compression=True
        )
        client.NextBusClient(
            output_format=client.ReturnFormat.JSON, use_compression=False
        )

    def test_attributes_set(self):
        """Test that the instance's attributes are set from the passed arguments."""

        output_format = "xml"
        agency = "foo"
        use_compression = False

        nextbus_client = client.NextBusClient(
            output_format=output_format, agency=agency, use_compression=use_compression
        )

        self.assertEqual(nextbus_client.output_format, client.ReturnFormat.XML)
        self.assertEqual(nextbus_client.agency, agency)
        self.assertEqual(nextbus_client.use_compression, use_compression)


@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetAgencyList(unittest.TestCase):
    """Tests for the get_agency_list method in the NextBusClient class."""

    def test_request_made_with_agency_list_command(self, perform_request):
        """Test that _perform_request method is called with the "agencyList" command in the
        parameters."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_agency_list()

        params = perform_request.call_args[1]["params"]
        self.assertIn("command", params)
        self.assertEqual(params["command"], "agencyList")


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetMessages(unittest.TestCase):
    """Tests for the get_messages method in the NextBusClient class."""

    def test_type_error_raised_if_route_tags_not_iterable(
        self, perform_request, get_agency
    ):
        """Test that a TypeError is raised if the value provided for the "route_tags" argument is
        neither a list nor a tuple."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        with self.assertRaises(TypeError):
            nextbus_client.get_messages(route_tags=None)

        with self.assertRaises(TypeError):
            nextbus_client.get_messages(route_tags="foo")

        with self.assertRaises(TypeError):
            nextbus_client.get_messages(route_tags=1)

    def test_type_error_not_raised_if_route_tags_is_iterable(
        self, perform_request, get_agency
    ):
        """Test that a TypeError is not raised if the value provided for the "route_tags" is a tuple
        or a list."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_messages(route_tags=["foo"], agency="bar")
        nextbus_client.get_messages(route_tags=("foo",), agency="bar")
        nextbus_client.get_messages(route_tags=(f for f in ("foo",)), agency="bar")

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        # Test with one route
        nextbus_client.get_messages(route_tags=["foo"], agency=agency)
        perform_request.assert_called_once_with(
            params={"command": "messages", "a": get_agency.return_value, "r": "foo"}
        )
        get_agency.assert_called_once_with(agency)

        perform_request.reset_mock()

        # Test with multiple routes
        nextbus_client.get_messages(route_tags=["foo", "bar"], agency=agency)
        perform_request.assert_called_once_with(
            params={
                "command": "messages",
                "a": get_agency.return_value,
                "r": "foo&r=bar",
            }
        )


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetRouteList(unittest.TestCase):
    """Tests for the get_route_list method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_route_list(agency)

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(
            params={"command": "routeList", "a": get_agency.return_value}
        )


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetRouteConfig(unittest.TestCase):
    """Tests for the get_route_config method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_route_config(agency=agency)

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(
            params={"command": "routeConfig", "a": get_agency.return_value}
        )

    def test_route_added_to_parameters_if_route_tag_not_none(
        self, perform_request, get_agency
    ):
        """Test that the "r" key is added to the parameters passed to the the _perform_request
        method if the value of the route_tag argument is not None."""

        route_tag = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_route_config(route_tag=route_tag)

        params = perform_request.call_args[1]["params"]
        self.assertIn("r", params)
        self.assertEqual(params["r"], route_tag)

    def test_route_not_added_to_parameters_if_route_tag_is_none(
        self, perform_request, get_agency
    ):
        """Test that the "r" key is not added to the parameters passed to the _perform_request
        method if the value of the route_tag argument is None."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_route_config(route_tag=None)

        params = perform_request.call_args[1]["params"]
        self.assertNotIn("r", params)


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetPredictions(unittest.TestCase):
    """Tests for the gtest_error_logged_if_json_decode_error_raisedet_predictions method in the
    NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        stop_tag = 12345
        route_tag = "foo"
        agency = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_predictions(
            stop_tag=stop_tag, route_tag=route_tag, agency=agency
        )

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(
            params={
                "command": "predictions",
                "a": get_agency.return_value,
                "s": stop_tag,
                "r": route_tag,
            }
        )


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetPredictionsForMultiStops(unittest.TestCase):
    """Tests for the get_predictions_for_multi_stops method in the NextBusClient class."""

    def test_type_error_raised_if_stops_is_not_iterable(
        self, perform_request, get_agency
    ):
        """Test that a TypeError is raised if the value for the "stops" argument is neither a list
        nor a tuple."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops={})

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops=set())

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops=None)

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops=True)

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops="foo")

        with self.assertRaises(TypeError):
            nextbus_client.get_predictions_for_multi_stops(route_stops=1)

    def test_no_exceptions_raised_if_stops_is_valid(self, perform_request, get_agency):
        """Test that no exceptions are raised if the value for the "stops" argument is either a list
        or a tuple containing dictionaries with the required keys."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        nextbus_client.get_predictions_for_multi_stops(
            route_stops=[
                client.RouteStop("foo", 1234),
                client.RouteStop("foo", "1234"),
            ]
        )

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        # Test with only one stop
        stop_tag = 1234
        route_tag = "bar"
        nextbus_client.get_predictions_for_multi_stops(
            agency=agency, route_stops=[client.RouteStop(route_tag, stop_tag)]
        )

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(
            params={
                "command": "predictionsForMultiStops",
                "a": get_agency.return_value,
                "stops": "{}|{}".format(route_tag, stop_tag),
            }
        )

        perform_request.reset_mock()

        # Test with multiple stops
        first_stop_tag = 1234
        first_route_tag = "baz"
        second_stop_tag = 5678
        second_route_tag = "buz"
        nextbus_client.get_predictions_for_multi_stops(
            agency=agency,
            route_stops=[
                client.RouteStop(first_route_tag, first_stop_tag),
                client.RouteStop(second_route_tag, second_stop_tag),
            ],
        )

        perform_request.assert_called_once_with(
            params={
                "command": "predictionsForMultiStops",
                "a": get_agency.return_value,
                "stops": "{}|{}&stops={}|{}".format(
                    first_route_tag, first_stop_tag, second_route_tag, second_stop_tag
                ),
            }
        )


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetSchedule(unittest.TestCase):
    """Tests for the get_schedule method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        route_tag = "foo"
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_schedule(route_tag=route_tag)

        perform_request.assert_called_once_with(
            params={"command": "schedule", "a": get_agency.return_value, "r": route_tag}
        )


@unittest.mock.patch("py_nextbus.client.NextBusClient._get_agency")
@unittest.mock.patch("py_nextbus.client.NextBusClient._perform_request")
class TestGetVehicleLocations(unittest.TestCase):
    """Tests for the get_vehicle_locations method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        route_tag = "foo"
        now = datetime.now()
        now_ms = now.timestamp() * 1000
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.get_vehicle_locations(route_tag=route_tag, since_time=now)

        perform_request.assert_called_once_with(
            params={
                "command": "vehicleLocations",
                "a": get_agency.return_value,
                "r": route_tag,
                "t": now_ms,
            }
        )


class TestGetAgency(unittest.TestCase):
    """Tests for the _get_agency method in the NextBusClient class."""

    def test_agency_argument_returned_if_not_none(self):
        """Test that the value of the "agency" argument is returned if it is not None."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)

        agency = "foo"
        nextbus_client.agency = "bar"

        response = nextbus_client._get_agency(agency)

        assert response == agency

    def test_agency_attribute_returned_if_not_none_and_agency_argument_is_none(self):
        """Test that the value of the NextBusClient instance's "agency" atrribute is returned if it
        is not None and the value of the "agency" argument is None."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.agency = "foo"

        response = nextbus_client._get_agency(None)

        assert response == nextbus_client.agency

    def test_value_error_raised_if_agency_argument_and_agency_attribute_are_none(self):
        """Test that a ValueError is raised if both the "agency" argument and the NextBusClient
        instance's "agency" attribute are None."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.agency = None

        with self.assertRaises(ValueError):
            nextbus_client._get_agency(None)


@unittest.mock.patch("py_nextbus.client.json.loads")
@unittest.mock.patch("py_nextbus.client.urllib.request")
class TestPerformRequest(unittest.TestCase):
    """Tests for the _perform_request method in the NextBusClient class."""

    def test_json_output_format_makes_request_to_nextbus_json_feed(
        self, request, loads
    ):
        """Test that requests made to the NextBus API when the instance's output_format is "json"
        are made to the NextBus public JSON feed."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client._perform_request(params={})

        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]["url"]
        assert request_url.startswith(client.NEXTBUS_JSON_FEED_URL)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_xml_output_format_makes_request_to_nextbus_xml_feed(self, request, loads):
        """Test that requests made to the NextBus API when the instance's output_format is "xml"
        are made to the NextBus public XML feed."""

        nextbus_client = client.NextBusClient(output_format="xml")
        nextbus_client._perform_request(params={})

        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]["url"]
        assert request_url.startswith(client.NEXTBUS_XML_FEED_URL)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_value_error_raised_if_output_format_is_not_json_or_xml(
        self, request, loads
    ):
        """Test that a ValueError is raised when the instance's output_format is neither "xml" nor
        "json"."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client.output_format = "foo"

        with self.assertRaises(ValueError):
            nextbus_client._perform_request(params={})

    @unittest.mock.patch("py_nextbus.client.urlencode")
    def test_parameters_added_to_url_as_query_string(self, urlencode, request, loads):
        """Test that the provided parameters are converted to a query string and added to the URL
        used for making a request to the NextBus API."""

        params = unittest.mock.MagicMock()
        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        nextbus_client._perform_request(params=params)

        urlencode.assert_called_once_with(params, safe="&=")
        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]["url"]
        assert request_url.endswith("?%s" % urlencode.return_value)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_accept_encoding_header_in_request_if_use_compression_is_true(
        self, request, loads
    ):
        """Test that the Accept-Encoding header is present in the request to the NextBus API if the
        use_compression attribute is True."""

        nextbus_client = client.NextBusClient(
            output_format=client.ReturnFormat.JSON, use_compression=True
        )
        nextbus_client._perform_request(params={})

        headers = request.Request.call_args[1]["headers"]
        self.assertIn("Accept-Encoding", headers)
        self.assertEqual(headers["Accept-Encoding"], "gzip, deflate")

    def test_accept_encoding_header_not_in_request_if_use_compression_is_false(
        self, request, loads
    ):
        """Test that the Accept-Encoding header is not present in the request to the NextBus API if
        the use_compression attribute is False."""

        nextbus_client = client.NextBusClient(
            output_format=client.ReturnFormat.JSON, use_compression=False
        )
        nextbus_client._perform_request(params={})

        headers = request.Request.call_args[1]["headers"]
        self.assertNotIn("Accept-Encoding", headers)

    def test_response_returned_as_dictionary_if_output_format_is_json(
        self, request, loads
    ):
        """Test that the response from the NextBus API is loaded as JSON and returned as a
        dictionary if the output_format is "json"."""

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        response = nextbus_client._perform_request(params={})

        loads.assert_called_once_with(
            request.urlopen.return_value.__enter__.return_value.read.return_value
        )
        self.assertEqual(response, loads.return_value)

    def test_response_returned_as_string_if_output_format_is_xml(self, request, loads):
        """Test that the response from the NextBus API is directly returned if the output_format is
        "xml"."""

        nextbus_client = client.NextBusClient(output_format="xml")
        response = nextbus_client._perform_request(params={})

        self.assertEqual(
            response,
            request.urlopen.return_value.__enter__.return_value.read.return_value,
        )

    @unittest.mock.patch("py_nextbus.client.LOG")
    def test_error_raised_if_http_error_raised(self, log, request, loads):
        """Test that an error is logged if a urllib HTTPError is raised when making the request to
        the NextBus API."""

        request.urlopen.side_effect = client.urllib.error.HTTPError(
            url="foo", code=500, msg="bar", hdrs={}, fp=unittest.mock.MagicMock()
        )

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        with self.assertRaises(client.NextBusHTTPError):
            nextbus_client._perform_request(params={})

    @unittest.mock.patch("py_nextbus.client.LOG")
    def test_error_raised_if_json_decode_error_raised(self, log, request, loads):
        """Test that an error is logged if a JSONDecodeError is raised when making the request to
        the NextBus API."""

        request.urlopen.side_effect = client.json.decoder.JSONDecodeError(
            msg="foo", doc="bar", pos=0
        )

        nextbus_client = client.NextBusClient(output_format=client.ReturnFormat.JSON)
        with self.assertRaises(client.NextBusFormatError):
            nextbus_client._perform_request(params={})


if __name__ == "__main__":
    unittest.main()
