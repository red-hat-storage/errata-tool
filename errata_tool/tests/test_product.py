def test_id(product):
    assert product.id == 104


def test_name(product):
    assert product.name == 'RHCEPH'


def test_description(product):
    assert product.description == 'Red Hat Ceph Storage'


def test_url(product):
    assert product.url == 'https://errata.devel.redhat.com/products/RHCEPH'
