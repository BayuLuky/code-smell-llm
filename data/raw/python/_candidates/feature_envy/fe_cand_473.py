def stat_file(self, path, info):
    def _onsuccess(blob):
        if blob:
            checksum = base64.b64decode(blob.md5_hash).hex()
            last_modified = time.mktime(blob.updated.timetuple())
            return {"checksum": checksum, "last_modified": last_modified}
        return {}

    blob_path = self._get_blob_path(path)
    return threads.deferToThread(self.bucket.get_blob, blob_path).addCallback(
        _onsuccess
    )
