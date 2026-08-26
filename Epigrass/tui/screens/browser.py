"""Model browser screen: discover and open .epg models."""
from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from .. import epg_utils


class ModelBrowserScreen(Screen):
    BINDINGS = [
        Binding("enter", "inspect", "Inspect"),
        Binding("r", "results", "Results"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]

    def __init__(self, base_dir: str | Path = ".") -> None:
        super().__init__()
        self.base_dir = Path(base_dir)
        self.models: list[Path] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="browser-hint")
        yield DataTable(id="model-table", cursor_type="row", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#model-table", DataTable)
        table.add_columns("Model", "Type", "Steps", "Sites file", "Edges file", "Modified")
        self.query_one("#browser-hint", Static).update(
            f"Models found under [b]{self.base_dir.resolve()}[/b]  "
            "([b]enter[/b] inspect · [b]r[/b] results · [b]ctrl+r[/b] refresh)"
        )
        self.run_worker(self._load_models, thread=True, exclusive=True)

    def _load_models(self) -> None:
        self.models = epg_utils.find_models(self.base_dir)
        rows = []
        for path in self.models:
            info = epg_utils.summarize(path)
            rows.append((
                str(info.get("path", path)),
                str(info.get("modtype", "?")),
                str(info.get("steps", "?")),
                str(info.get("sites", "?")),
                str(info.get("edges", "?")),
            ))
        self.app.call_from_thread(self._populate, rows)

    def _populate(self, rows: list[tuple]) -> None:
        table = self.query_one("#model-table", DataTable)
        table.clear()
        for row in rows:
            table.add_row(*row)
        if not rows:
            table.add_row("No .epg files found", "", "", "", "", "")

    def action_refresh(self) -> None:
        self.run_worker(self._load_models, thread=True, exclusive=True)

    def _selected_model(self) -> Path | None:
        table = self.query_one("#model-table", DataTable)
        if not self.models:
            return None
        try:
            row = table.cursor_row
            return self.models[row]
        except IndexError:
            return None

    @on(DataTable.RowSelected)
    def _row_selected(self, event: DataTable.RowSelected) -> None:
        # Enter on a focused DataTable fires RowSelected, shadowing the
        # screen-level binding.
        self.action_inspect()

    def action_inspect(self) -> None:
        model = self._selected_model()
        if model:
            self.app.open_inspector(model)

    def action_results(self) -> None:
        model = self._selected_model()
        if model:
            self.app.open_results(model.parent)
