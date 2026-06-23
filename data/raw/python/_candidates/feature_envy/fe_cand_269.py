def get_completion_args(self) -> t.Tuple[t.List[str], str]:
    cwords = split_arg_string(os.environ["COMP_WORDS"])
    cword = int(os.environ["COMP_CWORD"])
    args = cwords[1:cword]

    try:
        incomplete = cwords[cword]
    except IndexError:
        incomplete = ""

    return args, incomplete
