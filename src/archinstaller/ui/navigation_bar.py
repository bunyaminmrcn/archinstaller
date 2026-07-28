from __future__ import annotations
from typing import TYPE_CHECKING
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk

if TYPE_CHECKING:
    from archinstaller.ui.wizard_stack import WizardStack


class NavigationBar(Gtk.ActionBar):
    def __init__(self, wizard: WizardStack, **kwargs) -> None:
        super().__init__(**kwargs)
        self._wizard = wizard

        self.btn_back = Gtk.Button(label="← Back")
        self.btn_back.set_sensitive(False)
        self.btn_back.connect("clicked", self._on_back)

        self.btn_forward = Gtk.Button(label="Next →")
        self.btn_forward.get_style_context().add_class("suggested-action")
        self.btn_forward.set_sensitive(False)
        self.btn_forward.connect("clicked", self._on_forward)

        self.btn_cancel = Gtk.Button(label="Quit")
        self.btn_cancel.connect("clicked", self._on_cancel)

        self.pack_start(self.btn_cancel)
        self.pack_end(self.btn_forward)
        self.pack_end(self.btn_back)

        wizard.connect("navigation-state-changed", self._on_nav_state_changed)

        cancel_controller = Gtk.ShortcutController()
        cancel_controller.add_shortcut(
            Gtk.Shortcut.new(
                Gtk.KeyvalTrigger.new(65307, Gdk.ModifierType.NO_MODIFIER_MASK),  # Escape
                Gtk.CallbackAction.new(self._on_cancel_shortcut),
            )
        )
        self.add_controller(cancel_controller)

    def _on_nav_state_changed(self, wizard: WizardStack, can_back: bool, can_forward: bool) -> None:
        self.btn_back.set_sensitive(can_back)
        self.btn_forward.set_sensitive(can_forward)

    def _on_back(self, btn: Gtk.Button) -> None:
        self._wizard.go_back()

    def _on_forward(self, btn: Gtk.Button) -> None:
        self._wizard.go_forward()

    def _on_cancel(self, btn: Gtk.Button) -> None:
        app = Gtk.Application.get_default()
        if app:
            app.quit()

    def _on_cancel_shortcut(self, action, param) -> bool:
        self._on_cancel(self.btn_cancel)
        return True

    def show_cancel_only(self) -> None:
        self.btn_back.set_visible(False)
        self.btn_forward.set_visible(False)
        self.btn_cancel.set_visible(True)

    def show_all_buttons(self) -> None:
        self.btn_back.set_visible(True)
        self.btn_forward.set_visible(True)
        self.btn_cancel.set_visible(True)

    def hide_all(self) -> None:
        self.btn_back.set_visible(False)
        self.btn_forward.set_visible(False)
        self.btn_cancel.set_visible(False)
