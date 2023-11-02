from __future__ import annotations

import json
import logging
import urllib.request
from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from typing import Any
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.parse import urlencode

LOG = logging.getLogger()

NEXTBUS_XML_FEED_URL = "https://retro.umoiq.com/service/publicXMLFeed"
NEXTBUS_JSON_FEED_URL = "https://retro.umoiq.com/service/publicJSONFeed"


class ReturnFormat(Enum):
    JSON = "json"
    XML = "xml"


class NextBusHTTPError(HTTPError):
    def __init__(self, message: str, http_err: HTTPError):
        self.__dict__.update(http_err.__dict__)
        self.message = message


class NextBusFormatError(ValueError):
    """Error with parsing a NextBus response."""


class RouteStop(NamedTuple):
    route_tag: str
    stop_tag: str | int

    def __str__(self) -> str:
        return f"{self.route_tag}|{self.stop_tag}"

    @classmethod
    def from_dict(cls, legacy_dict: dict[str, str]) -> RouteStop:
        return cls(legacy_dict["route_tag"], legacy_dict["stop_tag"])


class NextBusClient:
    """Minimalistic client for making requests using the NextBus API.

    This client makes no assumptions about the structure of the data returned by requests to
    NextBus, nor valid values for the query parameters in requests. All response content is returned
    as-is, and no validation is done on query parameters beyond which keys are required.

    All commands in revision 1.23 of the NextBus API are supported."""

    def __init__(
        self,
        output_format: ReturnFormat | str = ReturnFormat.JSON,
        agency: str | None = None,
        use_compression=True,
    ) -> None:
        """Arguments:
        output_format: (ReturnFormat[str]) Indicates the format of the data returned by requests,
            either ReturnFormat.JSON or ReturnFormat.XML.
        agency: (String) Name of a transit agency on NextBus. If an agency is specified for an
            instance of this class, an agency does not have to be provided with every request to
            the NextBus API (Other than the agencyList command).
        use_compression (Boolean) Indicates whether the response data from requests to NextBus
            should be compressed. Defaults to True.
        """

        if isinstance(output_format, str):
            output_format = ReturnFormat(output_format.lower())
        if not isinstance(output_format, ReturnFormat):
            raise TypeError("output_format must be a valid ReturnFormat")

        self.output_format = output_format
        self.agency = agency
        self.use_compression = use_compression

    def get_agency_list(self) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "agencyList" command to get the list of
        transit agencies with predictions on NextBus.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        params = {"command": "agencyList"}

        return self._perform_request(params=params)

    def get_messages(
        self, route_tags: Iterable[str], agency: str | None = None
    ) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "messages" command to get currently active
        messages to display for multiple routes.

        Arguments:
            route_tags: (Iterable of Strings) List of NextBus route tags for the routes to get
                messages for.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if not isinstance(route_tags, Iterable) or isinstance(route_tags, str):
            raise TypeError('"route_tags" must be a Iterable but not a single string.')

        agency = self._get_agency(agency)

        params = {
            "command": "messages",
            # Hacky way of repeating the "r" key in the query string for each route
            "r": "&r=".join(route_tags),
            "a": agency,
        }

        return self._perform_request(params=params)

    def get_route_list(self, agency: str | None = None) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "routeList" command to get a list of routes
        with predictions for a given transit agency.

        Arguments:
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {"command": "routeList", "a": agency}

        return self._perform_request(params=params)

    def get_route_config(
        self, route_tag: str | None = None, agency: str | None = None
    ) -> dict[str, Any] | str:
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
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {"command": "routeConfig", "a": agency}

        if route_tag is not None:
            params["r"] = route_tag

        return self._perform_request(params=params)

    def get_predictions(
        self, stop_tag: str | int, route_tag: str, agency: str | None = None
    ) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "predictions" command to get arrival time
        predictions for a single stop. A route tag can optionally be provided to filter the
        predictions down to only that particular route at the stop.

        Arguments:
            stop_tag: (String) Tag identifying a stop on NextBus.
            route_tag: (String) The NextBus route tag for a route.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            "command": "predictions",
            "a": agency,
            "s": stop_tag,
            "r": route_tag,
        }

        return self._perform_request(params=params)

    def get_predictions_for_multi_stops(
        self, route_stops: Iterable[RouteStop], agency: str | None = None
    ) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "predictionsForMultiStops" command to get
        arrival time predictions for multiple stops.

        Arguments:
            route_stops: (Iterable of RouteStops) Iterable of tuples identifying the combinations of
                routes and stops to get predictions for.
            agency: (String) Name of a transit agency on NextBus. This must be provided if the
                "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if not isinstance(route_stops, Iterable) or isinstance(route_stops, str):
            raise TypeError('"route_stops" must be iterable.')

        agency = self._get_agency(agency)

        params = {
            "command": "predictionsForMultiStops",
            # Hacky way of repeating the "stops" key in the query string for each route
            "stops": "&stops=".join(str(route_stop) for route_stop in route_stops),
            "a": agency,
        }
        return self._perform_request(params=params)

    def get_schedule(
        self, route_tag: str, agency: str | None = None
    ) -> dict[str, Any] | str:
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
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {"command": "schedule", "a": agency, "r": route_tag}

        return self._perform_request(params=params)

    def get_vehicle_locations(
        self, route_tag: str, since_time: datetime, agency: str | None = None
    ) -> dict[str, Any] | str:
        """Make a request to the NextBus API with the "vehicleLocations" command to get the all of
        the vehicles on a route with locations that have changed since a given time.

        Arguments:
            route_tag: (String) The NextBus route tag for a route.
            since_time: (Datetime) Python datetime that only vehicles with
                locations that have changed since this time will be returned.
            agency: (String) Optional name of a transit agency on NextBus. This must be provided if
                the "agency" instance attribute has not been set.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        agency = self._get_agency(agency)

        params = {
            "command": "vehicleLocations",
            "a": agency,
            "r": route_tag,
            "t": since_time.timestamp() * 1000,
        }

        return self._perform_request(params=params)

    def _get_agency(self, agency: str | None) -> str:
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

        agency = agency or self.agency
        if agency is None:
            raise ValueError('"agency" is required.')

        return agency

    def _perform_request(self, params: dict[str, Any]) -> dict[str, Any] | str:
        """Make a request to the NextBus API with given parameters.

        Arguments:
            params: (Dictionary) Query parameters to provide with the request.

        Returns:
            If the output_format is "json": Dictionary containing the JSON returned by the request.
            If the output_format is "xml": String containing the XML returned by the request.

        Raises:
            NextBusHTTPError: If an HTTP error occurs when making the request to the NextBus
                API.
            NextBusFormatError: If the output_format is "json" and the response was not
                valid JSON.
        """

        if self.output_format == ReturnFormat.JSON:
            base_url = NEXTBUS_JSON_FEED_URL
        elif self.output_format == ReturnFormat.XML:
            base_url = NEXTBUS_XML_FEED_URL
        else:
            raise ValueError("Invalid output_format: %s" % self.output_format)

        url = f"{base_url}?{urlencode(params, safe='&=')}"

        headers = {}

        if self.use_compression:
            headers["Accept-Encoding"] = "gzip, deflate"

        request = urllib.request.Request(
            url=url,
            headers=headers,
            method="GET",
        )

        try:
            LOG.debug("Making request to URL %s", url)
            with urllib.request.urlopen(request) as response:
                response_text = response.read()

                if self.output_format == ReturnFormat.JSON:
                    response = json.loads(response_text)
                elif self.output_format == ReturnFormat.XML:
                    response = response_text
                else:
                    raise NextBusFormatError(f"Unexpected format: {self.output_format}")

        except HTTPError as exc:
            raise NextBusHTTPError("Error from the NextBus API", exc) from exc
        except json.decoder.JSONDecodeError as exc:
            raise NextBusFormatError("Failed to parse JSON from request") from exc

        return response
