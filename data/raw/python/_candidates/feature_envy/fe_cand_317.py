def _truncate_html(self, length, truncate, text, truncate_len, words):
    """
    Truncate HTML to a certain number of chars (not counting tags and
    comments), or, if words is True, then to a certain number of words.
    Close opened tags if they were correctly closed in the given HTML.

    Preserve newlines in the HTML.
    """
    if words and length <= 0:
        return ""

    size_limited = False
    if len(text) > self.MAX_LENGTH_HTML:
        text = text[: self.MAX_LENGTH_HTML]
        size_limited = True

    html4_singlets = (
        "br",
        "col",
        "link",
        "base",
        "img",
        "param",
        "area",
        "hr",
        "input",
    )

    # Count non-HTML chars/words and keep note of open tags
    pos = 0
    end_text_pos = 0
    current_len = 0
    open_tags = []

    regex = re_words if words else re_chars

    while current_len <= length:
        m = regex.search(text, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m[1]:
            # It's an actual non-HTML word or char
            current_len += 1
            if current_len == truncate_len:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m[0])
        if not tag or current_len >= truncate_len:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        # Element names are always case-insensitive
        tagname = tagname.lower()
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1 :]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)

    truncate_text = self.add_truncation_text("", truncate)

    if current_len <= length:
        if size_limited and truncate_text:
            text += truncate_text
        return text

    out = text[:end_text_pos]
    if truncate_text:
        out += truncate_text
    # Close any tags still open
    for tag in open_tags:
        out += "</%s>" % tag
    # Return string
    return out
