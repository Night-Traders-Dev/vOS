from textual import events
from textual.app import App
from textual.widget import Label, TextInput, PasswordInput, Button
from textual.widgets import Footer

class LoginApp(App):
    async def on_mount(self) -> None:
        self.username_input = TextInput(prompt="Username: ")
        self.password_input = PasswordInput(prompt="Password: ")
        self.login_button = Button("Login", self.login)

        self.add(self.username_input)
        self.add(self.password_input)
        self.add(self.login_button)

        self.username_input.focus()

    async def login(self, text: str) -> None:
        username = self.username_input.text
        password = self.password_input.text

        if self.authenticate(username, password):
            self.username_input.clear()
            self.password_input.clear()
            self.footer.text = "Login successful!"
        else:
            self.footer.text = "Invalid username or password. Please try again."

    async def on_idle(self, event: events.Idle) -> None:
        self.footer.text = ""

    async def on_cancel(self, event: events.Cancel) -> None:
        self.quit()

    async def on_enter(self, event: events.Enter) -> None:
        await self.login(event.text)

    async def on_resize(self, event: events.Resize) -> None:
        self.username_input.center(align="center")
        self.password_input.center(align="center")
        self.login_button.center(align="center")

    async def on_mount(self) -> None:
        self.footer = Footer()
        self.add(self.footer)

    async def on_load(self, event: events.Load) -> None:
        await self.on_resize(None)

