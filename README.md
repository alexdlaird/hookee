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

That's it! `hookee` is now available as a Python package and is available from the command line.

### Configure `authtoken`

To get the most out of `hookee`, you'll want to obtain an [authtoken from `ngrok`](https://dashboard.ngrok.com/) (it's
free!) and install it in to `hookee`'s config file:

```sh
hookee authtoken $NGROK_AUTHTOKEN
```

## Basic Usage

`hookee` makes it easy to get webhooks on the fly right from the console. Simply start it with:

```sh
hookee start
```

With its default configuration, this will start a server on port 8000, open a [`ngrok`](https://ngrok.com/) tunnel
using [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/), and mount a URL at `/webhook`. Sending any request to
the `/webhook` endpoint will dump the request and response data to the console.

`hookee` can be configured in a number of ways to quickly and easily tweak request and response data. For example,
here is how you can customize the response body from `/webhook` using the `--response` arg.

```sh
hookee --response "<Response>Ok</Response>" \
    --content-type application/xml
```

`hookee` can also be started without a tunnel (removing the dependency on `ngrok` and an Internet connection). Using
the `--no-tunnel` flag only starts `hookee`'s server, allowing responses to be mocked locally. This can be particularly
useful when service discovery is done through a proxy service (ex. [HAProxy](https://www.haproxy.org/),
[Envoy](https://www.envoyproxy.io/), etc.), meaning you can tell `hookee` to start on the port of an expected downstream,
thus intercepting requests to that service to provide your own responses in an isolated environment, very useful for
rapid local development, cluster testing, and more.

```sh
hookee --no-tunnel --response "<Response>Ok</Response>" \
    --content-type application/xml \
    --default-route /some/route \
    --port 19780
```

To see the ways `hookee` can be tweaked right from the console, view its documented args and commands like this:

```sh
hookee --help
```

## Documentation

For more advanced usage, including how `hookee`'s default configuration can be changed, extended through plugins,
API integrations, and more, see its official documentation is available
at [Read the Docs](http://hookee.readthedocs.io).

## Contributing

If you would like to get involved, be sure to review
the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/main/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [sponsorship](https://github.com/sponsors/alexdlaird)
would
also be greatly appreciated!
