def _callback(self, response, **cb_kwargs):
    rule = self._rules[response.meta["rule"]]
    return self._parse_response(
        response, rule.callback, {**rule.cb_kwargs, **cb_kwargs}, rule.follow
    )
