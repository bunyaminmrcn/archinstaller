from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from archinstaller.config import InstallerConfig, PartitionSpec
from archinstaller.constants import StepID, PartitionRole, FilesystemType
from archinstaller.services.disk_scanner import scan_disks, generate_default_partitions
from archinstaller.ui.step_base import StepPage


class PartitioningStep(StepPage):
    step_id = StepID.PARTITIONING
    title = "Partitioning"
    subtitle = "Select target disk and partitioning method"

    def build_ui(self) -> None:
        disk_label = Gtk.Label(label="Target Disk", halign=Gtk.Align.START)
        disk_label.get_style_context().add_class("heading")

        self._disk_store = Gtk.ListStore(str, str, str)  # device, model, size
        self._disk_combo = Gtk.ComboBox.new_with_model(self._disk_store)
        renderer = Gtk.CellRendererText()
        self._disk_combo.pack_start(renderer, True)
        self._disk_combo.add_attribute(renderer, "text", 0)

        refresh_btn = Gtk.Button(label="Refresh Disks")
        refresh_btn.connect("clicked", self._on_refresh)
        refresh_btn.set_halign(Gtk.Align.START)
        refresh_btn.set_margin_top(4)

        self._uefi_switch = Gtk.Switch()
        self._uefi_switch.set_active(True)
        uefi_box = Gtk.Box(spacing=8)
        uefi_box.set_margin_top(18)
        uefi_box.append(Gtk.Label(label="UEFI System:", halign=Gtk.Align.START))
        uefi_box.append(self._uefi_switch)
        uefi_box.append(Gtk.Label(label="(disable for BIOS/legacy)"))

        scheme_label = Gtk.Label(label="Partition Scheme", halign=Gtk.Align.START)
        scheme_label.get_style_context().add_class("heading")
        scheme_label.set_margin_top(18)
        self._scheme_combo = Gtk.ComboBoxText()
        self._scheme_combo.append_text("GPT")
        self._scheme_combo.append_text("MBR (BIOS)")
        self._scheme_combo.set_active(0)

        method_label = Gtk.Label(label="Partitioning Method", halign=Gtk.Align.START)
        method_label.get_style_context().add_class("heading")
        method_label.set_margin_top(18)

        self._auto_radio = Gtk.CheckButton.new_with_label("Automatic (recommended)")
        self._manual_radio = Gtk.CheckButton.new_with_label("Manual")
        self._auto_radio.set_group(None)
        self._manual_radio.set_group(self._auto_radio)
        self._auto_radio.set_active(True)
        self._auto_radio.connect("toggled", self.notify_complete)

        self._wipe_check = Gtk.CheckButton.new_with_label("Wipe disk (erase all data)")
        self._wipe_check.set_active(True)

        warning_label = Gtk.Label(label="⚠ Wiping will permanently erase all data on the selected disk.")
        warning_label.get_style_context().add_class("warning")
        warning_label.set_margin_top(6)

        self.content_box.append(disk_label)
        self.content_box.append(self._disk_combo)
        self.content_box.append(refresh_btn)
        self.content_box.append(uefi_box)
        self.content_box.append(scheme_label)
        self.content_box.append(self._scheme_combo)
        self.content_box.append(method_label)
        self.content_box.append(self._auto_radio)
        self.content_box.append(self._manual_radio)
        self.content_box.append(self._wipe_check)
        self.content_box.append(warning_label)

        GLib.idle_add(self._on_refresh)

    def _on_refresh(self, btn=None) -> None:
        self._disk_store.clear()
        self._disks = scan_disks()
        for d in self._disks:
            size_human = self._fmt_size(d.size_bytes)
            self._disk_store.append([f"{d.device} — {d.model} ({size_human})", d.device, size_human])
        if len(self._disk_store) > 0:
            self._disk_combo.set_active(0)
        self.notify_complete()

    def _fmt_size(self, b: int) -> str:
        for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PiB"

    @property
    def is_complete(self) -> bool:
        selected = self._disk_combo.get_active()
        return selected >= 0

    def on_enter(self, config: InstallerConfig) -> None:
        pass

    def on_leave(self, config: InstallerConfig) -> None:
        active = self._disk_combo.get_active()
        if active >= 0 and self._disks:
            disk = self._disks[active]
            config.target_disk = disk.device
            config.is_uefi = self._uefi_switch.get_active()
            config.partition_scheme = "gpt" if self._scheme_combo.get_active() == 0 else "msdos"
            config.wipe_disk = self._wipe_check.get_active()

            if self._auto_radio.get_active():
                config.partitions = generate_default_partitions(disk, config.is_uefi)
