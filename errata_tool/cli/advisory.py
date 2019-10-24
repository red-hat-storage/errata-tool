from errata_tool.erratum import Erratum


def add_parser(subparsers):
    """Add our advisory parser to this top-level subparsers object. """
    group = subparsers.add_parser('advisory', help='Get or create an advisory')

    # advisory-level subcommands:
    sub = group.add_subparsers(dest='advisory_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('errata_id', help='advisory id, "12345"')
    get_parser.set_defaults(func=get)

    # "create"
    create_parser = sub.add_parser('create')
    create_parser.add_argument('--product', required=True,
                               help='eg. "RHCEPH"')
    create_parser.add_argument('--release', required=True,
                               help='eg. "rhceph-2.5"')
    create_parser.add_argument('--type', required=False,
                               choices=('RHSA', 'RHBA', 'RHEA'),
                               default='RHBA', help='eg. "RHBA"')
    create_parser.add_argument('--security-impact', required=False,
                               choices=('Low', 'Moderate', 'Important',
                                        'Critical'),
                               help='only required for RHSA')
    create_parser.add_argument('--synopsis', required=True,
                               help='eg. "Red Hat Product 2.1 bug fix update"')
    create_parser.add_argument('--topic', required=True,
                               help='eg. "An update for Red Hat Product 2.1 is'
                                    ' now available."')
    create_parser.add_argument('--description', required=True,
                               help='eg. "This update contains the following'
                                    ' fixes ..."')
    create_parser.add_argument('--solution', required=True,
                               help='eg. "Before applying this update..."')
    create_parser.add_argument('--qe-email', required=True,
                               help='eg. "someone@redhat.com"')
    create_parser.add_argument('--qe-group', required=True,
                               help='eg. "RHC (Ceph) QE"')
    create_parser.add_argument('--owner-email', required=True,
                               help='eg. "kdreyer@redhat.com"')
    create_parser.add_argument('--manager-email', required=True,
                               help='eg. "ohno@redhat.com"')
    create_parser.set_defaults(func=create)

    # "push"
    push_parser = sub.add_parser('push')
    push_parser.add_argument('errata_id', help='advisory id, "12345"')
    push_parser.add_argument('--target', choices=('stage', 'live'),
                             default='stage',
                             help='stage (default) or live')
    push_parser.set_defaults(func=push)

    # TODO:
    # "new-state"           Change erratum state
    # "add-bugs"            Add bugs to erratum
    # "remove-bugs"         Provide a list of bugs to remove from erratum
    # "add-builds"          Add build to erratum (you may specify nvr)
    # "remove-builds"       Remove build from erratum


def get(args):
    e = Erratum(errata_id=args.errata_id)
    print(e)


def push(args):
    e = Erratum(errata_id=args.errata_id)
    e.push(target=args.target)


def create(args):
    e = Erratum(product=args.product,
                release=args.release,
                errata_type=args.type,
                synopsis=args.synopsis,
                topic=args.topic,
                description=args.description,
                solution=args.solution,
                qe_email=args.qe_email,
                qe_group=args.qe_group,
                owner_email=args.owner_email,
                manager_email=args.manager_email,
                )
    if args.dry_run:
        env = 'prod'
        if args.stage:
            env = 'stage'
        print('DRY RUN: would create new advisory in %s:' % env)
        print('Product: %s' % args.product)
        print('Release: %s' % args.release)
        print('Erratum type: %s' % args.type)
        print('Synopsis: %s' % args.synopsis)
        print('Topic: %s' % args.topic)
        print('Description: %s' % args.description)
        print('Solution: %s' % args.solution)
        print('QE Email: %s' % args.qe_email)
        print('QE Group: %s' % args.qe_group)
        print('Owner Email: %s' % args.owner_email)
        print('Manager Email: %s' % args.manager_email)
        return
    e.commit()
    print(e)
