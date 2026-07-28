from __future__ import annotations
from typing import TYPE_CHECKING
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject

if TYPE_CHECKING:
    from archinstaller.config import InstallerConfig
    from archinstaller.constants import StepID


class StepPage(Adw.Bin):
    step_id: StepID
    title: str = ""
    subtitle: str = ""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._wizard = None
        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._content.set_margin_start(24)
        self._content.set_margin_end(24)
        self._content.set_margin_top(12)
        self._content.set_margin_bottom(12)
        self.build_ui()
        self.set_child(self._content)

    @property
    def content_box(self) -> Gtk.Box:
        return self._content

    @property
    def wizard(self):
        from archinstaller.ui.wizard_stack import WizardStack
        if self._wizard is None:
            raise RuntimeError("StepPage not attached to WizardStack")
        return self._wizard

    def set_wizard(self, wizard) -> None:
        self._wizard = wizard

    def build_ui(self) -> None:
        raise NotImplementedError

    def on_enter(self, config: InstallerConfig) -> None:
        raise NotImplementedError

    def on_leave(self, config: InstallerConfig) -> None:
        raise NotImplementedError

    @property
    def is_complete(self) -> bool:
        return True

    def get_next_step(self, config: InstallerConfig):
        from archinstaller.constants import StepID
        ids = list(StepID)
        try:
            idx = ids.index(self.step_id)
            return ids[idx + 1]
        except IndexError:
            return None

    def notify_complete(self) -> None:
        if self._wizard is not None:
            self._wizard._emit_navigation_state()
