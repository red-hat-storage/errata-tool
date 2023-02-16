from errata_tool.erratum import Erratum
from errata_tool.bug import Bug
from time import sleep


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
    push_parser.add_argument(
        '--wait-for-state',
        choices=(
            'SHIPPED_LIVE',
            'PUSH_READY'),
        help='state : PUSH_READY or SHIPPED_LIVE')
    push_parser.add_argument(
        '--push-when-ready',
        action='store_true',
        help='Push if the advisory enters state PUSH_READY')
    push_parser.add_argument('--verbose', action='store_true',
                             help='print current state of the advisory')
    push_parser.set_defaults(func=push)

    add_bugs_parser = sub.add_parser('add-bugs')
    add_bugs_parser.add_argument('errata_id', help='advisory id, "12345"')
    add_bugs_parser.add_argument(
        '--bug-ids', required=True, help='bugzilla bug ids, "12345"', nargs='+'
    )
    add_bugs_parser.set_defaults(func=add_bugs)

    # TODO:
    # "new-state"           Change erratum state
    # "remove-bugs"         Provide a list of bugs to remove from erratum
    # "add-builds"          Add build to erratum (you may specify nvr)
    # "remove-builds"       Remove build from erratum


def add_bugs(args):
    e = Erratum(errata_id=args.errata_id)
    bugs_to_attach = []
    for bug_id in args.bug_ids:
        bug = Bug(bug_id)
        if args.errata_id in bug.all_advisory_ids:
            continue
        bugs_to_attach.append(bug)

    e.addBugs([b.id for b in bugs_to_attach])
    if args.dry_run:
        print(
            "DRY RUN: would add the following Bugs to advisory "
            + "'{}': {}".format(args.errata_id, bugs_to_attach))
        return

    e.commit()
    print(e)


def get(args):
    e = Erratum(errata_id=args.errata_id)
    print(e)


def push(args):
    e = Erratum(errata_id=args.errata_id)

    if args.push_when_ready:
        push_when_ready(args)
    if args.wait_for_state:
        wait_for_state(args)
    else:
        e.push(target=args.target)


def wait_for_state(args):
    # Check every 5 minutes for the state of the advisory
    wait_interval = 60*5
    e = Erratum(errata_id=args.errata_id)

    if args.wait_for_state == 'PUSH_READY':
        while e.errata_state not in ('PUSH_READY', 'IN_PUSH', 'SHIPPED_LIVE'):
            sleep(wait_interval)
            # Get current state upon re-creating the object
            e = Erratum(errata_id=args.errata_id)
            if args.verbose:
                print(e.errata_id, 'is in state:', e.errata_state)
        if args.push_when_ready:
            push_when_ready(args)

    if args.wait_for_state == 'SHIPPED_LIVE':
        if args.push_when_ready:
            push_when_ready(args)
        while e.errata_state != 'SHIPPED_LIVE':
            sleep(wait_interval)
            e = Erratum(errata_id=args.errata_id)
            if args.verbose:
                print(e.errata_id, 'is in state:', e.errata_state)


def push_when_ready(args):
    e = Erratum(errata_id=args.errata_id)
    if e.errata_state in ('PUSH_READY'):
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
