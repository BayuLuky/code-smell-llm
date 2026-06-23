def _enqueue_request(self, request: Request, spider: Spider) -> Deferred:
    key, slot = self._get_slot(request, spider)
    request.meta[self.DOWNLOAD_SLOT] = key

    def _deactivate(response: Response) -> Response:
        slot.active.remove(request)
        return response

    slot.active.add(request)
    self.signals.send_catch_log(
        signal=signals.request_reached_downloader, request=request, spider=spider
    )
    deferred: Deferred = Deferred().addBoth(_deactivate)
    slot.queue.append((request, deferred))
    self._process_queue(spider, slot)
    return deferred
