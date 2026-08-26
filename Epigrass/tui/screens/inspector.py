"""Model inspector: overview, validation and raw editing of a .epg file."""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (DataTable, Footer, Label, Static, TabbedContent,
                             TabPane, TextArea)

from .. import epg_utils


class ModelInspectorScreen(Screen):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("f9", "run", "Run"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, epg_path: str | Path) -> None:
        super().__init__()
        self.epg_path = Path(epg_path)

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="overview"):
            with TabPane("Overview", id="overview"):
                yield DataTable(id="overview-table", cursor_type="row",
                                zebra_stripes=True)
            with TabPane("Validation", id="validation"):
                yield Static(id="validation-result")
            with TabPane("Edit", id="edit"):
                yield Label("ctrl+s saves the file as shown.")
                yield TextArea("", id="raw-editor", show_line_numbers=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#overview-table", DataTable)
        table.add_columns("Section", "Key", "Value")
        self.query_one("#raw-editor", TextArea).load_text(
            self.epg_path.read_text(encoding="utf-8", errors="replace")
        )
        self._refresh()

    def _refresh(self) -> None:
        try:
            parsed = epg_utils.parse_epg(self.epg_path)
        except Exception as exc:
            self.query_one("#validation-result", Static).update(
                f"[b red]Could not parse:[/] {exc}"
            )
            return
        table = self.query_one("#overview-table", DataTable)
        table.clear()
        for row in epg_utils.overview_rows(parsed):
            table.add_row(*row)
        errors = epg_utils.validate_epg(self.epg_path, parsed)
        widget = self.query_one("#validation-result", Static)
        if errors:
            widget.update("\n".join(f"[red]✗ {e}[/red]" for e in errors))
        else:
            widget.update("[green]✓ Model script is valid.[/green]")

    def action_save(self) -> None:
        area = self.query_one("#raw-editor", TextArea)
        self.epg_path.write_text(area.text, encoding="utf-8")
        self._refresh()
        self.notify(f"Saved {self.epg_path.name}")

    def action_run(self) -> None:
        self.app.open_run_config(self.epg_path)

    def action_back(self) -> None:
        self.app.pop_screen()
