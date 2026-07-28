from archinstaller.config import PartitionSpec
from archinstaller.backend.executor import CommandExecutor


def create_partition_table(executor: CommandExecutor, disk: str, scheme: str = "gpt") -> None:
    executor.run_sync(["sgdisk", "-Z", disk])
    if scheme == "gpt":
        executor.run_sync(["sgdisk", "-o", disk])
    else:
        executor.run_sync(["parted", "-s", disk, "mklabel", "msdos"])


def create_partition(executor: CommandExecutor, spec: PartitionSpec, number: int) -> str:
    disk = spec.disk_device
    partition_num = str(number)

    if spec.size_bytes == 0:
        executor.run_sync(["sgdisk", "-n", f"{partition_num}:0:0", disk])
    else:
        size_sectors = spec.size_bytes // 512
        executor.run_sync(["sgdisk", "-n", f"{partition_num}:0:+{size_sectors}", disk])

    from archinstaller.constants import PartitionRole

    if spec.role == PartitionRole.ESP:
        executor.run_sync(["sgdisk", "-t", f"{partition_num}:ef00", disk])
    elif spec.role == PartitionRole.BOOT:
        executor.run_sync(["sgdisk", "-t", f"{partition_num}:8300", disk])
    elif spec.role == PartitionRole.SWAP:
        executor.run_sync(["sgdisk", "-t", f"{partition_num}:8200", disk])
    elif spec.role == PartitionRole.ROOT:
        executor.run_sync(["sgdisk", "-t", f"{partition_num}:8304", disk])
    elif spec.role == PartitionRole.HOME:
        executor.run_sync(["sgdisk", "-t", f"{partition_num}:8302", disk])

    if spec.label:
        executor.run_sync(["sgdisk", "-c", f"{partition_num}:{spec.label}", disk])

    return f"{disk}{partition_num if disk[-1].isdigit() else partition_num}"


def wipe_disk(executor: CommandExecutor, disk: str) -> None:
    executor.run_sync(["sgdisk", "-Z", disk])
    executor.run_sync(["wipefs", "-a", disk])
