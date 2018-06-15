"""Unit tests for nextbus.py"""

# pylint: disable=unused-argument, protected-access, no-self-use, invalid-name

import unittest
import unittest.mock

import nextbus

class TestInit(unittest.TestCase):
    """Tests for the constructor of the NextBusClient class."""

    def test_type_error_raised_if_output_format_is_not_string(self):
        """Test that a TypeError is raised when the value for the output_format argument is not a
        string."""

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format=None)

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format=1)

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format=True)

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format=['json'])

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format={'output_format': 'json'})

    def test_value_error_raised_if_output_format_is_not_json_or_xml(self):
        """Test that a ValueError is raised if the value for the output_format argument is a string
        but is neither "json" nor "xml"."""

        with self.assertRaises(ValueError):
            nextbus.NextBusClient(output_format='foo')

    def test_no_exceptions_raised_if_output_format_is_valid(self):
        """Test that no exceptions are raised if the value for the output_format argument is either
        "json" or "xml"."""

        nextbus.NextBusClient(output_format='json')
        nextbus.NextBusClient(output_format='JSON')
        nextbus.NextBusClient(output_format='Json')
        nextbus.NextBusClient(output_format='xml')
        nextbus.NextBusClient(output_format='XML')
        nextbus.NextBusClient(output_format='Xml')

    def test_type_error_raised_if_use_compression_is_not_boolean(self):
        """Test that a TypeError is raised if the value for the use_compression argument is not a
        boolean."""

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format='json',
                                  use_compression='True')

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format='json',
                                  use_compression=1)

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format='json',
                                  use_compression=None)

        with self.assertRaises(TypeError):
            nextbus.NextBusClient(output_format='json',
                                  use_compression=[True])

    def test_no_exceptions_raised_if_use_compression_is_boolean(self):
        """Test that no exceptions are raised if the value for the use_compression argument is a
        boolean."""

        nextbus.NextBusClient(output_format='json',
                              use_compression=True)
        nextbus.NextBusClient(output_format='json',
                              use_compression=False)

    def test_attributes_set(self):
        """Test that the instance's attributes are set from the passed arguments."""

        output_format = 'xml'
        agency = 'foo'
        use_compression = False

        client = nextbus.NextBusClient(output_format=output_format,
                                       agency=agency,
                                       use_compression=use_compression)

        self.assertEqual(client.output_format, output_format)
        self.assertEqual(client.agency, agency)
        self.assertEqual(client.use_compression, use_compression)

