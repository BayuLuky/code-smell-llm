def invoke(
    self,
    cli: "BaseCommand",
    args: t.Optional[t.Union[str, t.Sequence[str]]] = None,
    input: t.Optional[t.Union[str, bytes, t.IO[t.Any]]] = None,
    env: t.Optional[t.Mapping[str, t.Optional[str]]] = None,
    catch_exceptions: bool = True,
    color: bool = False,
    **extra: t.Any,
) -> Result:
    """Invokes a command in an isolated environment.  The arguments are
    forwarded directly to the command line script, the `extra` keyword
    arguments are passed to the :meth:`~clickpkg.Command.main` function of
    the command.

    This returns a :class:`Result` object.

    :param cli: the command to invoke
    :param args: the arguments to invoke. It may be given as an iterable
                 or a string. When given as string it will be interpreted
                 as a Unix shell command. More details at
                 :func:`shlex.split`.
    :param input: the input data for `sys.stdin`.
    :param env: the environment overrides.
    :param catch_exceptions: Whether to catch any other exceptions than
                             ``SystemExit``.
    :param extra: the keyword arguments to pass to :meth:`main`.
    :param color: whether the output should contain color codes. The
                  application can still override this explicitly.

    .. versionchanged:: 8.0
        The result object has the ``return_value`` attribute with
        the value returned from the invoked command.

    .. versionchanged:: 4.0
        Added the ``color`` parameter.

    .. versionchanged:: 3.0
        Added the ``catch_exceptions`` parameter.

    .. versionchanged:: 3.0
        The result object has the ``exc_info`` attribute with the
        traceback if available.
    """
    exc_info = None
    with self.isolation(input=input, env=env, color=color) as outstreams:
        return_value = None
        exception: t.Optional[BaseException] = None
        exit_code = 0

        if isinstance(args, str):
            args = shlex.split(args)

        try:
            prog_name = extra.pop("prog_name")
        except KeyError:
            prog_name = self.get_default_prog_name(cli)

        try:
            return_value = cli.main(args=args or (), prog_name=prog_name, **extra)
        except SystemExit as e:
            exc_info = sys.exc_info()
            e_code = t.cast(t.Optional[t.Union[int, t.Any]], e.code)

            if e_code is None:
                e_code = 0

            if e_code != 0:
                exception = e

            if not isinstance(e_code, int):
                sys.stdout.write(str(e_code))
                sys.stdout.write("\n")
                e_code = 1

            exit_code = e_code

        except Exception as e:
            if not catch_exceptions:
                raise
            exception = e
            exit_code = 1
            exc_info = sys.exc_info()
        finally:
            sys.stdout.flush()
            stdout = outstreams[0].getvalue()
            if self.mix_stderr:
                stderr = None
            else:
                stderr = outstreams[1].getvalue()  # type: ignore

    return Result(
        runner=self,
        stdout_bytes=stdout,
        stderr_bytes=stderr,
        return_value=return_value,
        exit_code=exit_code,
        exception=exception,
        exc_info=exc_info,  # type: ignore
    )
