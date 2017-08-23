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
