import unittest
import unittest.mock

import nextbus

@unittest.mock.patch('nextbus.json.loads')
@unittest.mock.patch('nextbus.urllib.request')
class TestPerformRequest(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()