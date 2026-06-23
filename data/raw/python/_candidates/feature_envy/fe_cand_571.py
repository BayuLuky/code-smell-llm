def _iter_links(self, document):
    for el in document.iter(etree.Element):
        if not self.scan_tag(_nons(el.tag)):
            continue
        attribs = el.attrib
        for attrib in attribs:
            if not self.scan_attr(attrib):
                continue
            yield (el, attrib, attribs[attrib])
