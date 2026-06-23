def trim_punctuation(self, word):
    """
    Trim trailing and wrapping punctuation from `word`. Return the items of
    the new state.
    """
    lead, middle, trail = "", word, ""
    # Continue trimming until middle remains unchanged.
    trimmed_something = True
    while trimmed_something:
        trimmed_something = False
        # Trim wrapping punctuation.
        for opening, closing in self.wrapping_punctuation:
            if middle.startswith(opening):
                middle = middle[len(opening) :]
                lead += opening
                trimmed_something = True
            # Keep parentheses at the end only if they're balanced.
            if (
                middle.endswith(closing)
                and middle.count(closing) == middle.count(opening) + 1
            ):
                middle = middle[: -len(closing)]
                trail = closing + trail
                trimmed_something = True
        # Trim trailing punctuation (after trimming wrapping punctuation,
        # as encoded entities contain ';'). Unescape entities to avoid
        # breaking them by removing ';'.
        middle_unescaped = html.unescape(middle)
        stripped = middle_unescaped.rstrip(self.trailing_punctuation_chars)
        if middle_unescaped != stripped:
            punctuation_count = len(middle_unescaped) - len(stripped)
            trail = middle[-punctuation_count:] + trail
            middle = middle[:-punctuation_count]
            trimmed_something = True
    return lead, middle, trail
