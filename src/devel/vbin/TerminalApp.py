from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import TextArea

class TerminalWidget(TextArea):

    def on_mount(self):
        self.show_line_numbers = False
        self.insert("$ ")

    def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            curline, currow = self.get_cursor_line_start_location()
            command = self.get_line(curline)
            command = str(command).strip("$ ")
            self.insert("\n" + command + "\n$ ")
            event.prevent_default()


class TerminalApp(App):

    CSS_PATH = "TerminalUI.tcss"

    def compose(self) -> ComposeResult:
        yield TerminalWidget.code_editor(language="python")



app = TerminalApp()
if __name__ == "__main__":
    app.run()
