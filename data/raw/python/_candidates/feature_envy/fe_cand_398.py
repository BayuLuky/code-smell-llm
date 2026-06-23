def log_message(self, format, *args):
    extra = {
        "request": self.request,
        "server_time": self.log_date_time_string(),
    }
    if args[1][0] == "4":
        # 0x16 = Handshake, 0x03 = SSL 3.0 or TLS 1.x
        if args[0].startswith("\x16\x03"):
            extra["status_code"] = 500
            logger.error(
                "You're accessing the development server over HTTPS, but "
                "it only supports HTTP.",
                extra=extra,
            )
            return

    if args[1].isdigit() and len(args[1]) == 3:
        status_code = int(args[1])
        extra["status_code"] = status_code

        if status_code >= 500:
            level = logger.error
        elif status_code >= 400:
            level = logger.warning
        else:
            level = logger.info
    else:
        level = logger.info

    level(format, *args, extra=extra)
