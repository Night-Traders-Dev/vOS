from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from textual.command import Hit, Hits, Provider
from textual import on, events
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vapi.widget_bridge import get_data

logged_in = False
animation = animations_instance()
animation.boot_animation_rich()

class VLoginCommands(Provider):
    async def shutdown_vos(self):
        self.dismiss(False)


    async def search(self, query: str) -> Hits:  
#        matcher = self.matcher(query)  
        icon: var[str] = var('🔎')

        command = "shutdown_vos()"
        score = matcher.match(command)  
        if score > 0:
            yield Hit(
                score,
                matcher.highlight(command),  
                text="Shutdown",
                help="quit vOS",
                command = command
            )


class VLogin(Screen[bool]):

    COMMANDS = Screen.COMMANDS | {VLoginCommands}

    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        self.title = "vOS Login"
        yield Input(placeholder="User name", id="username")
        yield Input(placeholder="Password", password= True, id="password")
        yield Horizontal(
            Button("Login", id="login"),
            Button("Shutdown", id="shutdown"),
            )

    def on_mount(self) -> None:
        self.title = "vOS Login"
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


