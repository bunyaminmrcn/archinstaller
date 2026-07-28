from __future__ import annotations
import crypt
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class PasswordEntry(Gtk.Box):
    def __init__(self, placeholder: str = "Password", show_strength: bool = False, **kwargs) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4, **kwargs)

        self._entry = Gtk.PasswordEntry()
        self._entry.set_show_peek_icon(True)
        self._entry.set_placeholder_text(placeholder)

        self.append(self._entry)

        if show_strength:
            self._level_bar = Gtk.LevelBar()
            self._level_bar.set_mode(Gtk.LevelBarMode.DISCRETE)
            self._level_bar.set_min_value(0)
            self._level_bar.set_max_value(5)
            self._level_bar.set_value(0)
            self.append(self._level_bar)
            self._entry.connect("changed", self._on_changed)
        else:
            self._level_bar = None

    def _on_changed(self, entry: Gtk.PasswordEntry) -> None:
        if self._level_bar is None:
            return
        pwd = entry.get_text()
        score = 0
        if len(pwd) >= 4:
            score += 1
        if len(pwd) >= 8:
            score += 1
        if len(pwd) >= 12:
            score += 1
        if any(c.isupper() for c in pwd):
            score += 1
        if any(c.isdigit() for c in pwd):
            score += 1
        if any(not c.isalnum() for c in pwd):
            score += 1
        self._level_bar.set_value(min(score, 5))

    def get_text(self) -> str:
        return self._entry.get_text()

    def set_text(self, text: str) -> None:
        self._entry.set_text(text)

    def get_hashed(self) -> str:
        pwd = self.get_text()
        if not pwd:
            return ""
        return crypt.crypt(pwd, crypt.mksalt(crypt.METHOD_SHA512))

    def connect_changed(self, handler) -> int:
        return self._entry.connect("changed", handler)
