class CaselessKeyword(Keyword):
    """
    Caseless version of L{Keyword}.

    Example::
        OneOrMore(CaselessKeyword("CMD")).parseString("cmd CMD Cmd10") # -> ['CMD', 'CMD']

    (Contrast with example for L{CaselessLiteral}.)
    """
    def __init__( self, matchString, identChars=None ):
        super(CaselessKeyword,self).__init__( matchString, identChars, caseless=True )

    def parseImpl( self, instring, loc, doActions=True ):
        if ( (instring[ loc:loc+self.matchLen ].upper() == self.caselessmatch) and
             (loc >= len(instring)-self.matchLen or instring[loc+self.matchLen].upper() not in self.identChars) ):
            return loc+self.matchLen, self.match
        raise ParseException(instring, loc, self.errmsg, self)
