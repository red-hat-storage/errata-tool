import pprint


def test_id(product):
    assert product.id == 104


def test_name(product):
    assert product.name == 'RHCEPH'


def test_description(product):
    assert product.description == 'Red Hat Ceph Storage'


def test_url(product):
    assert product.url == 'https://errata.devel.redhat.com/products/RHCEPH'


def test_product_releases_count(product):
    # Test against active async RHCEPH releases instead of all releases which
    # are quite numerous
    assert len(product.releases()) == 2


def test_product_releases_is_active(product):
    for release in product.releases():
        assert release.is_active is True
        assert release.enabled is True


def test_product_releases_is_async(product):
    for release in product.releases():
        assert release.type == 'Async'


def test_product_releases_release_date(product):
    for release in product.releases():
        assert release.internal_target_release is None
        assert release.ship_date is None
        assert release.zstream_target_release is None


def test_product_release_pretty_print(product):
    pretty_printer = pprint.PrettyPrinter()

    # Since there are only a few releases being tested, it's simpler to compare
    # the entire output than to compare each release in a loop
    output = '''[{'active': True,
  'allow_pkg_dupes': False,
  'blocker_flags': [],
  'description': 'Red Hat Ceph Storage Huge Debuginfo Subpackage',
  'enabled': True,
  'internal_target_release': None,
  'name': 'ceph-debuginfo',
  'product': 'RHCEPH',
  'product_versions': ['RHEL-7-CEPH-2', 'RHEL-7-CEPH-3'],
  'program_manager': None,
  'ship_date': None,
  'supports_component_acl': False,
  'type': 'Async',
  'zstream_target_release': None},
 {'active': True,
  'allow_pkg_dupes': False,
  'blocker_flags': [],
  'description': 'Red Hat Ceph Storage 3 ELS',
  'enabled': True,
  'internal_target_release': None,
  'name': 'rhceph-3-els',
  'product': 'RHCEPH',
  'product_versions': ['RHEL-7-RHCEPH-3-ELS'],
  'program_manager': 'coolmanager@redhat.com',
  'ship_date': None,
  'supports_component_acl': False,
  'type': 'Async',
  'zstream_target_release': None}]'''

    rendered = pretty_printer.pformat([
        release.render()
        for release in product.releases()
    ])

    assert rendered == output
