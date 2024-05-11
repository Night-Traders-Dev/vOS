from textual.app import App
from textual import events
from textual.widgets import Button, Label, Panel
from rich.panel import Panel as RichPanel


class Toolbar(Button):
    def __init__(self, items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = items
        self.style = "toolbar"
        self.action = self.toggle_start_menu

    async def toggle_start_menu(self, event):
        if not self.parent.start_menu_content.parent:
            await self.parent.root_container.insert(0, self.parent.start_menu)
        else:
            await self.parent.start_menu_content.detach()


class DesktopUI(App):
    CSS_PATH = "desktop_ui.tcss"

    async def on_load(self, event: events.Load) -> None:
        self.taskbar = Toolbar(
            items=["Start", "Program 1", "Program 2", "Program 3"],
            name="start_button",
        )

        self.start_menu_content = Panel(
            RichPanel("Program 1 Details"),
            RichPanel("Program 2 Details"),
            RichPanel("Program 3 Details"),
        )
        self.start_menu_content.style = "start_menu_content"

        self.start_menu = Panel(self.start_menu_content)
        self.start_menu.style = "start_menu"

        self.root_container = Panel(
            self.taskbar,
            self.start_menu,
            direction="vertical",
        )
        self.root_container.style = "root_container"

        self.layout = Panel(
            self.root_container,
        )

    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(self.layout)

    async def action_program_1(self, event: events.Click) -> None:
        print("Program 1 action triggered")

    async def action_program_2(self, event: events.Click) -> None:
        print("Program 2 action triggered")

    async def action_program_3(self, event: events.Click) -> None:
        print("Program 3 action triggered")


if __name__ == "__main__":
    app = DesktopUI()
    app.run()
