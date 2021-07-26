from sys import stdout, version_info
import yaml
import warnings
from errata_tool.product import Product
from errata_tool.variant import Variant

MIN_PYTHON = (3, 7)
if version_info < MIN_PYTHON:
    warnings.warn("Run with Python 3.7+ for ordered YAML output")


def add_parser(subparsers):
    """Add our dump-config parser to this top-level subparsers object. """
    group = subparsers.add_parser('dump-config', help='Get a product')

    # dump-config-level subcommands:
    sub = group.add_subparsers(dest='dump-config_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('name', help='eg. "RHCEPH"')
    get_parser.set_defaults(func=get)


def get(args):
    product = Product(name=args.name)
    product_rendered = [product.render()]

    release_groups_rendered = []

    for release in product.releases():
        release_groups_rendered.append(release.render())

    cdn_repos_rendered = []
    for product_version in product_rendered[0]['product_versions']:
        for variant in product_version['variants']:
            for cdn_repo in Variant(name=variant['name']).cdn_repos():
                cdn_repos_rendered.append(cdn_repo.render())

    output = {
        'products': product_rendered,
        'release_groups': release_groups_rendered,
        'cdn_repos': sorted(cdn_repos_rendered, key=lambda x: x['name'])
    }

    yaml.dump(output, stdout, sort_keys=False)
