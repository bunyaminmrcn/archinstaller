import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from archinstaller.ui.main_window import MainWindow


class ArchInstallerApp(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id="io.archinstaller.ArchInstaller",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.connect("activate", self._on_activate)

    def _on_activate(self, app: Adw.Application) -> None:
        self._window = MainWindow(application=app)
        self._window.present()
