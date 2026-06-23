def _signal_kill(self, signum: int, _: Any) -> None:
    from twisted.internet import reactor

    install_shutdown_handlers(signal.SIG_IGN)
    signame = signal_names[signum]
    logger.info(
        "Received %(signame)s twice, forcing unclean shutdown", {"signame": signame}
    )
    reactor.callFromThread(self._stop_reactor)
