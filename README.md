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

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
