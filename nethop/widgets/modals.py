"""Modal screens for iface picker and nickname."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from ..network import IfaceCandidate


class NicknameModal(ModalScreen[str | None]):
    """Prompt for a host nickname. Empty clears."""

    CSS = """
    NicknameModal {
        align: center middle;
    }
    #nick-dialog {
        width: 60;
        height: auto;
        border: tall #1e2a36;
        background: #0d1218;
        padding: 1 2;
    }
    #nick-dialog Input {
        margin: 1 0;
    }
    #nick-buttons {
        height: auto;
        align: right middle;
    }
    #nick-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, ip: str, current: str = "") -> None:
        super().__init__()
        self.ip = ip
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="nick-dialog"):
            yield Label(f"Nickname for [b]{self.ip}[/b] (empty to clear)")
            yield Input(value=self.current, placeholder="e.g. staging-api", id="nick-input")
            with Horizontal(id="nick-buttons"):
                yield Button("Save", variant="primary", id="nick-save")
                yield Button("Cancel", id="nick-cancel")

    def on_mount(self) -> None:
        self.query_one("#nick-input", Input).focus()

    @on(Input.Submitted, "#nick-input")
    def _submit(self) -> None:
        self.dismiss(self.query_one("#nick-input", Input).value)

    @on(Button.Pressed, "#nick-save")
    def _save(self) -> None:
        self.dismiss(self.query_one("#nick-input", Input).value)

    @on(Button.Pressed, "#nick-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)


class InterfaceModal(ModalScreen[IfaceCandidate | None]):
    """Pick a LAN interface / CIDR for discovery."""

    CSS = """
    InterfaceModal {
        align: center middle;
    }
    #iface-dialog {
        width: 72;
        height: 18;
        border: tall #1e2a36;
        background: #0d1218;
        padding: 1 1;
    }
    #iface-list {
        height: 1fr;
        border: tall #15202b;
    }
    """

    def __init__(self, candidates: list[IfaceCandidate], current_cidr: str = "") -> None:
        super().__init__()
        self.candidates = candidates
        self.current_cidr = current_cidr

    def compose(self) -> ComposeResult:
        with Vertical(id="iface-dialog"):
            yield Static("Select LAN interface  ·  Enter confirm  ·  Esc cancel", classes="pane-title")
            yield ListView(id="iface-list")

    def on_mount(self) -> None:
        lv = self.query_one("#iface-list", ListView)
        focus_i = 0
        for i, c in enumerate(self.candidates):
            mark = "●" if c.cidr == self.current_cidr else " "
            tunnel = "  [dim](tunnel?)[/dim]" if c.prefix >= 31 else ""
            label = (
                f"{mark} [b]{c.name}[/b]  {c.ip}/{c.prefix}  →  {c.cidr}"
                f"  [dim]score {c.score}[/dim]{tunnel}"
            )
            lv.append(ListItem(Static(label), id=f"iface-{i}"))
            if c.cidr == self.current_cidr:
                focus_i = i
        if self.candidates:
            lv.index = focus_i
        lv.focus()

    @on(ListView.Selected, "#iface-list")
    def _selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is None or idx < 0 or idx >= len(self.candidates):
            self.dismiss(None)
            return
        self.dismiss(self.candidates[idx])

    def on_key(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.key == "escape":
            self.dismiss(None)
