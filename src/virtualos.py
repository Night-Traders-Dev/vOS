from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events, work
from textual.screen import Screen
from textual.color import Color
from vapi.vapi import passwordtools_instance
from vapi.vapi import fs_instance
from vapi.vapi import animations_instance
from vapi.vapi_ui import QShell_widget
from vapi.vapi_ui import VLogin_widget
from vapi.vapi_ui import FSTree_widget
from vapi.widget_bridge import set_data
from time import sleep

class VOSInit(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

class vOS(App):

    def on_mount(self) -> None:
        self.screen.styles.background = Color(94, 39, 80)
        self.screen.styles.border = ("ascii", Color(233, 84, 32))



    SCREENS = {
         "vosinit": VOSInit,
         "qshell": QShell_widget,
         "voslogin": VLogin_widget,
         "fstree": FSTree_widget,
        }

#    BINDINGS = [
#            Binding(key="ctrl+c", action="quit", description="Quit the app"),
#        ]


    @work
    async def on_mount(self) -> None:
        while True:
            self.push_screen("vosinit")
            if await self.push_screen_wait("voslogin"):
                self.qshell_screen = await self.push_screen_wait("qshell")
                if self.qshell_screen == "logout":
                    self.notify("Logged Out")
                    self.push_screen("voslogin")
                elif self.qshell_screen == "fstree":
                    self.fstree_screen = await self.push_screen_wait("fstree")
                    if self.fstree_screen == False:
                        self.push_screen("qshell")
                    else:
                        break # Exit fstree loop
                else:
                    break  # Exit the loop if qshell is not logged out
            else:
                break  # Exit the loop if voslogin fails

if __name__ == "__main__":
     vOS().run()
