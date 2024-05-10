from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static

ERROR_TEXT = """
An error has occurred. 

Press CTRL+C to shutdown vOS. If you do this,
you will lose any unsaved information in all open applications.

Error: 0E : 016F : BFF9B3D4
"""


class KernelPanic(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static(ERROR_TEXT)
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


class KernelPanicApp(App):
    CSS_PATH = "kernel_panic.tcss"
    BINDINGS = [("b", "push_screen('KernelPanic')", "KernelPanic")]

    def on_mount(self) -> None:
        self.install_screen(KernelPanic(), name="KernelPanic")


