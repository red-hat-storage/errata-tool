def test_variants_count(product_version):
    assert len(product_version.variants()) == 3


def test_variant_names(product_version):
    variants = product_version.variants()
    assert variants[0].name == '7Server-RHEL-7-RHCEPH-3.1-MON'
    assert variants[1].name == '7Server-RHEL-7-RHCEPH-3.1-OSD'
    assert variants[2].name == '7Server-RHEL-7-RHCEPH-3.1-Tools'


def test_variant_descriptions(product_version):
    variants = product_version.variants()
    assert variants[0].description == 'Red Hat Ceph Storage 3.1 MON'
    assert variants[1].description == 'Red Hat Ceph Storage 3.1 OSD'
    assert variants[2].description == 'Red Hat Ceph Storage 3.1 Tools'


def test_cpe(product_version):
    variants = product_version.variants()
    for variant in variants:
        assert variant.cpe == 'cpe:/a:redhat:ceph_storage:3::el7'
