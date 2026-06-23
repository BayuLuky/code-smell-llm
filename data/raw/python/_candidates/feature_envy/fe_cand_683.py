def spider_closed(self, spider, reason):
    gc.collect()
    self.stats.set_value(
        "memdebug/gc_garbage_count", len(gc.garbage), spider=spider
    )
    for cls, wdict in live_refs.items():
        if not wdict:
            continue
        self.stats.set_value(
            f"memdebug/live_refs/{cls.__name__}", len(wdict), spider=spider
        )
