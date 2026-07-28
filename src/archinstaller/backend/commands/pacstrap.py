import subprocess
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.exceptions import CommandFailedError


def install_base(executor: CommandExecutor, packages: list[str], target_root: str = "/mnt") -> None:
    cmd = ["pacstrap", "-K", target_root] + packages
    executor.run_sync(cmd)


def create_luks(device: str, luks_name: str, passphrase: str) -> None:
    proc = subprocess.run(
        ["cryptsetup", "luksFormat", "--type", "luks2", device],
        input=passphrase + "\n",
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CommandFailedError(["cryptsetup", "luksFormat"], proc.returncode, proc.stderr)
    proc = subprocess.run(
        ["cryptsetup", "open", device, luks_name],
        input=passphrase + "\n",
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CommandFailedError(["cryptsetup", "open"], proc.returncode, proc.stderr)
