import pprint

def test_id(product_version):
    assert product_version.id == 783


def test_name(product_version):
    assert product_version.name == 'RHEL-7-RHCEPH-3.1'


def test_description(product_version):
    expected = 'Red Hat Ceph Storage 3.1'
    assert product_version.description == expected


def test_released_builds(product_version):
    builds = product_version.releasedBuilds()
    assert isinstance(builds, list)
    # Check for an expected ceph NVR.
    expected = 'ceph-12.2.5-42.el7cp'
    found = [build for build in builds if build['build'] == expected]
    assert found[0] == {'build': expected,
                        'errata_id': 33840,
                        'created_at': "2018-09-26T18:17:33Z",
                        'updated_at': "2018-09-26T18:17:33Z",
                        }


def test_product_version_pretty_print(product_version):
    pretty_printer = pprint.PrettyPrinter()
    output = """{'brew_tags': ['ceph-3.1-rhel-7-candidate'],
 'default_brew_tag': 'ceph-3.1-rhel-7-candidate',
 'description': 'Red Hat Ceph Storage 3.1',
 'enabled': False,
 'is_server_only': True,
 'name': 'RHEL-7-RHCEPH-3.1',
 'push_targets': ['ftp', 'cdn_stage', 'cdn_docker_stage', 'cdn_docker', 'cdn'],
 'rhel_release_name': 'RHEL-7',
 'sig_key_name': 'redhatrelease2',
 'variants': [{'description': 'Red Hat Ceph Storage 3.1 MON',
               'enabled': True,
               'name': '7Server-RHEL-7-RHCEPH-3.1-MON',
               'push_targets': ['cdn_stage', 'cdn'],
               'rhel_variant': '7Server',
               'tps_stream': 'RHEL-7-Main-Server'},
              {'description': 'Red Hat Ceph Storage 3.1 OSD',
               'enabled': True,
               'name': '7Server-RHEL-7-RHCEPH-3.1-OSD',
               'push_targets': ['cdn_stage', 'cdn'],
               'rhel_variant': '7Server',
               'tps_stream': 'RHEL-7-Main-Server'},
              {'description': 'Red Hat Ceph Storage 3.1 Tools',
               'enabled': True,
               'name': '7Server-RHEL-7-RHCEPH-3.1-Tools',
               'push_targets': ['cdn_stage', 'cdn'],
               'rhel_variant': '7Server',
               'tps_stream': 'RHEL-7-Main-Server'}]}"""

    assert pretty_printer.pformat(product_version.render()) == output
