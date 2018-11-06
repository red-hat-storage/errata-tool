from errata_tool.product_version import ProductVersion


def test_id(product):
    assert product.id == 104


def test_name(product):
    assert product.name == 'RHCEPH'


def test_description(product):
    assert product.description == 'Red Hat Ceph Storage'


def test_supports_pdc(product):
    assert product.supports_pdc is True


def test_url(product):
    assert product.url == 'https://errata.devel.redhat.com/products/RHCEPH'


def test_product_versions(product):
    pvs = product.productVersions(enabled=1)
    assert pvs == [ProductVersion(803)]
