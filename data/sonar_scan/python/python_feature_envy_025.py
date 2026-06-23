def run(self, args, opts):
    settings = self.crawler_process.settings
    if opts.get:
        s = settings.get(opts.get)
        if isinstance(s, BaseSettings):
            print(json.dumps(s.copy_to_dict()))
        else:
            print(s)
    elif opts.getbool:
        print(settings.getbool(opts.getbool))
    elif opts.getint:
        print(settings.getint(opts.getint))
    elif opts.getfloat:
        print(settings.getfloat(opts.getfloat))
    elif opts.getlist:
        print(settings.getlist(opts.getlist))
