class InstallError(Exception):
    pass


class CommandFailedError(InstallError):
    def __init__(self, cmd: list[str], returncode: int, stderr: str) -> None:
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        cmd_str = " ".join(cmd)
        super().__init__(f"Command failed with exit code {returncode}: {cmd_str}\n{stderr}")


class PartitionError(InstallError):
    pass


class MountError(InstallError):
    pass


class BootloaderError(InstallError):
    pass
