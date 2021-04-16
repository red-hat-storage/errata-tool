python-errata-tool
==================


.. image:: https://travis-ci.org/red-hat-storage/errata-tool.svg?branch=master
          :target: https://travis-ci.org/red-hat-storage/errata-tool

.. image:: https://badge.fury.io/py/errata-tool.svg
             :target: https://badge.fury.io/py/errata-tool


.. _about:

About
-----
python-errata-tool is a Python library that wraps the Errata Tool's REST API.
It uses `requests_gssapi <https://pypi.python.org/pypi/requests-gssapi>`_
to authenticate and parses JSON responses into
:class:`~errata_tool.erratum.Erratum` objects. You can use it to create new
advisories, or read and update existing advisories. The
:class:`~errata_tool.connector.ErrataConnector` class also provides lower-level
access to all of the Errata Tool's REST API.

Contents
--------
.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
