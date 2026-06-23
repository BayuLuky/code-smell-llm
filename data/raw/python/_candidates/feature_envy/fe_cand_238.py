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
