.. rst-class:: hide-header

********************************************************************************************************
hookee - Command line webhooks, on demand: see, answer, forward, and capture requests from your terminal
********************************************************************************************************

.. only:: html

   .. image:: _static/logo-light.png
      :alt: hookee - Command line webhooks, on demand: see, answer, forward, and capture requests from your terminal
      :align: center
      :width: 280px
      :class: hero-logo only-light

   .. image:: _static/logo-dark.png
      :alt: hookee - Command line webhooks, on demand: see, answer, forward, and capture requests from your terminal
      :align: center
      :width: 280px
      :class: hero-logo only-dark

.. only:: not html

   .. image:: _html/_images/logo.png
      :alt: hookee - Command line webhooks, on demand: see, answer, forward, and capture requests from your terminal
      :align: center

.. image:: https://img.shields.io/pypi/v/hookee
   :target: https://pypi.org/project/hookee
.. image:: https://img.shields.io/pypi/pyversions/hookee.svg
   :target: https://pypi.org/project/hookee
.. image:: https://img.shields.io/codecov/c/github/alexdlaird/hookee
   :target: https://codecov.io/gh/alexdlaird/hookee
.. image:: https://img.shields.io/github/actions/workflow/status/alexdlaird/hookee/build.yml
   :target: https://github.com/alexdlaird/hookee/actions/workflows/build.yml
.. image:: https://img.shields.io/readthedocs/hookee
   :target: https://hookee.readthedocs.io/en/stable
.. image:: https://img.shields.io/github/license/alexdlaird/hookee
   :target: https://github.com/alexdlaird/hookee

``hookee`` gives you a public URL to your terminal with one command. Point any service's webhooks at it, then see,
answer, and forward every request as it happens, with no code.

- **See any webhook, instantly.** Run ``hookee``, paste its URL into any service's console, and every request is dumped
  to your terminal, with JSON, XML, and form bodies formatted.
- **Answer it from the command line.** Respond with any body, status code, headers, or delay, and see how the service
  reacts.
- **Sit in front of your app.** ``--forward-to`` relays every request to your local app and shows both sides, including
  streamed responses.
- **Debug a phone or browser against your local backend.** Every API call shows up in your console, with nothing to
  set up on the device.
- **Capture real payloads as test fixtures.** Save each request, and your app's response, as JSON.
- **Verify signatures, test error handling, and mock services.** Check that requests really came from the service,
  break one endpoint while the rest keep working, or stand in for an API your app calls.

Installation
============

``hookee`` is available on `PyPI <https://pypi.org/project/hookee/>`_ and can be installed
using ``pip``:

.. code-block:: sh

    pip install hookee

or ``conda``:

.. code-block:: sh

    conda install -c conda-forge hookee

That's it! ``hookee`` is now available as a Python package and is available from the command line.

Configure ``authtoken``
-----------------------

