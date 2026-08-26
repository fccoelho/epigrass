"""Results browser: inspect outdata-* directories from past runs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (DataTable, Footer, Header, ListView, ListItem,
                             Label, Static)

#: output files that can be previewed as tables
PREVIEWABLE = ("*.csv", "*.csv.gz", "*.tsv")


class ResultsBrowserScreen(Screen):
    BINDINGS = [
        Binding("enter", "open", "Open"),
        Binding("d", "dashboard", "Dashboard"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, base_dir: str | Path) -> None:
        super().__init__()
        self.base_dir = Path(base_dir)
        self.runs: list[Path] = []
        self.file_paths: list[Path] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="results-hint")
        with Horizontal(id="results-body"):
            yield ListView(id="run-list")
            with Vertical():
                yield Label("Files in selected run")
                yield DataTable(id="file-table", cursor_type="row",
                                zebra_stripes=True)
        yield DataTable(id="preview-table", cursor_type="cell")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#preview-table", DataTable).display = False
        table = self.query_one("#file-table", DataTable)
        table.add_columns("File", "Size")
        self.runs = sorted(
            (r for r in self.base_dir.glob("outdata-*") if r.is_dir()),
            reverse=True,
        )
        self.query_one("#results-hint", Static).update(
            f"Result directories in [b]{self.base_dir.resolve()}[/b] "
            "(newest first)"
        )
        if self.runs:
            self.query_one("#run-list", ListView).extend(
                [ListItem(Label(r.name)) for r in self.runs]
            )
        else:
            self.query_one("#run-list", ListView).append(
                ListItem(Label("No outdata-* directories found"))
            )

    @on(ListView.Selected, "#run-list")
    def _run_selected(self, event: ListView.Selected) -> None:
        self._preview_hide()
        index = event.list_view.index
        if index is None or index >= len(self.runs):
            return
        run_dir = self.runs[index]
        table = self.query_one("#file-table", DataTable)
        table.clear()
        self.file_paths = [
            f for f in sorted(run_dir.iterdir())
            if f.is_file() and any(f.match(p) for p in PREVIEWABLE)
        ]
        for f in self.file_paths:
            size = f.stat().st_size
            human = f"{size / 1e6:.1f} MB" if size >= 1e6 else f"{size / 1e3:.1f} kB"
            table.add_row(f.name, human)
        if not self.file_paths:
            table.add_row("(no previewable files)", "")

    @on(DataTable.RowSelected, "#file-table")
    def _file_selected(self, event: DataTable.RowSelected) -> None:
        # Enter on a focused DataTable fires RowSelected, shadowing the
        # screen-level binding.
        self.action_open()

    @on(DataTable.RowSelected, "#preview-table")
    def _preview_selected(self, event: DataTable.RowSelected) -> None:
        self._preview_hide()

    def action_open(self) -> None:
        preview = self.query_one("#preview-table", DataTable)
        if preview.display:
            self._preview_hide()
            return
        table = self.query_one("#file-table", DataTable)
        try:
            path = self.file_paths[table.cursor_row]
        except (AttributeError, IndexError):
            return
        if not path.is_file():
            return
        self.run_worker(lambda: self._load_preview(path), thread=True, exclusive=True)

    def _load_preview(self, path: Path) -> None:
        try:
            df = pd.read_csv(path, nrows=200)
            rows = [list(map(str, r)) for r in df.itertuples(index=False)]
            self.app.call_from_thread(self._show_preview, path, list(df.columns), rows)
        except Exception as exc:
            self.app.call_from_thread(self._show_preview, path,
                                      ["error"], [[f"Could not read {path.name}: {exc}"]])

    def _show_preview(self, path: Path, columns: list, rows: list) -> None:
        preview = self.query_one("#preview-table", DataTable)
        preview.clear(columns=True)
        preview.add_columns(*columns)
        for row in rows:
            preview.add_row(*row)
        preview.display = True
        self.notify(f"Previewing {path.name} (first {len(rows)} rows)")

    def _preview_hide(self) -> None:
        preview = self.query_one("#preview-table", DataTable)
        preview.display = False
        preview.clear(columns=True)

    def action_dashboard(self) -> None:
        if not self.runs:
            self.notify("No results to visualize", severity="warning")
            return
        epgs = sorted(self.base_dir.glob("*.epg"))
        if not epgs:
            self.notify("No .epg file in the model directory to launch the "
                        "dashboard with", severity="warning")
            return
        self.app.launch_dashboard(epgs[0], view_only=True)

    def action_back(self) -> None:
        preview = self.query_one("#preview-table", DataTable)
        if preview.display:
            self._preview_hide()
            return
        self.app.pop_screen()
