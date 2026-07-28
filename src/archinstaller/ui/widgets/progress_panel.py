from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject


class ProgressPanel(Gtk.Box):
    __gsignals__ = {
        "cancelled": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, show_cancel: bool = True, **kwargs) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_fraction(0.0)
        self._progress_bar.set_show_text(True)
        self._progress_bar.set_hexpand(True)

        self._status_label = Gtk.Label(label="Ready", halign=Gtk.Align.START)

        self.append(self._progress_bar)
        self.append(self._status_label)

        if show_cancel:
            self._cancel_btn = Gtk.Button(label="Cancel")
            self._cancel_btn.get_style_context().add_class("destructive-action")
            self._cancel_btn.set_halign(Gtk.Align.CENTER)
            self._cancel_btn.connect("clicked", self._on_cancel)
            self.append(self._cancel_btn)
        else:
            self._cancel_btn = None

    def set_progress(self, fraction: float, text: str = "") -> None:
        self._progress_bar.set_fraction(fraction)
        if text:
            self._progress_bar.set_text(text)

    def set_status(self, status: str) -> None:
        self._status_label.set_text(status)

    def set_finished(self) -> None:
        self._progress_bar.set_fraction(1.0)
        self._progress_bar.set_text("Complete")
        if self._cancel_btn:
            self._cancel_btn.set_visible(False)

    def _on_cancel(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        btn.set_label("Cancelling...")
        self.emit("cancelled")