To get the most out of ``hookee``, you'll want to obtain an `authtoken from ngrok <https://dashboard.ngrok.com/>`_
(it's free!) and install it into ``hookee``'s config file:

.. code-block:: sh

    hookee authtoken $NGROK_AUTHTOKEN

Basic Usage
===========

Start ``hookee``, and it gives you a public URL whose ``/webhook`` endpoint dumps every request it receives, and the
response sent back, to your console:

.. code-block:: sh

    hookee

With its default configuration, this starts a server on port 8000, opens an `ngrok <https://ngrok.com/>`_ tunnel to it
using `pyngrok <https://pyngrok.readthedocs.io/en/stable/>`_, and mounts a URL at ``/webhook``.

Each workflow below is a single command:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - You want to ...
     - Run
   * - See what a webhook sends
     - ``hookee``
   * - `Reply without writing code <#customizing-the-response>`_
     - ``hookee --response-file reply.xml``
   * - `Test error handling and retries <#customizing-the-response>`_
     - ``hookee --status-code 503 --delay 10``
   * - `Forward to your app, and watch both sides <#forwarding-to-your-app>`_
     - ``hookee --forward-to http://localhost:3000``
   * - `Capture real payloads as fixtures <#capturing-real-payloads>`_
     - ``hookee --forward-to http://localhost:3000 --save-dir tests/fixtures``
   * - `Record a third-party API's real responses <#recording-a-third-party-api>`_
     - ``hookee --forward-to https://api.example.com --host-header api.example.com --save-dir tests/fixtures``
   * - `Verify webhook signatures <#verifying-webhooks>`_
     - ``hookee --verify-webhook <provider>:<secret>``
   * - `Debug a device against your local API <#debugging-your-app-from-a-device>`_
     - ``hookee --forward-to http://localhost:3000 --url my-api.ngrok.dev``
   * - `Break one endpoint, keep the rest working <#debugging-your-app-from-a-device>`_
     - ``hookee --forward-to http://localhost:3000 --response-route "^GET /api/" --status-code 503``
   * - `Mock a service your app calls <#mocking-an-external-service>`_
     - ``hookee --response-file feed.ics``
   * - `Run locally, without a tunnel <#running-without-a-tunnel>`_
     - ``hookee --no-tunnel --port 19780 --response "Ok"``

To see every way ``hookee`` can be configured right from the console:

.. code-block:: sh

    hookee --help

Configuration
=============

Enabling/Disabling Plugins
--------------------------

Out of the box, a `Flask Blueprint <https://flask.palletsprojects.com/en/1.1.x/blueprints/#my-first-blueprint>`_ will
mount a URL at ``/webhook``, and default plugins for dumping request data to the console and echoing back the request
body as the response will be enabled.

Plugins can be enabled and disabled easily from the command line. Here is how you disable the default response plugin
in favor of your own JSON response plugin:

.. code-block:: sh

    hookee disable-plugin response_echo
    hookee enable-plugin my_json_plugin
    hookee start

Custom request or response plugins can be built and, when enabled, the default ``/webhook`` endpoint will utilize
them. Or you can add additional Blueprint plugins to register endpoints of your own—see `the Plugins section <#plugins>`_
below for documentation on plugin development.

Changing the Defaults
---------------------

If you find yourself continually reusing the same args to configure ``hookee`` when starting it, you can instead just
update the config's defaults. For example, if you always want to reuse the same ``ngrok`` endpoint:

.. code-block:: sh

    hookee --url my-hooks.ngrok.io --basic-auth "username:password" \
        --default-route /my/path

You can update these defaults like this:

.. code-block:: sh

    hookee update-config url my-hooks.ngrok.io
    hookee update-config basic-auth "username:password"
    hookee update-config default-route /my/path

From now on, these args are no longer necessary when starting ``hookee``:

.. code-block:: sh

    hookee

Customizing the Response
========================

If you don't want to bother with building your own plugins, the response from ``/webhook`` can be customized right from
the command line with the ``--response`` arg.

.. code-block:: sh

    hookee --response "<Response>Ok</Response>" \
        --content-type application/xml

This approach can be particularly useful in tutorials where you want to quickly allow a developer to see and interact
with webhooks from your service before they've done any actual integration with your service themselves—all they would
have to do is copy and paste a simple ``hookee`` command like the one shown above.

As with any config, if you find yourself continually passing this response to ``hookee`` every time you run it, you
can make it the default:

.. code-block:: sh

    hookee update-config response "<Response>Ok</Response>"
    hookee update-config content-type application/xml

If you'd rather keep the response in a file, use ``--response-file`` (its ``Content-Type`` is guessed from the file's
extension). You can also set the status code and headers, and use ``--delay`` to wait before responding, which is
useful for seeing how a service handles errors and slow responses.

.. code-block:: sh

    hookee --response-file response.xml \
        --status-code 201 \
        --response-header "X-Hookee: yes" \
        --delay 1

If you want a bit more flexibility, you can use ``--response-script`` to inject any script that implements
``run(request, response)``. So, for example, if you have ``my_response_script.py`` that builds a simple
Flask XML response:

.. code-block:: python

    from flask import current_app

    def run(request, response):
        return current_app.response_class(
            """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
            <Response>Ok</Response>""",
            mimetype="application/xml",
        )

You can utilize it with:

.. code-block:: sh

    hookee --response-script my_response_script.py

You can do the same with the ``--request-script`` arg.

Forwarding to Your App
======================

Once you've seen what a service's webhooks look like and started writing your own handler, ``hookee`` can sit
between the service and your app. With the ``--forward-to`` arg, each request is still dumped to the console, then
forwarded to your app, and its response is sent back to the service, so you can watch both sides of every webhook as
you build.

.. code-block:: sh

    hookee --forward-to http://localhost:3000

Every request ``hookee`` receives is forwarded to the given base URL at the same path, with the same query string,
so pointing a service at ``https://<random>.ngrok.app/events`` sends its webhooks to ``http://localhost:3000/events``.
Requests are forwarded exactly as ``hookee`` received them, and the app's response is sent back as-is, even if it's an
error or a redirect. If the app can't be reached, ``hookee`` responds with a ``502`` and shows the reason in the
console. The only path that isn't forwarded is ``hookee``'s own ``/status`` endpoint, though ``/status/`` still is.

Streamed responses, like server-sent events or a streamed AI response, are passed on as they arrive, and each part
is shown in the console as it arrives.

``hookee`` listens on port ``8000`` by default, so if your app does too, start ``hookee`` on a different port with the
``--port`` arg.

Here is what ``hookee`` shows for a webhook forwarded to a local app, with some headers omitted:

