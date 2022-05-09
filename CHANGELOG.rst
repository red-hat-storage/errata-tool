v1.27.1
=======

* The ``render()`` method on the ``ProductVersion`` class now displays the
  ``allow_rhn_debuginfo`` value for each Product Version. The ``dump-config``
  command now prints this configuration setting.

v1.27.0
=======

* Erratum instances have a new ``.jira_issues`` attribute. This is a list of
  the jira ticket IDs attached to the advisory.


v1.26.0
=======
* CLI: do not print duplicate CDN repositories in ``dump-config`` sub-command.

* README: Fix code examples for ``metadataCdnRepos()`` and
  ``textOnlyRepos()``.

v1.25.0
=======
* CLI: add a new ``dump-config`` sub-command. This makes it easier to dump a
  product's existing Errata Tool configuration into a format that Ansible can
  read later. This makes it easier for release engineers to transition
  products to use errata-tool-ansible.

* Add a new ``releases()`` method to the ``Product`` class. This returns a
  list of releases associated with a product.

* Add a new ``render()`` method to the ``Release`` class. This makes it easier
  to obtain the data from this class in a structured way.

v1.24.0
=======
* Replace requests-kerberos dependency with requests-gssapi. requests-kerberos
  is not well-maintained upstream and Fedora is dropping it entirely.
  requests-gssapi is an up-to-date replacement.

* Remove the ``._username`` property from the ``ErrataConnector`` class. The
  purpose of this property was to discover the Kerberos username. This is
  unnecessary and difficult to support with the switch to
  python-requests-gssapi.

* Add a new ``product_versions()`` method to the ``Product`` class. This
  returns a list of product versions associated with a product.

* Update ``Product`` and ``ProductVersion`` classes to use the Errata Tool's
  newer v1 API endpoints. This provides more data fields on these classes.

* Add a new ``render()`` method to the ``Product``, ``ProductVersion``, and
  ``Variant`` classes. This makes it easier to obtain the data from these
  classes in a structured way.

* Make the unit test suite pass on EPEL 7's pytest 2.7.0.

v1.23.0
=======
* Add a new ``CdnRepo`` class to represent Errata Tool CDN repository records.
  Add a new ``cdn_repos()`` method to the ``Variant`` class to find a list of
  cdn repos associated with a product variant.

* Add a new ``variants()`` method to the ``ProductVersion`` class to find
  the list of variants associated with a product version.

* Add a new ``params`` kwarg to the ``ErrataConnector._get()`` method. This
  properly encodes values for query strings in GET urls.

* Handle "+" characters in ``Release`` names.

* Fix the ability to modify owner emails and manager emails on existing
  advisories with ``Erratum.update(owner_email=<value>)`` or
  ``Erratum.update(manager_email=<value>)``.

* Improve project CI with GitHub Actions and codecov.io.

* Fix warnings in RPM packaging

v1.22.0
=======
* Respect the batch_id for an ``Erratum`` attribute when calculating
  ``.publish_date`` and the class ``str`` representation. The
  ``errata-tool advisory get <advisory_id>`` command now shows the batch ID if
  the advisory is part of a batch update.

* Fix the ability to set a new severity value on existing advisories with
  ``Erratum.update(security_impact=<value>)``.

* CLI: code optimization make it easier to add new sub-commands.

* RPM packaging is Python 3-only on Fedora and RHEL 8.

v1.21.0
=======

* Lazy-load full Erratum information within the ``Build`` class.
  Prior to this change, when users queried a build, python-errata-tool would
  immediately load a lot of information about every advisory for that build.
  With this change, the ``Build`` class only loads the full advisories when
  users access the ``.released_errata`` property.

  Users can also access the advisory ID numbers without loading all of the
  information about each advisory. This change adds two new properties to the
  ``Build`` class: ``.released_errata_id`` and ``.all_errata_ids``.

* Get paginated data in the ``Erratum.externalTests()`` method. Prior to this
  change, ``externalTests()`` would only return the first few test results.
  The ``externalTests()`` method now returns the entire list of test results.

* CLI: add a ``--status OPEN`` alias to the
  ``errata-tool release list-advisories`` command. This allows users to list
  all the in-progress advisories for a release.

* Erratum: fix a crash when the Errata Tool returns ``None`` for a
  SHIPPED_LIVE advisory's ``actual_ship_date``.

* Clean up API documentation

* Test suite improvements

v1.20.0
=======

