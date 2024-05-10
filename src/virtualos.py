from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events, work
from textual.screen import Screen
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vapi.vapi_ui import QShell_widget
from vapi.vapi_ui import VLogin_widget
from vapi.vapi_ui import FSTree_widget
from vapi.widget_bridge import set_data
from time import sleep

fstree_widget = FSTree_widget()
active_shell = QShell_widget()
login_widget = VLogin_widget()

set_data("shell", active_shell)
set_data("fstree", fstree_widget)
set_data("login", login_widget)

class VOSInit(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

class vOS(App):

    SCREENS = {
         "vosinit": VOSInit,
         "qshell": QShell_widget,
         "voslogin": VLogin_widget,
        }

    BINDINGS = [
            Binding(key="ctrl+c", action="quit", description="Quit the app"),
        ]


    @work
    async def on_mount(self) -> None:
        while True:
            self.push_screen("vosinit")
            if await self.push_screen_wait("voslogin"):
                if await self.push_screen_wait("qshell") == "logout":
                    self.notify("Logged Out")
                else:
                    break  # Exit the loop if qshell is not logged out
            else:
                break  # Exit the loop if voslogin fails

if __name__ == "__main__":
     vOS().run()
