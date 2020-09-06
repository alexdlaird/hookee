# hookee - command line webhooks, on demand

[![PyPI version](https://badge.fury.io/py/hookee.svg)](https://badge.fury.io/py/hookee)
[![Build Status](https://travis-ci.org/alexdlaird/hookee.svg?branch=master)](https://travis-ci.org/alexdlaird/hookee)
[![codecov](https://codecov.io/gh/alexdlaird/hookee/branch/master/graph/badge.svg)](https://codecov.io/gh/alexdlaird/hookee)
[![Documentation Status](https://readthedocs.org/projects/hookee/badge/?version=latest)](https://hookee.readthedocs.io/en/latest/?badge=latest)
[![PyPI license](https://img.shields.io/pypi/l/hookee.svg)](https://pypi.org/project/hookee/)

`hookee` is a utility that provides command line webhooks, on demand! Dump useful request data to the
console, process requests and responses, customize response data, and configure `hookee` and its routes
further in any number of ways through custom plugins.

## Installation

`hookee` is available on [PyPI](https://pypi.org/project/hookee/) and can be installed
using `pip`:

```sh
pip install hookee
```

or `conda`:

```sh
conda install -c conda-forge hookee
```

That's it! `hookee` is now available on the command line and as a package to our Python projects.

## Basic Usage

This package puts `hookee` on our path, so it can be used by simply executing it from the command line.

```sh
hookee start
```

This will start a server on the default port 5000, open a [`ngrok`](https://ngrok.com/) tunnel to this server
using [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/), and mount a URL at `/webhook`. Sending any request to
the `/webhook` endpoint will dump the request and response content to the console.

We can also customize the response from `/webhook`, quick and dirty, using the `--response` arg.

```sh
hookee --response "<Response>Ok</Response>" --content-type application/xml
```

For more advanced customization of requests, responses, and available routes, refer to the documentation.

## Documentation

For more advanced usage, including extending `hookee` through plugins, `hookee`'s official documentation is
available at [http://hookee.readthedocs.io](http://hookee.readthedocs.io).

## Contributing

If you would like to get involved, be sure to review the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/master/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [a donation](https://www.paypal.me/alexdlaird>) would
also be greatly appreciated!
