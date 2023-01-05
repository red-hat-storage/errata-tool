``errata-tool``
===============

.. image:: https://github.com/red-hat-storage/errata-tool/workflows/tests/badge.svg
             :target: https://github.com/red-hat-storage/errata-tool/actions

.. image:: https://badge.fury.io/py/errata-tool.svg
             :target: https://badge.fury.io/py/errata-tool

.. image:: https://codecov.io/gh/red-hat-storage/errata-tool/branch/master/graph/badge.svg
             :target: https://codecov.io/gh/red-hat-storage/errata-tool


Modern Python API to Red Hat's Errata Tool.

python-errata-tool is a Python library that wraps the Errata Tool's REST API.
It uses `requests_gssapi <https://pypi.python.org/pypi/requests-gssapi>`_
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

Creating a new bugfix advisory:

.. code-block:: python

    e = Erratum(product='RHCEPH',
                release='rhceph-2.1',
                #errata_type='RHBA'         # Default; may be omitted
                synopsis='Red Hat Ceph Storage 2.1 bug fix update',
                topic='An update for Red Hat Ceph 2.1 is now available.',
                description='This update contains the following fixes ...',
                solution='Before applying this update...',
                qe_email='someone@redhat.com',
                qe_group='RHC (Ceph) QE',
                owner_email='kdreyer@redhat.com',
                manager_email='ohno@redhat.com',
                )
    e.commit()
    print(e.url())

Creating a new enhancement (feature) advisory:

.. code-block:: python

    e = Erratum(product='RHCEPH',
                release='rhceph-2.1',
                errata_type='RHEA',          # Set to RHEA for RHEA
                synopsis='Red Hat Ceph Storage 2.1 enhancement update',
                topic='An update for Red Hat Ceph 2.1 is now available.',
                description='This update contains the following features ...',
                solution='Before applying this update...',
                qe_email='someone@redhat.com',
                qe_group='RHC (Ceph) QE',
                owner_email='kdreyer@redhat.com',
                manager_email='ohno@redhat.com',
                )
    e.commit()
    print(e.url())

Creating a new security advisory. Note that RHSA (Security)
advisories are given one of four impacts (Low, Moderate,
Important, and Critical). See this link for more information:
https://access.redhat.com/security/updates/classification

.. code-block:: python

    e = Erratum(product='RHCEPH',
                release='rhceph-2.1',
                errata_type='RHSA',          # Set to RHSA for RHSA
                security_impact='Moderate',  # Required for RHSA
                synopsis='Red Hat Ceph Storage 2.1 security update',
                topic='An update for Red Hat Ceph 2.1 is now available.',
                description='This update contains the following fixes ...',
                solution='Before applying this update...',
                qe_email='someone@redhat.com',
                qe_group='RHC (Ceph) QE',
                owner_email='kdreyer@redhat.com',
                manager_email='ohno@redhat.com',
                )
    e.commit()
    print(e.url())


errata-tool command-line interface
----------------------------------

The ``errata-tool`` CLI is a thin wrapper around the classes. You can use it to
query information from the Errata Tool or create new releases (releng)::

    errata-tool -h

    usage: errata-tool [-h] [--stage] [--dry-run] {advisory,product,release} ...

    positional arguments:
      {advisory,product,release}
        advisory            Get or create an advisory
        product             Get a product
        release             Get or create a release (RCM)

    optional arguments:
      --stage               use staging ET instance
      --dry-run             show what would happen, but don't do it

errata-tool command-line interface examples
-------------------------------------------

Waiting and conditionally pushing an advisory:

As a release engineer one often checks the status of an advisory if it is ready
to be pushed. To avoid human polling of the state and to automate the advisory
push two options are provided under the ``errata-tool advisory push`` option::

    errata-tool advisory push --help
    usage: errata-tool advisory push [-h] [--target {stage,live}]
    [--wait-for-state {SHIPPED_LIVE,PUSH_READY}] [--push-when-ready]
    [--verbose] errata_id

    positional arguments:
      errata_id             advisory id, "12345"

    optional arguments:
      -h, --help            show this help message and exit
      --target {stage,live}
                            stage (default) or live
      --wait-for-state {SHIPPED_LIVE,PUSH_READY}
                            state : PUSH_READY or SHIPPED_LIVE
      --push-when-ready     Push if the advisory enters state PUSH_READY
      --verbose             print current state of the advisory

The ``--wait-for-state`` option polls at regular interval for the advisory to
enter one of the two desired states - PUSH_READY or SHIPPED_LIVE

when the advisory reaches that state the polling stops and the script exits with
a successful exit code ``$? eq 0``.

Caveat: The script will wait forever until that state is reached or interrupted
by the user. The option to have a cap on the wait time was dropped to keep the
usage simple and for the lack of a compelling use case.


The ``--push-when-ready`` option pushes the advisory if it is in  PUSH_READY
state. The ``--push-when-ready`` option can be used with ``--wait-for-state``
option to repeatedly poll the advisory until it reaches PUSH_READY state before
pushing it.
Here are some usecases:

- usecase 1: Push advisory if it is in state PUSH_READY state


