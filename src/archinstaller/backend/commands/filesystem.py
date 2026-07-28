from archinstaller.config import PartitionSpec
from archinstaller.constants import FilesystemType
from archinstaller.backend.executor import CommandExecutor


FS_MKFS_CMD: dict[FilesystemType, str] = {
    FilesystemType.EXT4: "mkfs.ext4",
    FilesystemType.BTRFS: "mkfs.btrfs",
    FilesystemType.XFS: "mkfs.xfs",
    FilesystemType.F2FS: "mkfs.f2fs",
    FilesystemType.FAT32: "mkfs.vfat",
    FilesystemType.NTFS: "mkfs.ntfs",
}


def _get_device_name(spec: PartitionSpec) -> str:
    if spec.encrypt and spec.luks_name:
        return f"/dev/mapper/{spec.luks_name}"
    return spec.device or spec.disk_device


def create_filesystem(executor: CommandExecutor, spec: PartitionSpec, passphrase: str = "") -> None:
    device = spec.device
    if not device:
        return

    if spec.encrypt and spec.luks_name:
        from archinstaller.backend.commands.pacstrap import create_luks as _luks_format
        _luks_format(spec.device, spec.luks_name, passphrase)
        device = f"/dev/mapper/{spec.luks_name}"

    if spec.fs_type == FilesystemType.SWAP:
        executor.run_sync(["mkswap", device])
        return

    cmd_name = FS_MKFS_CMD.get(spec.fs_type, "mkfs.ext4")
    cmd = [cmd_name]

    if spec.fs_type == FilesystemType.FAT32:
        cmd.extend(["-F32"])
    if spec.fs_type == FilesystemType.BTRFS:
        cmd.extend(["-f"])

    if spec.mkfs_options:
        cmd.extend(spec.mkfs_options.split())

    if spec.label:
        cmd.extend(["-L", spec.label])

    cmd.append(device)
    executor.run_sync(cmd)


def format_all(executor: CommandExecutor, partitions: list[PartitionSpec], passphrase: str = "") -> None:
    for spec in partitions:
        if spec.fs_type != FilesystemType.SWAP:
            create_filesystem(executor, spec, passphrase)


def mount_partition(executor: CommandExecutor, spec: PartitionSpec, target_root: str) -> None:
    device = _get_device_name(spec)
    mount_point = f"{target_root}{spec.mount_point}"
    if spec.fs_type == FilesystemType.SWAP:
        executor.run_sync(["swapon", device])
        return

    options = spec.mount_options.split(",") if spec.mount_options else ["defaults", "noatime"]
    cmd = ["mount", "-o", ",".join(opt for opt in options if opt)]
    cmd.extend([device, mount_point])
    executor.run_sync(cmd)


def mount_all(executor: CommandExecutor, partitions: list[PartitionSpec], target_root: str = "/mnt") -> None:
    sorted_parts = sorted(partitions, key=lambda p: (2 if p.mount_point == "/boot/efi" else
                                                      1 if p.mount_point == "/boot" else 0))
    for spec in sorted_parts:
        mount_partition(executor, spec, target_root)


def unmount_all(executor: CommandExecutor, target_root: str = "/mnt") -> None:
    executor.run_sync(["umount", "-R", target_root])
    executor.run_sync(["swapoff", "-a"])
