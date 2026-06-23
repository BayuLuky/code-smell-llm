class BaseIterable:
    def __init__(
        self, queryset, chunked_fetch=False, chunk_size=GET_ITERATOR_CHUNK_SIZE
    ):
        self.queryset = queryset
        self.chunked_fetch = chunked_fetch
        self.chunk_size = chunk_size

    async def _async_generator(self):
        # Generators don't actually start running until the first time you call
        # next() on them, so make the generator object in the async thread and
        # then repeatedly dispatch to it in a sync thread.
        sync_generator = self.__iter__()

        def next_slice(gen):
            return list(islice(gen, self.chunk_size))

        while True:
            chunk = await sync_to_async(next_slice)(sync_generator)
            for item in chunk:
                yield item
            if len(chunk) < self.chunk_size:
                break

    # __aiter__() is a *synchronous* method that has to then return an
    # *asynchronous* iterator/generator. Thus, nest an async generator inside
    # it.
    # This is a generic iterable converter for now, and is going to suffer a
    # performance penalty on large sets of items due to the cost of crossing
    # over the sync barrier for each chunk. Custom __aiter__() methods should
    # be added to each Iterable subclass, but that needs some work in the
    # Compiler first.
    def __aiter__(self):
        return self._async_generator()
