def process_response(self, request, response, spider):
    if request.meta.get("dont_retry", False):
        return response
    if response.status in self.retry_http_codes:
        reason = response_status_message(response.status)
        return self._retry(request, reason, spider) or response
    return response
