#!/usr/bin/env python3
import sys
import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from archinstaller.application import ArchInstallerApp


def main() -> int:
    app = ArchInstallerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
