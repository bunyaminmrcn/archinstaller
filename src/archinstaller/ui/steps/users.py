from __future__ import annotations
import crypt
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from archinstaller.config import InstallerConfig, UserAccount
from archinstaller.constants import StepID
from archinstaller.ui.step_base import StepPage


class UsersStep(StepPage):
    step_id = StepID.USERS
    title = "Users"
    subtitle = "Set root password and create user accounts"

    def build_ui(self) -> None:
        root_label = Gtk.Label(label="Root Password", halign=Gtk.Align.START)
        root_label.get_style_context().add_class("heading")

        self._root_password = Gtk.PasswordEntry()
        self._root_password.set_show_peek_icon(True)
        self._root_password.set_placeholder_text("Leave blank to disable root login")

        self._root_confirm = Gtk.PasswordEntry()
        self._root_confirm.set_show_peek_icon(True)
        self._root_confirm.set_placeholder_text("Confirm root password")

        self._root_pwd_warning = Gtk.Label()
        self._root_pwd_warning.get_style_context().add_class("warning")
        self._root_pwd_warning.set_visible(False)
        self._root_confirm.connect("changed", self._on_root_pwd_changed)

        user_label = Gtk.Label(label="User Account", halign=Gtk.Align.START)
        user_label.get_style_context().add_class("heading")
        user_label.set_margin_top(18)

        self._username = Gtk.Entry()
        self._username.set_placeholder_text("Username")

        self._full_name = Gtk.Entry()
        self._full_name.set_placeholder_text("Full name (optional)")

        self._user_password = Gtk.PasswordEntry()
        self._user_password.set_show_peek_icon(True)
        self._user_password.set_placeholder_text("Password")

        self._user_confirm = Gtk.PasswordEntry()
        self._user_confirm.set_show_peek_icon(True)
        self._user_confirm.set_placeholder_text("Confirm password")

        self._user_pwd_warning = Gtk.Label()
        self._user_pwd_warning.get_style_context().add_class("warning")
        self._user_pwd_warning.set_visible(False)
        self._user_confirm.connect("changed", self._on_user_pwd_changed)

        self._admin_check = Gtk.CheckButton.new_with_label("Administrator (sudo access)")
        self._admin_check.set_active(True)

        self.content_box.append(root_label)
        self.content_box.append(self._root_password)
        self.content_box.append(self._root_confirm)
        self.content_box.append(self._root_pwd_warning)
        self.content_box.append(user_label)
        self.content_box.append(self._username)
        self.content_box.append(self._full_name)
        self.content_box.append(self._user_password)
        self.content_box.append(self._user_confirm)
        self.content_box.append(self._user_pwd_warning)
        self.content_box.append(self._admin_check)

    def _on_root_pwd_changed(self, entry: Gtk.PasswordEntry) -> None:
        p1 = self._root_password.get_text()
        p2 = self._root_confirm.get_text()
        if p1 and p2 and p1 != p2:
            self._root_pwd_warning.set_text("Passwords do not match")
            self._root_pwd_warning.set_visible(True)
        elif p1 and len(p1) < 4:
            self._root_pwd_warning.set_text("Password too short (minimum 4 characters)")
            self._root_pwd_warning.set_visible(True)
        else:
            self._root_pwd_warning.set_visible(False)
        self.notify_complete()

    def _on_user_pwd_changed(self, entry: Gtk.PasswordEntry) -> None:
        p1 = self._user_password.get_text()
        p2 = self._user_confirm.get_text()
        if p1 and p2 and p1 != p2:
            self._user_pwd_warning.set_text("Passwords do not match")
            self._user_pwd_warning.set_visible(True)
        elif p1 and len(p1) < 4:
            self._user_pwd_warning.set_text("Password too short (minimum 4 characters)")
            self._user_pwd_warning.set_visible(True)
        else:
            self._user_pwd_warning.set_visible(False)
        self.notify_complete()

    @property
    def is_complete(self) -> bool:
        root_pwd = self._root_password.get_text()
        root_pwd2 = self._root_confirm.get_text()
        username = self._username.get_text().strip()
        user_pwd = self._user_password.get_text()
        user_pwd2 = self._user_confirm.get_text()
        has_root = bool(root_pwd and root_pwd == root_pwd2 and len(root_pwd) >= 4)
        has_user = bool(username and user_pwd and user_pwd == user_pwd2 and len(user_pwd) >= 4)
        if not has_root and not has_user:
            self._root_pwd_warning.set_text("Either root password or a user is required")
            self._root_pwd_warning.set_visible(True)
            return False
        self._root_pwd_warning.set_visible(False)
        return True

    def on_enter(self, config: InstallerConfig) -> None:
        pass

    def on_leave(self, config: InstallerConfig) -> None:
        root_pwd = self._root_password.get_text()
        root_pwd2 = self._root_confirm.get_text()
        if root_pwd and root_pwd == root_pwd2:
            config.root_password_hashed = crypt.crypt(root_pwd, crypt.mksalt(crypt.METHOD_SHA512))

        username = self._username.get_text().strip()
        user_pwd = self._user_password.get_text()
        user_pwd2 = self._user_confirm.get_text()
        if username and user_pwd and user_pwd == user_pwd2:
            config.users = [
                UserAccount(
                    username=username,
                    password_hashed=crypt.crypt(user_pwd, crypt.mksalt(crypt.METHOD_SHA512)),
                    full_name=self._full_name.get_text().strip(),
                    is_admin=self._admin_check.get_active(),
                    autologin=False,
                )
            ]
