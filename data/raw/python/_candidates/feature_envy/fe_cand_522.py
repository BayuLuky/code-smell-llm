def __init__(self, token, parser):
    self.token = token
    matches = filter_re.finditer(token)
    var_obj = None
    filters = []
    upto = 0
    for match in matches:
        start = match.start()
        if upto != start:
            raise TemplateSyntaxError(
                "Could not parse some characters: "
                "%s|%s|%s" % (token[:upto], token[upto:start], token[start:])
            )
        if var_obj is None:
            var, constant = match["var"], match["constant"]
            if constant:
                try:
                    var_obj = Variable(constant).resolve({})
                except VariableDoesNotExist:
                    var_obj = None
            elif var is None:
                raise TemplateSyntaxError(
                    "Could not find variable at start of %s." % token
                )
            else:
                var_obj = Variable(var)
        else:
            filter_name = match["filter_name"]
            args = []
            constant_arg, var_arg = match["constant_arg"], match["var_arg"]
            if constant_arg:
                args.append((False, Variable(constant_arg).resolve({})))
            elif var_arg:
                args.append((True, Variable(var_arg)))
            filter_func = parser.find_filter(filter_name)
            self.args_check(filter_name, filter_func, args)
            filters.append((filter_func, args))
        upto = match.end()
    if upto != len(token):
        raise TemplateSyntaxError(
            "Could not parse the remainder: '%s' "
            "from '%s'" % (token[upto:], token)
        )

    self.filters = filters
    self.var = var_obj
    self.is_var = isinstance(var_obj, Variable)
