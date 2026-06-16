class FTPFilesStore:
    FTP_USERNAME = None
    FTP_PASSWORD = None
    USE_ACTIVE_MODE = None

    def __init__(self, uri):
        if not uri.startswith("ftp://"):
            raise ValueError(f"Incorrect URI scheme in {uri}, expected 'ftp'")
        u = urlparse(uri)
        self.port = u.port
        self.host = u.hostname
        self.port = int(u.port or 21)
        self.username = u.username or self.FTP_USERNAME
        self.password = u.password or self.FTP_PASSWORD
        self.basedir = u.path.rstrip("/")

    def persist_file(self, path, buf, info, meta=None, headers=None):
        path = f"{self.basedir}/{path}"
        return threads.deferToThread(
            ftp_store_file,
            path=path,
            file=buf,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_active_mode=self.USE_ACTIVE_MODE,
        )

    def stat_file(self, path, info):
        def _stat_file(path):
            try:
                ftp = FTP()
                ftp.connect(self.host, self.port)
                ftp.login(self.username, self.password)
                if self.USE_ACTIVE_MODE:
                    ftp.set_pasv(False)
                file_path = f"{self.basedir}/{path}"
                last_modified = float(ftp.voidcmd(f"MDTM {file_path}")[4:].strip())
                m = hashlib.md5()
                ftp.retrbinary(f"RETR {file_path}", m.update)
                return {"last_modified": last_modified, "checksum": m.hexdigest()}
            # The file doesn't exist
            except Exception:
                return {}

        return threads.deferToThread(_stat_file, path)
