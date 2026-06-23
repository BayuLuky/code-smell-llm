class IssueRole(object):
    EXTERNAL_REPO_REGEX = re.compile(r"^(\w+)/(.+)([#@])([\w]+)$")

    def __init__(
        self, uri_config_option, format_kwarg, github_uri_template, format_text=None
    ):
        self.uri_config_option = uri_config_option
        self.format_kwarg = format_kwarg
        self.github_uri_template = github_uri_template
        self.format_text = format_text or self.default_format_text

    @staticmethod
    def default_format_text(issue_no):
        return "#{0}".format(issue_no)

    def make_node(self, name, issue_no, config, options=None):
        name_map = {"pr": "pull", "issue": "issues", "commit": "commit"}
        options = options or {}
        repo_match = self.EXTERNAL_REPO_REGEX.match(issue_no)
        if repo_match:  # External repo
            username, repo, symbol, issue = repo_match.groups()
            if name not in name_map:
                raise ValueError(
                    "External repo linking not supported for :{}:".format(name)
                )
            path = name_map.get(name)
            ref = "https://github.com/{issues_github_path}/{path}/{n}".format(
                issues_github_path="{}/{}".format(username, repo), path=path, n=issue
            )
            formatted_issue = self.format_text(issue).lstrip("#")
            text = "{username}/{repo}{symbol}{formatted_issue}".format(**locals())
            link = nodes.reference(text=text, refuri=ref, **options)
            return link

        if issue_no not in ("-", "0"):
            uri_template = getattr(config, self.uri_config_option, None)
            if uri_template:
                ref = uri_template.format(**{self.format_kwarg: issue_no})
            elif config.issues_github_path:
                ref = self.github_uri_template.format(
                    issues_github_path=config.issues_github_path, n=issue_no
                )
            else:
                raise ValueError(
                    "Neither {} nor issues_github_path is set".format(
                        self.uri_config_option
                    )
                )
            issue_text = self.format_text(issue_no)
            link = nodes.reference(text=issue_text, refuri=ref, **options)
        else:
            link = None
        return link

    def __call__(
        self, name, rawtext, text, lineno, inliner, options=None, content=None
    ):
        options = options or {}
        content = content or []
        issue_nos = [each.strip() for each in utils.unescape(text).split(",")]
        config = inliner.document.settings.env.app.config
        ret = []
        for i, issue_no in enumerate(issue_nos):
            node = self.make_node(name, issue_no, config, options=options)
            ret.append(node)
            if i != len(issue_nos) - 1:
                sep = nodes.raw(text=", ", format="html")
                ret.append(sep)
        return ret, []