This release deletes all references to PDC (rhbz#1692965). In particular this
removes:

* The ``.is_pdc`` attribute from ``Release`` class

* The ``.supports_pdc`` attribute from ``Product`` class

* Support for reading or updating PDC-type advisories (``Erratum`` class)

v1.19.0
=======

* Add a new ``.get_erratum_data()`` method to the ``Erratum`` class to
  query the server's JSON for an advisory. Use this when debugging
  interactions with the Errata Tool or when passing this data on to other
  non-Python tools.

* Add a new ``.publish_date_override`` attribute to the ``Erratum`` class to
  get the overridden date for an advisory.

v1.18.0
=======

* Make the ``.package_owner_email`` attribute to the ``Erratum`` class
  correspond to the Errata Tool's "package owner" for an advisory. Prior to
  this change, ``.package_owner_email`` was the advisory reporter, not the
  package owner.

* Add a new ``.reporter`` attribute to the ``Erratum`` class to
  get the reporter email address for an advisory.

v1.17.0
=======

* Add a new ``.manager_id`` attribute to the ``Erratum`` class to
  get the manager for an advisory. You can now optionally set the manager for
  a new advisory using the manager ID number instead of an email address. This
  makes it easier to clone advisories.

* Fix the ``__str__`` method for the ``User`` class to print a real value
  instead of crashing.

v1.16.0
=======

* Add a new ``.releasedBuilds()`` method to the ``ProductVersion`` class to
  query all the released builds for this Product Version.

* Add a new ``.product_versions`` attribute to the ``Release`` class to
  get the Product Versions for a release.

* Improve debugging information for HTTP errors.

* Add API documentation for ``push()`` and ``addBuilds()`` methods.

* Fix an argparse crash in the errata-tool CLI when running on Python 3.

v1.15.0
=======

* Add a new ``.text_only_cpe`` attribute to the ``Erratum`` class to
  get or set the CPE text for a text-only RHSA.

v1.14.0
=======

* Add a new ``.textOnlyRepos()`` method to the ``Erratum`` class to set or
  get the CDN repositories for a text-only advisory.

* Add a new ``.batch_id`` attribute to the ``Erratum`` class to
  identify batches for an advisory.

* Add a new ``.cve_names`` attribute to the ``Erratum`` class to
  identify CVEs for an advisory.

* Add API documentation at https://errata-tool.readthedocs.io/en/latest/

v1.13.0
=======

* Add a new ``.missing_prod_listings`` attribute to the ``Erratum`` class to
  find builds on an advisory that lack any product listings.

* When receiving an HTTP 500 response from the Errata Tool, add the server's
  specific message to the ``ErrataException`` that we raise. This allows
  callers to discover the specific error details.

v1.12.0
=======

* Add new ``Build`` and ``ProductVersion`` classes

* Add new ``build`` CLI sub-command to query builds by NVR

* The ``create()`` method to the ``Release`` class always creates non-PDC
  releases now.

v1.11.3
=======

* Build system: install errata_tool.cli

v1.11.2
=======

* Build system: fix syntax error in Makefile

v1.11.1
=======

* Build system: avoid stray files in tarball during sdist build

v1.11.0
=======

* Add RHSA support (new ``security_impact`` kwarg when creating advisories)

* Add a new ``reloadBuilds()`` method to the ``Erratum`` class to reload an
  advisory's product listings.

* Discover the Kerberos username in the ``ErrataConnector`` class.

* Add a new ``.content_types`` attribute to the ``Erratum`` class to discover
  if an advisory is an RPM or Docker advisory.

* Add a new ``metadataCdnRepos()`` method to the ``Erratum`` class to set or
  get the CDN repositories for a container advisory.

* Add a new ``externalTests()`` method to the ``Erratum`` class to discover the
  state of RPMDiff tests.

* Add a new ``advisories()`` method to the ``Release`` class to discover all
  advisories for a release.

* Add a new ``push()`` method to the ``Erratum`` class to push content to the
  stage or live CDN.

* Add basic ``errata-tool`` CLI.

* Several documentation fixes

v1.10.0
=======

* Add new Product, User, and Release classes

* Disable mutual auth for all HTTPS requests

* Code linting cleanup

* Include tests and license in source distribution

* Remove rpmdiff support (rpmdiff is now decoupled from ET)

* More examples in README

v1.9.0
======

* Fix traceback in ``ProductList`` if a release has no versions associated.

* Fix ability to change an existing advisory to be text-only or non-text-only.

* Basic PDC support: Gracefully handle PDC prefixes for advisory types.

v1.8.2
======

* New project URL: https://github.com/red-hat-storage/errata-tool

* Avoid re-adding the RHSA severity prefix to an advisory's synopsis when
  making unrelated updates.

v1.8.1
======

* Fix setuptools packaging problem with latest requests and urllib3.

v1.8.0
======

* Add ``.creation_date``, ``.ship_date``, and ``.age`` attributes to
  advisories.

  Age is the number of days between creation and ship date,
  or creation date and "today" if an erratum is not shipped.

  This is useful for assembling historical data.

* Product list functional changes

  1) Fetch all versions and releases for active products,
     even disabled ones,
  2) Assume users don't want inactive versions or releases,
     but allow them to query them using disabled=True when
     passed to get_versions() and get_releases()
  3) Allow users to drop certain releases if they want,
  4) Don't muck with async releases by default.

  Product table version bumped since 'enabled' is now part
  of version/release information.

