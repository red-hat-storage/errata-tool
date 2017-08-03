``errata-tool``
===============

.. image:: https://travis-ci.org/red-hat-storage/errata-tool.svg?branch=master
          :target: https://travis-ci.org/red-hat-storage/errata-tool

.. image:: https://badge.fury.io/py/errata-tool.svg
             :target: https://badge.fury.io/py/errata-tool

Modern Python API to Red Hat's Errata Tool.

python-errata-tool is a Python library that wraps the Errata Tool's REST API.
It uses `requests_kerberos <https://pypi.python.org/pypi/requests-kerberos>`_
to authenticate and parses JSON responses into ``Erratum`` objects. You can
use it to create new advisories, or read and update existing advisories. The
``ErratumConnector`` class also provides lower-level access to all of the
Errata Tool's REST API.

Example:

.. code-block:: python

    from errata_tool import Erratum

    e = Erratum(errata_id=1234)

    print(e.errata_state)
    # prints "NEW_FILES"

    print(e.url())
    # prints "https://errata.devel.redhat.com/advisory/1234"

Creating a new advisory:

.. code-block:: python

    e = Erratum(product='RHCEPH',
                release='RHCEPH-2-RHEL-7',
                synopsis='Red Hat Ceph Storage 2.1 bug fix update',
                topic='An update for Red Hat Ceph 2.1 is now available.',
                description='This update contains the following fixes ...',
                solution='Before applying this update...',
                qe_email='someone@redhat.com',
                qe_group='RHC (Ceph) QE',
                errata_type='RHBA',
                owner_email='kdreyer@redhat.com',
                manager_email='ohno@redhat.com',
                )
    e.commit()
    print(e.url())

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

Checking whether an advisory is text-only:

.. code-block:: python

    e = Erratum(errata_id=24075)

    if e.text_only:
        # it's text-only
    else:
        # it's not text-only

Adding builds:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.addBuilds(['ceph-10.2.3-17.el7cp'], release='RHEL-7-CEPH-2')

Changing state:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.setState('QE')

Changing docs reviewer:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.changeDocsReviewer('kdreyer@redhat.com')

Adding someone to the CC list:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.addCC('kdreyer@redhat.com')


Using the staging server
------------------------

To use the staging Errata Tool environment without affecting production, set
the ``ErrataConnector._url`` member variable to the staging URL.

.. code-block:: python

    from errata_tool import ErrataConnector, Erratum

    ErrataConnector._url = 'https://errata.stage.engineering.redhat.com/'
    # Now try something like creating an advisory, and it will not show up in
    # prod, or bother people with emails, etc.
    e = Erratum(product='RHCEPH',
                release='RHCEPH-2-RHEL-7',
                synopsis='Red Hat Ceph Storage 2.1 bug fix update',
                ...
                )
    e.commit()


Debugging many Errata Tool API calls
------------------------------------

Maybe your application makes many API calls (lots of advisories, builds, etc),
When processing large numbers of errata from higher-level tools, it's helpful
to understand where the time is spent to see if multiple calls can be avoided.

Set ``ErrataConnector.debug = True``, and then your connector object will
record information about each call it makes.  Each GET/PUT/POST is recorded,
along with totals / mean / min / max.

URL APIs are deduplicated based on their name, so two calls to different
errata on the same API is recorded as a single API.

To extract the information and print it, one might use PrettyTable:

.. code-block:: python

    e = Erratum(errata_id=24075)
    pt = PrettyTable()
    for c in ErrataConnector.timings:
        for u in ErrataConnector.timings[c]:
            pt.add_row([c, u,
                       ErrataConnector.timings[c][u]['count'],
                       ErrataConnector.timings[c][u]['total'],
                       ErrataConnector.timings[c][u]['mean'],
                       ErrataConnector.timings[c][u]['min'],
                       ErrataConnector.timings[c][u]['max']])
    print(pt.get_string())


SSL errors
----------

This library verifies the ET server's HTTPS certificate by default. This is
more of a python-requests thing, but if you receive an SSL verification error,
it's probably because you don't have the Red Hat IT CA set up for your Python
environment. Particularly if you're running this in a virtualenv, you'll want
to set the following configuration variable::

    REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt

Where "RH-IT-Root-CA.crt" is the public cert that signed the ET server's
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
