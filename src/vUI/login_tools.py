from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label
from textual.validation import Function, Number, ValidationResult, Validator
from textual.reactive import reactive
from textual.widget import Widget
from textual import on

class LoginScreen(App):
    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]


    def compose(self) -> ComposeResult:

        yield Header()
        yield Footer()
        yield Input(placeholder="Username: ", id="username")
        yield Input(placeholder="Password: ", password=True, id="password")
        yield Button("Login", variant="primary")

    def on_mount(self) -> None:
        self.title = "vOS Login Page"
        self.username = ""
        self.password = ""

    @on(Input.Submitted)
    def username_input(self):
        for input in self.query(Input):
            if self.username == "":
                self.username = input.value
            else:
                self.password = input.value
                input.value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.username == "admin" and self.password == "secret":
            print(f"Hello, {self.username}!")
            self.mount(Label(f" Welcome {self.username}"))
        else:
            print(f"Account not found!")
            self.mount(Label("Account not found!"))


if __name__ == "__main__":
    app = LoginScreen()
    app.run()
