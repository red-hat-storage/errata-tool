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

Removing bugs:

.. code-block:: python

    e = Erratum(errata_id=22986)

    e.removeBugs([12345, 123678])

    # You can simply call "commit()" without checking the return code, or check
    # it and use refresh() to refresh our local instance data for the errata
    # advisory.
    need_refresh = e.commit()

    if need_refresh:
        print('refreshing')
        e.refresh()
