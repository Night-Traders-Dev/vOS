from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events
from vapi import passwordtools_instance_sys
from vapi import fs_instance_sys
from vapi import animations_instance_sys
from vterminal import QShell
from vterminal import VirtualOS

logged_in = False
active_shell = QShell()
animation = animations_instance_sys()
animation.boot_animation_rich()

class VLogin(Widget):

    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="User name", id="username")
        yield Input(placeholder="Password", password= True, id="password")
        yield Button("Login!")

    def on_mount(self) -> None:
        self.title = "vOS Login"
        self.passwordtools = passwordtools_instance_sys()
        self.shell = active_shell
        self.shell.display = False

    @on(Input.Submitted)
    def login_input(self):
        self.login()

    @on(Button.Pressed)
    def login(self) -> None:
        self.fs = fs_instance_sys()
        self.passwordtools.check_passwd_file(self.fs)
        self.username = self.query_one("#username", Input).value
        self.password = self.query_one("#password", Input).value
        if self.username == "":
            self.notify("Username missing!", severity="warning")
        elif self.password == "":
            self.notify("Password missing!", severity="warning")
        else:
            self.auth()

    def auth(self):
        login = self.passwordtools.authenticate(self.username, self.password)
        if login:
            self.notify("Login Successful!")
            virtualos_init = VirtualOS(self.username)
            self.display = False
            self.shell.display = True
            logged_in = True
            return True
        else:
            self.mount(Label("Account not found!"))
            return False


class vOS(App):


    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        login_prompt = VLogin()
        yield Header()
        yield Footer()
        yield login_prompt
        yield active_shell

if __name__ == "__main__":
     vOS().run()

