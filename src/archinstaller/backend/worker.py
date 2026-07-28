from datetime import datetime, timezone
from collections.abc import Callable

import gi
gi.require_version("GLib", "2.0")
from gi.repository import GLib

from archinstaller.config import InstallerConfig
from archinstaller.constants import DesktopEnvironment
from archinstaller.backend.executor import CommandExecutor
from archinstaller.backend.commands.partitioning import wipe_disk, create_partition_table, create_partition
from archinstaller.backend.commands.filesystem import create_filesystem, mount_all, unmount_all
from archinstaller.backend.commands.pacstrap import install_base
from archinstaller.backend.commands.chroot import generate_fstab, enable_service
from archinstaller.backend.commands.bootloader import install_bootloader
from archinstaller.backend.commands.locale import set_locale, set_timezone, set_keyboard, set_hostname
from archinstaller.backend.commands.users import create_users, enable_sudo_wheel
from archinstaller.backend.commands.aur import install_aur_helper, install_aur_packages
from archinstaller.backend.exceptions import InstallError

TARGET_ROOT = "/mnt"


class InstallWorker:
    def __init__(self) -> None:
        self._executor = CommandExecutor()
        self._cancelled = False
        self._handlers: dict[str, list[Callable]] = {
            "progress": [],
            "status": [],
            "log_line": [],
            "finished": [],
            "error": [],
        }

    def connect(self, signal: str, handler: Callable) -> None:
        if signal in self._handlers:
            self._handlers[signal].append(handler)

    def _emit(self, signal: str, data=None) -> None:
        for handler in self._handlers.get(signal, []):
            GLib.idle_add(handler, data)

    def _log(self, message: str) -> None:
        self._emit("log_line", message)
        try:
            with open("/var/log/arch-installer.log", "a") as f:
                f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")
        except Exception:
            pass

    def _status(self, message: str, fraction: float) -> None:
        self._emit("progress", fraction)
        self._emit("status", message)
        self._log(message)

    def start(self, config: InstallerConfig) -> None:
        self._cancelled = False
        self._executor.reset()
        config.install_timestamp = datetime.now(timezone.utc).isoformat()
        import threading
        t = threading.Thread(target=self._run, args=(config,), daemon=True)
        t.start()

    def cancel(self) -> None:
        self._cancelled = True
        self._executor.cancel()

    def _run(self, config: InstallerConfig) -> None:
        steps = [
            (0.00, 0.18, "Preparing disk", self._step_partition),
            (0.18, 0.36, "Formatting partitions", self._step_format),
            (0.36, 0.58, "Installing base system", self._step_pacstrap),
            (0.58, 0.62, "Generating fstab", self._step_fstab),
            (0.62, 0.67, "Configuring locale", self._step_locale),
            (0.67, 0.72, "Creating users", self._step_users),
            (0.72, 0.82, "Installing bootloader", self._step_bootloader),
            (0.82, 0.92, "Setting up AUR", self._step_aur),
            (0.92, 0.99, "Finalizing", self._step_finalize),
        ]
        try:
            for start_fraction, end_fraction, label, step_fn in steps:
                if self._cancelled:
                    self._log("Installation cancelled by user")
                    self._emit("error", "Cancelled by user")
                    return
                self._status(label, start_fraction)
                step_fn(config)
                self._status(f"{label} done", end_fraction)
            self._status("Installation complete!", 1.0)
            self._emit("finished", None)
        except InstallError as e:
            self._log(f"Installation failed: {e}")
            self._emit("error", str(e))

    def _step_partition(self, config: InstallerConfig) -> None:
        if config.wipe_disk:
            self._log(f"Wiping disk {config.target_disk}")
            wipe_disk(self._executor, config.target_disk)
            self._log(f"Creating {config.partition_scheme} partition table on {config.target_disk}")
            create_partition_table(self._executor, config.target_disk, config.partition_scheme)
            for i, spec in enumerate(config.partitions, 1):
                if self._cancelled:
                    return
                self._log(f"Creating partition {i}: {spec.mount_point} ({spec.fs_type})")
                device = create_partition(self._executor, spec, i)
                spec.device = device

    def _step_format(self, config: InstallerConfig) -> None:
        for spec in config.partitions:
            if self._cancelled:
                return
            self._log(f"Formatting {spec.device} as {spec.fs_type}")
            create_filesystem(self._executor, spec, config.encryption_passphrase)

        self._log("Mounting partitions")
        root_spec = next((p for p in config.partitions if p.mount_point == "/"), None)
        compression = root_spec.btrfs_compression if root_spec else "zstd"
        mount_all(self._executor, config.partitions, TARGET_ROOT, compression)

    def _step_pacstrap(self, config: InstallerConfig) -> None:
        packages = ["base", config.kernel, "linux-firmware", "base-devel",
                     "sudo", "networkmanager", "grub", "efibootmgr", "dosfstools",
                     "mtools", "os-prober", "vim", "man-db", "man-pages",
                     "texinfo", "git"]

        if config.desktop != DesktopEnvironment.NONE:
            from archinstaller.services.package_list import get_de_packages
            packages.extend(get_de_packages(config.desktop))

        if config.enable_multilib:
            self._log("Enabling multilib repository")
            import os
            pacman_conf = f"{TARGET_ROOT}/etc/pacman.conf"
            if os.path.exists(pacman_conf):
                with open(pacman_conf, "r") as f:
                    content = f.read()
                content = content.replace("#[multilib]", "[multilib]")
                content = content.replace("#Include = /etc/pacman.d/mirrorlist", "Include = /etc/pacman.d/mirrorlist")
                with open(pacman_conf, "w") as f:
                    f.write(content)

        if config.extra_packages:
            packages.extend(config.extra_packages)

        from archinstaller.constants import FilesystemType
        if any(p.fs_type == FilesystemType.BTRFS for p in config.partitions):
            packages.append("btrfs-progs")
        if config.enable_snapper:
            packages.append("snapper")

        self._log(f"Running pacstrap with {len(packages)} packages")
        install_base(self._executor, packages, TARGET_ROOT)

    def _step_fstab(self, config: InstallerConfig) -> None:
        self._log("Generating fstab")
        generate_fstab(self._executor, TARGET_ROOT)

    def _step_locale(self, config: InstallerConfig) -> None:
        self._log("Configuring locale, timezone, and keyboard")
        set_locale(self._executor, config, TARGET_ROOT)
        set_timezone(self._executor, config, TARGET_ROOT)
        set_keyboard(self._executor, config, TARGET_ROOT)
        set_hostname(self._executor, config, TARGET_ROOT)

    def _step_users(self, config: InstallerConfig) -> None:
        self._log("Setting up users")
        enable_sudo_wheel(self._executor, TARGET_ROOT)
        create_users(self._executor, config, TARGET_ROOT)

    def _step_bootloader(self, config: InstallerConfig) -> None:
        self._log(f"Installing bootloader: {config.bootloader}")
        install_bootloader(self._executor, config, TARGET_ROOT)

    def _step_aur(self, config: InstallerConfig) -> None:
        if not config.enable_aur:
            return
        self._log(f"Installing AUR helper: {config.aur_helper.value}")
        install_aur_helper(self._executor, config, TARGET_ROOT)
        if config.aur_packages:
            self._log(f"Installing {len(config.aur_packages)} AUR packages")
            install_aur_packages(self._executor, config, TARGET_ROOT)

    def _step_finalize(self, config: InstallerConfig) -> None:
        self._log("Enabling NetworkManager")
        enable_service(self._executor, "NetworkManager", TARGET_ROOT)
        if config.bootloader == "grub-uefi" or config.bootloader == "grub-bios":
            enable_service(self._executor, "grub-btrfsd", TARGET_ROOT)
        self._log("All done — system is ready for reboot")
