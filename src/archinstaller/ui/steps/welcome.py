from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID, AVAILABLE_LOCALES, AVAILABLE_KEYBOARDS
from archinstaller.ui.step_base import StepPage


class WelcomeStep(StepPage):
    step_id = StepID.WELCOME
    title = "Welcome"
    subtitle = "Choose your language and keyboard layout"

    def build_ui(self) -> None:
        lang_label = Gtk.Label(label="Language / Locale", halign=Gtk.Align.START)
        lang_label.get_style_context().add_class("heading")
        self._locale_combo = Gtk.ComboBoxText()
        for loc in AVAILABLE_LOCALES:
            self._locale_combo.append_text(loc)
        self._locale_combo.set_active(0)

        kb_label = Gtk.Label(label="Keyboard Layout", halign=Gtk.Align.START)
        kb_label.get_style_context().add_class("heading")
        kb_label.set_margin_top(18)
        self._keyboard_combo = Gtk.ComboBoxText()
        for kb in AVAILABLE_KEYBOARDS:
            self._keyboard_combo.append_text(kb)
        self._keyboard_combo.set_active(0)

        self.content_box.append(lang_label)
        self.content_box.append(self._locale_combo)
        self.content_box.append(kb_label)
        self.content_box.append(self._keyboard_combo)

    def on_enter(self, config: InstallerConfig) -> None:
        pass

    def on_leave(self, config: InstallerConfig) -> None:
        config.locale = self._locale_combo.get_active_text() or "en_US.UTF-8"
        config.keyboard_layout = self._keyboard_combo.get_active_text() or "us"
