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
