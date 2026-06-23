class SpiderInfo:
    def __init__(self, spider):
        self.spider = spider
        self.downloading = set()
        self.downloaded = {}
        self.waiting = defaultdict(list)
