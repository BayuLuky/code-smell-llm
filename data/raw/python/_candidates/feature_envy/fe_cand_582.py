def __init__(
    self,
    charset: str = "utf-8",
    env: t.Optional[t.Mapping[str, t.Optional[str]]] = None,
    echo_stdin: bool = False,
    mix_stderr: bool = True,
) -> None:
    self.charset = charset
    self.env: t.Mapping[str, t.Optional[str]] = env or {}
    self.echo_stdin = echo_stdin
    self.mix_stderr = mix_stderr