.. code-block:: bash

    errata-tool --stage advisory push --target live --push-when-ready 12345


- usecase 2: Wait for advisory to enter PUSH_READY state and push the advisory


.. code-block:: bash

    errata-tool --stage advisory push --target live  --push-when-ready \
    --wait-for-state PUSH_READY 12345


- usecase 3: Wait for advisory to enter SHIPPED_LIVE, push the advisory if
               it enters PUSH_READY state while waiting.


.. code-block:: bash

    errata-tool --stage advisory push --target live  --push-when-ready \
    --wait-for-state SHIPPED_LIVE 12345


- usecase 4: Push independent advisories before pushing those which are
           dependent on the independent advisories

           See: https://issues.redhat.com/browse/SPMM-9887

.. code-block:: bash

    # Ship advisory 12346 after shipping 12345
    errata-tool --stage advisory push --target live  --push-when-ready \
    --wait-for-state SHIPPED_LIVE 12345 && \
    errata-tool --stage advisory push --target live  --push-when-ready \
    --wait-for-state PUSH_READY 12346

More Python Examples
--------------------

Getting an erratum's name:

.. code-block:: python

    e = Erratum(errata_id=22986)

    print(e.errata_name)
    # prints "RH*A-YYYY:NNNNN", for example "RHBA-2018:12345"

Adding bugs:

.. code-block:: python

    e = Erratum(errata_id=22986)

    e.addBugs([12345, 123678])

    e.commit()

    # You can read the current list of bugs with the "e.errata_bugs" property.

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
        # If it's an RHSA, you may want to get/set e.text_only_cpe here.
    else:
        # it's not text-only

Adding builds:

.. code-block:: python

    e = Erratum(errata_id=24075)

    # The "release" kwarg is the Errata Tools's "product version" in
    # composedb, for example "RHEL-7-CEPH-2".
    e.addBuilds(['ceph-10.2.3-17.el7cp'], release='RHEL-7-CEPH-2')

Adding container builds:

.. code-block:: python

    e = Erratum(errata_id=34279)

    # For non-RPM Brew builds, you must specify the file_types kwarg.
    # For container builds, this is "tar".
    e.addBuilds('rhceph-rhel7-container-3-9',
                release='RHEL-7-CEPH-3',
                file_types={'rhceph-rhel7-container-3-9': ['tar']})

Changing state:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.setState('QE')
    e.commit()

Changing docs reviewer:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.changeDocsReviewer('kdreyer@redhat.com')

Adding someone to the CC list:

.. code-block:: python

    e = Erratum(errata_id=24075)

    e.addCC('kdreyer@redhat.com')

Changing an advisory type:

.. code-block:: python

    e = Erratum(errata_id=33840)

    e.update(errata_type='RHBA')
    e.commit()

Reloading the all specific builds that lack product listings:

.. code-block:: python

    e = Erratum(errata_id=24075)

    if e.missing_product_listings:  # a (possibly-empty) list of build NVRs
        result = e.reloadBuilds(no_rpm_listing_only=True)
        # result is a dict for this job tracker

Determining if an advisory has RPMs or containers:

.. code-block:: python

    e = Erratum(errata_id=24075)

    content_types = e.content_types
    # result is a list, like ["rpm"], or ["docker"]

Get active RPMDiff results for an advisory:

.. code-block:: python

    e = Erratum(errata_id=24075)

    bad = []
    for result in e.externalTests(test_type='rpmdiff'):
        if result['attributes']['status'] not in ('PASSED', 'WAIVED'):
            # See result['attributes']['external_id'] for the integer to pass
            # into RPMDiff's run API.
            bad.append(result)


Set the CDN repos for a container advisory (only applies for advisories
containing Docker images):

.. code-block:: python

    e = Erratum(errata_id=24075)

    assert 'docker' in e.content_types
    e.metadataCdnRepos(enable=['rhel-7-server-rhceph-3-mon-rpms__x86_64'])

Same thing, but for text-only advisories:

.. code-block:: python

    e = Erratum(errata_id=24075)

    assert e.text_only
    e.textOnlyRepos(enable=['rhel-7-server-rhceph-3-mon-rpms__x86_64'])


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
    print(r.edit_url)  # https://errata.devel.redhat.com/release/edit/792

Finding all "NEW_FILES" advisories for a release:

.. code-block:: python

    from errata_tool.release import Release

    rel = Release(name='rhceph-3.0')

    advisories = rel.advisories()
    new_files = [a for a in advisories if a['status'] == 'NEW_FILES']
    print(new_files)  # prints the list of advisories' data

Creating a new release (this requires the "releng" role in the Errata Tool):

.. code-block:: python

    from errata_tool.release import Release
    r = Release.create(
        name='rhceph-3.0',
        product='RHCEPH',
        product_versions=['RHEL-7-CEPH-3'],
        type='QuarterlyUpdate',
        program_manager='anharris',
        blocker_flags='ceph-3.0',
        default_brew_tag='ceph-3.0-rhel-7-candidate',
    )
    print('created new rhceph-3.0 release')
    print('visit %s to edit further' % r.edit_url)


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
                release='rhceph-2.1',
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
