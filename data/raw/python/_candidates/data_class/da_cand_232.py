class ZeroOrMore(_MultipleMatch):
    """
    Optional repetition of zero or more of the given expression.

    Parameters:
     - expr - expression that must match zero or more times
     - stopOn - (default=C{None}) - expression for a terminating sentinel
          (only required if the sentinel would ordinarily match the repetition 
          expression)          

    Example: similar to L{OneOrMore}
    """
    def __init__( self, expr, stopOn=None):
        super(ZeroOrMore,self).__init__(expr, stopOn=stopOn)
        self.mayReturnEmpty = True

    def parseImpl( self, instring, loc, doActions=True ):
        try:
            return super(ZeroOrMore, self).parseImpl(instring, loc, doActions)
        except (ParseException,IndexError):
            return loc, []

    def __str__( self ):
        if hasattr(self,"name"):
            return self.name

        if self.strRepr is None:
            self.strRepr = "[" + _ustr(self.expr) + "]..."

        return self.strRepr
