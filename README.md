# py_nextbusnext

## This is forked from py_nextbus for maintanence
_It is no longer API compatible to the upstream_

A minimalistic Python 3 client to simplify making requests to the NextBus API. Response content can be returned as either JSON or XML, using the respective NextBus public feed.

All commands in the NextBus API as of revision 1.23 are supported.

See the NextBus XML feed documentation for more information: https://retro.umoiq.com/xmlFeedDocs/NextBusXMLFeed.pdf

Note: Other than the output format, the NextBus XML feed and JSON feeds are the same. The XML feed documentation also applies to the JSON feed.

Installation
---

Install with pip:

`pip install py-nextbusnext`

Usage
---

```
>>> import py_nextbus
>>> client = py_nextbus.NextBusClient(output_format='json')
>>> agencies = client.get_agency_list()
```
