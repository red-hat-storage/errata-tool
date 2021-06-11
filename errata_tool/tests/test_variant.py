def test_id(rhceph_variant):
    assert rhceph_variant.id == 3085


def test_name(rhceph_variant):
    assert rhceph_variant.name == '8Base-RHCEPH-5.0-MON'


def test_description(rhceph_variant):
    assert rhceph_variant.description == 'Red Hat Ceph Storage 5.0 MON'


def test_url(rhceph_variant):
    assert rhceph_variant.url == \
        'https://errata.devel.redhat.com/variants/8Base-RHCEPH-5.0-MON'


def test_cpe(rhceph_variant):
    assert rhceph_variant.cpe == 'cpe:/a:redhat:ceph_storage:5::el8'
