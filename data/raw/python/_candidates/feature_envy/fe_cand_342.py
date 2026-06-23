def add_options(self, parser):
    ScrapyCommand.add_options(self, parser)
    parser.add_argument("--spider", dest="spider", help="use this spider")
    parser.add_argument(
        "--headers",
        dest="headers",
        action="store_true",
        help="print response HTTP headers instead of body",
    )
    parser.add_argument(
        "--no-redirect",
        dest="no_redirect",
        action="store_true",
        default=False,
        help="do not handle HTTP 3xx status codes and print response as-is",
    )
