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

Getting an errata's name:

.. code-block:: python

    e = Erratum(errata_id=22986)

    print(e.errata_name)
    # prints "RH*A-YYYY:NNNNN", for example "RHBA-2018:12345"

Adding bugs:

.. code-block:: python

    e = Erratum(errata_id=22986)

    e.addBugs([12345, 123678])

    e.commit()

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

    # For non-PDC advisories, the "release" kwarg is the Errata Tools's
    # "product version", in composedb, for example "RHEL-7-CEPH-2".
    # For PDC advisories, the "release" kwarg is the PDC identifier,
    # for example "rhceph-2.4@rhel-7".
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


Working with products
---------------------

The ``errata_tool.product.Product`` class can look up existing products.

Looking up a product:

.. code-block:: python

    from errata_tool.product import Product

    p = Product('RHCEPH')
    print(p.id)  # 104
    print(p.name)  # "RHCEPH"
    print(p.description)  # "Red Hat Ceph Storage"
    print(p.supports_pdc)  # True


Working with releases
---------------------

The ``errata_tool.release.Release`` class can look up existing releases or
create new release entries.

Looking up a release:

.. code-block:: python

    from errata_tool.release import Release

    r = Release(name='rhceph-2.4')
    print(r.id)  # 792
    print(r.name)  # "rhceph-2.4"
    print(r.description)  # "Red Hat Ceph Storage 2.4"
    print(r.type)  # "QuarterlyUpdate"
    print(r.is_active)  # True
    print(r.enabled)  # True
    print(r.blocker_flags)  # ['ceph-2.y', 'pm_ack', 'devel_ack', 'qa_ack']
    print(r.is_pdc)  # True
    print(r.edit_url)  # https://errata.devel.redhat.com/release/edit/792

Creating a new release (this requires the "releng" role in the Errata Tool):

.. code-block:: python

    from errata_tool.release import Release
    r = Release.create(
        name='rhceph-3.0',
        product='RHCEPH',
        type='QuarterlyUpdate',
        program_manager='anharris',
        blocker_flags='ceph-3.0',
    )
    print('created new rhceph-3.0 release')
    print('visit %s to add PDC associations' % r.edit_url)


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

If you've already added the Red Hat IT CA to your system-wide bundle, you can
have your Python code always use this file:

.. code-block:: python

    if 'REQUESTS_CA_BUNDLE' not in os.environ:
        os.environ['REQUESTS_CA_BUNDLE'] = '/etc/pki/tls/certs/ca-bundle.crt'

This will make requests behave the same inside or outside your virtualenv. In
other words, with this code, your program will always validate the Red Hat IT
CA.

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
