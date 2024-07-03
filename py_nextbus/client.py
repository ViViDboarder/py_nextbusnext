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
API_KEY_RE = re.compile(r"api_key.*key=([a-z0-9]+)")


class NextBusError(Exception):
    pass


class NextBusHTTPError(HTTPError, NextBusError):
    def __init__(self, message: str, http_err: HTTPError):
        self.__dict__.update(http_err.__dict__)
        self.message = message


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
    referer = "https://retro.umoiq.com/"
    base_url = "https://retro.umoiq.com/api/pub/v1"

    def __init__(
        self,
        agency_id: str | None = None,
    ) -> None:
        self.agency_id = agency_id
        self.api_key: str | None = None
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": self.referer,
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
        route_id: str,
        direction_id: str | None = None,
        agency_id: str | None = None,
    ) -> dict[str, Any]:
        agency_id = agency_id or self.agency_id
        if not agency_id:
            raise NextBusValidationError("Agency ID is required")

        params: dict[str, Any] = {"coincident": True}
        if direction_id:
            params["direction"] = direction_id

        result = self._get(
            f"agencies/{agency_id}/routes/{route_id}/stops/{stop_id}/predictions",
            params,
        )
        return cast(dict[str, Any], result)

    def _fetch_api_key(self) -> str:
        response = requests.get(self.referer)
        response.raise_for_status()

        key_search = API_KEY_RE.search(response.text)
        if not key_search:
            raise NextBusValidationError("Could not find API key on page")

        api_key = key_search.group(1)

        return api_key

    def _get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if params is None:
            params = {}
        if not self.api_key:
            self.api_key = self._fetch_api_key()
        params["key"] = self.api_key
        params["timestamp"] = int(time() * 1000)

        try:
            url = f"{self.base_url}/{endpoint}"
            LOG.debug("GET %s", url)
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except HTTPError as exc:
            if exc.response.status_code == 401:
                self.api_key = None

            raise NextBusHTTPError("Error from the NextBus API", exc) from exc
        except json.decoder.JSONDecodeError as exc:
            raise NextBusFormatError("Failed to parse JSON from request") from exc
