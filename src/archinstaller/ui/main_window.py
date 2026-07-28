from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig
from archinstaller.constants import StepID
from archinstaller.ui.wizard_stack import WizardStack
from archinstaller.ui.navigation_bar import NavigationBar
from archinstaller.ui.steps import (
    WelcomeStep,
    LocationStep,
    PartitioningStep,
    FilesystemsStep,
    UsersStep,
    DesktopStep,
    BootloaderStep,
    SummaryStep,
    InstallStep,
)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_title("Arch Linux Installer")
        self.set_default_size(900, 650)

        self._config = InstallerConfig()
        self._wizard = WizardStack(self._config)
        self._nav_bar = NavigationBar(self._wizard)

        self._register_steps()
        self._build_ui()
        self._connect_signals()

    def _register_steps(self) -> None:
        self._wizard.register_step(StepID.WELCOME, WelcomeStep())
        self._wizard.register_step(StepID.LOCATION, LocationStep())
        self._wizard.register_step(StepID.PARTITIONING, PartitioningStep())
        self._wizard.register_step(StepID.FILESYSTEMS, FilesystemsStep())
        self._wizard.register_step(StepID.USERS, UsersStep())
        self._wizard.register_step(StepID.DESKTOP, DesktopStep())
        self._wizard.register_step(StepID.BOOTLOADER, BootloaderStep())
        self._wizard.register_step(StepID.SUMMARY, SummaryStep())
        self._wizard.register_step(StepID.INSTALL, InstallStep())

    def _build_ui(self) -> None:
        self._header = Adw.HeaderBar()

        self._step_title = Gtk.Label()
        self._step_title.get_style_context().add_class("title")
        self._step_title.set_ellipsize(3)

        self._step_subtitle = Gtk.Label()
        self._step_subtitle.get_style_context().add_class("subtitle")
        self._step_subtitle.set_ellipsize(3)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title_box.append(self._step_title)
        title_box.append(self._step_subtitle)
        title_box.set_valign(Gtk.Align.CENTER)

        self._header.set_title_widget(title_box)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(self._header)
        content.append(self._wizard)
        content.append(self._nav_bar)

        self.set_content(content)

    def _connect_signals(self) -> None:
        self._wizard.connect("step-changed", self._on_step_changed)

    def _on_step_changed(self, wizard: WizardStack, from_id: int, to_id: int) -> None:
        page = wizard.current_page
        if page is not None:
            self._step_title.set_text(page.title)
            self._step_subtitle.set_text(page.subtitle)
            self._step_subtitle.set_visible(bool(page.subtitle))
