rhacm_versions = [
    ('1.0', '7'),
    ('2.0', '7'),
    ('2.1', '7'),
    ('2.2', '7'),
    ('2.3', '7'),
    ('1.0', '8'),
    ('2.0', '8'),
    ('2.1', '8'),
    ('2.2', '8'),
    ('2.3', '8'),
]


def test_rhacm_product_version_count(rhacm_product):
    assert len(rhacm_product.product_versions()) == 10


def test_rhacm_product_version_names(rhacm_product):
    for index, product_version in enumerate(rhacm_product.product_versions()):
        version, release = rhacm_versions[index]
        assert product_version.name == 'RHEL-%s-RHACM-%s' % (release, version)


def test_rhacm_product_version_descriptions(rhacm_product):
    for index, product_version in enumerate(rhacm_product.product_versions()):
        version, release = rhacm_versions[index]
        assert product_version.description == 'Red Hat Advanced Cluster ' + \
            'Management for Kubernetes %s for RHEL %s' % (version, release)


def test_rhacm_product_version_default_brew_tags(rhacm_product):
    for index, product_version in enumerate(rhacm_product.product_versions()):
        version, release = rhacm_versions[index]
        assert product_version.default_brew_tag == \
            'rhacm-%s-rhel-%s-container-candidate' % (version, release)
