from textual.app import App, ComposeResult
from textual.color import Color
from textual.widgets import Static, Digits, Button
from textual.widget import Widget
from textual.geometry import Region
from textual.screen import Screen
from textual import on, events, work
from datetime import datetime

class DesktopBase(Screen):

    def compose(self) -> ComposeResult:
        self.dash = Widget(id="dash")
        yield self.dash
        yield Static(id="topbar")
        yield Static("", id="clock")

    # Clock Method
    @on(events.Mount)
    def clock_timer(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one("#clock", Static).update(f"{clock:%T}")
    # End Clock


    # MouseMove Alternative
    def is_mouse_over_widget(self, widget_x, widget_y, widget_width, widget_height, mouse_x, mouse_y, screen_width, screen_height):
        return widget_x <= mouse_x <= widget_x + widget_width and widget_y <= mouse_y <= widget_y + widget_height

    # Dash Reveal Trigger
    @on(events.MouseEvent)
    def dash_trigger(self, event: events.MouseEvent) -> None:
        dash_loc = self.dash.region
        term_height = 24
        term_width = 80
        if self.is_mouse_over_widget(dash_loc.x, dash_loc.y, dash_loc.width, dash_loc.height, event.x, event.y, term_width, term_height):
            if self.dash.opacity == 0.0:
                self.dash.styles.animate("opacity", value=100.0, duration=1.5)
            else:
                pass
        else:
            self.dash.styles.animate("opacity", value=0.0, duration=0.5)
    # End Dash Reveal


class Desktop(App):
    CSS_PATH = "ui.tcss"
    SCREENS = {"DesktopBase": DesktopBase()}

    @work
    async def on_mount(self) -> None:
        await self.push_screen_wait("DesktopBase")

if __name__ == "__main__":
    app = Desktop()
    app.run()
