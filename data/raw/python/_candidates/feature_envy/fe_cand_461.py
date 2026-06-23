def add_options(self, parser):
    ScrapyCommand.add_options(self, parser)
    parser.add_argument(
        "-l",
        "--list",
        dest="list",
        action="store_true",
        help="only list contracts, without checking them",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="print contract tests for all spiders",
    )
