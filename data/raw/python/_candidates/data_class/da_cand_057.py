class S3FeedStorage(BlockingFeedStorage):
    def __init__(
        self,
        uri,
        access_key=None,
        secret_key=None,
        acl=None,
        endpoint_url=None,
        *,
        feed_options=None,
        session_token=None,
        region_name=None,
    ):
        if not is_botocore_available():
            raise NotConfigured("missing botocore library")
        u = urlparse(uri)
        self.bucketname = u.hostname
        self.access_key = u.username or access_key
        self.secret_key = u.password or secret_key
        self.session_token = session_token
        self.keyname = u.path[1:]  # remove first "/"
        self.acl = acl
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        if IS_BOTO3_AVAILABLE:
            import boto3.session

            session = boto3.session.Session()

            self.s3_client = session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                aws_session_token=self.session_token,
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
            )
        else:
            warnings.warn(
                "`botocore` usage has been deprecated for S3 feed "
                "export, please use `boto3` to avoid problems",
                category=ScrapyDeprecationWarning,
            )

            import botocore.session

            session = botocore.session.get_session()

            self.s3_client = session.create_client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                aws_session_token=self.session_token,
                endpoint_url=self.endpoint_url,
                region_name=self.region_name,
            )

        if feed_options and feed_options.get("overwrite", True) is False:
            logger.warning(
                "S3 does not support appending to files. To "
                "suppress this warning, remove the overwrite "
                "option from your FEEDS setting or set it to True."
            )

    @classmethod
    def from_crawler(cls, crawler, uri, *, feed_options=None):
        return build_storage(
            cls,
            uri,
            access_key=crawler.settings["AWS_ACCESS_KEY_ID"],
            secret_key=crawler.settings["AWS_SECRET_ACCESS_KEY"],
            session_token=crawler.settings["AWS_SESSION_TOKEN"],
            acl=crawler.settings["FEED_STORAGE_S3_ACL"] or None,
            endpoint_url=crawler.settings["AWS_ENDPOINT_URL"] or None,
            region_name=crawler.settings["AWS_REGION_NAME"] or None,
            feed_options=feed_options,
        )

    def _store_in_thread(self, file):
        file.seek(0)
        if IS_BOTO3_AVAILABLE:
            kwargs = {"ExtraArgs": {"ACL": self.acl}} if self.acl else {}
            self.s3_client.upload_fileobj(
                Bucket=self.bucketname, Key=self.keyname, Fileobj=file, **kwargs
            )
        else:
            kwargs = {"ACL": self.acl} if self.acl else {}
            self.s3_client.put_object(
                Bucket=self.bucketname, Key=self.keyname, Body=file, **kwargs
            )
        file.close()
