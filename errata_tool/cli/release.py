import sys
import posixpath
from errata_tool.connector import ErrataConnector
from errata_tool.release import Release
from errata_tool.release import NoReleaseFoundError


def add_parser(subparsers):
    """Add our release parser to this top-level subparsers object. """
    group = subparsers.add_parser('release',
                                  help='Get or create a release (RCM)')

    # release-level subcommands:
    sub = group.add_subparsers(dest='release_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get', help='get a release')
    get_parser.add_argument('name', help='eg. "rhceph-2.4"')
    get_parser.set_defaults(func=get)

    # "create"
    # There are many arguments to create(), and they might change over time.
    # Use named args here for future flexibility.
    create_parser = sub.add_parser('create', help='create a new release (RCM)')
    create_parser.add_argument('--name', required=True,
                               help='eg. "rhceph-2.4"')
    create_parser.add_argument('--product', required=True,
                               help='eg. "RHCEPH"')
    create_parser.add_argument('--product_version', required=True,
                               action='append',
                               help='eg. "RHEL-7-CEPH-3"')
    create_parser.add_argument('--type', required=True,
                               help='eg. "QuarterlyUpdate"')
    create_parser.add_argument('--program_manager', required=True,
                               help='eg. "anharris"')
    create_parser.add_argument('--blocker_flags', required=True,
                               help='eg. "ceph-2.y"')
    create_parser.add_argument('--default_brew_tag', required=True,
                               help='eg. "ceph-3.0-rhel-7-candidate"')
    create_parser.set_defaults(func=create)

    # "list-advisories"
    ls_parser = sub.add_parser('list-advisories',
                               help='list advisories for this release')
    ls_parser.add_argument('name', help='eg. "rhceph-2.4"')
    ls_parser.set_defaults(func=list_advisories)
    ls_parser.add_argument('--status', required=False,
                           choices=('NEW_FILES', 'QE', 'REL_PREP',
                                    'IN_PUSH', 'SHIPPED_LIVE', 'OPEN'),
                           help='optionally filter by status')


def get(args):
    try:
        r = Release(name=args.name)
        print('Name: %s' % r.name)
        print('Description: %s' % r.description)
        print('URL: %s' % r.url)
    except NoReleaseFoundError:
        print('%s release not found' % args.name)
        sys.exit(1)


def create(args):
    try:
        r = Release(name=args.name)
        print('%s is already defined at %s' % (r.name, r.url))
        sys.exit(1)
    except NoReleaseFoundError:
        pass
    if args.dry_run:
        print('DRY RUN: would create new release:')
        print('Name: %s' % args.name)
        print('Product: %s' % args.product)
        print('Product Versions: %s' % args.product_version)
        print('Type: %s' % args.type)
        print('Program manager: %s' % args.program_manager)
        print('Blocker flags: %s' % args.blocker_flags)
        print('Default Brew tag: %s' % args.default_brew_tag)
        return
    r = Release.create(
        name=args.name,
        product=args.product,
        product_versions=args.product_version,
        type=args.type,
        program_manager=args.program_manager,
        blocker_flags=args.blocker_flags,
        default_brew_tag=args.default_brew_tag,
    )
    print('created new %s release' % args.name)
    print('visit %s to edit further' % r.edit_url)


def list_advisories(args):
    try:
        r = Release(name=args.name)
    except NoReleaseFoundError:
        print('%s release not found' % args.name)
        sys.exit(1)
    advisories = r.advisories()
    if args.status == 'OPEN':  # an alias meaning "all open statuses"
        interested_status = ['NEW_FILES', 'QE', 'REL_PREP', 'IN_PUSH']
    else:
        interested_status = [args.status]

    if args.status:
        advisories = [a for a in advisories if a['status']
                      in interested_status]
        if not advisories:
            print('no %s advisories found for release %s' % (args.status,
                                                             args.name))
    else:
        if not advisories:
            print('no advisories found for release %s' % args.name)
    for advisory in advisories:
        # hack, avoid initializing the full Erratum class just to get the URL:
        url = posixpath.join(ErrataConnector._url, 'errata',
                             str(advisory['id']))
        print('------------------------------')
        print('URL: %s' % url)
        print('synopsis: %s' % advisory['synopsis'])
        print('status: %s' % advisory['status'])
