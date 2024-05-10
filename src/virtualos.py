from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vapi.vapi_ui import QShell_widget
from vapi.vapi_ui import VLogin_widget
from vapi.vapi_ui import FSTree_widget
from vapi.widget_bridge import set_data

fstree_widget = FSTree_widget()
login_widget = VLogin_widget()
active_shell = QShell_widget()

set_data("shell", active_shell)
set_data("fstree", fstree_widget)
set_data("login", login_widget)

class vOS(App):


    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield login_widget
#        yield fstree_widget
        yield active_shell

if __name__ == "__main__":
     vOS().run()
