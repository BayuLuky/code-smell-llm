def resolveHostName(
    self,
    resolutionReceiver,
    hostName: str,
    portNumber=0,
    addressTypes=None,
    transportSemantics="TCP",
):
    try:
        addresses = dnscache[hostName]
    except KeyError:
        return self.original_resolver.resolveHostName(
            _CachingResolutionReceiver(resolutionReceiver, hostName),
            hostName,
            portNumber,
            addressTypes,
            transportSemantics,
        )
    else:
        resolutionReceiver.resolutionBegan(HostResolution(hostName))
        for addr in addresses:
            resolutionReceiver.addressResolved(addr)
        resolutionReceiver.resolutionComplete()
        return resolutionReceiver
