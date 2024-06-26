from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.color import Color
from textual import on, events
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vapi.widget_bridge import get_data

logged_in = False
animation = animations_instance()
animation.boot_animation_rich()



class VLogin(Screen[bool]):

    CSS_PATH = "vlogin.tcss"

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        self.title = "vOS Login"
        yield Input(placeholder="User name", id="username")
        yield Input(placeholder="Password", password= True, id="password")
        yield Horizontal(
            Button("Login", id="login"),
            Button("Shutdown", id="shutdown"),
            classes="login_buttons",
            )

    def on_mount(self) -> None:
        self.title = "vOS Login"
        self.screen.styles.background = Color(94, 39, 80)
        self.screen.styles.border = ("ascii", Color(233, 84, 32))
        self.passwordtools = passwordtools_instance()



    @on(Input.Submitted)
    def login_input(self):
        self.login()

    @on(Button.Pressed, "#login")
    def login(self) -> None:
        self.fs = fs_instance()
        self.passwordtools.check_passwd_file(self.fs)
        self.uservalue = self.query_one("#username", Input)
        self.passvalue = self.query_one("#password", Input)
        self.username = self.uservalue.value
        self.password = self.passvalue.value
        if self.username == "":
            self.notify("Username missing!", severity="warning")
        elif self.password == "":
            self.notify("Password missing!", severity="warning")
        else:
            self.auth()


    @on(Button.Pressed, "#shutdown")
    def shutdown(self) -> None:
        self.dismiss(False)


    def auth(self):
        login = self.passwordtools.authenticate(self.username, self.password)
        if login:
            self.notify("Login Successful!", title="vOS Notification")
            self.title = "qShell"
            logged_in = True
            self.uservalue.value = ""
            self.passvalue.value = ""
            self.dismiss(True)
        else:
            self.mount(Label("Account not found!"))
            self.passvalue.value = ""


