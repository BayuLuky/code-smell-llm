def write_config(self, filename):
    parser = configparser.RawConfigParser()
    parser.add_section("aliases")
    for key, value in self.aliases.items():
        parser.set("aliases", key, value)
    with open(filename, "wb") as file:
        parser.write(file)
