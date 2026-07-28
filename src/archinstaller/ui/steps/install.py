from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID
from archinstaller.backend.worker import InstallWorker
from archinstaller.ui.step_base import StepPage
from archinstaller.ui.widgets.carousel import ImageCarousel


class InstallStep(StepPage):
    step_id = StepID.INSTALL
    title = "Install"
    subtitle = "Installing Arch Linux..."

    def build_ui(self) -> None:
        self._worker = InstallWorker()

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_fraction(0.0)
        self._progress_bar.set_show_text(True)
        self._progress_bar.set_margin_bottom(12)

        self._status_label = Gtk.Label(label="Ready to install")
        self._status_label.set_margin_bottom(8)

        self._log_view = Gtk.TextView()
        self._log_view.set_editable(False)
        self._log_view.set_cursor_visible(False)
        self._log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._log_view.set_monospace(True)
        self._log_view.get_style_context().add_class("card")
        self._log_buffer = self._log_view.get_buffer()

        log_scrolled = Gtk.ScrolledWindow(vexpand=True)
        log_scrolled.set_child(self._log_view)
        log_scrolled.set_min_content_height(250)

        self._carousel = ImageCarousel(interval_ms=6000, width=680, height=400)
        carousel_scroll = Gtk.ScrolledWindow()
        carousel_scroll.set_child(self._carousel)
        carousel_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)

        self._paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self._paned.set_wide_handle(True)
        self._paned.set_position(380)
        self._paned.set_start_child(carousel_scroll)
        self._paned.set_end_child(log_scrolled)
        self._paned.set_vexpand(True)

        self._cancel_btn = Gtk.Button(label="Cancel Installation")
        self._cancel_btn.get_style_context().add_class("destructive-action")
        self._cancel_btn.set_halign(Gtk.Align.CENTER)
        self._cancel_btn.set_margin_top(12)
        self._cancel_btn.connect("clicked", self._on_cancel)

        self._done_btn = Gtk.Button(label="Reboot Now")
        self._done_btn.get_style_context().add_class("suggested-action")
        self._done_btn.set_halign(Gtk.Align.CENTER)
        self._done_btn.set_margin_top(12)
        self._done_btn.set_visible(False)
        self._done_btn.connect("clicked", self._on_reboot)

        self._error_label = Gtk.Label()
        self._error_label.get_style_context().add_class("error")
        self._error_label.set_visible(False)
        self._error_label.set_margin_top(8)

        self.content_box.append(self._progress_bar)
        self.content_box.append(self._status_label)
        self.content_box.append(self._paned)
        self.content_box.append(self._error_label)
        self.content_box.append(self._cancel_btn)
        self.content_box.append(self._done_btn)

        self._worker.connect("progress", self._on_progress)
        self._worker.connect("status", self._on_status)
        self._worker.connect("log_line", self._on_log_line)
        self._worker.connect("finished", self._on_finished)
        self._worker.connect("error", self._on_error)

    def on_enter(self, config: InstallerConfig) -> None:
        errors = config.validate()
        if errors:
            self._error_label.set_text("Cannot install:\n" + "\n".join(f"• {e}" for e in errors))
            self._error_label.set_visible(True)
            return

        self._error_label.set_visible(False)
        self._cancel_btn.set_visible(True)
        self._cancel_btn.set_sensitive(True)
        self._done_btn.set_visible(False)
        self._progress_bar.set_fraction(0.0)
        self._status_label.set_text("Starting installation...")
        self._log_buffer.set_text("")
        self._carousel.start()

        self._worker.start(config)

    def on_leave(self, config: InstallerConfig) -> None:
        self._carousel.stop()

    @property
    def is_complete(self) -> bool:
        return True

    def _on_progress(self, fraction: float) -> None:
        self._progress_bar.set_fraction(fraction)
        self._progress_bar.set_text(f"{int(fraction * 100)}%")

    def _on_status(self, status: str) -> None:
        self._status_label.set_text(status)

    def _on_log_line(self, line: str) -> None:
        end_iter = self._log_buffer.get_end_iter()
        self._log_buffer.insert(end_iter, line + "\n")
        adj = self._log_view.get_vadjustment()
        if adj:
            adj.set_value(adj.get_upper() - adj.get_page_size())

    def _on_finished(self, _data) -> None:
        self._carousel.stop()
        self._status_label.set_text("Installation complete!")
        self._progress_bar.set_fraction(1.0)
        self._progress_bar.set_text("100%")
        self._cancel_btn.set_visible(False)
        self._done_btn.set_visible(True)
        GLib.idle_add(self._log_buffer.insert, self._log_buffer.get_end_iter(),
                      "\n── Installation finished successfully ──\n")

    def _on_error(self, error_msg: str) -> None:
        self._carousel.stop()
        self._status_label.set_text("Installation failed")
        self._error_label.set_text(f"Error: {error_msg}")
        self._error_label.set_visible(True)
        self._cancel_btn.set_visible(True)
        self._cancel_btn.set_label("Close")

    def _on_cancel(self, btn: Gtk.Button) -> None:
        self._worker.cancel()
        self._cancel_btn.set_sensitive(False)
        self._cancel_btn.set_label("Cancelling...")

    def _on_reboot(self, btn: Gtk.Button) -> None:
        import subprocess
        subprocess.run(["reboot"])
