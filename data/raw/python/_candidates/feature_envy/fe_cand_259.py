def extract_contracts(self, method):
    contracts = []
    for line in method.__doc__.split("\n"):
        line = line.strip()

        if line.startswith("@"):
            name, args = re.match(r"@(\w+)\s*(.*)", line).groups()
            args = re.split(r"\s+", args)

            contracts.append(self.contracts[name](method, *args))

    return contracts
