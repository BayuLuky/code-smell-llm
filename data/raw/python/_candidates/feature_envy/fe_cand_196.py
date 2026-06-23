def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(cmd_folder):
        if filename.endswith(".py") and filename.startswith("cmd_"):
            rv.append(filename[4:-3])
    rv.sort()
    return rv
