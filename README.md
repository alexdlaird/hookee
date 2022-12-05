<p align="center"><img alt="hookee - command line webhooks, on demand" src="https://hookee.readthedocs.io/en/latest/_images/logo.png" /></p>

[![PyPI Version](https://badge.fury.io/py/hookee.svg)](https://badge.fury.io/py/hookee)
[![CI/CD](https://github.com/alexdlaird/hookee/workflows/CI/CD/badge.svg)](https://github.com/alexdlaird/hookee/actions?query=workflow%3ACI%2FCD)
[![Codecov](https://codecov.io/gh/alexdlaird/hookee/branch/main/graph/badge.svg)](https://codecov.io/gh/alexdlaird/hookee)
[![Docs](https://readthedocs.org/projects/hookee/badge/?version=latest)](https://hookee.readthedocs.io/en/latest/?badge=latest)
[![Python Versions](https://img.shields.io/pypi/pyversions/hookee.svg)](https://pypi.org/project/hookee/)
[![PyPI License](https://img.shields.io/pypi/l/hookee.svg)](https://pypi.org/project/hookee/)
[![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Check+out+%23hookee%2C+a+utility+that+provides+command+line+%23webhooks%2C+on+demand.%0D%0A%0D%0A&url=https://github.com/alexdlaird/hookee&via=alexdlaird&hashtags=python,flask,ngrok,pyngrok)

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

That's it! `hookee` is now available as a Python package is available from the command line.

## Basic Usage

`hookee` makes it easy to get webhooks on the fly right from the console. Simply start it with:

```sh
hookee start
```

With its default configuration, this will start a server on port 8000, open a [`ngrok`](https://ngrok.com/) tunnel
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

For more advanced usage, including how `hookee`'s default configuration can be changed, extended through plugins,
API integrations, and more, see its official documentation is available at [http://hookee.readthedocs.io](http://hookee.readthedocs.io).

## Contributing

If you would like to get involved, be sure to review the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/main/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [a donation](https://www.paypal.me/alexdlaird) would
also be greatly appreciated!
