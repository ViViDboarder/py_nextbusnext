# py_nextbusnext

## This is forked from py_nextbus for maintanence
_It is no longer API compatible to the upstream_

A minimalistic Python 3 client to get routes and predictions from the NextBus API.

Installation
---

Install with pip:

`pip install py-nextbusnext`

Usage
---

```
>>> import py_nextbus
>>> client = py_nextbus.NextBusClient()
>>> agencies = client.get_agencies()
```
