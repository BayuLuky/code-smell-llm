class CloseMatch(Token):
    """
    A variation on L{Literal} which matches "close" matches, that is, 
    strings with at most 'n' mismatching characters. C{CloseMatch} takes parameters:
     - C{match_string} - string to be matched
     - C{maxMismatches} - (C{default=1}) maximum number of mismatches allowed to count as a match

    The results from a successful parse will contain the matched text from the input string and the following named results:
     - C{mismatches} - a list of the positions within the match_string where mismatches were found
     - C{original} - the original match_string used to compare against the input string

    If C{mismatches} is an empty list, then the match was an exact match.

    Example::
        patt = CloseMatch("ATCATCGAATGGA")
        patt.parseString("ATCATCGAAXGGA") # -> (['ATCATCGAAXGGA'], {'mismatches': [[9]], 'original': ['ATCATCGAATGGA']})
        patt.parseString("ATCAXCGAAXGGA") # -> Exception: Expected 'ATCATCGAATGGA' (with up to 1 mismatches) (at char 0), (line:1, col:1)

        # exact match
        patt.parseString("ATCATCGAATGGA") # -> (['ATCATCGAATGGA'], {'mismatches': [[]], 'original': ['ATCATCGAATGGA']})

        # close match allowing up to 2 mismatches
        patt = CloseMatch("ATCATCGAATGGA", maxMismatches=2)
        patt.parseString("ATCAXCGAAXGGA") # -> (['ATCAXCGAAXGGA'], {'mismatches': [[4, 9]], 'original': ['ATCATCGAATGGA']})
    """
    def __init__(self, match_string, maxMismatches=1):
        super(CloseMatch,self).__init__()
        self.name = match_string
        self.match_string = match_string
        self.maxMismatches = maxMismatches
        self.errmsg = "Expected %r (with up to %d mismatches)" % (self.match_string, self.maxMismatches)
        self.mayIndexError = False
        self.mayReturnEmpty = False

    def parseImpl( self, instring, loc, doActions=True ):
        start = loc
        instrlen = len(instring)
        maxloc = start + len(self.match_string)

        if maxloc <= instrlen:
            match_string = self.match_string
            match_stringloc = 0
            mismatches = []
            maxMismatches = self.maxMismatches

            for match_stringloc,s_m in enumerate(zip(instring[loc:maxloc], self.match_string)):
                src,mat = s_m
                if src != mat:
                    mismatches.append(match_stringloc)
                    if len(mismatches) > maxMismatches:
                        break
            else:
                loc = match_stringloc + 1
                results = ParseResults([instring[start:loc]])
                results['original'] = self.match_string
                results['mismatches'] = mismatches
                return loc, results

        raise ParseException(instring, loc, self.errmsg, self)