* Add new ``addCC()`` method to advisories.  Use this to add someone to the CC
  list for an advisory.

v1.7.0
======

* Add ``changeDocsReviewer()`` method to set the docs reviewer on advisories.

* Add product, release, and version handling (new ``ProductList`` class).

* Add Python 3 support.

* Build both python2 and python3 subpackages on Fedora so that
  errata-tool can be integrated with other py2 libraries and scripts.

* Add basic unit tests.

* Fix code examples in README.

v1.6.1
======

* When creating or updating an advisory, do not update the QE Owner or QE Group
  if ``qe_email`` or ``qe_group`` have been set to empty strings.

v1.6.0
======

* Centralize URL construction logic in ``connector.py``. Methods can now
  use ErrataConnector's ``canonical_url()`` to determine the proper URL for an
  API endpoint.

* Document ``setState()`` method, and give an example of setting an advisory to
  "QE" state.

* Add ``addFlags()`` and ``removeFlags()`` Erratum methods.

* Add ship target (``published_date_override``) to Erratum debug output.

* Support setting an Erratum's QE group.

v1.5.1
======

* Document example of using the staging ET server

v1.5.0
======

* Drop the client-side check to make sure advisory was NEW_FILES before it
  would attempt to change anything.

  This appears to be a legacy check that is no longer needed. We now let the
  Errata Tool return server-side errors if an update is not allowed.

v1.4.1
======

* connector: Fix logic causing extraneous tracebacks on PUT/POST

* Allow setting to REL_PREP state

v1.4.0
======

* Add errata call timings (see ``ErrataConnector.debug`` and
  ``ErrataConnector.timings`` documentation in README)

v1.3.0
======

* Add needs_distqa flag checking

* Don't double-add builds (avoids traceback)

* ``ErrataConnector`` is now a proper new-style class, to make it easier to
  inherit with child classes.

* packaging: ``setup.py bump`` now takes a --version flag, to make it easier to
  adopt semver

v1.2.6
======

* New internal method you may want to override in a subclass:
  ``Erratum._check_bugs()``

* If an advisory is an RHSA, the ``current_flags`` attribute can contain
  either ``request_security`` or ``needs_security``.

v1.2.5
======

* Remove extra print from ``errataum.addBuildsDirect()``

v1.2.4
======

* Refactor Erratum's internal `_fetch` method (code reorganization). This will
  make it easier to subclass and extend functionality. New internal methods you   may want to override:

  * ``Erratum._cache_bug_info()``

  * ``Erratum._need_rel_prep()``

v1.2.3
======

* Prepend exceptions with erratum ID if possible

v1.2.2
======

* Erratum instances have a new ``.text_only`` attribute that is ``True`` if an
  advisory is text-only, and ``False`` if an advisory is a "normal" one. This
  attribute is writable, and you can also set the ``text_only=True`` kwarg
  during the ``Erratum`` constructor when creating an entirely new advisory.

v1.2.1
======

* Erratum instances have a new ``.embargoed`` attribute that is ``True`` if an
  advisory is embargoed, and ``False`` if an advisory is not embargoed.

v1.2.0
======

* ``addBuilds()`` handles non-RPMs.

* add ``setFileInfo()``

* This release changes the signature of ``addBuilds()`` slightly. Prior to this
  release, you could call it like so:

  .. code-block:: python

    advisory.addBuilds(['build1', 'build2'], product_version)

  After this change, release must be specified as a kwarg:

  .. code-block:: python

      advisory.addBuilds(['build1', 'build2'], release=product_version)

v1.1.1
======

* RPM packaging fixes

* Add full MIT license text to git repository and packaging

v1.1.0
======

* More documentation in README

* Verify HTTPS certs by default

* Fix flake8 style errors

* Add bare-bones test suite

* Remove RHOS-specific calls to ``syncBugs()``

v1.0.0
======

* Initial release
