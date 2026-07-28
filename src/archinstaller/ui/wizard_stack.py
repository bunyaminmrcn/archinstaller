from __future__ import annotations
from typing import TYPE_CHECKING
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject

if TYPE_CHECKING:
    from archinstaller.config import InstallerConfig
    from archinstaller.constants import StepID
    from archinstaller.ui.step_base import StepPage


class WizardStack(Gtk.Box):
    __gsignals__ = {
        "step-changed": (
            GObject.SignalFlags.RUN_FIRST, None,
            (int, int),
        ),
        "navigation-state-changed": (
            GObject.SignalFlags.RUN_FIRST, None,
            (bool, bool),
        ),
    }

    def __init__(self, config: InstallerConfig, **kwargs) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self._config = config
        self._history: list[StepID] = []
        self._current: StepID | None = None
        self._steps: dict[StepID, StepPage] = {}

        self._stack = Gtk.Stack(
            transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT,
            transition_duration=300,
            vexpand=True,
        )
        self.append(self._stack)

    def register_step(self, step_id: StepID, page: StepPage) -> None:
        page.set_wizard(self)
        self._steps[step_id] = page
        self._stack.add_named(page, str(step_id.value))
        if self._current is None:
            self._current = step_id
            from archinstaller.constants import StepID as S
            first_step_id = min(self._steps.keys(), key=lambda k: k.value)
            self._current = first_step_id
            page.on_enter(self._config)
            self._stack.set_visible_child_name(str(first_step_id.value))

    @property
    def current_step(self):
        return self._current

    @property
    def current_page(self) -> StepPage | None:
        if self._current is None:
            return None
        return self._steps.get(self._current)

    @property
    def can_go_back(self) -> bool:
        return len(self._history) > 0

    @property
    def can_go_forward(self) -> bool:
        step = self.current_page
        return step is not None and step.is_complete

    def go_forward(self) -> None:
        current = self.current_page
        if current is None:
            return
        if not current.is_complete:
            return
        current.on_leave(self._config)
        next_id = current.get_next_step(self._config)
        if next_id is None or next_id not in self._steps:
            return
        old_id = self._current
        self._history.append(old_id)
        self._current = next_id
        self._steps[next_id].on_enter(self._config)
        self._stack.set_visible_child_name(str(next_id.value))
        self.emit("step-changed", int(old_id), int(next_id))
        self._emit_navigation_state()

    def go_back(self) -> None:
        if not self._history:
            return
        current = self.current_page
        old_id = self._current
        new_id = self._history.pop()
        self._current = new_id
        self._steps[new_id].on_enter(self._config)
        self._stack.set_visible_child_name(str(new_id.value))
        self.emit("step-changed", int(old_id), int(new_id))
        self._emit_navigation_state()

    def go_to_step(self, step_id: StepID) -> None:
        if step_id not in self._steps or self._current is None:
            return
        old_id = self._current
        if old_id != step_id:
            self._history.append(old_id)
        self._current = step_id
        self._steps[step_id].on_enter(self._config)
        self._stack.set_visible_child_name(str(step_id.value))
        self.emit("step-changed", int(old_id), int(step_id))
        self._emit_navigation_state()

    def _emit_navigation_state(self) -> None:
        self.emit("navigation-state-changed", self.can_go_back, self.can_go_forward)
