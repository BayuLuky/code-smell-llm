def read_config(self, filename):
    parser = configparser.RawConfigParser()
    parser.read([filename])
    try:
        self.aliases.update(parser.items("aliases"))
    except configparser.NoSectionError:
        pass
