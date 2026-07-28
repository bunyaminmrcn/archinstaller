from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject

from archinstaller.config import DiskInfo, PartitionInfo


class DiskListView(Gtk.Box):
    __gsignals__ = {
        "disk-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.set_spacing(8)

        label = Gtk.Label(label="Available Disks", halign=Gtk.Align.START)
        label.get_style_context().add_class("heading")

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_min_content_height(200)

        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list_box.get_style_context().add_class("rich-list")
        self._list_box.connect("row-selected", self._on_selected)
        scrolled.set_child(self._list_box)

        self.append(label)
        self.append(scrolled)

    def populate(self, disks: list[DiskInfo]) -> None:
        self._list_box.remove_all()
        for disk in disks:
            size_str = self._fmt_size(disk.size_bytes)
            row = Gtk.ListBoxRow()

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)

            device_label = Gtk.Label(label=disk.device, halign=Gtk.Align.START)
            device_label.get_style_context().add_class("heading")

            model_label = Gtk.Label(label=disk.model, halign=Gtk.Align.START)
            size_label = Gtk.Label(label=size_str, halign=Gtk.Align.END)
            size_label.set_hexpand(True)

            box.append(device_label)
            box.append(model_label)
            box.append(size_label)

            partitions_label = Gtk.Label(
                label=f"{len(disk.partitions)} partitions",
                halign=Gtk.Align.START,
            )
            partitions_label.set_margin_start(12)
            partitions_label.set_margin_bottom(8)
            partitions_label.set_sensitive(False)

            inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            inner.append(box)
            if disk.partitions:
                inner.append(partitions_label)

            row.set_child(inner)
            self._list_box.append(row)

    def _on_selected(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if row is not None:
            idx = row.get_index()
            self.emit("disk-selected", str(idx))

    @staticmethod
    def _fmt_size(b: int) -> str:
        for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b //= 1024
        return f"{b:.1f} PiB"

    @property
    def selected_index(self) -> int:
        row = self._list_box.get_selected_row()
        return row.get_index() if row else -1
