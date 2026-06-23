def get_completion_args(self) -> t.Tuple[t.List[str], str]:
    cwords = split_arg_string(os.environ["COMP_WORDS"])
    incomplete = os.environ["COMP_CWORD"]
    args = cwords[1:]

    # Fish stores the partial word in both COMP_WORDS and
    # COMP_CWORD, remove it from complete args.
    if incomplete and args and args[-1] == incomplete:
        args.pop()

    return args, incomplete
