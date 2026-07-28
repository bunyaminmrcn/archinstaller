import json
import subprocess

from archinstaller.config import DiskInfo, PartitionInfo, PartitionSpec
from archinstaller.constants import PartitionRole, FilesystemType
from archinstaller.backend.exceptions import CommandFailedError


def scan_disks() -> list[DiskInfo]:
    try:
        result = subprocess.run(
            ["lsblk", "-o", "NAME,TYPE,SIZE,MODEL,PTTYPE,TRAN,RM,PHY-SEC,FSTYPE,LABEL,MOUNTPOINTS", "--json"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise CommandFailedError(["lsblk"], result.returncode, result.stderr)
        data = json.loads(result.stdout)
    except FileNotFoundError:
        return []

    disks: list[DiskInfo] = []
    for dev in data.get("blockdevices", []):
        if dev.get("type") != "disk":
            continue
        disk = DiskInfo(
            device=f"/dev/{dev['name']}",
            model=dev.get("model", ""),
            size_bytes=dev.get("size", 0),
            sector_size=dev.get("phy-sec", 512),
            transport=dev.get("tran", ""),
            partition_table=dev.get("pttype", ""),
            is_removable=dev.get("rm", False),
        )
        for child in dev.get("children", []):
            if child.get("type") == "part":
                flags = []
                if child.get("mountpoints"):
                    flags = [m for m in child["mountpoints"] if m]

                disk.partitions.append(PartitionInfo(
                    device=f"/dev/{child['name']}",
                    size_bytes=child.get("size", 0),
                    start_bytes=0,
                    end_bytes=0,
                    fs_type=child.get("fstype", ""),
                    label=child.get("label", ""),
                    flags=flags,
                ))
        disks.append(disk)

    return disks


def generate_default_partitions(disk: DiskInfo, is_uefi: bool = True) -> list[PartitionSpec]:
    size = disk.size_bytes
    min_root = 20 * 1024 * 1024 * 1024

    specs: list[PartitionSpec] = []

    if is_uefi:
        efi_size = 512 * 1024 * 1024
        specs.append(PartitionSpec(
            disk_device=disk.device,
            role=PartitionRole.ESP,
            size_bytes=efi_size,
            fs_type=FilesystemType.FAT32,
            mount_point="/boot/efi",
        ))
        remaining = size - efi_size
        if remaining <= min_root:
            specs.append(PartitionSpec(
                disk_device=disk.device,
                role=PartitionRole.ROOT,
                size_bytes=0,
                fs_type=FilesystemType.BTRFS,
                mount_point="/",
            ))
        else:
            specs.append(PartitionSpec(
                disk_device=disk.device,
                role=PartitionRole.ROOT,
                size_bytes=min_root,
                fs_type=FilesystemType.BTRFS,
                mount_point="/",
            ))
            home_remaining = remaining - min_root
            if home_remaining > 2 * 1024 * 1024 * 1024:
                specs.append(PartitionSpec(
                    disk_device=disk.device,
                    role=PartitionRole.HOME,
                    size_bytes=0,
                    fs_type=FilesystemType.BTRFS,
                    mount_point="/home",
                ))
    else:
        if size <= min_root:
            specs.append(PartitionSpec(
                disk_device=disk.device,
                role=PartitionRole.ROOT,
                size_bytes=0,
                fs_type=FilesystemType.BTRFS,
                mount_point="/",
            ))
        else:
            specs.append(PartitionSpec(
                disk_device=disk.device,
                role=PartitionRole.ROOT,
                size_bytes=min_root,
                fs_type=FilesystemType.BTRFS,
                mount_point="/",
            ))
            specs.append(PartitionSpec(
                disk_device=disk.device,
                role=PartitionRole.HOME,
                size_bytes=0,
                fs_type=FilesystemType.BTRFS,
                mount_point="/home",
            ))

    return specs
