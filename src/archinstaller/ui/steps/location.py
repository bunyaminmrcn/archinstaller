from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID, MIRROR_COUNTRIES, TIMEZONE_REGIONS
from archinstaller.ui.step_base import StepPage


class LocationStep(StepPage):
    step_id = StepID.LOCATION
    title = "Location"
    subtitle = "Select your timezone and mirror country"

    def build_ui(self) -> None:
        tz_label = Gtk.Label(label="Timezone", halign=Gtk.Align.START)
        tz_label.get_style_context().add_class("heading")

        self._region_combo = Gtk.ComboBoxText()
        self._region_combo.connect("changed", self._on_region_changed)
        for region in TIMEZONE_REGIONS:
            self._region_combo.append_text(region)
        self._region_combo.set_active(0)

        self._timezone_combo = Gtk.ComboBoxText()

        mirror_label = Gtk.Label(label="Mirror Country", halign=Gtk.Align.START)
        mirror_label.get_style_context().add_class("heading")
        mirror_label.set_margin_top(18)

        self._mirror_combo = Gtk.ComboBoxText()
        for name in MIRROR_COUNTRIES:
            self._mirror_combo.append_text(name)
        idx = list(MIRROR_COUNTRIES.keys()).index("Worldwide") if "Worldwide" in MIRROR_COUNTRIES else 0
        self._mirror_combo.set_active(idx)

        self.content_box.append(tz_label)
        self.content_box.append(self._region_combo)
        self.content_box.append(self._timezone_combo)
        self.content_box.append(mirror_label)
        self.content_box.append(self._mirror_combo)

        self._on_region_changed(self._region_combo)

    def _on_region_changed(self, combo: Gtk.ComboBoxText) -> None:
        self._timezone_combo.remove_all()
        region = combo.get_active_text()
        if region and region in TIMEZONE_REGIONS:
            for tz in TIMEZONE_REGIONS[region]:
                self._timezone_combo.append_text(tz)
            self._timezone_combo.set_active(0)

    def on_enter(self, config: InstallerConfig) -> None:
        pass

    def on_leave(self, config: InstallerConfig) -> None:
        config.timezone = self._timezone_combo.get_active_text() or "UTC"
        config.mirror_country = self._mirror_combo.get_active_text() or ""
