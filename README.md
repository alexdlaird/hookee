# hookee - command line webhooks, on demand

[![PyPI version](https://badge.fury.io/py/hookee.svg)](https://badge.fury.io/py/hookee)
[![Build Status](https://travis-ci.org/alexdlaird/hookee.svg?branch=master)](https://travis-ci.org/alexdlaird/hookee)
[![codecov](https://codecov.io/gh/alexdlaird/hookee/branch/master/graph/badge.svg)](https://codecov.io/gh/alexdlaird/hookee)
[![PyPI license](https://img.shields.io/pypi/l/hookee.svg)](https://pypi.org/project/hookee/)

`hookee` is a simple command line utility which generates webhooks on demand and dumps useful information to the
console when requests are sent to those endpoints.

This is still a pre-release of `hookee`, so more details and extensibility are coming soon.

## Installation

`hookee` is available on [PyPI](https://pypi.org/project/hookee/) and can be installed
using `pip`:

```sh
pip install hookee
```

That's it! `hookee` is now available on the command line and as a package to our Python projects.

## Basic Usage

This package puts `hookee` on your path, so it can be used by simply executing it from the command line.

```sh
hookee start
```

This will start a server on the default port 5000, open a [`ngrok`](https://ngrok.com/) tunnel to this server
using [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/), and mount a URL at `/webhook`. Sending any request to
the `/webhook` endpoint will dump the request and response content to the console.

More details, configuration, and extensibility coming soon, as this is still a pre-release of `hookee`. For now,
POC features are documented in `hookee --help` as they are released.
