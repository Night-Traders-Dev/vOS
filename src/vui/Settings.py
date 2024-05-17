from textual.app import ComposeResult
from textual.color import Color
from textual.widgets import Static, Label, ListItem, ListView, Rule
from textual.containers import Grid
from textual.geometry import Region
from textual.screen import Screen, ModalScreen
from textual import on, events, work
from datetime import datetime

class SettingsScreen(Screen):

    CSS_PATH = "Desktop.tcss"

    def compose(self) -> ComposeResult:
        yield Static(id="topbarsettings")
        yield Static("", id="clocksettings")
        yield ListView(
            ListItem(Label("User Account", classes="sidebutton")),
            ListItem(Label("Display Settings", classes="sidebutton")),
            ListItem(Label("QSE Config", classes="sidebutton")),id="sidebar"
        )
