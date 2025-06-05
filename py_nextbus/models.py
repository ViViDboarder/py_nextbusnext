from typing import TypedDict


class AgencyInfo(TypedDict):
    id: str
    name: str
    shortName: str
    region: str
    website: str
    logo: str
    nxbs2RedirectUrl: str


class PredictionRouteInfo(TypedDict):
    id: str
    title: str
    description: str
    color: str
    textColor: str
    hidden: bool


class RouteInfo(PredictionRouteInfo):
    rev: int
    timestamp: str


class RouteBoundingBox(TypedDict):
    latMin: float
    latMax: float
    lonMin: float
    lonMax: float


class StopInfo(TypedDict):
    id: str
    lat: float
    lon: float
    name: str
    code: str
    hidden: bool
    showDestinationSelector: bool
    directions: list[str]


class PredictionStopInfo(TypedDict):
    id: str
    lat: float
    lon: float
    name: str
    code: str
    hidden: bool
    showDestinationSelector: bool
    route: str


class Point(TypedDict):
    lat: float
    lon: float


class RoutePath(TypedDict):
    id: str
    points: list[Point]


class DirectionInfo(TypedDict):
    id: str
    shortName: str
    name: str
    useForUi: bool
    stops: list[str]


class RouteDetails(TypedDict):
    id: str
    rev: int
    title: str
    description: str
    color: str
    textColor: str
    hidden: bool
    boundingBox: RouteBoundingBox
    stops: list[StopInfo]
    directions: list[DirectionInfo]
    paths: list[RoutePath]
    timestamp: str


class PredictionDirection(TypedDict):
    id: str
    name: str
    destinationName: str


class PredictionValue(TypedDict):
    timestamp: int
    minutes: int
    affectedByLayover: bool
    isDeparture: bool
    occupancyStatus: int
    occupancyDescription: str
    vehiclesInConsist: int
    linkedVehicleIds: str
    vehicleId: str
    vehicleType: str | None
    direction: PredictionDirection
    tripId: str
    delay: int
    predUsingNavigationTm: bool
    departure: bool


class StopPrediction(TypedDict):
    serverTimestamp: int
    nxbs2RedirectUrl: str
    route: PredictionRouteInfo
    stop: PredictionStopInfo
    values: list[PredictionValue]
