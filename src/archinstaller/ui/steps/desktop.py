from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID, AurHelper, DesktopEnvironment, EXTRA_PACKAGE_GROUPS
from archinstaller.ui.step_base import StepPage


_POPULAR_AUR_PACKAGES = [
    ("google-chrome", "Google Chrome"),
    ("visual-studio-code-bin", "Visual Studio Code"),
    ("discord", "Discord"),
    ("spotify", "Spotify"),
    ("slack-desktop", "Slack"),
    ("zoom", "Zoom"),
    ("brave-bin", "Brave Browser"),
    ("mongodb-compass", "MongoDB Compass"),
    ("postman-bin", "Postman"),
    ("onlyoffice-bin", "OnlyOffice"),
    ("dropbox", "Dropbox"),
    ("1password", "1Password"),
    ("skypeforlinux-stable-bin", "Skype"),
    ("obs-studio-git", "OBS Studio (git)"),
    ("timeshift", "Timeshift"),
]


class DesktopStep(StepPage):
    step_id = StepID.DESKTOP
    title = "Desktop Environment"
    subtitle = "Choose your desktop environment and extra packages"

    def build_ui(self) -> None:
        de_label = Gtk.Label(label="Desktop Environment", halign=Gtk.Align.START)
        de_label.get_style_context().add_class("heading")

        self._de_radio_group: list[tuple[DesktopEnvironment, Gtk.CheckButton]] = []
        de_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        de_box.set_margin_top(6)

        first = True
        for de in DesktopEnvironment:
            label = de.value.replace("_", " ").title()
            btn = Gtk.CheckButton.new_with_label(label)
            if first:
                btn.set_active(True)
                first = False
            for other in self._de_radio_group:
                btn.set_group(other[1])
            self._de_radio_group.append((de, btn))
            de_box.append(btn)

        extras_label = Gtk.Label(label="Extra Packages", halign=Gtk.Align.START)
        extras_label.get_style_context().add_class("heading")
        extras_label.set_margin_top(18)

        self._package_checkboxes: list[tuple[str, Gtk.CheckButton]] = []
        extras_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        extras_box.set_margin_top(6)
        for name in EXTRA_PACKAGE_GROUPS:
            cb = Gtk.CheckButton.new_with_label(name)
            self._package_checkboxes.append((name, cb))
            extras_box.append(cb)

        multilib_box = Gtk.Box(spacing=8)
        multilib_box.set_margin_top(18)
        self._multilib_check = Gtk.CheckButton.new_with_label("Enable multilib repository (32-bit support)")

        aur_label = Gtk.Label(label="AUR Support", halign=Gtk.Align.START)
        aur_label.get_style_context().add_class("heading")
        aur_label.set_margin_top(18)

        self._aur_check = Gtk.CheckButton.new_with_label("Enable AUR (Arch User Repository)")
        self._aur_check.connect("toggled", self._on_aur_toggled)

        helper_label = Gtk.Label(label="AUR Helper", halign=Gtk.Align.START)
        helper_label.set_margin_start(24)
        helper_label.set_margin_top(6)

        self._aur_helper_combo = Gtk.ComboBoxText()
        self._aur_helper_combo.append_text("paru (recommended)")
        self._aur_helper_combo.append_text("yay")
        self._aur_helper_combo.set_active(0)
        self._aur_helper_combo.set_sensitive(False)
        self._aur_helper_combo.set_margin_start(24)

        aur_pkgs_label = Gtk.Label(label="Popular AUR Packages", halign=Gtk.Align.START)
        aur_pkgs_label.set_margin_start(24)
        aur_pkgs_label.set_margin_top(12)

        self._aur_packages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._aur_packages_box.set_margin_start(24)
        self._aur_packages_box.set_margin_top(4)

        self._aur_checkboxes: list[tuple[str, Gtk.CheckButton]] = []
        for pkg_name, pkg_label in _POPULAR_AUR_PACKAGES:
            cb = Gtk.CheckButton.new_with_label(f"{pkg_label} ({pkg_name})")
            cb.set_sensitive(False)
            self._aur_checkboxes.append((pkg_name, cb))
            self._aur_packages_box.append(cb)

        self.content_box.append(de_label)
        self.content_box.append(de_box)
        self.content_box.append(extras_label)
        self.content_box.append(extras_box)
        self.content_box.append(self._multilib_check)
        self.content_box.append(aur_label)
        self.content_box.append(self._aur_check)
        self.content_box.append(helper_label)
        self.content_box.append(self._aur_helper_combo)
        self.content_box.append(aur_pkgs_label)
        self.content_box.append(self._aur_packages_box)

    def _on_aur_toggled(self, btn: Gtk.CheckButton) -> None:
        active = btn.get_active()
        self._aur_helper_combo.set_sensitive(active)
        for _, cb in self._aur_checkboxes:
            cb.set_sensitive(active)

    def on_enter(self, config: InstallerConfig) -> None:
        pass

    def on_leave(self, config: InstallerConfig) -> None:
        for de, btn in self._de_radio_group:
            if btn.get_active():
                config.desktop = de
                break

        config.extra_packages = []
        for name, cb in self._package_checkboxes:
            if cb.get_active():
                config.extra_packages.extend(EXTRA_PACKAGE_GROUPS[name])

        config.enable_multilib = self._multilib_check.get_active()
        config.enable_aur = self._aur_check.get_active()

        if config.enable_aur:
            config.aur_helper = AurHelper.PARU if self._aur_helper_combo.get_active() == 0 else AurHelper.YAY
            config.aur_packages = []
            for pkg_name, cb in self._aur_checkboxes:
                if cb.get_active():
                    config.aur_packages.append(pkg_name)
        else:
            config.aur_helper = AurHelper.PARU
            config.aur_packages = []
