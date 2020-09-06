=========================================
hookee - command line webhooks, on demand
=========================================

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

``hookee`` is a simple command line utility which generates webhooks on demand and dumps useful information to the
console when requests are sent to those endpoints.

This is still a pre-release of ``hookee``, so more details and extensibility are coming soon.

Installation
------------

``hookee`` is available on `PyPI <https://pypi.org/project/hookee/>`_ and can be installed
using ``pip``:

.. code-block:: sh

    pip install hookee

or ``conda``:

.. code-block:: sh

    conda install -c conda-forge hookee

That's it! ``hookee`` is now available on the command line and as a package to our Python projects.

Basic Usage
-----------

This package puts ``hookee`` on our path, so it can be used by simply executing it from the command line.

.. code-block:: sh

    hookee start

This will start a server on the default port 5000, open a `ngrok <https://ngrok.com/>`_ tunnel to this server
using `pyngrok <https://pyngrok.readthedocs.io/en/latest/>`_, and mount a URL at ``/webhook``. Sending any request
to the ``/webhook`` endpoint will dump the request and response content to the console.

Configuration
-------------

Out of the box, a Flask Blueprint will mount the ``/webhook`` endpoint, and default plugins for dumping request
data to the console and sending a 200 JSON response will be enabled.

Plugins can be enabled and disabled easily from the command line. For instance, if we'd like an XML response instead:

.. code-block:: sh

    hookee disable-plugin response_json
    hookee disable-plugin response_xml
    hookee start

Our own custom request or response plugins can be developed to be processed by the ``/webhook`` endpoint, or we can
add additional Blueprint plugins to register endpoints of our own—see `the Plugins section <#plugins>`_ below for
documentation on plugin development.

Customizing the Response
------------------------

If we don't want to bother with plugin development and just want to customize the response from ``/webhook``, quick
and dirty, we can use the ``--response`` arg from the command line to inject our own response body.

.. code-block:: sh

    hookee --response "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>Ok</Response>" --content-type application/xml

If we want a bit more flexibility, we can use the ``--response-script`` arg to inject our own script. All it needs is a
``run(request, response)`` method. So, for example, if we have ``my_response.py`` that implements a simple XML response:

.. code-block:: python

    def run(request, response):
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
               "<Response>Ok</Response>"

We can utilize it with:

.. code-block:: sh

    hookee start --response my_response.py

We can also do the same with the ``--request-script`` arg.

Plugins
-------

``hookee`` comes with several built-in plugins that dump request and response data to the console and return a response
from ``/webhook``. Custom plugins can be developed and in stored in the config's ``plugins_dir`` (which defaults to
``~/.config/hookee/plugins``).

Plugins have a simple structure, depending on their type. Every plugin must define a ``plugin_type``, and valid values
are defined `here in VALID_PLUGIN_TYPES <https://github.com/alexdlaird/hookee/blob/master/hookee/pluginmanager.py>`_.

All types of plugins can optionally implement ``setup(cli_manager)``, which is called once for each plugin (if defined)
when they are first loaded.

Blueprint Plugins
=================

A Blueprint plugin must define ``blueprint = Blueprint("<plugin_name>", __name__)``. Past that, simply implement
`a Flask Blueprint <https://flask.palletsprojects.com/en/1.1.x/blueprints/#my-first-blueprint>`_ to add new routes
to ``hookee``.

For a custom Blueprint plugin to leverage request and response plugins the same way the default ``/webhook`` route
does, a route needs to call :func:`hookee.pluginmanager.PluginManager.run_request_plugins` and
:func:`hookee.pluginmanager.PluginManager.run_response_plugins`

Request and Response Plugins
============================

Request and response plugins are nearly identical to each other, they only differ in one arg. In either case they
implement ``run()``, but a request plugin implements ``run(request)``, and a response plugin implements
``run(request, response)``.

The `built-in plugins that come with hookee <https://github.com/alexdlaird/hookee/tree/master/hookee/plugins>`_ can
also be used as a reference.

Dive Deeper
-----------

For more advanced usage, dive deeper in to the rest of the documentation.

.. toctree::
   :maxdepth: 2

   api

.. include:: ../CONTRIBUTING.rst
