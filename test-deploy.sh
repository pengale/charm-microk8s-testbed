#!/bin/bash
# Quick script to do a test deploy. Will add and destroy a "testbed" model.

set -ex

juju destroy-model -y --force testbed || true
juju add-model testbed
juju model-config logging-config="<root>=DEBUG;unit=DEBUG"

charmcraft build
juju deploy ./bundle.yaml
juju debug-log
