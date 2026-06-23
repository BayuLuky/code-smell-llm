def _download(self, slot: Slot, request: Request, spider: Spider) -> Deferred:
    # The order is very important for the following deferreds. Do not change!

    # 1. Create the download deferred
    dfd = mustbe_deferred(self.handlers.download_request, request, spider)

    # 2. Notify response_downloaded listeners about the recent download
    # before querying queue for next request
    def _downloaded(response: Response) -> Response:
        self.signals.send_catch_log(
            signal=signals.response_downloaded,
            response=response,
            request=request,
            spider=spider,
        )
        return response

    dfd.addCallback(_downloaded)

    # 3. After response arrives, remove the request from transferring
    # state to free up the transferring slot so it can be used by the
    # following requests (perhaps those which came from the downloader
    # middleware itself)
    slot.transferring.add(request)

    def finish_transferring(_: Any) -> Any:
        slot.transferring.remove(request)
        self._process_queue(spider, slot)
        self.signals.send_catch_log(
            signal=signals.request_left_downloader, request=request, spider=spider
        )
        return _

    return dfd.addBoth(finish_transferring)
