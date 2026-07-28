from archinstaller.config import PartitionSpec, BTRFS_DEFAULT_SUBVOLUMES, BTRFS_NODATACOW_DIRS
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
        if spec.label:
            cmd.extend(["-L", spec.label])

    if spec.mkfs_options:
        cmd.extend(spec.mkfs_options.split())

    if spec.label and spec.fs_type != FilesystemType.BTRFS:
        cmd.extend(["-L", spec.label])

    cmd.append(device)
    executor.run_sync(cmd)


def _create_btrfs_subvolumes(executor: CommandExecutor, spec: PartitionSpec,
                              target_root: str, compression: str) -> None:
    import os
    device = _get_device_name(spec)
    mount_point = f"{target_root}{spec.mount_point}"

    mount_opts = ["defaults", "noatime"]
    if compression:
        mount_opts.append(f"compress={compression}")
    executor.run_sync(["mount", "-o", ",".join(mount_opts), device, mount_point])

    for subvol, enabled in BTRFS_DEFAULT_SUBVOLUMES.items():
        if enabled:
            executor.run_sync(["btrfs", "subvolume", "create", f"{mount_point}/{subvol}"])

    executor.run_sync(["umount", mount_point])

    root_mount_opts = mount_opts + ["subvol=@"]
    executor.run_sync(["mount", "-o", ",".join(root_mount_opts), device, mount_point])

    subvol_mounts = {
        "@home": f"{mount_point}/home",
        "@snapshots": f"{mount_point}/.snapshots",
        "@var_log": f"{mount_point}/var/log",
        "@var_cache": f"{mount_point}/var/cache",
        "@pkg": f"{mount_point}/var/cache/pacman/pkg",
    }

    for subvol, subvol_path in subvol_mounts.items():
        if subvol in BTRFS_DEFAULT_SUBVOLUMES and BTRFS_DEFAULT_SUBVOLUMES[subvol]:
            os.makedirs(subvol_path, exist_ok=True)
            subvol_mount_opts = mount_opts + [f"subvol={subvol}"]
            executor.run_sync(["mount", "-o", ",".join(subvol_mount_opts), device, subvol_path])

    for nodatacow_dir in BTRFS_NODATACOW_DIRS:
        full_path = f"{mount_point}{nodatacow_dir}"
        os.makedirs(full_path, exist_ok=True)
        executor.run_sync(["chattr", "+C", full_path])


def mount_partition(executor: CommandExecutor, spec: PartitionSpec, target_root: str,
                     btrfs_compression: str = "zstd") -> None:
    device = _get_device_name(spec)
    mount_point = f"{target_root}{spec.mount_point}"

    if spec.fs_type == FilesystemType.SWAP:
        executor.run_sync(["swapon", device])
        return

    if spec.fs_type == FilesystemType.BTRFS and spec.mount_point == "/":
        _create_btrfs_subvolumes(executor, spec, target_root, btrfs_compression)
        return

    options = spec.mount_options.split(",") if spec.mount_options else ["defaults", "noatime"]
    cmd = ["mount", "-o", ",".join(opt for opt in options if opt)]
    cmd.extend([device, mount_point])
    executor.run_sync(cmd)


def mount_all(executor: CommandExecutor, partitions: list[PartitionSpec],
              target_root: str = "/mnt", btrfs_compression: str = "zstd") -> None:
    import os

    sorted_parts = sorted(partitions, key=lambda p: (2 if p.mount_point == "/boot/efi" else
                                                      1 if p.mount_point == "/boot" else 0))
    for spec in sorted_parts:
        if spec.mount_point not in ("/", "/boot/efi", "/boot"):
            if spec.fs_type not in (FilesystemType.SWAP, FilesystemType.NTFS):
                os.makedirs(f"{target_root}{spec.mount_point}", exist_ok=True)
        if spec.role.value == "root":
            mount_partition(executor, spec, target_root, btrfs_compression)
        else:
            mount_partition(executor, spec, target_root)


def format_all(executor: CommandExecutor, partitions: list[PartitionSpec], passphrase: str = "") -> None:
    for spec in partitions:
        if spec.fs_type != FilesystemType.SWAP:
            create_filesystem(executor, spec, passphrase)


def unmount_all(executor: CommandExecutor, target_root: str = "/mnt") -> None:
    executor.run_sync(["umount", "-R", target_root])
    executor.run_sync(["swapoff", "-a"])
