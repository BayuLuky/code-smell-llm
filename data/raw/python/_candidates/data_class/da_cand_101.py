class NotAny(ParseElementEnhance):
    """
    Lookahead to disallow matching with the given parse expression.  C{NotAny}
    does I{not} advance the parsing position within the input string, it only
    verifies that the specified parse expression does I{not} match at the current
    position.  Also, C{NotAny} does I{not} skip over leading whitespace. C{NotAny}
    always returns a null token list.  May be constructed using the '~' operator.

    Example::

    """
    def __init__( self, expr ):
        super(NotAny,self).__init__(expr)
        #~ self.leaveWhitespace()
        self.skipWhitespace = False  # do NOT use self.leaveWhitespace(), don't want to propagate to exprs
        self.mayReturnEmpty = True
        self.errmsg = "Found unwanted token, "+_ustr(self.expr)

    def parseImpl( self, instring, loc, doActions=True ):
        if self.expr.canParseNext(instring, loc):
            raise ParseException(instring, loc, self.errmsg, self)
        return loc, []

    def __str__( self ):
        if hasattr(self,"name"):
            return self.name

        if self.strRepr is None:
            self.strRepr = "~{" + _ustr(self.expr) + "}"

        return self.strRepr
