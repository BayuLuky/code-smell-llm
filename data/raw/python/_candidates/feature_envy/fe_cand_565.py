def process_request(self, request, spider):
    if request.meta.get("dont_obey_robotstxt"):
        return
    if request.url.startswith("data:") or request.url.startswith("file:"):
        return
    d = maybeDeferred(self.robot_parser, request, spider)
    d.addCallback(self.process_request_2, request, spider)
    return d