.. code-block:: text

    Headers: {
        "Host": "<random>.ngrok.app",
        "Content-Type": "application/json",
        "X-Forwarded-Proto": "https",
        "X-Webhook-Signature": "t=1792540800,v1=5257a869e7"
    }
    Body Type: JSON
    Body: {
        "event": "message.created",
        "id": "evt_123",
        "data": {
            "text": "Hello"
        }
    }

    ------------------------------------Response------------------------------------

    Forwarded To: http://localhost:3000/events
    Status Code: 200
    Headers: {
        "Content-Type": "application/json"
    }
    Body: {
        "received": "evt_123"
    }

Debugging Your App from a Device
--------------------------------

When you're building a mobile app or a web frontend, ``hookee`` can stand in front of your whole local backend. Use
``hookee``'s public HTTPS URL as the app's API host, whether it's running on a physical device, an emulator, or in a
browser, and every API call it makes will show up in your console. There's nothing to install or configure on the
device itself.

.. code-block:: sh

    hookee --forward-to http://localhost:3000 --url my-api.ngrok.dev

Since requests are forwarded with the ``Host`` header they arrived with, your backend will need to accept ``hookee``'s
public domain, for instance in Django's ``ALLOWED_HOSTS`` and your CORS settings.

If you want to see how your app handles a failing or slow API, use the ``--response-route`` arg. It limits the response
args to the requests you choose, with a regex that's matched against each request's method and path, so everything
else keeps working normally.

.. code-block:: sh

    hookee --forward-to http://localhost:3000 \
        --response-route "^GET /planner/" \
        --status-code 503

Mocking an External Service
===========================

``hookee`` can also be used the other way around, as the external service your app calls. Give your app ``hookee``'s
public URL in place of the real service, then serve whatever response you need to test, including errors and slow
responses. Each request is dumped to the console, so you can also check exactly what your app sends. And since the URL
is public, this works even if your app refuses to call local or private addresses, which many apps do for URLs their
users give them, like calendar feeds or link previews.

For example, to serve a calendar feed, give your app the ``/webhook`` URL ``hookee`` shows when it starts (or use
``--default-route`` to match the path your app calls), and run:

.. code-block:: sh

    hookee --response-file feed.ics --response-header 'ETag: "v1"'

Then test what your app does when the feed hasn't changed, or when it's too slow to respond:

.. code-block:: sh

    hookee --status-code 304 --response-header 'ETag: "v1"'
    hookee --response-file feed.ics --delay 60

Capturing Real Payloads
=======================

If you want to see exactly what a service sends, the ``--save-dir`` arg saves each request, along with the response
sent for it, to the given directory as a JSON file. This gives you real payloads to reuse, for instance as fixtures in
your app's tests. When used with ``--forward-to``, each file is a complete test case: a real request, and the response
your app gave for it.

.. code-block:: sh

    hookee --forward-to http://localhost:3000 --save-dir tests/fixtures

Here is a saved webhook, with some headers omitted:

.. code-block:: json

    {
        "timestamp": "2026-10-20T14:09:33.806623",
        "request": {
            "method": "POST",
            "path": "/events",
            "query": {},
            "headers": {
                "Host": "<random>.ngrok.app",
                "Content-Type": "application/json",
                "X-Webhook-Signature": "t=1792540800,v1=5257a869e7"
            },
            "body": "{\"event\": \"message.created\", \"id\": \"evt_123\", \"data\": {\"text\": \"Hello\"}}",
            "body_encoding": "utf-8"
        },
        "response": {
            "status_code": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "{\"received\":\"evt_123\"}\n",
            "body_encoding": "utf-8"
        }
    }

Bodies that aren't text are saved with a ``body_encoding`` of ``base64``. A test can then replay the saved request
against your app, and check that it still responds the same way:

.. code-block:: python

    import json

    from myapp.app import app


    def test_incoming_event():
        with open("tests/fixtures/incoming-event.json") as f:
            saved = json.load(f)
        request = saved["request"]

        response = app.test_client().open(request["path"], method=request["method"],
                                          headers=request["headers"], data=request["body"])

        assert response.status_code == saved["response"]["status_code"]
        assert response.get_data(as_text=True) == saved["response"]["body"]

Headers that carry credentials, like ``Authorization`` and ``Cookie``, are masked in saved files and in the console, so
they don't end up in fixtures you commit. To keep them, pass ``--show-sensitive-headers``.

Recording a Third-Party API
---------------------------

Payloads can be captured in the other direction, too. To record the real responses from an API your app calls, forward
``hookee`` to that API, and use ``--host-header`` so the API receives its own host name:

.. code-block:: sh

    hookee --forward-to https://api.example.com \
        --host-header api.example.com \
        --save-dir tests/fixtures

