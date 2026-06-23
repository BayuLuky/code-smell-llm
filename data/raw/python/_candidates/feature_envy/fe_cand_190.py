def add_options(self, parser):
    ScrapyCommand.add_options(self, parser)
    parser.add_argument(
        "--get", dest="get", metavar="SETTING", help="print raw setting value"
    )
    parser.add_argument(
        "--getbool",
        dest="getbool",
        metavar="SETTING",
        help="print setting value, interpreted as a boolean",
    )
    parser.add_argument(
        "--getint",
        dest="getint",
        metavar="SETTING",
        help="print setting value, interpreted as an integer",
    )
    parser.add_argument(
        "--getfloat",
        dest="getfloat",
        metavar="SETTING",
        help="print setting value, interpreted as a float",
    )
    parser.add_argument(
        "--getlist",
        dest="getlist",
        metavar="SETTING",
        help="print setting value, interpreted as a list",
    )
