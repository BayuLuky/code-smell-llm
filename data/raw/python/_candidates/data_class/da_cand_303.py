class Lexer:
    """
    A generic multi-state regex-based lexer.
    """

    def __init__(self, states, first):
        self.regexes = {}
        self.toks = {}

        for state, rules in states.items():
            parts = []
            for tok in rules:
                groupid = "t%d" % tok.id
                self.toks[groupid] = tok
                parts.append("(?P<%s>%s)" % (groupid, tok.regex))
            self.regexes[state] = re.compile("|".join(parts), re.MULTILINE | re.VERBOSE)

        self.state = first

    def lex(self, text):
        """
        Lexically analyze `text`.

        Yield pairs (`name`, `tokentext`).
        """
        end = len(text)
        state = self.state
        regexes = self.regexes
        toks = self.toks
        start = 0

        while start < end:
            for match in regexes[state].finditer(text, start):
                name = match.lastgroup
                tok = toks[name]
                toktext = match[name]
                start += len(toktext)
                yield (tok.name, toktext)

                if tok.next:
                    state = tok.next
                    break

        self.state = state
