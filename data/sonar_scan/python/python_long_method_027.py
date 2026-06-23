def test_n_max_elements_to_show(print_changed_only_false):
    n_max_elements_to_show = 30
    pp = _EstimatorPrettyPrinter(
        compact=True,
        indent=1,
        indent_at_name=True,
        n_max_elements_to_show=n_max_elements_to_show,
    )

    # No ellipsis
    vocabulary = {i: i for i in range(n_max_elements_to_show)}
    vectorizer = CountVectorizer(vocabulary=vocabulary)

    expected = r"""
CountVectorizer(analyzer='word', binary=False, decode_error='strict',
                dtype=<class 'numpy.int64'>, encoding='utf-8', input='content',
                lowercase=True, max_df=1.0, max_features=None, min_df=1,
                ngram_range=(1, 1), preprocessor=None, stop_words=None,
                strip_accents=None, token_pattern='(?u)\\b\\w\\w+\\b',
                tokenizer=None,
                vocabulary={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
                            8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14,
                            15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
                            21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26,
                            27: 27, 28: 28, 29: 29})"""

    expected = expected[1:]  # remove first \n
    assert pp.pformat(vectorizer) == expected

    # Now with ellipsis
    vocabulary = {i: i for i in range(n_max_elements_to_show + 1)}
    vectorizer = CountVectorizer(vocabulary=vocabulary)

    expected = r"""
CountVectorizer(analyzer='word', binary=False, decode_error='strict',
                dtype=<class 'numpy.int64'>, encoding='utf-8', input='content',
                lowercase=True, max_df=1.0, max_features=None, min_df=1,
                ngram_range=(1, 1), preprocessor=None, stop_words=None,
                strip_accents=None, token_pattern='(?u)\\b\\w\\w+\\b',
                tokenizer=None,
                vocabulary={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
                            8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14,
                            15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20,
                            21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26,
                            27: 27, 28: 28, 29: 29, ...})"""

    expected = expected[1:]  # remove first \n
    assert pp.pformat(vectorizer) == expected

    # Also test with lists
    param_grid = {"C": list(range(n_max_elements_to_show))}
    gs = GridSearchCV(SVC(), param_grid)
    expected = """
GridSearchCV(cv='warn', error_score='raise-deprecating',
             estimator=SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
                           decision_function_shape='ovr', degree=3,
                           gamma='auto_deprecated', kernel='rbf', max_iter=-1,
                           probability=False, random_state=None, shrinking=True,
                           tol=0.001, verbose=False),
             iid='warn', n_jobs=None,
             param_grid={'C': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                               15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                               27, 28, 29]},
             pre_dispatch='2*n_jobs', refit=True, return_train_score=False,
             scoring=None, verbose=0)"""

    expected = expected[1:]  # remove first \n
    assert pp.pformat(gs) == expected

    # Now with ellipsis
    param_grid = {"C": list(range(n_max_elements_to_show + 1))}
    gs = GridSearchCV(SVC(), param_grid)
    expected = """
GridSearchCV(cv='warn', error_score='raise-deprecating',
             estimator=SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
                           decision_function_shape='ovr', degree=3,
                           gamma='auto_deprecated', kernel='rbf', max_iter=-1,
                           probability=False, random_state=None, shrinking=True,
                           tol=0.001, verbose=False),
             iid='warn', n_jobs=None,
             param_grid={'C': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                               15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                               27, 28, 29, ...]},
             pre_dispatch='2*n_jobs', refit=True, return_train_score=False,
             scoring=None, verbose=0)"""

    expected = expected[1:]  # remove first \n
    assert pp.pformat(gs) == expected
