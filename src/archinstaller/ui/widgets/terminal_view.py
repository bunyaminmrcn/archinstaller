from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class TerminalView(Gtk.ScrolledWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(vexpand=True, **kwargs)
        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(False)
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text_view.set_monospace(True)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_string("""
            textview {
                font-family: monospace;
                font-size: 13px;
                background-color: @theme_bg_color;
                padding: 8px;
            }
        """)
        style_context = self._text_view.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.set_child(self._text_view)

    @property
    def buffer(self) -> Gtk.TextBuffer:
        return self._text_view.get_buffer()

    def append_line(self, text: str) -> None:
        buf = self._text_view.get_buffer()
        end_iter = buf.get_end_iter()
        buf.insert(end_iter, text + "\n")
        adj = self._text_view.get_vadjustment()
        if adj:
            adj.set_value(adj.get_upper() - adj.get_page_size())

    def clear(self) -> None:
        self._text_view.get_buffer().set_text("")