@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetAgencyList(unittest.TestCase):
    """Tests for the get_agency_list method in the NextBusClient class."""

    def test_request_made_with_agency_list_command(self, perform_request):
        """Test that _perform_request method is called with the "agencyList" command in the
        parameters."""

        client = nextbus.NextBusClient(output_format='json')
        client.get_agency_list()

        params = perform_request.call_args[1]['params']
        self.assertIn('command', params)
        self.assertEqual(params['command'], 'agencyList')

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetMessages(unittest.TestCase):
    """Tests for the get_messages method in the NextBusClient class."""

    def test_type_error_raised_if_route_tags_not_list_or_tuple(self, perform_request, get_agency):
        """Test that a TypeError is raised if the value provided for the "route_tags" argument is
        neither a list nor a tuple."""

        client = nextbus.NextBusClient(output_format='json')

        with self.assertRaises(TypeError):
            client.get_messages(route_tags={})

        with self.assertRaises(TypeError):
            client.get_messages(route_tags=None)

        with self.assertRaises(TypeError):
            client.get_messages(route_tags='foo')

        with self.assertRaises(TypeError):
            client.get_messages(route_tags=1)

        with self.assertRaises(TypeError):
            client.get_messages(route_tags=set())

    def test_type_error_not_raised_if_route_tags_is_list_or_tuple(
            self, perform_request, get_agency):
        """Test that a TypeError is not raised if the value provided for the "route_tags" is a tuple
        or a list."""

        client = nextbus.NextBusClient(output_format='json')
        client.get_messages(route_tags=['foo'],
                            agency='bar')
        client.get_messages(route_tags=('foo',),
                            agency='bar')

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = 'foo'
        client = nextbus.NextBusClient(output_format='json')

        # Test with one route
        client.get_messages(route_tags=['foo'],
                            agency=agency)
        perform_request.assert_called_once_with(params={
            'command': 'messages',
            'a': get_agency.return_value,
            'r': 'foo'
        })
        get_agency.assert_called_once_with(agency)

        perform_request.reset_mock()

        # Test with multiple routes
        client.get_messages(route_tags=['foo', 'bar'],
                            agency=agency)
        perform_request.assert_called_once_with(params={
            'command': 'messages',
            'a': get_agency.return_value,
            'r': 'foo&r=bar'
        })

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetRouteList(unittest.TestCase):
    """Tests for the get_route_list method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_route_list(agency)

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(params={
            'command': 'routeList',
            'a': get_agency.return_value
        })

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetRouteConfig(unittest.TestCase):
    """Tests for the get_route_config method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_route_config(agency=agency)

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(params={
            'command': 'routeConfig',
            'a': get_agency.return_value
        })

    def test_route_added_to_parameters_if_route_tag_not_none(self, perform_request, get_agency):
        """Test that the "r" key is added to the parameters passed to the the _perform_request
        method if the value of the route_tag argument is not None."""

        route_tag = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_route_config(route_tag=route_tag)

        params = perform_request.call_args[1]['params']
        self.assertIn('r', params)
        self.assertEqual(params['r'], route_tag)

    def test_route_not_added_to_parameters_if_route_tag_is_none(self, perform_request, get_agency):
        """Test that the "r" key is not added to the parameters passed to the _perform_request
        method if the value of the route_tag argument is None."""

        client = nextbus.NextBusClient(output_format='json')
        client.get_route_config(route_tag=None)

        params = perform_request.call_args[1]['params']
        self.assertNotIn('r', params)

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetPredictions(unittest.TestCase):
    """Tests for the get_predictions method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        stop_id = 12345
        agency = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_predictions(stop_id=stop_id,
                               agency=agency)

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(params={
            'command': 'predictions',
            'a': get_agency.return_value,
            'stopId': stop_id
        })

    def test_route_tag_added_to_parameters_if_not_none(self, perform_request, get_agency):
        """Test that the "routeTag" key is added to the parameters passed to the the
        _perform_request method if the value of the route_tag argument is not None."""

        route_tag = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_predictions(stop_id=12345,
                               route_tag=route_tag)

        params = perform_request.call_args[1]['params']
        self.assertIn('routeTag', params)
        self.assertEqual(params['routeTag'], route_tag)

    def test_route_tag_not_added_to_parameters_if_none(self, perform_request, get_agency):
        """Test that the "routeTag" key is not added to the parameters passed to the
        _perform_request method if the value of the route_tag argument is None."""

        client = nextbus.NextBusClient(output_format='json')
        client.get_predictions(stop_id=12345,
                               route_tag=None)

        params = perform_request.call_args[1]['params']
        self.assertNotIn('routeTag', params)

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetPredictionsForMultiStops(unittest.TestCase):
    """Tests for the get_predictions_for_multi_stops method in the NextBusClient class."""

    def test_type_error_raised_if_stops_is_not_list_or_tuple(self, perform_request, get_agency):
        """Test that a TypeError is raised if the value for the "stops" argument is neither a list
        nor a tuple."""

        client = nextbus.NextBusClient(output_format='json')

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops={})

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops=set())

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops=None)

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops=True)

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops='foo')

        with self.assertRaises(TypeError):
            client.get_predictions_for_multi_stops(stops=1)

    def test_value_error_raised_if_stops_does_not_contain_dictionaries_with_required_keys(
            self, perform_request, get_agency):
        """Test that a ValueError is raised if the value for the "stops" argument is a list or a
        tuple but does not contain dictionaries with the required keys."""

        client = nextbus.NextBusClient(output_format='json')

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=['foo'])

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=[1])

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=[['foo']])

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=[{}])

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=[{
                'stop_id': 1234
            }])
        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=[{
                'route_tag': 'foo'
            }])
        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(
                stops=[
                    {
                        'stop_id': 1234,
                        'route_tag': 'foo'
                    },
                    None
                ]
            )
        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=('foo',))

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=(1,))

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=(('foo'),))

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=({},))

        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=({
                'stop_id': 1234
            },))
        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(stops=({
                'route_tag': 'foo'
            },))
        with self.assertRaises(ValueError):
            client.get_predictions_for_multi_stops(
                stops=(
                    {
                        'stop_id': 1234,
                        'route_tag': 'foo'
                    },
                    None
                )
            )

    def test_no_exceptions_raised_if_stops_is_valid(self, perform_request, get_agency):
        """Test that no exceptions are raised if the value for the "stops" argument is either a list
        or a tuple containing dictionaries with the required keys."""

        client = nextbus.NextBusClient(output_format='json')

        client.get_predictions_for_multi_stops(stops=[{
            'route_tag': 'foo',
            'stop_id': 1234
        }])

        client.get_predictions_for_multi_stops(stops=({
            'route_tag': 'foo',
            'stop_id': 1234
        },))

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        agency = 'foo'
        client = nextbus.NextBusClient(output_format='json')

        # Test with only one stop
        stop_id = 1234
        route_tag = 'bar'
        client.get_predictions_for_multi_stops(
            agency=agency,
            stops=[{
                'route_tag': route_tag,
                'stop_id': stop_id
            }]
        )

        get_agency.assert_called_once_with(agency)
        perform_request.assert_called_once_with(params={
            'command': 'predictionsForMultiStops',
            'a': get_agency.return_value,
            'stops': '%s|%s' % (route_tag, stop_id)
        })

        perform_request.reset_mock()

        # Test with multiple stops
        first_stop_id = 1234
        first_route_tag = 'baz'
        second_stop_id = 5678
        second_route_tag = 'buz'
        client.get_predictions_for_multi_stops(
            agency=agency,
            stops=[
                {
                    'route_tag': first_route_tag,
                    'stop_id': first_stop_id
                },
                {
                    'route_tag': second_route_tag,
                    'stop_id': second_stop_id
                }
            ]
        )

        perform_request.assert_called_once_with(params={
            'command': 'predictionsForMultiStops',
            'a': get_agency.return_value,
            'stops': '%s|%s&stops=%s|%s' % (first_route_tag, first_stop_id, second_route_tag,
                                            second_stop_id)
        })

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetSchedule(unittest.TestCase):
    """Tests for the get_schedule method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        route_tag = 'foo'
        client = nextbus.NextBusClient(output_format='json')
        client.get_schedule(route_tag=route_tag)

        perform_request.assert_called_once_with(params={
            'command': 'schedule',
            'a': get_agency.return_value,
            'r': route_tag
        })

