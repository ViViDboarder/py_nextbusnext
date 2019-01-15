import json
import logging
import urllib.error
import urllib.parse
import urllib.request

LOG = logging.getLogger()

NEXTBUS_XML_FEED_URL = 'http://webservices.nextbus.com/service/publicXMLFeed'
NEXTBUS_JSON_FEED_URL = 'http://webservices.nextbus.com/service/publicJSONFeed'

class NextBusClient():
    """Minimalistic client for making requests using the NextBus API.

    This client makes no assumptions about the structure of the data returned by requests to
    NextBus, nor valid values for the query parameters in requests. All response content is returned
    as-is, and no validation is done on query parameters beyond which keys are required.

    All commands in revision 1.23 of the NextBus API are supported."""

    def __init__(self, output_format, agency=None, use_compression=True):
        """Arguments:
            output_format: (String) Indicates the format of the data returned by requests, either
                "json" or "xml".
            agency: (String) Name of a transit agency on NextBus. If an agency is specified for an
                instance of this class, an agency does not have to be provided with every request to
                the NextBus API (Other than the agencyList command).
            use_compression (Boolean) Indicates whether the response data from requests to NextBus
                should be compressed.
        """

        if not isinstance(output_format, str):
            raise TypeError('"output_format" must be a string.')

        if output_format.lower() not in ['json', 'xml']:
            raise ValueError('"output_format" must be either "json" or "xml".')

        if not isinstance(use_compression, bool):
            raise TypeError('"use_compression" must be a boolean.')

        self.output_format = output_format.lower()
        self.agency = agency
        self.use_compression = use_compression

    def get_agency_list(self):
        """Make a request to the NextBus API with the "agencyList" command to get the list of
        transit agencies with predictions on NextBus.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        params = {
            'command': 'agencyList'
        }

        return self._perform_request(params=params)

    def get_messages(self, route_tags, agency=None):
        """Make a request to the NextBus API with the "messages" command to get currently active
        messages to display for multiple routes.

        Arguments:
            route_tags: (List or tuple) List of NextBus route tags for the routes to get messages
                for.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if not isinstance(route_tags, list) and not isinstance(route_tags, tuple):
            raise TypeError('"route_tags" must be a list or tuple.')

        agency = self._get_agency(agency)

        params = {
            'command': 'messages',
            # Hacky way of repeating the "r" key in the query string for each route
            'r': '&r='.join(route_tags),
            'a': agency
        }

        return self._perform_request(params=params)

    def get_route_list(self, agency=None):
        """Make a request to the NextBus API with the "routeList" command to get a list of routes
        with predictions for a given transit agency.

        Arguments:
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            'command': 'routeList',
            'a': agency
        }

        return self._perform_request(params=params)

    def get_route_config(self, route_tag=None, agency=None):
        """Make a request to the NextBus API with the "routeConfig" command to get the details of a
        single route, including all stops, and latitude and longitude of the route's path.

        Arguments:
            route_tag: (String) The NextBus route tag for a route. If this is None, the route
                configuration for all routes will be returned.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            'command': 'routeConfig',
            'a': agency
        }

        if route_tag is not None:
            params['r'] = route_tag

        return self._perform_request(params=params)

    def get_predictions(self, stop_tag, route_tag, agency=None):
        """Make a request to the NextBus API with the "predictions" command to get arrival time
        predictions for a single stop. A route tag can optionally be provided to filter the
        predictions down to only that particular route at the stop.

        Arguments:
            stop_tag: (String) Tag identifying a stop on NextBus.
            route_tag: (String) The NextBus route tag for a route. If this is None, predictions for
                all routes that serve the given stop will be returned.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            'command': 'predictions',
            'a': agency,
            's': stop_tag,
            'r': route_tag,
        }

        return self._perform_request(params=params)

    def get_predictions_for_multi_stops(self, stops, agency=None):
        """Make a request to the NextBus API with the "predictionsForMultiStops" command to get
        arrival time predictions for multiple stops.

        Arguments:
            stops: (List or tuple) List or tuple of dictionaries identifying the combinations of
                routes and stops to get predictions for. Each dictionary must contain the keys
                "stop_tag" and "route_tag", indicating each stop to get predictions for, and the
                route to get predictions for at that stop, respectively.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if not isinstance(stops, list) and not isinstance(stops, tuple):
            raise TypeError('"stops" must be a list or a tuple.')

        for stop in stops:
            if not isinstance(stop, dict) or 'route_tag' not in stop or 'stop_tag' not in stop:
                raise ValueError('"stops" must contain dictionaries with the "route_tag" and ' \
                                 '"stop_tag" keys')

        agency = self._get_agency(agency)

        params = {
            'command': 'predictionsForMultiStops',
            # Hacky way of repeating the "stops" key in the query string for each route
            'stops': '&stops='.join(['%s|%d' % (stop['route_tag'],
                                                stop['stop_tag']) for stop in stops]),
            'a': agency
        }
        return self._perform_request(params=params)

    def get_schedule(self, route_tag, agency=None):
        """Make a request to the NextBus API with the "schedule" command to get the schedule for a
        single route.

        Arguments:
            route_tag: (String) The NextBus route tag for a route.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            'command': 'schedule',
            'a': agency,
            'r': route_tag
        }

        return self._perform_request(params=params)

    def get_vehicle_locations(self, route_tag, timestamp, agency=None):
        """Make a request to the NextBus API with the "vehicleLocations" command to get the all of
        the vehicles on a route with locations that have changed since a given time.

        Arguments:
            route_tag: (String) The NextBus route tag for a route.
            timestamp: (Integer) Unix timestamp in milliseconds indicating that only vehicles with
                locations that have changed since this time will be returned.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            'command': 'vehicleLocations',
            'a': agency,
            'r': route_tag,
            't': timestamp
        }

        return self._perform_request(params=params)

    def _get_agency(self, agency):
        """Get the agency name from either the provided argument or "agency" instance attribute.

        Args:
            agency: Name of a transit agency on NextBus.

        Returns:
            The value of the "agency" argument if it is not None, or the value of the instance's
            "agency" atrribute if that is not None.

        Raises:
            ValueError: If both the value of the "agency" argument and this instance's "agency"
                atrribute are None.
        """

        if agency is None:
            if self.agency is None:
                raise ValueError('"agency" is required.')
            else:
                return self.agency
        else:
            return agency

    def _perform_request(self, params):
        """Make a request to the NextBus API with given parameters.

        Arguments:
            params: (Dictionary) Query parameters to provide with the request.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            urllib.error.HTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            json.decoder.JSONDecodeError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if self.output_format == 'json':
            base_url = NEXTBUS_JSON_FEED_URL
        elif self.output_format == 'xml':
            base_url = NEXTBUS_XML_FEED_URL
        else:
            raise ValueError('Invalid output_format: %s' % self.output_format)

        url = '%s?%s' % (base_url, urllib.parse.urlencode(params, safe='&='))

        headers = {}

        if self.use_compression:
            headers['Accept-Encoding'] = 'gzip, deflate'

        request = urllib.request.Request(url=url,
                                         headers=headers,
                                         method='GET')

        try:
            LOG.info('Making request to URL %s', url)
            with urllib.request.urlopen(request) as response:
                response_text = response.read()

                if self.output_format == 'json':
                    response = json.loads(response_text)
                elif self.output_format == 'xml':
                    response = response_text

        except urllib.error.HTTPError as exc:
            LOG.error('Request returned status %s due to reason: %s', exc.code, exc.reason)
            raise exc
        except json.decoder.JSONDecodeError as exc:
            LOG.error('Request did not return valid JSON. %s', exc)
            raise exc
        else:
            return response
