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
        self.custom_model_path = epg_utils.custom_model_path(self.epg_path)
        try:
            parsed = epg_utils.parse_epg(self.epg_path)
        except Exception:
            parsed = {}
        self.is_custom = epg_utils.is_custom(parsed)
        self._custom_loaded = ""

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
            if self.is_custom:
                with TabPane("CustomModel.py", id="custom"):
                    yield Label("", id="custom-hint")
                    yield TextArea("", id="custom-editor",
                                   show_line_numbers=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#overview-table", DataTable)
        table.add_columns("Section", "Key", "Value")
        self.query_one("#raw-editor", TextArea).load_text(
            self.epg_path.read_text(encoding="utf-8", errors="replace")
        )
        if self.is_custom:
            exists = self.custom_model_path.is_file()
            self._custom_loaded = (
                self.custom_model_path.read_text(encoding="utf-8",
                                                 errors="replace")
                if exists else epg_utils.CUSTOM_MODEL_TEMPLATE
            )
            self.query_one("#custom-editor", TextArea).load_text(
                self._custom_loaded
            )
            self.query_one("#custom-hint", Label).update(
                f"[b]{self.custom_model_path}[/b] — "
                + ("ctrl+s saves the file as shown."
                   if exists else
                   "file does not exist yet: a template is preloaded — edit it "
                   "and press ctrl+s to create it.")
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
        saved = [self.epg_path.name]
        if self.is_custom:
            custom = self.query_one("#custom-editor", TextArea)
            if custom.text != self._custom_loaded:
                self.custom_model_path.write_text(custom.text, encoding="utf-8")
                self._custom_loaded = custom.text
                saved.append(self.custom_model_path.name)
        self._refresh()
        self.notify(f"Saved {', '.join(saved)}")

    def action_run(self) -> None:
        self.app.open_run_config(self.epg_path)

    def action_back(self) -> None:
        self.app.pop_screen()
