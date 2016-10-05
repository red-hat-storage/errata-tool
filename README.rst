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

Checking whether an advisory is embargoed:

.. code-block:: python

    e = Erratum(errata_id=22986)

    if e.embargoed:
        # it's embargoed
    else:
        # it's not embargoed


SSL errors
----------

This library verifies the ET server's HTTPS certificate by default. This is
more of a python-requests thing, but if you receive an SSL verification error,
it's probably because you don't have the Red Hat IT CA set up for your Python
environment. Particularly if you're running this in a virtualenv, you'll want
to set the following configuration variable::

    REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt

Where "RH-IT-Root-CA.crt" is the public cert that signed the Chacra server's
HTTPS certificate.

When using RHEL 7's python-requests RPM, requests simply checks
``/etc/pki/tls/certs/ca-bundle.crt``, so you'll need to add the IT CA cert to
that big bundle file.

Building RPMs
-------------

Install fedpkg, then use the Makefile::

    $ make srpm

You can then upload the SRPM to Copr. Or, to build RPMs on your local
computer, using mock::

    $ make rpm


Changelog
---------
Check out the `CHANGELOG`_.

.. _CHANGELOG: CHANGELOG.rst
