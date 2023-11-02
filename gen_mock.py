from py_nextbus import NextBusClient
from tests.mock_responses import TEST_AGENCY_ID
from tests.mock_responses import TEST_ROUTE_ID
from tests.mock_responses import TEST_STOP_ID


client = NextBusClient()
agencies = client.agencies()
print("Agencies:")
print(agencies)

routes = client.routes(TEST_AGENCY_ID)
print("\nRoutes:")
print(routes)

route_details = client.route_details(TEST_ROUTE_ID, TEST_AGENCY_ID)
print("\nRoute Details:")
print(route_details)

predictions = client.predictions_for_stop(
    TEST_STOP_ID, TEST_ROUTE_ID, agency_id=TEST_AGENCY_ID
)
print("\nPredictions:")
print(predictions)
