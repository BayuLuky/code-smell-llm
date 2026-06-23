def parseImpl( self, instring, loc, doActions=True ):
    maxExcLoc = -1
    maxException = None
    for e in self.exprs:
        try:
            ret = e._parse( instring, loc, doActions )
            return ret
        except ParseException as err:
            if err.loc > maxExcLoc:
                maxException = err
                maxExcLoc = err.loc
        except IndexError:
            if len(instring) > maxExcLoc:
                maxException = ParseException(instring,len(instring),e.errmsg,self)
                maxExcLoc = len(instring)

    # only got here if no expression matched, raise exception for match that made it the furthest
    else:
        if maxException is not None:
            maxException.msg = self.errmsg
            raise maxException
        else:
            raise ParseException(instring, loc, "no defined alternatives to match", self)
