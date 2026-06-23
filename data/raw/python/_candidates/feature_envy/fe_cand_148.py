def __iter__(self) -> Iterator[Dict[str, Any]]:
    for elem in self._root.getchildren():
        d: Dict[str, Any] = {}
        for el in elem.getchildren():
            tag = el.tag
            name = tag.split("}", 1)[1] if "}" in tag else tag

            if name == "link":
                if "href" in el.attrib:
                    d.setdefault("alternate", []).append(el.get("href"))
            else:
                d[name] = el.text.strip() if el.text else ""

        if "loc" in d:
            yield d