@unittest.mock.patch('nextbus.NextBusClient._get_agency')
@unittest.mock.patch('nextbus.NextBusClient._perform_request')
class TestGetVehicleLocations(unittest.TestCase):
    """Tests for the get_vehicle_locations method in the NextBusClient class."""

    def test_parameters_passed_to_perform_request(self, perform_request, get_agency):
        """Test that the correct parameters are passed to the _perform_request method."""

        route_tag = 'foo'
        timestamp = 12345
        client = nextbus.NextBusClient(output_format='json')
        client.get_vehicle_locations(route_tag=route_tag,
                                     timestamp=timestamp)

        perform_request.assert_called_once_with(params={
            'command': 'vehicleLocations',
            'a': get_agency.return_value,
            'r': route_tag,
            't': timestamp
        })

class TestGetAgency(unittest.TestCase):
    """Tests for the _get_agency method in the NextBusClient class."""

    def test_agency_argument_returned_if_not_none(self):
        """Test that the value of the "agency" argument is returned if it is not None."""

        client = nextbus.NextBusClient(output_format='json')

        agency = 'foo'
        client.agency = 'bar'

        response = client._get_agency(agency)

        assert response == agency

    def test_agency_attribute_returned_if_not_none_and_agency_argument_is_none(self):
        """Test that the value of the NextBusClient instance's "agency" atrribute is returned if it
        is not None and the value of the "agency" argument is None."""

        client = nextbus.NextBusClient(output_format='json')
        client.agency = 'foo'

        response = client._get_agency(None)

        assert response == client.agency

    def test_value_error_raised_if_agency_argument_and_agency_attribute_are_none(self):
        """Test that a ValueError is raised if both the "agency" argument and the NextBusClient
        instance's "agency" attribute are None."""

        client = nextbus.NextBusClient(output_format='json')
        client.agency = None

        with self.assertRaises(ValueError):
            client._get_agency(None)

