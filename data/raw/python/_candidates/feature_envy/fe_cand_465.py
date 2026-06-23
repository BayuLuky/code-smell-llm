def close(self):
    from twisted.internet import reactor

    d = self._pool.closeCachedConnections()
    # closeCachedConnections will hang on network or server issues, so
    # we'll manually timeout the deferred.
    #
    # Twisted issue addressing this problem can be found here:
    # https://twistedmatrix.com/trac/ticket/7738.
    #
    # closeCachedConnections doesn't handle external errbacks, so we'll
    # issue a callback after `_disconnect_timeout` seconds.
    delayed_call = reactor.callLater(self._disconnect_timeout, d.callback, [])

    def cancel_delayed_call(result):
        if delayed_call.active():
            delayed_call.cancel()
        return result

    d.addBoth(cancel_delayed_call)
    return d
