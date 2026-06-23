def policy(self, resp_or_url, request):
    """
    Determine Referrer-Policy to use from a parent Response (or URL),
    and a Request to be sent.

    - if a valid policy is set in Request meta, it is used.
    - if the policy is set in meta but is wrong (e.g. a typo error),
      the policy from settings is used
    - if the policy is not set in Request meta,
      but there is a Referrer-policy header in the parent response,
      it is used if valid
    - otherwise, the policy from settings is used.
    """
    policy_name = request.meta.get("referrer_policy")
    if policy_name is None:
        if isinstance(resp_or_url, Response):
            policy_header = resp_or_url.headers.get("Referrer-Policy")
            if policy_header is not None:
                policy_name = to_unicode(policy_header.decode("latin1"))
    if policy_name is None:
        return self.default_policy()

    cls = _load_policy_class(policy_name, warning_only=True)
    return cls() if cls else self.default_policy()
