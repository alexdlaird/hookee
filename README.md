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

That's it! `hookee` is now installed.

## Basic Usage

`hookee` makes it easy to get webhooks on the fly right from the console. Simply start it with:

```sh
hookee start
```

With its default configuration, this will start a server on port 5000, open a [`ngrok`](https://ngrok.com/) tunnel
using [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/), and mount a URL at `/webhook`. Sending any request to
the `/webhook` endpoint will dump the request and response data to the console.

`hookee` can be configured in a number of ways to quickly and easily tweak request and response data. For example,
here we are customizing the response body from `/webhook` using the `--response` arg.

```sh
hookee --response "<Response>Ok</Response>" --content-type application/xml
```

To see the ways `hookee` can be tweaked right from the console, view its documented args and commands like this:

```sh
hookee --help
```

## Documentation

For more advanced usage, including how `hookee` default configuration can be changed, extended through plugins,
and more, see its official documentation is available at [http://hookee.readthedocs.io](http://hookee.readthedocs.io).

## Contributing

If you would like to get involved, be sure to review the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/master/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [a donation](https://www.paypal.me/alexdlaird>) would
also be greatly appreciated!
