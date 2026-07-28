from archinstaller.config import InstallerConfig
from archinstaller.constants import BootloaderType
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.commands.chroot import arch_chroot


def install_bootloader(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    if config.bootloader == BootloaderType.GRUB_BIOS:
        _install_grub_bios(executor, config, target_root)
    elif config.bootloader == BootloaderType.GRUB_UEFI:
        _install_grub_uefi(executor, config, target_root)
    elif config.bootloader == BootloaderType.SYSTEMD_BOOT:
        _install_systemd_boot(executor, config, target_root)


def _install_grub_bios(executor: CommandExecutor, config: InstallerConfig, target_root: str) -> None:
    arch_chroot(executor, ["grub-install", "--target=i386-pc", config.target_disk], target_root)
    arch_chroot(executor, ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], target_root)


def _install_grub_uefi(executor: CommandExecutor, config: InstallerConfig, target_root: str) -> None:
    arch_chroot(executor, [
        "grub-install", "--target=x86_64-efi",
        f"--efi-directory={config.efi_mount_point}",
        "--bootloader-id=GRUB",
    ], target_root)
    arch_chroot(executor, ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], target_root)


def _install_systemd_boot(executor: CommandExecutor, config: InstallerConfig, target_root: str) -> None:
    arch_chroot(executor, ["bootctl", "install"], target_root)

    root_part = next((p for p in config.partitions if p.mount_point == "/"), None)
    if not root_part:
        raise RuntimeError("No root partition found for systemd-boot config")

    if config.encryption_passphrase and root_part.encrypt:
        root_option = f"root=/dev/mapper/{root_part.luks_name}"
    else:
        root_option = f"root=PARTUUID=$(blkid -s PARTUUID -o value {root_part.device})" if root_part.device else "root=/dev/sda2"

    loader_conf_path = f"{target_root}/boot/loader/loader.conf"
    with open(loader_conf_path, "w") as f:
        f.write("default arch-*\ntimeout 3\neditor 0\n")

    entries_dir = f"{target_root}/boot/loader/entries"
    import os
    os.makedirs(entries_dir, exist_ok=True)

    entry_path = f"{entries_dir}/arch.conf"
    entry_lines = [
        "title   Arch Linux",
        f"linux   /vmlinuz-{config.kernel}",
        f"initrd  /initramfs-{config.kernel}.img",
        f"options {root_option} rw",
    ]
    with open(entry_path, "w") as f:
        f.write("\n".join(entry_lines) + "\n")