Then point your app's base URL for that API at ``hookee``'s public URL. Each call is dumped to the console,
forwarded to the real API, and saved along with the API's response, ready to use as a fixture. Note that if a response
links back to the API by its full URL, like a redirect, your app will follow it straight to the API, so that follow-up
call won't be recorded.

Verifying Webhooks
==================

Most services sign their webhooks, so you can check that a request really came from them. With the
``--verify-webhook`` arg, ``ngrok``'s `verify-webhook <https://ngrok.com/docs/traffic-policy/actions/verify-webhook/>`_
action checks each request's signature, and ``hookee`` shows whether it was verified. Requests are never blocked, so
you can see a failed signature right alongside the request that caused it.

.. code-block:: sh

    hookee --verify-webhook <provider>:<secret>

The value is a provider and its secret, separated by a colon. ``ngrok``'s documentation lists the supported providers
and what each uses as its secret. When used with ``--forward-to``, your app also receives the result in the
``X-Hookee-Webhook-Verified`` header, as ``true`` or ``false``.

Running Without a Tunnel
========================

``hookee`` can also be started without a tunnel (removing the dependency on ``ngrok`` and an Internet connection).
Using the ``--no-tunnel`` flag only starts ``hookee``'s server, allowing responses to be mocked locally. This can be
particularly useful when service discovery is done through a proxy service (ex. `HAProxy <https://www.haproxy.org/>`_,
`Envoy <https://www.envoyproxy.io/>`_, etc.), meaning you can tell ``hookee`` to start on the port of an expected
downstream, thus intercepting requests to that service to provide your own responses in an isolated environment,
very useful for rapid local development, cluster testing, and more.

.. code-block:: sh

    hookee --no-tunnel --response "<Response>Ok</Response>" \
        --content-type application/xml \
        --default-route /some/route \
        --port 19780

Plugins
=======

``hookee`` comes with several built-in plugins that dump request and response data to the console and return a response
from ``/webhook``. You can also build your own plugins and store them in the config's ``plugins_dir`` (which defaults to
``~/.config/hookee/plugins``).

Plugins have a simple structure. Every plugin must define a ``plugin_type``, and valid values are:

- ``blueprint``
- ``request``
- ``response``

All plugin types can optionally implement ``setup(hookee_manager)``, which will be called on the plugin when it is
first loaded. References to :class:`~hookee.pluginmanager.PluginManager`, :class:`~hookee.util.PrintUtil`, and more
can be access from the passed in :class:`~hookee.hookeemanager.HookeeManager`.

Plugins can also optionally define a ``description``, which will be output when listing available and enabled plugins.

Blueprint Plugins
-----------------

A Blueprint plugin must define ``blueprint = Blueprint("<plugin_name>", __name__)``. Past that, simply implement
`a Flask Blueprint <https://flask.palletsprojects.com/en/1.1.x/blueprints/#my-first-blueprint>`_. Any defined route
in this Blueprint, when the plugin is enabled, will be added to ``hookee``.

For a Blueprint plugin to leverage enabled request and response plugins the same way the default ``/webhook`` route
does, you can call :func:`hookee.pluginmanager.PluginManager.run_request_plugins` and
:func:`hookee.pluginmanager.PluginManager.run_response_plugins`

Request and Response Plugins
----------------------------

Request and response plugins are nearly identical to each other, they only differ in one arg. A request plugin
must implement ``run(request)`` (and return the ``request``), and a response plugin must implement
``run(request, response)`` (and return the ``response``).

The `built-in plugins that come with hookee <https://github.com/alexdlaird/hookee/tree/main/hookee/plugins>`_ may
be a useful reference when developing new plugins for ``hookee``.

Integrating with ``hookee``
===========================

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1DO1yOw8sCkybSFP_Ci8sDmsSbOgB8r54?usp=sharing

You can also integrate with ``hookee`` instead of using its command line interface.
:class:`~hookee.hookeemanager.HookeeManager` is a good starting point for custom integrations. If you still want
access to the output that would otherwise have gone to the console (for instance, request data dumped from plugins),
you can `setup the  logger <https://docs.python.org/3/howto/logging.html>`_. For example, this would add a handler
to the ``hookee`` logger that logs output back to the console:

.. code-block:: python

    import logging

    logger = logging.getLogger("hookee")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

Dive Deeper
===========

Under the hood, ``hookee`` uses `Flask <https://flask.palletsprojects.com/en/1.1.x/>`_ as its server and
`pyngrok <https://pyngrok.readthedocs.io/en/stable/>`_ to open and manage its tunnel. Being familiar with these
two packages would allow ``hookee`` to be configured and extended further.

For more advanced ``hookee`` usage, its own API documentation is also available.

.. toctree::
   :maxdepth: 2

   api

.. include:: ../CONTRIBUTING.rst
