from rich.table import Table

from textual.geometry import Size
from textual.app import App, ComposeResult
from textual.widgets import Static


class SysMon(Static):
    def on_mount(self) -> None:
        table = Table("Process", "PID", "Cache", "User", "Uptime", expand=True)
        table.show_cursor = True
        table.show_row_labels = True
        for n in range(1, 16):
            table.add_row(
                "Process",
                str(n),
                "Cache",
                "Root",
                "Uptime"
            )
        self.update(table)


    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Force content width size."""
        return 50

class SysMonApp(App):
    CSS_PATH = "sysmon.tcss"

    def compose(self) -> ComposeResult:
        yield SysMon()


if __name__ == "__main__":
    app = SysMonApp()
    app.run()
