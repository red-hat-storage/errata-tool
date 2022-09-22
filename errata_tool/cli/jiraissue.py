from errata_tool.jira_issue import JiraIssue


def add_parser(subparsers):
    """Add build parser to this top-level subparsers object."""
    group = subparsers.add_parser('jiraissue', help='Jira Issue information')

    # build-level sub-commands:
    sub = group.add_subparsers(dest='jira_subcommand')
    sub.required = True

    # "get"
    get_parser = sub.add_parser('get')
    get_parser.add_argument('id', help='jira issue id of given '
                            'issue')
    get_parser.set_defaults(func=get)

    get_all_parser = sub.add_parser('get_errata_ids')
    get_all_parser.add_argument('id', help='jira issue id of given '
                                'issue')
    get_all_parser.set_defaults(func=get_errata_ids)


def get(args):
    """Get information about jira issue
    :param args: parsed cli arguments
    """
    issue = JiraIssue(args.id)

    print(issue)
    print(issue._data)


def get_errata_ids(args):
    """Get information about jira issue
    :param args: parsed cli arguments
    """
    issue = JiraIssue(args.id)
    for id in issue.all_advisory_ids:
        print(id)
