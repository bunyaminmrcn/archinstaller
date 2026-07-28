import os
from archinstaller.backend.executor import CommandExecutor


def arch_chroot(executor: CommandExecutor, command: list[str], target_root: str = "/mnt") -> None:
    executor.run_sync(["arch-chroot", target_root] + command)


def shell_arch_chroot(executor: CommandExecutor, cmd_str: str, target_root: str = "/mnt") -> None:
    executor.run_sync(["arch-chroot", target_root, "bash", "-c", cmd_str])


def generate_fstab(executor: CommandExecutor, target_root: str = "/mnt") -> None:
    with open(f"{target_root}/etc/fstab", "a") as f:
        pass
    proc = executor.run_sync(["genfstab", "-U", target_root])
    with open(f"{target_root}/etc/fstab", "w") as f:
        f.write(proc.stdout)


def enable_service(executor: CommandExecutor, service: str, target_root: str = "/mnt") -> None:
    arch_chroot(executor, ["systemctl", "enable", service], target_root)
