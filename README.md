# microk8s-testbed

## Description

This is a charm built to deploy an machine, install microk8s and
Juju on it, and bootstrap a Juju controller on microk8s.

## Usage

The intent is to provide a straightforward way of testing things out
in microk8s, with easy teardown and redeploy.

Note that you need to deploy this on a relatively beefy machine. For
example:

    juju deploy microk8s-testbed \
        --constraints "mem=8G root-disk=40G cpus=2"

## Developing

This charm uses Python Tox to run its unit and functional
tests. Instructions on installing tox live here:

https://tox.readthedocs.io/en/latest/install.html

In brief, you can:

    pip install tox

Or you can:

    apt/brew install tox

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment, which tox has been setup
to call:

    tox

You can also run a destructive deploy test, which will create a
testbed model on the currently bootstrapped Juju controller
(destroying it first to clean up if need be), then deploy microk8s +
Juju to a machine in it. Run it with:

    tox -e deploy
