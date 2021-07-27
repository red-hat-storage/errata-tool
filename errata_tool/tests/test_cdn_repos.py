import pprint


arches = [
    'ppc64le',
    's390x',
    'x86_64',
]

content_types = [
    ('debug-rpms',  'Debuginfo'),
    ('rpms',        'Binary'),
    ('source-rpms', 'Source'),
]


def repo_sets(repos):
    # Helper function to group RPM repos into sets of three (Debuginfo, Binary,
    # and Source) for easier looping
    return [repos[i:i + 3] for i in range(0, len(repos), 3)]


def test_cdn_repo_count(rhceph_variant):
    assert len(rhceph_variant.cdn_repos()) == 9


def test_cdn_repo_names(rhceph_variant):
    cdn_repos = rhceph_variant.cdn_repos()
    for repo_arch_index, repo_set in enumerate(repo_sets(cdn_repos)):
        for content_type_index, repo in enumerate(repo_set):
            assert repo.name == 'rhceph-5-mon-for-rhel-8-%s-%s' % \
                (arches[repo_arch_index],
                 content_types[content_type_index][0])


def test_cdn_repo_release_types(rhceph_variant):
    for repo in rhceph_variant.cdn_repos():
        assert repo.release_type == 'Primary'


def test_cdn_repo_content_types(rhceph_variant):
    cdn_repos = rhceph_variant.cdn_repos()
    for index, repo_set in enumerate(repo_sets(cdn_repos)):
        assert repo_set[index].content_type == content_types[index][1]


def test_cdn_repo_tps(rhceph_variant):
    for repo in rhceph_variant.cdn_repos():
        assert repo.use_for_tps is False


def test_cdn_repo_without_packages_pretty_print(rhceph_variant):
    pretty_printer = pprint.PrettyPrinter()
    cdn_repos = rhceph_variant.cdn_repos()

    for repo_arch_index, repo_set in enumerate(repo_sets(cdn_repos)):
        for content_type_index, repo in enumerate(repo_set):
            arch = arches[repo_arch_index]
            rpm_type = content_types[content_type_index][0]
            content_type = content_types[content_type_index][1]
            output = """{'arch': '%s',
 'content_type': '%s',
 'name': 'rhceph-5-mon-for-rhel-8-%s-%s',
 'release_type': 'Primary',
 'use_for_tps': False,
 'variants': ['8Base-RHCEPH-5.0-MON']}""" % \
                (arch, content_type, arch, rpm_type)

            assert pretty_printer.pformat(repo.render()) == output


def test_cdn_repo_with_containers_pretty_print(rhacm_variant):
    pretty_printer = pprint.PrettyPrinter()
    cdn_repos = rhacm_variant.cdn_repos()

    repos = [
        ('management-ingress', 'management-ingress'),
        ('openshift-hive', 'openshift-hive-operator'),
        ('search-aggregator', 'search-aggregator'),
    ]

    for index, repo in enumerate(repos):
        name, container = repo
        pad = ' ' * (len(container))
        output = """{'arch': 'multi',
 'content_type': 'Docker',
 'name': 'redhat-rhacm2-%s-rhel7',
 'packages': {'%s-container': ['v{{version(2)}}',
%s                             '{{version}}',
%s                             '{{version}}-{{release}}']},
 'release_type': 'Primary',
 'use_for_tps': False,
 'variants': ['7Server-RHACM-2.0',
              '7Server-RHACM-2.1',
              '7Server-RHACM-2.2',
              '7Server-RHACM-2.3']}""" % (name, container, pad, pad)

        assert pretty_printer.pformat(cdn_repos[index].render()) == output
