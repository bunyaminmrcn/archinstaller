from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID
from archinstaller.ui.step_base import StepPage


class SummaryStep(StepPage):
    step_id = StepID.SUMMARY
    title = "Summary"
    subtitle = "Review your installation settings before proceeding"

    def build_ui(self) -> None:
        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(False)
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self._text_view.set_monospace(True)
        self._text_view.get_style_context().add_class("card")

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_child(self._text_view)
        scrolled.set_min_content_height(350)

        self._warnings_label = Gtk.Label()
        self._warnings_label.get_style_context().add_class("warning")
        self._warnings_label.set_visible(False)
        self._warnings_label.set_margin_top(8)

        self.content_box.append(scrolled)
        self.content_box.append(self._warnings_label)

    def on_enter(self, config: InstallerConfig) -> None:
        buffer = self._text_view.get_buffer()
        buffer.set_text(self._build_summary(config))

        errors = config.validate()
        if errors:
            self._warnings_label.set_text("\n".join(f"• {e}" for e in errors))
            self._warnings_label.set_visible(True)
        else:
            self._warnings_label.set_visible(False)

    def on_leave(self, config: InstallerConfig) -> None:
        pass

    @property
    def is_complete(self) -> bool:
        return True

    def _build_summary(self, config: InstallerConfig) -> str:
        lines = []
        lines.append("═══ ARCH LINUX INSTALLATION SUMMARY ═══")
        lines.append("")

        lines.append("── Locale ──")
        lines.append(f"  Language:        {config.language}")
        lines.append(f"  Locale:          {config.locale}")
        lines.append(f"  Keyboard:        {config.keyboard_layout}")
        lines.append(f"  Timezone:        {config.timezone}")
        lines.append(f"  Mirrors:         {config.mirror_country or 'Worldwide'}")
        lines.append("")

        lines.append("── Disks ──")
        lines.append(f"  Target disk:     {config.target_disk}")
        lines.append(f"  Wipe disk:       {'Yes ⚠' if config.wipe_disk else 'No'}")
        lines.append(f"  Scheme:          {config.partition_scheme.upper()}")
        lines.append(f"  UEFI:            {'Yes' if config.is_uefi else 'No (BIOS/Legacy)'}")
        lines.append(f"  Encryption:      {'LUKS' if config.encryption_passphrase else 'None'}")
        lines.append("  Partitions:")
        for p in config.partitions:
            size_str = f"{p.size_bytes / (1024**3):.1f} GiB" if p.size_bytes else "Remaining"
            lines.append(f"    {p.mount_point or '(none)':12s} {str(p.role):8s} {str(p.fs_type):6s} {size_str}")
        lines.append("")

        lines.append("── Users ──")
        lines.append(f"  Root password:   {'Set' if config.root_password_hashed else 'Disabled'}")
        for u in config.users:
            lines.append(f"  User:            {u.username} {'(admin)' if u.is_admin else ''}")
        lines.append("")

        lines.append("── System ──")
        lines.append(f"  Hostname:        {config.network.hostname}")
        lines.append(f"  Desktop:         {config.desktop.value}")
        if config.extra_packages:
            lines.append(f"  Extra packages:  {len(config.extra_packages)} selected")
        lines.append(f"  Bootloader:      {config.bootloader.value}")
        lines.append(f"  Kernel:          {config.kernel}")
        lines.append(f"  Multilib:        {'Enabled' if config.enable_multilib else 'Disabled'}")
        lines.append("")
        lines.append("── AUR ──")
        if config.enable_aur:
            lines.append(f"  AUR Helper:      {config.aur_helper.value}")
            if config.aur_packages:
                lines.append(f"  AUR Packages:    {', '.join(config.aur_packages)}")
        else:
            lines.append(f"  AUR:             Disabled")
        lines.append("")

        lines.append("═══ Ready to install ═══")
        return "\n".join(lines)
