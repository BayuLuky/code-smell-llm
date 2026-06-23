def _check_version() -> None:
    import subprocess

    output = subprocess.run(
        ["bash", "-c", 'echo "${BASH_VERSION}"'], stdout=subprocess.PIPE
    )
    match = re.search(r"^(\d+)\.(\d+)\.\d+", output.stdout.decode())

    if match is not None:
        major, minor = match.groups()

        if major < "4" or major == "4" and minor < "4":
            echo(
                _(
                    "Shell completion is not supported for Bash"
                    " versions older than 4.4."
                ),
                err=True,
            )
    else:
        echo(
            _("Couldn't detect Bash version, shell completion is not supported."),
            err=True,
        )
