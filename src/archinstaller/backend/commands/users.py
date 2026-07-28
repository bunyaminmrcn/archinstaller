import tempfile
import os
from archinstaller.config import InstallerConfig
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.commands.chroot import arch_chroot


def set_root_password(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    if not config.root_password_hashed:
        return
    arch_chroot(executor, [
        "usermod", "-p", config.root_password_hashed, "root"
    ], target_root)


def create_user(executor: CommandExecutor, username: str, password_hashed: str,
                full_name: str = "", is_admin: bool = True, target_root: str = "/mnt") -> None:
    cmd = ["useradd", "-m"]
    if full_name:
        cmd.extend(["-c", full_name])
    cmd.append(username)
    arch_chroot(executor, cmd, target_root)

    if is_admin:
        arch_chroot(executor, ["usermod", "-aG", "wheel", username], target_root)

    arch_chroot(executor, [
        "usermod", "-p", password_hashed, username
    ], target_root)


def create_users(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    set_root_password(executor, config, target_root)
    for user in config.users:
        create_user(
            executor,
            user.username,
            user.password_hashed,
            user.full_name,
            user.is_admin,
            target_root,
        )


def enable_sudo_wheel(executor: CommandExecutor, target_root: str = "/mnt") -> None:
    with open(f"{target_root}/etc/sudoers.d/10-wheel", "w") as f:
        f.write("%wheel ALL=(ALL:ALL) ALL\n")
    os.chmod(f"{target_root}/etc/sudoers.d/10-wheel", 0o440)
