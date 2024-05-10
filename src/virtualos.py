from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vui.vterminal import QShell

logged_in = False
active_shell = QShell()
animation = animations_instance()
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
        self.passwordtools = passwordtools_instance()
        self.shell = active_shell
        self.shell.display = False

    @on(Input.Submitted)
    def login_input(self):
        self.login()

    @on(Button.Pressed)
    def login(self) -> None:
        self.fs = fs_instance()
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
            self.display = False
            self.title = "qShell"
            self.shell.display = True
            logged_in = True
        else:
            self.mount(Label("Account not found!"))


class vOS(App):


    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        login_prompt = VLogin()
        VHeader = Header()
        VHeader.show_clock = True
        yield VHeader
        yield Footer()
        yield login_prompt
        yield active_shell

if __name__ == "__main__":
     vOS().run()

