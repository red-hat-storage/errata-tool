def test_id(variant):
    assert variant.id == 3085


def test_name(variant):
    assert variant.name == '8Base-RHCEPH-5.0-MON'


def test_description(variant):
    assert variant.description == 'Red Hat Ceph Storage 5.0 MON'


def test_url(variant):
    assert variant.url == \
        'https://errata.devel.redhat.com/variants/8Base-RHCEPH-5.0-MON'


def test_cpe(variant):
    assert variant.cpe == 'cpe:/a:redhat:ceph_storage:5::el8'
