[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENCE)
[![Gitter](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/polyaxon/polyaxon)

# polyaxon-events

Kubernetes events monitor and publisher for Polyaxon.


It contains a set of monitors to be launched as a lightweight containers inside the Kubernetes cluster to monitor and publish:
 * Errors and warnings events for of the cluster namespace.
 * Experiment jobs pods status change.
 * Experiment jobs containers resources.
 * Experiment jobs sidecar logs.
