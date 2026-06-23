def _finish(self, request):
    self.concurrent -= 1
    if not request.finished and not request._disconnected:
        request.finish()
