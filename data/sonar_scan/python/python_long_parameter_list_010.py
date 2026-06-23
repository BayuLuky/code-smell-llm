def __init__(
    self,
    input="content",
    encoding="utf-8",
    decode_error="strict",
    strip_accents=None,
    lowercase=True,
    preprocessor=None,
    tokenizer=None,
    stop_words=None,
    token_pattern=r"(?u)\b\w\w+\b",
    ngram_range=(1, 1),
    analyzer="word",
    max_df=1.0,
    min_df=1,
    max_features=None,
    vocabulary=None,
    binary=False,
    dtype=np.int64,
):
    self.input = input
    self.encoding = encoding
    self.decode_error = decode_error
    self.strip_accents = strip_accents
    self.preprocessor = preprocessor
    self.tokenizer = tokenizer
    self.analyzer = analyzer
    self.lowercase = lowercase
    self.token_pattern = token_pattern
    self.stop_words = stop_words
    self.max_df = max_df
    self.min_df = min_df
    self.max_features = max_features
    self.ngram_range = ngram_range
    self.vocabulary = vocabulary
    self.binary = binary
    self.dtype = dtype
