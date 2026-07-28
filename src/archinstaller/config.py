from dataclasses import dataclass, field
from .constants import (
    AurHelper,
    DesktopEnvironment,
    FilesystemType,
    BootloaderType,
    PartitionRole,
)


@dataclass
class PartitionSpec:
    disk_device: str = ""
    device: str | None = None
    role: PartitionRole = PartitionRole.ROOT
    size_bytes: int = 0
    fs_type: FilesystemType = FilesystemType.BTRFS
    label: str = ""
    mount_point: str = ""
    mkfs_options: str = ""
    mount_options: str = "defaults,noatime"
    encrypt: bool = False
    luks_name: str = ""
    btrfs_compression: str = "zstd"


BTRFS_DEFAULT_SUBVOLUMES: dict[str, bool] = {
    "@": True,
    "@home": True,
    "@snapshots": True,
    "@var_log": True,
    "@var_cache": True,
    "@pkg": True,
}

BTRFS_NODATACOW_DIRS: list[str] = [
    "/var/lib/libvirt/images",
    "/var/lib/postgres",
    "/var/lib/mysql",
    "/var/lib/mongodb",
    "/var/lib/docker",
]


@dataclass
class DiskInfo:
    device: str = ""
    model: str = ""
    size_bytes: int = 0
    sector_size: int = 512
    transport: str = ""
    partition_table: str = ""
    partitions: list["PartitionInfo"] = field(default_factory=list)
    is_removable: bool = False


@dataclass
class PartitionInfo:
    device: str = ""
    size_bytes: int = 0
    start_bytes: int = 0
    end_bytes: int = 0
    fs_type: str = ""
    label: str = ""
    flags: list[str] = field(default_factory=list)


@dataclass
class UserAccount:
    username: str = ""
    password_hashed: str = ""
    full_name: str = ""
    autologin: bool = False
    is_admin: bool = True


@dataclass
class NetworkConfig:
    hostname: str = "archlinux"
    enable_networkmanager: bool = True
    enable_sshd: bool = False
    dns_servers: list[str] = field(default_factory=list)
    ntp_servers: list[str] = field(default_factory=list)


@dataclass
class InstallerConfig:
    language: str = "en_US"
    locale: str = "en_US.UTF-8"
    keyboard_layout: str = "us"
    keyboard_variant: str = ""
    timezone: str = "UTC"
    mirror_country: str = ""

    target_disk: str = ""
    wipe_disk: bool = False
    partition_scheme: str = "gpt"
    partitions: list[PartitionSpec] = field(default_factory=list)
    encryption_passphrase: str = ""

    root_password_hashed: str = ""
    users: list[UserAccount] = field(default_factory=list)

    network: NetworkConfig = field(default_factory=NetworkConfig)

    desktop: DesktopEnvironment = DesktopEnvironment.GNOME
    extra_packages: list[str] = field(default_factory=list)
    enable_multilib: bool = False
    enable_aur: bool = False
    aur_helper: AurHelper = AurHelper.PARU
    aur_packages: list[str] = field(default_factory=list)

    enable_snapper: bool = False

    bootloader: BootloaderType = BootloaderType.GRUB_UEFI
    kernel: str = "linux"
    initramfs_hooks: str = "base udev autodetect modconf block filesystems keyboard fsck"

    is_uefi: bool = True
    efi_mount_point: str = "/boot/efi"

    install_timestamp: str = ""
    log_file: str = "/var/log/arch-installer.log"

    def get_mount_map(self) -> dict[str, PartitionSpec]:
        return {p.mount_point: p for p in self.partitions if p.mount_point}

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.target_disk:
            errors.append("No target disk selected.")
        root_specs = [p for p in self.partitions if p.role == PartitionRole.ROOT]
        if not root_specs:
            errors.append("No root partition (/) defined.")
        if self.is_uefi:
            esp_specs = [p for p in self.partitions if p.role == PartitionRole.ESP]
            if not esp_specs:
                errors.append("UEFI mode requires an EFI System Partition (ESP).")
        if not self.root_password_hashed and not any(u.is_admin for u in self.users):
            errors.append("Either a root password or an administrator user is required.")
        if not self.network.hostname.strip():
            errors.append("Hostname cannot be empty.")
        if self.encryption_passphrase:
            luks_specs = [p for p in self.partitions if p.encrypt]
            if not luks_specs:
                errors.append("Encryption passphrase set but no encrypted partitions defined.")
        return errors
