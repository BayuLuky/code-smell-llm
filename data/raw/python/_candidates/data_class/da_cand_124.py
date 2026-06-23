class CaselessPreservingLiteral(CaselessLiteral):
    """ Like CaselessLiteral, but returns the match as found
        instead of as defined.
    """
    def __init__( self, matchString ):
        super().__init__(matchString.upper())
        self.name = "'%s'" % matchString
        self.errmsg = "Expected " + self.name
        self.myException.msg = self.errmsg

    def parseImpl( self, instring, loc, doActions=True ):
        test = instring[ loc:loc+self.matchLen ]
        if test.upper() == self.match:
            return loc+self.matchLen, test
        #~ raise ParseException( instring, loc, self.errmsg )
        exc = self.myException
        exc.loc = loc
        exc.pstr = instring
        raise exc   
