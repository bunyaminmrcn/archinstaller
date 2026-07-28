from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID, BootloaderType
from archinstaller.ui.step_base import StepPage


class BootloaderStep(StepPage):
    step_id = StepID.BOOTLOADER
    title = "Bootloader"
    subtitle = "Configure the bootloader and kernel"

    def build_ui(self) -> None:
        bl_label = Gtk.Label(label="Bootloader", halign=Gtk.Align.START)
        bl_label.get_style_context().add_class("heading")

        self._grub_uefi = Gtk.CheckButton.new_with_label("GRUB (UEFI)")
        self._grub_bios = Gtk.CheckButton.new_with_label("GRUB (BIOS/Legacy)")
        self._systemd_boot = Gtk.CheckButton.new_with_label("systemd-boot")
        self._grub_uefi.set_group(None)
        self._grub_bios.set_group(self._grub_uefi)
        self._systemd_boot.set_group(self._grub_uefi)
        self._grub_uefi.set_active(True)

        bl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bl_box.set_margin_top(6)
        bl_box.append(self._grub_uefi)
        bl_box.append(self._grub_bios)
        bl_box.append(self._systemd_boot)

        kernel_label = Gtk.Label(label="Kernel", halign=Gtk.Align.START)
        kernel_label.get_style_context().add_class("heading")
        kernel_label.set_margin_top(18)

        self._kernel_combo = Gtk.ComboBoxText()
        for k in ("linux", "linux-lts", "linux-zen", "linux-hardened"):
            self._kernel_combo.append_text(k)
        self._kernel_combo.set_active(0)

        efi_label = Gtk.Label(label="EFI Mount Point", halign=Gtk.Align.START)
        efi_label.get_style_context().add_class("heading")
        efi_label.set_margin_top(18)

        self._efi_entry = Gtk.Entry()
        self._efi_entry.set_text("/boot/efi")

        self.content_box.append(bl_label)
        self.content_box.append(bl_box)
        self.content_box.append(kernel_label)
        self.content_box.append(self._kernel_combo)
        self.content_box.append(efi_label)
        self.content_box.append(self._efi_entry)

    def on_enter(self, config: InstallerConfig) -> None:
        if config.bootloader == BootloaderType.GRUB_UEFI:
            self._grub_uefi.set_active(True)
        elif config.bootloader == BootloaderType.GRUB_BIOS:
            self._grub_bios.set_active(True)
        elif config.bootloader == BootloaderType.SYSTEMD_BOOT:
            self._systemd_boot.set_active(True)
        self._kernel_combo.set_active_text(config.kernel)
        self._efi_entry.set_text(config.efi_mount_point)

    def on_leave(self, config: InstallerConfig) -> None:
        if self._grub_bios.get_active():
            config.bootloader = BootloaderType.GRUB_BIOS
        elif self._systemd_boot.get_active():
            config.bootloader = BootloaderType.SYSTEMD_BOOT
        else:
            config.bootloader = BootloaderType.GRUB_UEFI
        config.kernel = self._kernel_combo.get_active_text() or "linux"
        config.efi_mount_point = self._efi_entry.get_text().strip() or "/boot/efi"
