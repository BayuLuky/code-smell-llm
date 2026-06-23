def add_pre_hook(self, request, results):
    if hasattr(self, "pre_process"):
        cb = request.callback

        @wraps(cb)
        def wrapper(response, **cb_kwargs):
            try:
                results.startTest(self.testcase_pre)
                self.pre_process(response)
                results.stopTest(self.testcase_pre)
            except AssertionError:
                results.addFailure(self.testcase_pre, sys.exc_info())
            except Exception:
                results.addError(self.testcase_pre, sys.exc_info())
            else:
                results.addSuccess(self.testcase_pre)
            finally:
                cb_result = cb(response, **cb_kwargs)
                if isinstance(cb_result, (AsyncGenerator, CoroutineType)):
                    raise TypeError("Contracts don't support async callbacks")
                return list(  # pylint: disable=return-in-finally
                    iterate_spider_output(cb_result)
                )

        request.callback = wrapper

    return request
