from archinstaller.config import InstallerConfig
from archinstaller.constants import AurHelper
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.commands.chroot import arch_chroot
from archinstaller.backend.exceptions import InstallError


def install_aur_helper(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> str:
    helper = config.aur_helper
    git_url = f"https://aur.archlinux.org/{helper.value}.git"
    build_dir = f"/tmp/{helper.value}-build"

    arch_chroot(executor, ["pacman", "-S", "--needed", "--noconfirm", "base-devel", "git"], target_root)

    arch_chroot(executor, ["bash", "-c", f"""
        useradd -m -s /bin/bash aurbuild 2>/dev/null || true
        echo 'aurbuild ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/aurbuild
    """], target_root)

    arch_chroot(executor, ["su", "-", "aurbuild", "-c", f"""
        rm -rf {build_dir}
        git clone {git_url} {build_dir}
        cd {build_dir}
        makepkg -si --noconfirm
    """], target_root)

    arch_chroot(executor, ["bash", "-c", f"""
        rm -rf {build_dir}
        rm -f /etc/sudoers.d/aurbuild
    """], target_root)

    return helper.value


def install_aur_packages(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    if not config.aur_packages:
        return
    helper = config.aur_helper.value
    arch_chroot(executor, ["su", "-", "aurbuild", "-c",
        f"{helper} -S --noconfirm --needed {' '.join(config.aur_packages)}",
    ], target_root)
