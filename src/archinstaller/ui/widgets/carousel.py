from __future__ import annotations
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Gio, Gdk


_DE_SCREENSHOTS: list[tuple[str, str]] = [
    ("gnome", "GNOME Desktop"),
    ("plasma", "KDE Plasma"),
    ("xfce", "Xfce Desktop"),
    ("cinnamon", "Cinnamon Desktop"),
    ("mate", "MATE Desktop"),
    ("budgie", "Budgie Desktop"),
    ("sway", "Sway WM"),
    ("hyprland", "Hyprland"),
    ("i3", "i3 Window Manager"),
    ("deepin", "Deepin Desktop"),
]

_SVG_TEMPLATES: dict[str, str] = {
    "gnome": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#1a1a2e'/>
  <rect x='0' y='0' width='680' height='32' fill='#0d0d1a' rx='4'/>
  <circle cx='16' cy='16' r='5' fill='#ff5f56'/>
  <circle cx='32' cy='16' r='5' fill='#ffbd2e'/>
  <circle cx='48' cy='16' r='5' fill='#27c93f'/>
  <text x='340' y='22' font-family='sans-serif' font-size='10' fill='#888' text-anchor='middle'>Activities</text>
  <rect x='190' y='40' width='300' height='160' fill='#2d2d4a' rx='8'/>
  <rect x='200' y='50' width='130' height='60' fill='#4a6fa5' rx='6'/>
  <rect x='340' y='50' width='130' height='60' fill='#7b3fa3' rx='6'/>
  <rect x='200' y='120' width='270' height='70' fill='#3a5a8a' rx='6'/>
  <rect x='190' y='210' width='300' height='80' fill='#2d2d4a' rx='8'/>
  <circle cx='220' cy='250' r='16' fill='#5b8bd4'/>
  <rect x='244' y='238' width='200' height='10' fill='#4a6fa5' rx='4'/>
  <rect x='244' y='254' width='160' height='8' fill='#3a5a8a' rx='4'/>
  <rect x='190' y='300' width='145' height='85' fill='#2d2d4a' rx='8'/>
  <rect x='345' y='300' width='145' height='85' fill='#2d2d4a' rx='8'/>
  <rect x='200' y='310' width='120' height='55' fill='#4a6fa5' rx='4'/>
  <rect x='355' y='310' width='120' height='55' fill='#5b8bd4' rx='4'/>
  <rect x='0' y='392' width='680' height='8' fill='#1e1e36'/>
  <text x='340' y='378' font-family='sans-serif' font-size='9' fill='#555'>GNOME 45</text>
</svg>""",

    "plasma": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#1b1e2b'/>
  <rect x='0' y='360' width='680' height='40' fill='#2a2e3b'/>
  <rect x='10' y='366' width='40' height='28' fill='#3daee9' rx='6'/><circle cx='30' cy='380' r='7' fill='#fff'/>
  <rect x='58' y='366' width='400' height='28' fill='#232734' rx='6'/>
  <circle cx='462' cy='380' r='10' fill='#4a4d58'/>
  <rect x='480' y='366' width='28' height='28' fill='#4a4d58' rx='6'/>
  <rect x='516' y='366' width='28' height='28' fill='#4a4d58' rx='6'/>
  <rect x='620' y='366' width='28' height='28' fill='#3daee9' rx='6'/>
  <rect x='0' y='0' width='680' height='28' fill='#2a2e3b'/>
  <rect x='10' y='6' width='80' height='16' fill='#3daee9' rx='4'/>
  <rect x='100' y='6' width='60' height='16' fill='#404450' rx='4'/>
  <text x='340' y='17' font-family='sans-serif' font-size='8' fill='#666' text-anchor='middle'>KDE Plasma</text>
  <rect x='10' y='38' width='200' height='310' fill='#232734' rx='6'/>
  <rect x='18' y='48' width='184' height='30' fill='#3daee9' rx='4'/>
  <rect x='18' y='86' width='184' height='25' fill='#2e3444' rx='4'/>
  <rect x='18' y='118' width='184' height='25' fill='#2e3444' rx='4'/>
  <rect x='220' y='38' width='450' height='310' fill='#232734' rx='6'/>
  <rect x='230' y='48' width='200' height='100' fill='#2e3444' rx='4'/>
  <rect x='440' y='48' width='200' height='100' fill='#2e3444' rx='4'/>
  <rect x='230' y='158' width='410' height='180' fill='#2e3444' rx='4'/>
  <text x='340' y='392' font-family='sans-serif' font-size='8' fill='#555'>KDE Plasma 6</text>
</svg>""",

    "xfce": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#2c3e50'/>
  <rect x='0' y='0' width='680' height='28' fill='#34495e'/>
  <rect x='6' y='4' width='50' height='20' fill='#3498db' rx='3'/>
  <rect x='62' y='4' width='40' height='20' fill='#3d566e' rx='3'/>
  <rect x='620' y='4' width='24' height='20' fill='#3d566e' rx='3'/>
  <text x='340' y='17' font-family='sans-serif' font-size='8' fill='#aaa' text-anchor='middle'>Xfce Terminal</text>
  <rect x='0' y='332' width='680' height='68' fill='#34495e'/>
  <rect x='6' y='340' width='30' height='52' fill='#3498db' rx='3'/>
  <rect x='42' y='340' width='160' height='52' fill='#4a6785' rx='6'/>
  <rect x='208' y='340' width='160' height='52' fill='#4a6785' rx='6'/>
  <rect x='628' y='340' width='30' height='52' fill='#3d566e' rx='3'/>
  <circle cx='660' cy='370' r='12' fill='#3d566e'/>
  <rect x='6' y='36' width='668' height='290' fill='#1a252f' rx='4'/>
  <text x='340' y='180' font-family='monospace' font-size='13' fill='#2ecc71' text-anchor='middle'>$ sudo pacman -S xfce4</text>
  <text x='340' y='200' font-family='monospace' font-size='13' fill='#ecf0f1' text-anchor='middle'>resolving dependencies...</text>
  <text x='340' y='220' font-family='monospace' font-size='13' fill='#2ecc71' text-anchor='middle'>Proceed with installation? [Y/n]</text>
  <text x='8' y='58' font-family='monospace' font-size='10' fill='#5a5'>File  Edit  View  Terminal  Help</text>
</svg>""",

    "cinnamon": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#2b2b2b'/>
  <rect x='0' y='360' width='680' height='40' fill='#333'/>
  <rect x='10' y='366' width='36' height='28' fill='#4a9e4a' rx='4'/>
  <rect x='52' y='372' width='36' height='16' fill='#444' rx='3'/>
  <rect x='310' y='366' width='60' height='28' fill='#444' rx='6'/>
  <rect x='376' y='370' width='12' height='20' fill='#555' rx='2'/>
  <rect x='630' y='366' width='28' height='28' fill='#444' rx='4'/>
  <rect x='0' y='0' width='680' height='28' fill='#3c3c3c'/>
  <text x='340' y='18' font-family='sans-serif' font-size='9' fill='#aaa' text-anchor='middle'>Cinnamon</text>
  <rect x='10' y='36' width='660' height='316' fill='#3c3c3c' rx='4'/>
  <rect x='20' y='46' width='640' height='120' fill='#4a4a4a' rx='4'/>
  <rect x='30' y='56' width='180' height='100' fill='#5a5a5a' rx='3'/>
  <rect x='220' y='56' width='180' height='100' fill='#5a5a5a' rx='3'/>
  <rect x='410' y='56' width='240' height='100' fill='#5a5a5a' rx='3'/>
  <rect x='20' y='176' width='310' height='166' fill='#4a4a4a' rx='4'/>
  <rect x='340' y='176' width='320' height='166' fill='#4a4a4a' rx='4'/>
  <text x='340' y='394' font-family='sans-serif' font-size='8' fill='#666'>Menu  ⏻</text>
</svg>""",

    "mate": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#588b6a'/>
  <rect x='0' y='0' width='680' height='26' fill='#4a7a5a'/>
  <rect x='6' y='4' width='60' height='18' fill='#6aaa7a' rx='3'/><text x='36' y='16' font-family='sans-serif' font-size='8' fill='#fff' text-anchor='middle'>Applications</text>
  <rect x='72' y='4' width='50' height='18' fill='#6aaa7a' rx='3'/><text x='97' y='16' font-family='sans-serif' font-size='8' fill='#fff' text-anchor='middle'>Places</text>
  <rect x='620' y='4' width='40' height='18' fill='#5a8a6a' rx='3'/>
  <rect x='0' y='368' width='680' height='32' fill='#4a7a5a'/>
  <rect x='6' y='374' width='28' height='20' fill='#5a8a6a' rx='3'/>
  <rect x='40' y='374' width='200' height='20' fill='#5a8a6a' rx='3'/>
  <rect x='246' y='374' width='28' height='20' fill='#5a8a6a' rx='3'/>
  <rect x='340' y='374' width='28' height='20' fill='#5a8a6a' rx='3'/>
  <rect x='7' y='30' width='666' height='332' fill='#c8e6c9' rx='4'/>
  <rect x='14' y='38' width='260' height='140' fill='#fff' rx='3'/>
  <rect x='282' y='38' width='384' height='260' fill='#fff' rx='3'/>
  <rect x='14' y='186' width='260' height='168' fill='#fff' rx='3'/>
</svg>""",

    "budgie": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#1c2333'/>
  <rect x='0' y='0' width='64' height='400' fill='#151b28'/>
  <circle cx='32' cy='36' r='12' fill='#5294e2'/>
  <rect x='10' y='60' width='44' height='10' fill='#3b4b66' rx='3'/>
  <rect x='10' y='78' width='44' height='10' fill='#3b4b66' rx='3'/>
  <rect x='10' y='96' width='44' height='10' fill='#3b4b66' rx='3'/>
  <rect x='10' y='114' width='44' height='10' fill='#3b4b66' rx='3'/>
  <rect x='10' y='132' width='44' height='10' fill='#5294e2' rx='3'/>
  <rect x='0' y='360' width='680' height='40' fill='#151b28'/>
  <rect x='70' y='370' width='28' height='20' fill='#5294e2' rx='4'/>
  <rect x='104' y='370' width='400' height='20' fill='#252f42' rx='4'/>
  <rect x='580' y='370' width='30' height='20' fill='#252f42' rx='4'/>
  <rect x='616' y='370' width='30' height='20' fill='#252f42' rx='4'/>
  <rect x='72' y='8' width='600' height='346' fill='#252f42' rx='6'/>
  <rect x='82' y='18' width='160' height='160' fill='#344060' rx='4'/>
  <rect x='250' y='18' width='410' height='160' fill='#344060' rx='4'/>
  <rect x='82' y='188' width='578' height='156' fill='#344060' rx='4'/>
</svg>""",

    "sway": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#282828'/>
  <rect x='0' y='0' width='680' height='22' fill='#1d2021'/>
  <rect x='6' y='3' width='80' height='16' fill='#458588' rx='3'/>
  <rect x='92' y='3' width='80' height='16' fill='#689d6a' rx='3'/>
  <text x='340' y='15' font-family='monospace' font-size='8' fill='#ebdbb2' text-anchor='middle'>[1]  ~/projects  zsh</text>
  <rect x='0' y='22' width='340' height='378' fill='#282828'/>
  <rect x='340' y='22' width='340' height='378' fill='#1d2021'/>
  <text x='10' y='42' font-family='monospace' font-size='9' fill='#83a598'>~/projects</text>
  <text x='10' y='58' font-family='monospace' font-size='9' fill='#ebdbb2'>$ ls -la</text>
  <text x='10' y='74' font-family='monospace' font-size='8' fill='#a89984'>total 48</text>
  <text x='10' y='88' font-family='monospace' font-size='8' fill='#b8bb26'>drwxr-xr-x</text><text x='80' y='88' font-family='monospace' font-size='8' fill='#ebdbb2'> src</text>
  <text x='10' y='102' font-family='monospace' font-size='8' fill='#b8bb26'>drwxr-xr-x</text><text x='80' y='102' font-family='monospace' font-size='8' fill='#ebdbb2'> build</text>
  <text x='10' y='116' font-family='monospace' font-size='8' fill='#fabd2f'>-rw-r--r--</text><text x='80' y='116' font-family='monospace' font-size='8' fill='#ebdbb2'> Cargo.toml</text>
  <text x='10' y='132' font-family='monospace' font-size='9' fill='#ebdbb2'>$ </text>
  <text x='350' y='42' font-family='monospace' font-size='9' fill='#83a598'>~/.config</text>
  <text x='350' y='58' font-family='monospace' font-size='9' fill='#ebdbb2'>$ nvim sway/config</text>
  <text x='350' y='74' font-family='monospace' font-size='8' fill='#a89984'>1  set $mod Mod4</text>
  <text x='350' y='88' font-family='monospace' font-size='8' fill='#a89984'>2  bindsym $mod+Return exec foot</text>
  <text x='350' y='102' font-family='monospace' font-size='8' fill='#a89984'>3  bindsym $mod+d exec fuzzel</text>
</svg>""",

    "hyprland": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#0f1014'/>
  <rect x='0' y='0' width='680' height='26' fill='#16181e'/>
  <rect x='8' y='6' width='60' height='14' fill='#cba6f7' rx='3'/>
  <rect x='74' y='6' width='14' height='14' fill='#89b4fa' rx='3'/>
  <rect x='300' y='6' width='80' height='14' fill='#313244' rx='3'/>
  <text x='340' y='16' font-family='monospace' font-size='7' fill='#a6adc8' text-anchor='middle'>12:34</text>
  <rect x='616' y='6' width='28' height='14' fill='#313244' rx='3'/>
  <rect x='648' y='6' width='24' height='14' fill='#313244' rx='3'/>
  <rect x='10' y='34' width='330' height='356' fill='#181a22' rx='8'/>
  <rect x='14' y='42' width='48' height='14' fill='#cba6f7' rx='3'/><text x='38' y='53' font-family='monospace' font-size='7' fill='#11111b' text-anchor='middle'>nvim</text>
  <rect x='64' y='42' width='48' height='14' fill='#313244' rx='3'/><text x='88' y='53' font-family='monospace' font-size='7' fill='#cdd6f4' text-anchor='middle'>file.rs</text>
  <text x='14' y='72' font-family='monospace' font-size='8' fill='#a6adc8'> 1  fn main() {"{"}</text>
  <text x='14' y='86' font-family='monospace' font-size='8' fill='#cdd6f4'> 2      let world = "🌍";</text>
  <text x='14' y='100' font-family='monospace' font-size='8' fill='#cdd6f4'> 3      println!("Hello");</text>
  <text x='14' y='114' font-family='monospace' font-size='8' fill='#89b4fa'> 4  {"}"}</text>
  <text x='14' y='132' font-family='monospace' font-size='7' fill='#585b70'>~  NORMAL  main.rs  rust</text>
  <rect x='350' y='34' width='320' height='356' fill='#181a22' rx='8'/>
  <rect x='354' y='42' width='48' height='14' fill='#a6e3a1' rx='3'/><text x='378' y='53' font-family='monospace' font-size='7' fill='#11111b' text-anchor='middle'>kitty</text>
  <text x='354' y='72' font-family='monospace' font-size='8' fill='#a6e3a1'>$ cargo run</text>
  <text x='354' y='86' font-family='monospace' font-size='8' fill='#cdd6f4'>Compiling hello</text>
  <text x='354' y='100' font-family='monospace' font-size='8' fill='#cdd6f4'>Finished dev</text>
  <text x='354' y='114' font-family='monospace' font-size='8' fill='#a6e3a1'>Hello 🌍</text>
</svg>""",

    "i3": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#1c2023'/>
  <rect x='0' y='0' width='680' height='20' fill='#252a2d'/>
  <text x='340' y='13' font-family='monospace' font-size='7' fill='#7ec27e' text-anchor='middle'>[1:term] [2:www] [3:code] [4:music]   Sat 14:22</text>
  <rect x='0' y='20' width='680' height='380' fill='#1c2023'/>
  <rect x='0' y='20' width='340' height='380' stroke='#252a2d' stroke-width='2' fill='none'/>
  <rect x='0' y='240' width='340' height='160' stroke='#252a2d' stroke-width='2' fill='none'/>
  <text x='10' y='40' font-family='monospace' font-size='9' fill='#5bc0eb'>~/projects  master</text>
  <text x='10' y='56' font-family='monospace' font-size='9' fill='#f0c674'>$ nvim app.py</text>
  <text x='10' y='74' font-family='monospace' font-size='8' fill='#707880'> 1  import flask</text>
  <text x='10' y='88' font-family='monospace' font-size='8' fill='#b5bd68'> 2  app = flask.Flask()</text>
  <text x='10' y='102' font-family='monospace' font-size='8' fill='#b5bd68'> 3  </text>
  <text x='10' y='260' font-family='monospace' font-size='8' fill='#5bc0eb'>$ htop</text>
  <rect x='344' y='24' width='336' height='376' fill='#1c2023'/>
  <text x='354' y='44' font-family='monospace' font-size='9' fill='#de935f'>~/.config/i3</text>
  <text x='354' y='60' font-family='monospace' font-size='9' fill='#f0c674'>$ cat config</text>
  <text x='354' y='78' font-family='monospace' font-size='8' fill='#707880'>1  set $mod Mod4</text>
  <text x='354' y='94' font-family='monospace' font-size='8' fill='#707880'>2  bindsym $mod+Enter exec kitty</text>
  <text x='354' y='110' font-family='monospace' font-size='8' fill='#707880'>3  gaps inner 12</text>
</svg>""",

    "deepin": """<svg xmlns='http://www.w3.org/2000/svg' width='680' height='400' viewBox='0 0 680 400'>
  <rect width='680' height='400' fill='#f0f4f8'/>
  <rect x='0' y='352' width='680' height='48' fill='#ffffff'/>
  <rect x='0' y='352' width='680' height='1' fill='#e2e8f0'/>
  <circle cx='340' cy='376' r='20' fill='#3b82f6'/>
  <rect x='14' y='362' width='42' height='28' fill='#3b82f6' rx='8'/>
  <rect x='68' y='364' width='180' height='24' fill='#f0f4f8' rx='6'/>
  <rect x='634' y='364' width='28' height='24' fill='#e2e8f0' rx='6'/>
  <rect x='14' y='14' width='652' height='100' fill='#ffffff' rx='12'/>
  <circle cx='44' cy='64' r='24' fill='#e0e7ff'/>
  <text x='80' y='58' font-family='sans-serif' font-size='14' fill='#1e293b' font-weight='bold'>Welcome to Deepin</text>
  <text x='80' y='78' font-family='sans-serif' font-size='10' fill='#64748b'>Beautiful &amp; efficient</text>
  <rect x='14' y='126' width='200' height='110' fill='#ffffff' rx='10'/>
  <rect x='30' y='140' width='80' height='30' fill='#dbeafe' rx='6'/>
  <rect x='120' y='140' width='80' height='30' fill='#dbeafe' rx='6'/>
  <rect x='226' y='126' width='200' height='110' fill='#ffffff' rx='10'/>
  <rect x='438' y='126' width='228' height='218' fill='#ffffff' rx='10'/>
  <text x='190' y='388' font-family='sans-serif' font-size='9' fill='#94a3b8'>Deepin 23</text>
</svg>""",
}


class ImageCarousel(Gtk.Box):
    def __init__(self, interval_ms: int = 5000, width: int = 680, height: int = 400, **kwargs) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self._interval = interval_ms
        self._current = 0
        self._running = False
        self._pictures: list[tuple[str, Gtk.Picture]] = []
        self._label: Gtk.Label | None = None

        css_provider = Gtk.CssProvider()
        css_provider.load_from_string("""
            .carousel-frame {
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            }
            .carousel-label {
                font-size: 13px;
                font-weight: bold;
                color: @theme_fg_color;
                margin-top: 6px;
            }
        """)
        style_context = self.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._stack = Gtk.Stack(
            transition_type=Gtk.StackTransitionType.CROSSFADE,
            transition_duration=600,
        )
        self._stack.get_style_context().add_class("carousel-frame")
        self._stack.set_size_request(width, height)
        self.append(self._stack)

        self._label = Gtk.Label(halign=Gtk.Align.CENTER)
        self._label.get_style_context().add_class("carousel-label")
        self.append(self._label)

        self._dots_box = Gtk.Box(halign=Gtk.Align.CENTER, spacing=6)
        self._dots_box.set_margin_top(6)
        self.append(self._dots_box)

        self._populate()

    def _populate(self) -> None:
        for i, (de_key, de_name) in enumerate(_DE_SCREENSHOTS):
            svg_data = _SVG_TEMPLATES.get(de_key)
            if svg_data:
                pic = Gtk.Picture.new_for_paintable(
                    self._svg_to_paintable(svg_data)
                )
                pic.set_can_shrink(True)
                self._stack.add_named(pic, str(i))
                self._pictures.append((de_name, pic))

                dot = Gtk.DrawingArea()
                dot.set_size_request(8, 8)
                dot.set_draw_func(self._draw_dot, i == 0)
                self._dots_box.append(dot)

        if self._pictures:
            self._stack.set_visible_child_name("0")
            self._label.set_text(self._pictures[0][0])

    @staticmethod
    def _svg_to_paintable(svg: str) -> Gdk.Texture | None:
        try:
            stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(svg.encode()))
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream(stream, None)
            if pixbuf is None:
                return None
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            return texture
        except Exception:
            return None

    def _draw_dot(self, area: Gtk.DrawingArea, cr, _w: int, _h: int, active: bool) -> None:
        cr.set_source_rgba(0.3, 0.5, 0.9, 1.0) if active else cr.set_source_rgba(0.5, 0.5, 0.5, 0.4)
        cr.arc(4, 4, 4, 0, 2 * 3.14159)
        cr.fill()

    def start(self) -> None:
        if self._running or not self._pictures:
            return
        self._running = True
        GLib.timeout_add(self._interval, self._next)

    def stop(self) -> None:
        self._running = False

    def _next(self) -> bool:
        if not self._running:
            return False
        self._current = (self._current + 1) % len(self._pictures)
        name, _ = self._pictures[self._current]
        self._stack.set_visible_child_name(str(self._current))
        if self._label:
            self._label.set_text(name)
        self._update_dots()
        return True

    def _update_dots(self) -> None:
        dot = self._dots_box.get_first_child()
        i = 0
        while dot is not None:
            dot.set_draw_func(self._draw_dot, i == self._current)
            dot.queue_draw()
            dot = dot.get_next_sibling()
            i += 1
