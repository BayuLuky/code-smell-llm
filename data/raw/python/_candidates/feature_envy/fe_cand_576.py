def _load_spiders(self, module: ModuleType) -> None:
    for spcls in iter_spider_classes(module):
        self._found[spcls.name].append((module.__name__, spcls.__name__))
        self._spiders[spcls.name] = spcls
