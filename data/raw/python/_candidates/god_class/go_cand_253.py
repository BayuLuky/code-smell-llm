class Group(MultiCommand):
    """A group allows a command to have subcommands attached. This is
    the most common way to implement nesting in Click.

    :param name: The name of the group command.
    :param commands: A dict mapping names to :class:`Command` objects.
        Can also be a list of :class:`Command`, which will use
        :attr:`Command.name` to create the dict.
    :param attrs: Other command arguments described in
        :class:`MultiCommand`, :class:`Command`, and
        :class:`BaseCommand`.

    .. versionchanged:: 8.0
        The ``commands`` argument can be a list of command objects.
    """

    #: If set, this is used by the group's :meth:`command` decorator
    #: as the default :class:`Command` class. This is useful to make all
    #: subcommands use a custom command class.
    #:
    #: .. versionadded:: 8.0
    command_class: t.Optional[t.Type[Command]] = None

    #: If set, this is used by the group's :meth:`group` decorator
    #: as the default :class:`Group` class. This is useful to make all
    #: subgroups use a custom group class.
    #:
    #: If set to the special value :class:`type` (literally
    #: ``group_class = type``), this group's class will be used as the
    #: default class. This makes a custom group class continue to make
    #: custom groups.
    #:
    #: .. versionadded:: 8.0
    group_class: t.Optional[t.Union[t.Type["Group"], t.Type[type]]] = None
    # Literal[type] isn't valid, so use Type[type]

    def __init__(
        self,
        name: t.Optional[str] = None,
        commands: t.Optional[
            t.Union[t.MutableMapping[str, Command], t.Sequence[Command]]
        ] = None,
        **attrs: t.Any,
    ) -> None:
        super().__init__(name, **attrs)

        if commands is None:
            commands = {}
        elif isinstance(commands, abc.Sequence):
            commands = {c.name: c for c in commands if c.name is not None}

        #: The registered subcommands by their exported names.
        self.commands: t.MutableMapping[str, Command] = commands

    def add_command(self, cmd: Command, name: t.Optional[str] = None) -> None:
        """Registers another :class:`Command` with this group.  If the name
        is not provided, the name of the command is used.
        """
        name = name or cmd.name
        if name is None:
            raise TypeError("Command has no name.")
        _check_multicommand(self, name, cmd, register=True)
        self.commands[name] = cmd

    @t.overload
    def command(self, __func: t.Callable[..., t.Any]) -> Command:
        ...

    @t.overload
    def command(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], Command]:
        ...

    def command(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Union[t.Callable[[t.Callable[..., t.Any]], Command], Command]:
        """A shortcut decorator for declaring and attaching a command to
        the group. This takes the same arguments as :func:`command` and
        immediately registers the created command with this group by
        calling :meth:`add_command`.

        To customize the command class used, set the
        :attr:`command_class` attribute.

        .. versionchanged:: 8.1
            This decorator can be applied without parentheses.

        .. versionchanged:: 8.0
            Added the :attr:`command_class` attribute.
        """
        from .decorators import command

        func: t.Optional[t.Callable[..., t.Any]] = None

        if args and callable(args[0]):
            assert (
                len(args) == 1 and not kwargs
            ), "Use 'command(**kwargs)(callable)' to provide arguments."
            (func,) = args
            args = ()

        if self.command_class and kwargs.get("cls") is None:
            kwargs["cls"] = self.command_class

        def decorator(f: t.Callable[..., t.Any]) -> Command:
            cmd: Command = command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        if func is not None:
            return decorator(func)

        return decorator

    @t.overload
    def group(self, __func: t.Callable[..., t.Any]) -> "Group":
        ...

    @t.overload
    def group(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], "Group"]:
        ...

    def group(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Union[t.Callable[[t.Callable[..., t.Any]], "Group"], "Group"]:
        """A shortcut decorator for declaring and attaching a group to
        the group. This takes the same arguments as :func:`group` and
        immediately registers the created group with this group by
        calling :meth:`add_command`.

        To customize the group class used, set the :attr:`group_class`
        attribute.

        .. versionchanged:: 8.1
            This decorator can be applied without parentheses.

        .. versionchanged:: 8.0
            Added the :attr:`group_class` attribute.
        """
        from .decorators import group

        func: t.Optional[t.Callable[..., t.Any]] = None

        if args and callable(args[0]):
            assert (
                len(args) == 1 and not kwargs
            ), "Use 'group(**kwargs)(callable)' to provide arguments."
            (func,) = args
            args = ()

        if self.group_class is not None and kwargs.get("cls") is None:
            if self.group_class is type:
                kwargs["cls"] = type(self)
            else:
                kwargs["cls"] = self.group_class

        def decorator(f: t.Callable[..., t.Any]) -> "Group":
            cmd: Group = group(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        if func is not None:
            return decorator(func)

        return decorator

    def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
        return self.commands.get(cmd_name)

    def list_commands(self, ctx: Context) -> t.List[str]:
        return sorted(self.commands)
