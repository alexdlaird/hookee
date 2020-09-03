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

:code:`hookee` is a simple command line utility which generates webhooks on demand and dumps useful information to the
console when requests are sent to those endpoints.

This is still a pre-release of :code:`hookee`, so more details and extensibility are coming soon.

Installation
------------

:code:`hookee` is available on `PyPI <https://pypi.org/project/hookee/>`_ and can be installed
using :code:`pip`:

.. code-block:: sh

    pip install hookee

or :code:`conda`:

.. code-block:: sh

    conda install -c conda-forge hookee

That's it! :code:`hookee` is now available on the command line and as a package to our Python projects.

Basic Usage
-----------

This package puts :code:`hookee` on our path, so it can be used by simply executing it from the command line.

.. code-block:: sh

    hookee start

This will start a server on the default port 5000, open a `ngrok <https://ngrok.com/>`_ tunnel to this server
using `pyngrok <https://pyngrok.readthedocs.io/en/latest/>`_, and mount a URL at :code:`/webhook`. Sending any request
to the :code:`/webhook` endpoint will dump the request and response content to the console.

Configuration
-------------

More details on configuration and extensibility are coming soon, as this is still a pre-release of :code:`hookee`. For
now, POC features are documented in :code:`hookee --help` as they are released.

Plugins
-------

The plugin system will also be documented further as :code:`hookee` moves away from being a POC. For now, custom
plugins can be developed and stored in :code:`~/.config/hookee/plugins`, and `the built-in plugins can be used as a reference <https://github.com/alexdlaird/hookee/tree/master/hookee/plugins>`_.

Dive Deeper
-----------

For more advanced usage, dive deeper in to the rest of the documentation.

.. toctree::
   :maxdepth: 2

   api

.. include:: ../CONTRIBUTING.rst
