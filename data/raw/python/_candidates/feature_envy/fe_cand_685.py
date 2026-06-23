def _adjust_delay(self, slot, latency, response):
    """Define delay adjustment policy"""

    # If a server needs `latency` seconds to respond then
    # we should send a request each `latency/N` seconds
    # to have N requests processed in parallel
    target_delay = latency / self.target_concurrency

    # Adjust the delay to make it closer to target_delay
    new_delay = (slot.delay + target_delay) / 2.0

    # If target delay is bigger than old delay, then use it instead of mean.
    # It works better with problematic sites.
    new_delay = max(target_delay, new_delay)

    # Make sure self.mindelay <= new_delay <= self.max_delay
    new_delay = min(max(self.mindelay, new_delay), self.maxdelay)

    # Dont adjust delay if response status != 200 and new delay is smaller
    # than old one, as error pages (and redirections) are usually small and
    # so tend to reduce latency, thus provoking a positive feedback by
    # reducing delay instead of increase.
    if response.status != 200 and new_delay <= slot.delay:
        return

    slot.delay = new_delay
