# microk8s-test

## Description

This is a charm that quickly deploys a machine, installs microk8s and
microstack on it, and bootstraps a Juju controller on microk8s.

## Usage

The intent is to provide a quick way of testing things out in
microk8s, while allowing the deployment to be torn down between times.

Note that you need to deploy this on a relatively beefy machine. For
example:

juju deploy microk8s-test --constraints "mem=8G root-disk=40G cpus=2"


## Developing

Install tox with your system's package manager. For example:

    sudo apt install tox

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment, which tox has been setup
to call:

    tox
    
You can also run a destructive deploy test, which will create a
testbed model on the currently bootstrapped Juju controller
(destroying it first to clean up if need be), then deploy microk8s +
Juju to a machine in it.
