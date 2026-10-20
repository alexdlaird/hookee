<p align="center"><img alt="hookee - Command line webhooks, on demand: see, answer, forward, and capture requests from your terminal" src="https://hookee.readthedocs.io/en/stable/_images/logo.png" /></p>

[![Version](https://img.shields.io/pypi/v/hookee)](https://pypi.org/project/hookee)
[![Python Versions](https://img.shields.io/pypi/pyversions/hookee.svg)](https://pypi.org/project/hookee/)
[![Coverage](https://img.shields.io/codecov/c/github/alexdlaird/hookee)](https://codecov.io/gh/alexdlaird/hookee)
[![Build](https://img.shields.io/github/actions/workflow/status/alexdlaird/hookee/build.yml)](https://github.com/alexdlaird/hookee/actions/workflows/build.yml)
[![Docs](https://img.shields.io/readthedocs/hookee)](https://hookee.readthedocs.io/en/stable)
[![GitHub License](https://img.shields.io/github/license/alexdlaird/hookee)](https://github.com/alexdlaird/hookee/blob/main/LICENSE)

`hookee` gives you a public URL to your terminal with one command. Point any service's webhooks at it, then see,
answer, and forward every request as it happens, with no code.

- **See any webhook, instantly.** Run `hookee`, paste its URL into any service's console, and every request is dumped
  to your terminal, with JSON, XML, and form bodies formatted.
- **Answer it from the command line.** Respond with any body, status code, headers, or delay, and see how the service
  reacts.
- **Sit in front of your app.** `--forward-to` relays every request to your local app and shows both sides, including
  streamed responses.
- **Debug a phone or browser against your local backend.** Every API call shows up in your console, with nothing to
  set up on the device.
- **Capture real payloads as test fixtures.** Save each request, and your app's response, as JSON.
- **Verify signatures, test error handling, and mock services.** Check that requests really came from the service,
  break one endpoint while the rest keep working, or stand in for an API your app calls.

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
free!) and install it into `hookee`'s config file:

```sh
hookee authtoken $NGROK_AUTHTOKEN
```

## Basic Usage

Start `hookee`, and it gives you a public URL whose `/webhook` endpoint dumps every request it receives, and the
response sent back, to your console:

```sh
hookee
```

Each workflow below is a single command:

| You want to ... | Run |
|---|---|
| [See what a webhook sends](https://hookee.readthedocs.io/en/stable/#basic-usage) | `hookee` |
| [Reply without writing code](https://hookee.readthedocs.io/en/stable/#customizing-the-response) | `hookee --response-file reply.xml` |
| [Test error handling and retries](https://hookee.readthedocs.io/en/stable/#customizing-the-response) | `hookee --status-code 503 --delay 10` |
| [Forward to your app, and watch both sides](https://hookee.readthedocs.io/en/stable/#forwarding-to-your-app) | `hookee --forward-to http://localhost:3000` |
| [Capture real payloads as fixtures](https://hookee.readthedocs.io/en/stable/#capturing-real-payloads) | `hookee --forward-to http://localhost:3000 --save-dir tests/fixtures` |
| [Record a third-party API's real responses](https://hookee.readthedocs.io/en/stable/#recording-a-third-party-api) | `hookee --forward-to https://api.example.com --host-header api.example.com --save-dir tests/fixtures` |
| [Verify webhook signatures](https://hookee.readthedocs.io/en/stable/#verifying-webhooks) | `hookee --verify-webhook <provider>:<secret>` |
| [Debug a device against your local API](https://hookee.readthedocs.io/en/stable/#debugging-your-app-from-a-device) | `hookee --forward-to http://localhost:3000 --url my-api.ngrok.dev` |
| [Break one endpoint, keep the rest working](https://hookee.readthedocs.io/en/stable/#debugging-your-app-from-a-device) | `hookee --forward-to http://localhost:3000 --response-route "^GET /api/" --status-code 503` |
| [Mock a service your app calls](https://hookee.readthedocs.io/en/stable/#mocking-an-external-service) | `hookee --response-file feed.ics` |
| [Run locally, without a tunnel](https://hookee.readthedocs.io/en/stable/#running-without-a-tunnel) | `hookee --no-tunnel --port 19780 --response "Ok"` |

To see every way `hookee` can be configured right from the console:

```sh
hookee --help
```

## Documentation

For more advanced usage, `hookee`'s official documentation is available
on [Read the Docs](https://hookee.readthedocs.io), including how to change its defaults, extend it with plugins, and
integrate it into your own code.

## Contributing

If you would like to get involved, be sure to review
the [Contribution Guide](https://github.com/alexdlaird/hookee/blob/main/CONTRIBUTING.rst).

Want to contribute financially? If you've found `hookee` useful, [sponsorship](https://github.com/sponsors/alexdlaird)
would also be greatly appreciated!
