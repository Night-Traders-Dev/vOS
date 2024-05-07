from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label
from textual.validation import Function, Number, ValidationResult, Validator
from textual.reactive import reactive
from textual.widget import Widget
from textual import on, events
from vapi import initialize_system

class vOSLoginApp(App):
    fs_instance, kernel_instance, animations_instance, vproc_instance, passwordtools_instance = initialize_system()
    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Input(placeholder="User name", id="username")
        yield Input(placeholder="Password", password= True, id="password")
        yield Button("Login!")

    def on_mount(self) -> None:
        self.title = "vOS Login"
        self.passwordtools = self.passwordtools_instance

    @on(Input.Submitted)
    def login_input(self):
        self.login()

    @on(Button.Pressed)
    def login(self) -> None:
        self.username = self.query_one("#username", Input).value
        self.password = self.query_one("#password", Input).value
        if self.username == "":
            self.notify("Username missing!")
        elif self.password == "":
            self.notify("Password missing!")
        else:
            self.auth()
    def auth(self):
       login = self.passwordtools.authenticate(self.username, self.password)
       if login:
            self.mount(Label(f" Welcome {self.username}"))
       else:
            self.mount(Label("Account not found!"))

if __name__ == "__main__":
     vOSLoginApp().run()

