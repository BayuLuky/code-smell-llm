def add_options(self, parser):
    ScrapyCommand.add_options(self, parser)
    parser.add_argument(
        "-a",
        dest="spargs",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="set spider argument (may be repeated)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        action="append",
        help="append scraped items to the end of FILE (use - for stdout),"
        " to define format set a colon at the end of the output URI (i.e. -o FILE:FORMAT)",
    )
    parser.add_argument(
        "-O",
        "--overwrite-output",
        metavar="FILE",
        action="append",
        help="dump scraped items into FILE, overwriting any existing file,"
        " to define format set a colon at the end of the output URI (i.e. -O FILE:FORMAT)",
    )
    parser.add_argument(
        "-t",
        "--output-format",
        metavar="FORMAT",
        help="format to use for dumping items",
    )
