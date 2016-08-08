``errata-tool``
===============

Modern Python API to Red Hat's Errata Tool.

.. image:: https://travis-ci.org/ktdreyer/errata-tool.svg?branch=master
          :target: https://travis-ci.org/ktdreyer/errata-tool

Example:

.. code-block:: python

    from errata_tool import Erratum

    e = Erratum(1234)

    print(e.errata_state)
    # prints "NEW_FILES"
