def _process_queue(self, spider: Spider, slot: Slot) -> None:
    from twisted.internet import reactor

    if slot.latercall and slot.latercall.active():
        return

    # Delay queue processing if a download_delay is configured
    now = time()
    delay = slot.download_delay()
    if delay:
        penalty = delay - now + slot.lastseen
        if penalty > 0:
            slot.latercall = reactor.callLater(
                penalty, self._process_queue, spider, slot
            )
            return

    # Process enqueued requests if there are free slots to transfer for this slot
    while slot.queue and slot.free_transfer_slots() > 0:
        slot.lastseen = now
        request, deferred = slot.queue.popleft()
        dfd = self._download(slot, request, spider)
        dfd.chainDeferred(deferred)
        # prevent burst if inter-request delays were configured
        if delay:
            self._process_queue(spider, slot)
            break
