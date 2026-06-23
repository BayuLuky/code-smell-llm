class NoMatch(Token):
    """
    A token that will never match.
    """
    def __init__( self ):
        super(NoMatch,self).__init__()
        self.name = "NoMatch"
        self.mayReturnEmpty = True
        self.mayIndexError = False
        self.errmsg = "Unmatchable token"

    def parseImpl( self, instring, loc, doActions=True ):
        raise ParseException(instring, loc, self.errmsg, self)
