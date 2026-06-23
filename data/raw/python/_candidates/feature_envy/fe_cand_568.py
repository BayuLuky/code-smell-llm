def store_response(self, spider, request, response):
    key = self._fingerprinter.fingerprint(request).hex()
    data = {
        "status": response.status,
        "url": response.url,
        "headers": dict(response.headers),
        "body": response.body,
    }
    self.db[f"{key}_data"] = pickle.dumps(data, protocol=4)
    self.db[f"{key}_time"] = str(time())
