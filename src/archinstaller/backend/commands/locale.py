from archinstaller.config import InstallerConfig
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.commands.chroot import arch_chroot


def set_locale(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    locale_gen_path = f"{target_root}/etc/locale.gen"
    try:
        with open(locale_gen_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return
    content = content.replace(f"#{config.locale}", config.locale)
    with open(locale_gen_path, "w") as f:
        f.write(content)
    arch_chroot(executor, ["locale-gen"], target_root)
    locale_conf = f"LANG={config.locale}\n"
    with open(f"{target_root}/etc/locale.conf", "w") as f:
        f.write(locale_conf)


def set_timezone(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    arch_chroot(executor, [
        "ln", "-sf", f"/usr/share/zoneinfo/{config.timezone}", "/etc/localtime"
    ], target_root)
    arch_chroot(executor, ["hwclock", "--systohc"], target_root)


def set_keyboard(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    vconsole_conf = f"KEYMAP={config.keyboard_layout}\n"
    if config.keyboard_variant:
        vconsole_conf += f"XKBVARIANT={config.keyboard_variant}\n"
    with open(f"{target_root}/etc/vconsole.conf", "w") as f:
        f.write(vconsole_conf)


def set_hostname(executor: CommandExecutor, config: InstallerConfig, target_root: str = "/mnt") -> None:
    with open(f"{target_root}/etc/hostname", "w") as f:
        f.write(f"{config.network.hostname}\n")
    with open(f"{target_root}/etc/hosts", "w") as f:
        f.write(f"127.0.0.1\tlocalhost\n::1\t\tlocalhost\n127.0.1.1\t{config.network.hostname}.localdomain\t{config.network.hostname}\n")
