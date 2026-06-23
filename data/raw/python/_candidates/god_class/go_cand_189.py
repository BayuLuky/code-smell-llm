class WatchmanReloader(BaseReloader):
    def __init__(self):
        self.roots = defaultdict(set)
        self.processed_request = threading.Event()
        self.client_timeout = int(os.environ.get("DJANGO_WATCHMAN_TIMEOUT", 5))
        super().__init__()

    @cached_property
    def client(self):
        return pywatchman.client(timeout=self.client_timeout)

    def _watch_root(self, root):
        # In practice this shouldn't occur, however, it's possible that a
        # directory that doesn't exist yet is being watched. If it's outside of
        # sys.path then this will end up a new root. How to handle this isn't
        # clear: Not adding the root will likely break when subscribing to the
        # changes, however, as this is currently an internal API,  no files
        # will be being watched outside of sys.path. Fixing this by checking
        # inside watch_glob() and watch_dir() is expensive, instead this could
        # could fall back to the StatReloader if this case is detected? For
        # now, watching its parent, if possible, is sufficient.
        if not root.exists():
            if not root.parent.exists():
                logger.warning(
                    "Unable to watch root dir %s as neither it or its parent exist.",
                    root,
                )
                return
            root = root.parent
        result = self.client.query("watch-project", str(root.absolute()))
        if "warning" in result:
            logger.warning("Watchman warning: %s", result["warning"])
        logger.debug("Watchman watch-project result: %s", result)
        return result["watch"], result.get("relative_path")

    @lru_cache
    def _get_clock(self, root):
        return self.client.query("clock", root)["clock"]

    def _subscribe(self, directory, name, expression):
        root, rel_path = self._watch_root(directory)
        # Only receive notifications of files changing, filtering out other types
        # like special files: https://facebook.github.io/watchman/docs/type
        only_files_expression = [
            "allof",
            ["anyof", ["type", "f"], ["type", "l"]],
            expression,
        ]
        query = {
            "expression": only_files_expression,
            "fields": ["name"],
            "since": self._get_clock(root),
            "dedup_results": True,
        }
        if rel_path:
            query["relative_root"] = rel_path
        logger.debug(
            "Issuing watchman subscription %s, for root %s. Query: %s",
            name,
            root,
            query,
        )
        self.client.query("subscribe", root, name, query)

    def _subscribe_dir(self, directory, filenames):
        if not directory.exists():
            if not directory.parent.exists():
                logger.warning(
                    "Unable to watch directory %s as neither it or its parent exist.",
                    directory,
                )
                return
            prefix = "files-parent-%s" % directory.name
            filenames = ["%s/%s" % (directory.name, filename) for filename in filenames]
            directory = directory.parent
            expression = ["name", filenames, "wholename"]
        else:
            prefix = "files"
            expression = ["name", filenames]
        self._subscribe(directory, "%s:%s" % (prefix, directory), expression)

    def _watch_glob(self, directory, patterns):
        """
        Watch a directory with a specific glob. If the directory doesn't yet
        exist, attempt to watch the parent directory and amend the patterns to
        include this. It's important this method isn't called more than one per
        directory when updating all subscriptions. Subsequent calls will
        overwrite the named subscription, so it must include all possible glob
        expressions.
        """
        prefix = "glob"
        if not directory.exists():
            if not directory.parent.exists():
                logger.warning(
                    "Unable to watch directory %s as neither it or its parent exist.",
                    directory,
                )
                return
            prefix = "glob-parent-%s" % directory.name
            patterns = ["%s/%s" % (directory.name, pattern) for pattern in patterns]
            directory = directory.parent

        expression = ["anyof"]
        for pattern in patterns:
            expression.append(["match", pattern, "wholename"])
        self._subscribe(directory, "%s:%s" % (prefix, directory), expression)

    def watched_roots(self, watched_files):
        extra_directories = self.directory_globs.keys()
        watched_file_dirs = [f.parent for f in watched_files]
        sys_paths = list(sys_path_directories())
        return frozenset((*extra_directories, *watched_file_dirs, *sys_paths))

    def _update_watches(self):
        watched_files = list(self.watched_files(include_globs=False))
        found_roots = common_roots(self.watched_roots(watched_files))
        logger.debug("Watching %s files", len(watched_files))
        logger.debug("Found common roots: %s", found_roots)
        # Setup initial roots for performance, shortest roots first.
        for root in sorted(found_roots):
            self._watch_root(root)
        for directory, patterns in self.directory_globs.items():
            self._watch_glob(directory, patterns)
        # Group sorted watched_files by their parent directory.
        sorted_files = sorted(watched_files, key=lambda p: p.parent)
        for directory, group in itertools.groupby(sorted_files, key=lambda p: p.parent):
            # These paths need to be relative to the parent directory.
            self._subscribe_dir(
                directory, [str(p.relative_to(directory)) for p in group]
            )

    def update_watches(self):
        try:
            self._update_watches()
        except Exception as ex:
            # If the service is still available, raise the original exception.
            if self.check_server_status(ex):
                raise

    def _check_subscription(self, sub):
        subscription = self.client.getSubscription(sub)
        if not subscription:
            return
        logger.debug("Watchman subscription %s has results.", sub)
        for result in subscription:
            # When using watch-project, it's not simple to get the relative
            # directory without storing some specific state. Store the full
            # path to the directory in the subscription name, prefixed by its
            # type (glob, files).
            root_directory = Path(result["subscription"].split(":", 1)[1])
            logger.debug("Found root directory %s", root_directory)
            for file in result.get("files", []):
                self.notify_file_changed(root_directory / file)

    def request_processed(self, **kwargs):
        logger.debug("Request processed. Setting update_watches event.")
        self.processed_request.set()

    def tick(self):
        request_finished.connect(self.request_processed)
        self.update_watches()
        while True:
            if self.processed_request.is_set():
                self.update_watches()
                self.processed_request.clear()
            try:
                self.client.receive()
            except pywatchman.SocketTimeout:
                pass
            except pywatchman.WatchmanError as ex:
                logger.debug("Watchman error: %s, checking server status.", ex)
                self.check_server_status(ex)
            else:
                for sub in list(self.client.subs.keys()):
                    self._check_subscription(sub)
            yield
            # Protect against busy loops.
            time.sleep(0.1)

    def stop(self):
        self.client.close()
        super().stop()

    def check_server_status(self, inner_ex=None):
        """Return True if the server is available."""
        try:
            self.client.query("version")
        except Exception:
            raise WatchmanUnavailable(str(inner_ex)) from inner_ex
        return True

    @classmethod
    def check_availability(cls):
        if not pywatchman:
            raise WatchmanUnavailable("pywatchman not installed.")
        client = pywatchman.client(timeout=0.1)
        try:
            result = client.capabilityCheck()
        except Exception:
            # The service is down?
            raise WatchmanUnavailable("Cannot connect to the watchman service.")
        version = get_version_tuple(result["version"])
        # Watchman 4.9 includes multiple improvements to watching project
        # directories as well as case insensitive filesystems.
        logger.debug("Watchman version %s", version)
        if version < (4, 9):
            raise WatchmanUnavailable("Watchman 4.9 or later is required.")
