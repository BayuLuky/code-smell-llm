def __init__( self, expr, savelist=False ):
    super(ParseElementEnhance,self).__init__(savelist)
    if isinstance( expr, basestring ):
        if issubclass(ParserElement._literalStringClass, Token):
            expr = ParserElement._literalStringClass(expr)
        else:
            expr = ParserElement._literalStringClass(Literal(expr))
    self.expr = expr
    self.strRepr = None
    if expr is not None:
        self.mayIndexError = expr.mayIndexError
        self.mayReturnEmpty = expr.mayReturnEmpty
        self.setWhitespaceChars( expr.whiteChars )
        self.skipWhitespace = expr.skipWhitespace
        self.saveAsList = expr.saveAsList
        self.callPreparse = expr.callPreparse
        self.ignoreExprs.extend(expr.ignoreExprs)
