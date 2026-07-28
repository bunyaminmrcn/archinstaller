from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from archinstaller.config import InstallerConfig, PartitionSpec
from archinstaller.constants import StepID, FilesystemType, PartitionRole
from archinstaller.ui.step_base import StepPage


_ROLE_LABELS = {
    PartitionRole.ROOT: "/ (Root)",
    PartitionRole.HOME: "/home",
    PartitionRole.ESP: "/boot/efi (ESP)",
    PartitionRole.SWAP: "Swap",
    PartitionRole.BOOT: "/boot",
}

_FS_OPTIONS: list[tuple[str, FilesystemType]] = [
    ("ext4", FilesystemType.EXT4),
    ("btrfs", FilesystemType.BTRFS),
    ("xfs", FilesystemType.XFS),
    ("f2fs", FilesystemType.F2FS),
]


class FilesystemsStep(StepPage):
    step_id = StepID.FILESYSTEMS
    title = "Filesystems"
    subtitle = "Configure partition filesystems and mount points"

    def build_ui(self) -> None:
        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._list_box.get_style_context().add_class("rich-list")

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_child(self._list_box)
        scrolled.set_min_content_height(300)

        self._encrypt_switch = Gtk.Switch()
        self._encrypt_switch.set_valign(Gtk.Align.CENTER)
        encrypt_box = Gtk.Box(spacing=8)
        encrypt_box.set_margin_top(12)
        encrypt_box.append(Gtk.Label(label="Encrypt root partition (LUKS)", halign=Gtk.Align.START))
        encrypt_box.append(self._encrypt_switch)
        self._encrypt_switch.connect("notify::active", self._on_encrypt_toggled)

        self._passphrase_entry = Gtk.PasswordEntry()
        self._passphrase_entry.set_show_peek_icon(True)
        self._passphrase_entry.set_placeholder_text("LUKS passphrase")
        self._passphrase_entry.set_visible(False)
        pass_box = Gtk.Box(spacing=8)
        pass_box.set_margin_top(6)
        pass_box.append(Gtk.Label(label="Passphrase:", halign=Gtk.Align.START))
        pass_box.append(self._passphrase_entry)

        self.content_box.append(scrolled)
        self.content_box.append(encrypt_box)
        self.content_box.append(pass_box)

    def _on_encrypt_toggled(self, switch, param) -> None:
        self._passphrase_entry.set_visible(switch.get_active())
        self.notify_complete()

    def on_enter(self, config: InstallerConfig) -> None:
        while True:
            row = self._list_box.get_first_child()
            if row is None:
                break
            self._list_box.remove(row)

        for i, spec in enumerate(config.partitions):
            self._list_box.append(self._build_partition_row(spec, i))

    def _build_partition_row(self, spec: PartitionSpec, index: int) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()

        role_label = _ROLE_LABELS.get(spec.role, spec.role.value)
        name = Gtk.Label(label=role_label, halign=Gtk.Align.START)
        name.get_style_context().add_class("heading")

        fs_combo = Gtk.ComboBoxText()
        for label, fst in _FS_OPTIONS:
            fs_combo.append_text(label)
        fs_active = next((i for i, (_, fst) in enumerate(_FS_OPTIONS) if fst == spec.fs_type), 0)
        fs_combo.set_active(fs_active)
        fs_combo.connect("changed", self._on_fs_changed, spec)

        size_label = Gtk.Label(
            label=self._fmt_size(spec.size_bytes) if spec.size_bytes else "Remaining space",
            halign=Gtk.Align.START,
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.append(name)
        box.append(fs_combo)
        box.append(size_label)

        row.set_child(box)
        return row

    def _on_fs_changed(self, combo: Gtk.ComboBoxText, spec: PartitionSpec) -> None:
        idx = combo.get_active()
        if 0 <= idx < len(_FS_OPTIONS):
            spec.fs_type = _FS_OPTIONS[idx][1]
        self.notify_complete()

    def _fmt_size(self, b: int) -> str:
        for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PiB"

    @property
    def is_complete(self) -> bool:
        if self._encrypt_switch.get_active():
            pwd = self._passphrase_entry.get_text()
            return len(pwd) >= 6
        return True

    def on_leave(self, config: InstallerConfig) -> None:
        if self._encrypt_switch.get_active():
            config.encryption_passphrase = self._passphrase_entry.get_text()
            for spec in config.partitions:
                if spec.role == PartitionRole.ROOT:
                    spec.encrypt = True
                    spec.luks_name = "luks-root"
