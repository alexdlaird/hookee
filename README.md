<p align="center"><img alt="hookee - command line webhooks, on demand" src="https://hookee.readthedocs.io/en/latest/_images/logo.png" /></p>

[![Version](https://img.shields.io/pypi/v/hookee)](https://pypi.org/project/hookee)
[![Python Versions](https://img.shields.io/pypi/pyversions/hookee.svg)](https://pypi.org/project/hookee/)
[![Coverage](https://img.shields.io/codecov/c/github/alexdlaird/hookee)](https://codecov.io/gh/alexdlaird/hookee)
[![Build](https://img.shields.io/github/actions/workflow/status/alexdlaird/hookee/build.yml)](https://github.com/alexdlaird/hookee/actions/workflows/build.yml)
[![Docs](https://img.shields.io/readthedocs/hookee)](https://hookee.readthedocs.io/en/latest)
[![GitHub License](https://img.shields.io/github/license/alexdlaird/hookee)](https://github.com/alexdlaird/hookee/blob/main/LICENSE)

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
using [`hookee`](https://hookee.readthedocs.io/en/latest/), and mount a URL at `/webhook`. Sending any request to
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
API integrations, and more, see its official documentation is available
at [http://hookee.readthedocs.io](http://hookee.readthedocs.io).

## Contributing

If you would like to get involved, be sure to review
the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/main/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [sponsorship](https://github.com/sponsors/alexdlaird)
would
also be greatly appreciated!
