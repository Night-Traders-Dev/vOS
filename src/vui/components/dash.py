import time
import asyncio
from textual import on, events
from textual.app import App, ComposeResult
from textual.reactive import reactive, var
from textual.widget import Widget

class VDash(Widget):
    def __init__(self):
        super().__init__()
        self.id = "vdash"
        self.dash = Widget(id="tdash")
        self.focus = True


    def compose(self) -> ComposeResult:
        yield self.dash


    @on(events.Click)
    def dash_trigger(self):
        if not self.dash.visible:
            self.dash.visible = True
        else:
            self.dash.visible = False
            asyncio.create_task(self.dash_timer())

    start: reactive[float] = reactive(time.time(), recompose=True)
    time: reactive[float] = reactive(time.time(), recompose=True)
    timer: reactive[float] = reactive(0.0, recompose=True)

    async def dash_timer(self):
        await self.set_interval(1, self.update_time)

    async def update_time(self) -> None:
        self.time = time.time()
        self.timer = self.time - self.start

    async def watch_time(self, timer: float) -> None:
        if self.timer >= 3.0:
            self.dash.visible = True
            self.time = 0.0
            self.start = 0.0
            self.current = 0.0

class DashWidget(Widget):
    def __init__(self):
        super().__init__()
        self.id = "background"

    def compose(self) -> ComposeResult:
        yield VDash()


class TestApp(App):
    def __init__(self):
        super().__init__()

    CSS_PATH = "dash.tcss"

    def compose(self) -> ComposeResult:
        yield DashWidget()


if __name__ == "__main__":
    app = TestApp()
    app.run()
