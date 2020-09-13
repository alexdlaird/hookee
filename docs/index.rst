.. rst-class:: hide-header

hookee - command line webhooks, on demand
=========================================

.. image:: _html/logo.png
   :alt: hookee - command line webhooks, on demand
   :align: center

.. image:: https://badge.fury.io/py/hookee.svg
   :target: https://badge.fury.io/py/hookee
.. image:: https://travis-ci.org/alexdlaird/hookee.svg?branch=master
   :target: https://travis-ci.org/alexdlaird/hookee
.. image:: https://codecov.io/gh/alexdlaird/hookee/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/alexdlaird/hookee
.. image:: https://readthedocs.org/projects/hookee/badge/?version=latest
   :target: https://hookee.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/pypi/l/hookee.svg
   :target: https://pypi.org/project/hookee/
.. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social
   :target: https://twitter.com/intent/tweet?text=Check+out+hookee%2C+a+utility+that+provides+command+line+webhooks%2C+on+demand.&url=https://github.com/alexdlaird/hookee&via=alexdlaird&hashtags=python,webhooks,flask,ngrok

``hookee`` is a utility that provides command line webhooks, on demand! Dump useful request data to the
console, process requests and responses, customize response data, and configure ``hookee`` and its routes
further in any number of ways through custom plugins.

Installation
------------

``hookee`` is available on `PyPI <https://pypi.org/project/hookee/>`_ and can be installed
using ``pip``:

.. code-block:: sh

    pip install hookee

or ``conda``:

.. code-block:: sh

    conda install -c conda-forge hookee

That's it! ``hookee`` is now installed.

Basic Usage
-----------

``hookee`` makes it easy to get webhooks on the fly right from the console. Simply start it like this:

.. code-block:: sh

    hookee start

With its default configuration, this will start a server on port 5000, open a `ngrok <https://ngrok.com/>`_ tunnel
using `pyngrok <https://pyngrok.readthedocs.io/en/latest/>`_, and mount a URL at ``/webhook``. Sending any
request to the ``/webhook`` endpoint will dump request and response data to the console.

To see the ways ``hookee`` can be tweaked right from the console, view its documented args and commands like this:

.. code-block:: sh

    hookee --help

Configuration
-------------

Enabling/Disabling Plugins
==========================

Out of the box, a `Flask Blueprint <https://flask.palletsprojects.com/en/1.1.x/blueprints/#my-first-blueprint>`_ will
mount a URL at ``/webhook``, and default plugins for dumping request data to the console and echoing back the request
body as the response will be enabled.

Plugins can be enabled and disabled easily from the command line. Here we are disabling the default response plugin
in favor of our own JSON response plugin:

.. code-block:: sh

    hookee disable-plugin response_echo
    hookee enable-plugin my_json_plugin
    hookee start

Custom request or response plugins can be built and, when enabled, the default ``/webhook`` endpoint will utilize
them. Or we can add additional Blueprint plugins to register endpoints of our own—see `the Plugins section <#plugins>`_
below for documentation on plugin development.

Changing the Defaults
=====================

If we find ourselves continually reusing the same args to configure ``hookee`` when starting it, we can instead just
updated the config's defaults. For example, if we always want to reuse the same ``ngrok`` endpoint:

.. code-block:: sh

    hookee --subdomain my_domain --region eu

We can update these defaults like this:

.. code-block:: sh

    hookee update-config subdomain my_domain
    hookee update-config region eu

From now on, these args are no longer necessary when starting ``hookee``:

.. code-block:: sh

    hookee

Customizing the Response
------------------------

If we don't want to bother with building our own plugins and just want to quickly customize the response from
``/webhook``, the ``--response`` arg is here for us.

.. code-block:: sh

    hookee --response "<Response>Ok</Response>" --content-type application/xml

As with any config, if we find ourselves continually passing this response to ``hookee`` every time we run it, we can
make it the default:

.. code-block:: sh

    hookee update-config response "<Response>Ok</Response>"
    hookee update-config content-type application/xml

If we want a bit more flexibility, we can use ``--response-script`` to inject any script that implements
``run(request, response)``. So, for example, if we have ``my_response_script.py`` that builds a simple
Flask XML response:

.. code-block:: python

    from flask import current_app

    def run(request, response):
        return current_app.response_class(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>Ok</Response>",
            mimetype="application/xml",
        )

We can utilize it with:

.. code-block:: sh

    hookee --response-script my_response_script.py

We can do the same with the ``--request-script`` arg.

Plugins
-------

``hookee`` comes with several built-in plugins that dump request and response data to the console and return a response
from ``/webhook``. We can also build our own plugins and store them in the config's ``plugins_dir`` (which defaults to
``~/.config/hookee/plugins``).

Plugins have a simple structure. Every plugin must define a ``plugin_type``, and valid values are:

- ``blueprint``
- ``request``
- ``response``

All plugin types can optionally implement ``setup(cli_manager)``, which will be called on the plugin when it is
first loaded.

Blueprint Plugins
=================

A Blueprint plugin must define ``blueprint = Blueprint("<plugin_name>", __name__)``. Past that, simply implement
`a Flask Blueprint <https://flask.palletsprojects.com/en/1.1.x/blueprints/#my-first-blueprint>`_. Any defined route
in this Blueprint, when the plugin is enabled, will be added to ``hookee``.

For a Blueprint plugin to leverage enabled request and response plugins the same way the default ``/webhook`` route
does, we can call :func:`hookee.pluginmanager.PluginManager.run_request_plugins` and
:func:`hookee.pluginmanager.PluginManager.run_response_plugins`

Request and Response Plugins
============================

Request and response plugins are nearly identical to each other, they only differ in one arg. A request plugin
must implement ``run(request)`` (and return the ``request``), and a response plugin must implement
``run(request, response)`` (and return the ``response``).

The `built-in plugins that come with hookee <https://github.com/alexdlaird/hookee/tree/master/hookee/plugins>`_ may
be a useful reference when developing new plugins for ``hookee``.

Dive Deeper
-----------

Under the hood, ``hookee`` uses `Flask <https://flask.palletsprojects.com/en/1.1.x/>`_ as its server and
`pyngrok <https://pyngrok.readthedocs.io/en/latest/>`_ to open and manage its tunnel. Being familiar with these
two packages would allow ``hookee`` to be configured and extended further.

For more advanced ``hookee`` usage, its own API documentation is also available.

.. toctree::
   :maxdepth: 2

   api

.. include:: ../CONTRIBUTING.rst
