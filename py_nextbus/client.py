from __future__ import annotations

import json
import logging
import re
from time import time
from typing import Any
from typing import cast
from typing import NamedTuple

import requests
from requests.exceptions import HTTPError

LOG = logging.getLogger()


class NextBusError(Exception):
    pass


class NextBusHTTPError(HTTPError, NextBusError):
    def __init__(self, message: str, http_err: HTTPError):
        self.__dict__.update(http_err.__dict__)
        self.message: str = message


class NextBusValidationError(ValueError, NextBusError):
    """Error with missing fields for a NextBus request."""


class NextBusFormatError(ValueError, NextBusError):
    """Error with parsing a NextBus response."""


class NextBusAuthError(NextBusError):
    """Error with authentication to the NextBus API."""


class RouteStop(NamedTuple):
    route_tag: str
    stop_tag: str | int

    def __str__(self) -> str:
        return f"{self.route_tag}|{self.stop_tag}"

    @classmethod
    def from_dict(cls, legacy_dict: dict[str, str]) -> RouteStop:
        return cls(legacy_dict["route_tag"], legacy_dict["stop_tag"])


class NextBusClient:
    base_url: str = "https://api.prd-1.iq.live.umoiq.com/v2.0/riders"

    def __init__(
        self,
        agency_id: str | None = None,
    ) -> None:
        self.agency_id: str | None = agency_id
        self.headers: dict[str, str] = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

    def agencies(self) -> list[dict[str, Any]]:
        result = self._get("agencies")
        return cast(list[dict[str, Any]], result)

    def routes(self, agency_id: str | None = None) -> list[dict[str, Any]]:
        if not agency_id:
            agency_id = self.agency_id

        result = self._get(f"agencies/{agency_id}/routes")
        return cast(list[dict[str, Any]], result)

    def route_details(
        self, route_id: str, agency_id: str | None = None
    ) -> dict[str, Any] | str:
        """Includes stops and directions."""
        agency_id = agency_id or self.agency_id
        if not agency_id:
            raise NextBusValidationError("Agency ID is required")

        result = self._get(f"agencies/{agency_id}/routes/{route_id}")
        return cast(dict[str, Any], result)

    def predictions_for_stop(
        self,
        stop_id: str | int,
        route_id: str | None = None,
        direction_id: str | None = None,
        agency_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Returns predictions for a stop."""
        agency_id = agency_id or self.agency_id
        if not agency_id:
            raise NextBusValidationError("Agency ID is required")

        if direction_id:
            if not route_id:
                raise NextBusValidationError("Direction ID provided without route ID")

        if route_id:
            result = self._get(
                f"agencies/{agency_id}/nstops/{route_id}:{stop_id}/predictions"
            )
        else:
            result = self._get(f"agencies/{agency_id}/stops/{stop_id}/predictions")

        predictions = cast(list[dict[str, Any]], result)

        # If route not provided, return all predictions as the API returned them
        if not route_id:
            return predictions

        # HACK: Filter predictions based on stop and route because the API seems to ignore the route
        predictions = [
            prediction_result
            for prediction_result in predictions
            if (
                prediction_result["stop"]["id"] == stop_id
                and prediction_result["route"]["id"] == route_id
            )
        ]

        # HACK: Filter predictions based on direction in case the API returns extra predictions
        if direction_id:
            for prediction_result in predictions:
                prediction_result["values"] = [
                    prediction
                    for prediction in prediction_result["values"]
                    if prediction["direction"]["id"] == direction_id
                ]

        return predictions

    def _get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if params is None:
            params = {}

        try:
            url = f"{self.base_url}/{endpoint}"
            LOG.debug("GET %s", url)
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as exc:
            raise NextBusHTTPError("Error from the NextBus API", exc) from exc
        except json.decoder.JSONDecodeError as exc:
            raise NextBusFormatError("Failed to parse JSON from request") from exc
