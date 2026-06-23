def search(text, pos):
    # Look for "<" or a non-tag word.
    partial = re_prt.search(text, pos)
    if partial is None or partial[1] is not None:
        return partial

    # "<" was found, look for a closing ">".
    end = text.find(">", partial.end(0))
    if end < 0:
        # ">" cannot be found, look for a word.
        return re_notag.search(text, pos + 1)
    else:
        # "<" followed by a ">" was found -- fake a match.
        end += 1
        return FakeMatch(text[partial.start(0) : end], end)
