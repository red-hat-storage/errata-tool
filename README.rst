``errata-tool``
===============

.. image:: https://travis-ci.org/ktdreyer/errata-tool.svg?branch=master
          :target: https://travis-ci.org/ktdreyer/errata-tool

Modern Python API to Red Hat's Errata Tool.

Example:

.. code-block:: python

    from errata_tool import Erratum

    e = Erratum(1234)

    print(e.errata_state)
    # prints "NEW_FILES"

    print(e.url())
    # prints "https://errata.devel.redhat.com/errata/1234"
