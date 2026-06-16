def parseImpl( self, instring, loc, doActions=True ):
    maxExcLoc = -1
    maxException = None
    matches = []
    for e in self.exprs:
        try:
            loc2 = e.tryParse( instring, loc )
        except ParseException as err:
            err.__traceback__ = None
            if err.loc > maxExcLoc:
                maxException = err
                maxExcLoc = err.loc
        except IndexError:
            if len(instring) > maxExcLoc:
                maxException = ParseException(instring,len(instring),e.errmsg,self)
                maxExcLoc = len(instring)
        else:
            # save match among all matches, to retry longest to shortest
            matches.append((loc2, e))

    if matches:
        matches.sort(key=lambda x: -x[0])
        for _,e in matches:
            try:
                return e._parse( instring, loc, doActions )
            except ParseException as err:
                err.__traceback__ = None
                if err.loc > maxExcLoc:
                    maxException = err
                    maxExcLoc = err.loc

    if maxException is not None:
        maxException.msg = self.errmsg
        raise maxException
    else:
        raise ParseException(instring, loc, "no defined alternatives to match", self)