@unittest.mock.patch('nextbus.json.loads')
@unittest.mock.patch('nextbus.urllib.request')
class TestPerformRequest(unittest.TestCase):
    """Tests for the _perform_request method in the NextBusClient class."""

    def test_json_output_format_makes_request_to_nextbus_json_feed(self, request, loads):
        """Test that requests made to the NextBus API when the instance's output_format is "json"
        are made to the NextBus public JSON feed."""

        client = nextbus.NextBusClient(output_format='json')
        client._perform_request(params={})

        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]['url']
        assert request_url.startswith(nextbus.NEXTBUS_JSON_FEED_URL)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_xml_output_format_makes_request_to_nextbus_xml_feed(self, request, loads):
        """Test that requests made to the NextBus API when the instance's output_format is "xml"
        are made to the NextBus public XML feed."""

        client = nextbus.NextBusClient(output_format='xml')
        client._perform_request(params={})

        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]['url']
        assert request_url.startswith(nextbus.NEXTBUS_XML_FEED_URL)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_value_error_raised_if_output_format_is_not_json_or_xml(self, request, loads):
        """Test that a ValueError is raised when the instance's output_format is neither "xml" nor
        "json"."""

        client = nextbus.NextBusClient(output_format='json')
        client.output_format = 'foo'

        with self.assertRaises(ValueError):
            client._perform_request(params={})

    @unittest.mock.patch('nextbus.urllib.parse.urlencode')
    def test_parameters_added_to_url_as_query_string(self, urlencode, request, loads):
        """Test that the provided parameters are converted to a query string and added to the URL
        used for making a request to the NextBus API."""

        params = unittest.mock.MagicMock()
        client = nextbus.NextBusClient(output_format='json')
        client._perform_request(params=params)

        urlencode.assert_called_once_with(params)
        # Get the URL of the request to the NextBus API
        request_url = request.Request.call_args[1]['url']
        assert request_url.endswith('?%s' % urlencode.return_value)
        request.urlopen.assert_called_once_with(request.Request.return_value)

    def test_accept_encoding_header_in_request_if_use_compression_is_true(self, request, loads):
        """Test that the Accept-Encoding header is present in the request to the NextBus API if the
        use_compression attribute is True."""

        client = nextbus.NextBusClient(output_format='json',
                                       use_compression=True)
        client._perform_request(params={})

        headers = request.Request.call_args[1]['headers']
        self.assertIn('Accept-Encoding', headers)
        self.assertEqual(headers['Accept-Encoding'], 'gzip, deflate')

    def test_accept_encoding_header_not_in_request_if_use_compression_is_false(
            self, request, loads):
        """Test that the Accept-Encoding header is not present in the request to the NextBus API if
        the use_compression attribute is False."""

        client = nextbus.NextBusClient(output_format='json',
                                       use_compression=False)
        client._perform_request(params={})

        headers = request.Request.call_args[1]['headers']
        self.assertNotIn('Accept-Encoding', headers)

    def test_response_returned_as_dictionary_if_output_format_is_json(self, request, loads):
        """Test that the response from the NextBus API is loaded as JSON and returned as a
        dictionary if the output_format is "json"."""

        client = nextbus.NextBusClient(output_format='json')
        response = client._perform_request(params={})

        loads.assert_called_once_with(
            request.urlopen.return_value.__enter__.return_value.read.return_value
        )
        self.assertEqual(response, loads.return_value)

    def test_response_returned_as_string_if_output_format_is_xml(self, request, loads):
        """Test that the response from the NextBus API is directly returned if the output_format is
        "xml"."""

        client = nextbus.NextBusClient(output_format='xml')
        response = client._perform_request(params={})

        self.assertEqual(response,
                         request.urlopen.return_value.__enter__.return_value.read.return_value)

    @unittest.mock.patch('nextbus.LOG')
    def test_error_logged_if_http_error_raised(self, log, request, loads):
        """Test that an error is logged if a urllib HTTPError is raised when making the request to
        the NextBus API."""

        request.urlopen.side_effect = nextbus.urllib.error.HTTPError(url='foo',
                                                                     code=500,
                                                                     msg='bar',
                                                                     hdrs={},
                                                                     fp=unittest.mock.MagicMock())

        client = nextbus.NextBusClient(output_format='json')
        with self.assertRaises(nextbus.urllib.error.HTTPError):
            client._perform_request(params={})

        log.error.assert_called_once()

    @unittest.mock.patch('nextbus.LOG')
    def test_error_logged_if_json_decode_error_raised(self, log, request, loads):
        """Test that an error is logged if a JSONDecodeError is raised when making the request to
        the NextBus API."""

        request.urlopen.side_effect = nextbus.json.decoder.JSONDecodeError(msg='foo',
                                                                           doc='bar',
                                                                           pos=0)

        client = nextbus.NextBusClient(output_format='json')
        with self.assertRaises(nextbus.json.decoder.JSONDecodeError):
            client._perform_request(params={})

        log.error.assert_called_once()

if __name__ == '__main__':
    unittest.main()
