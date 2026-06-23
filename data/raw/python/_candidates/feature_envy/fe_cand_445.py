def parseImpl( self, instring, loc, doActions=True ):
    # pass False as last arg to _parse for first element, since we already
    # pre-parsed the string as part of our And pre-parsing
    loc, resultlist = self.exprs[0]._parse( instring, loc, doActions, callPreParse=False )
    errorStop = False
    for e in self.exprs[1:]:
        if isinstance(e, And._ErrorStop):
            errorStop = True
            continue
        if errorStop:
            try:
                loc, exprtokens = e._parse( instring, loc, doActions )
            except ParseSyntaxException:
                raise
            except ParseBaseException as pe:
                pe.__traceback__ = None
                raise ParseSyntaxException._from_exception(pe)
            except IndexError:
                raise ParseSyntaxException(instring, len(instring), self.errmsg, self)
        else:
            loc, exprtokens = e._parse( instring, loc, doActions )
        if exprtokens or exprtokens.haskeys():
            resultlist += exprtokens
    return loc, resultlist
