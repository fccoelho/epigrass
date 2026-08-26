"""Run configuration screen: backend, credentials and run-time toggles."""
from __future__ import annotations

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (Button, Footer, Input, Label, Select, Static,
                             Switch)

from .. import epg_utils
from ..runner import BACKENDS, RunConfig


class RunConfigScreen(Screen):
    BINDINGS = [
        Binding("f9", "run", "Run"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, epg_path: str | Path) -> None:
        super().__init__()
        self.epg_path = Path(epg_path)

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("", id="model-summary")
            yield Label("Storage backend")
            yield Select(
                [(b, b) for b in BACKENDS], value="sqlite", id="backend",
                allow_blank=False,
            )
            with VerticalScroll(id="mysql-box"):
                yield Label("MySQL user")
                yield Input(placeholder="user", id="dbuser")
                yield Label("MySQL password")
                yield Input(placeholder="password", id="dbpass", password=True)
                yield Label("MySQL host")
                yield Input(value="localhost", id="dbhost")
            yield Horizontal(
                Static("Parallel multiprocessing "), Switch(value=False, id="parallel"),
                Static("Open dashboard after run "), Switch(value=False, id="dashboard"),
                Static("Gradio dashboard "), Switch(value=False, id="gradio"),
                id="toggles",
            )
            yield Static("", id="redis-status")
            yield Button("Run simulation  [F9]", id="run-btn", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        info = epg_utils.summarize(self.epg_path)
        errors = epg_utils.validate_epg(self.epg_path)
        status = ("[green]✓ valid[/green]" if not errors
                  else "\n".join(f"[red]✗ {e}[/red]" for e in errors))
        self.query_one("#model-summary", Static).update(
            f"[b]{self.epg_path}[/b]\n"
            f"Model type: {info.get('modtype', '?')}   Steps: {info.get('steps', '?')}\n"
            f"Validation: {status}"
        )
        self._toggle_mysql("sqlite")
        self.run_worker(self._ping_redis, thread=True, exclusive=True)

    def _ping_redis(self) -> None:
        status = "[green]✓ Redis server reachable[/green]"
        try:
            import redis

            redis.StrictRedis().ping()
        except Exception as exc:
            status = (f"[yellow]⚠ Redis not reachable ({exc.__class__.__name__}). "
                      "Simulations require a running Redis server.[/yellow]")
        self.app.call_from_thread(self._set_redis_status, status)

    def _set_redis_status(self, status: str) -> None:
        self.query_one("#redis-status", Static).update(status)

    @on(Select.Changed, "#backend")
    def _backend_changed(self, event: Select.Changed) -> None:
        self._toggle_mysql(str(event.value))

    def _toggle_mysql(self, backend: str) -> None:
        self.query_one("#mysql-box", VerticalScroll).display = backend == "mysql"

    @on(Button.Pressed, "#run-btn")
    def _run_pressed(self) -> None:
        self.action_run()

    def _collect_config(self) -> RunConfig:
        return RunConfig(
            backend=str(self.query_one("#backend", Select).value),
            dbuser=self.query_one("#dbuser", Input).value,
            dbpass=self.query_one("#dbpass", Input).value,
            dbhost=self.query_one("#dbhost", Input).value or "localhost",
            parallel=self.query_one("#parallel", Switch).value,
            dashboard=self.query_one("#dashboard", Switch).value,
            gradio=self.query_one("#gradio", Switch).value,
        )

    def action_run(self) -> None:
        config = self._collect_config()
        if config.backend == "mysql" and not (config.dbuser and config.dbpass):
            self.notify("MySQL backend needs a user and password", severity="error")
            return
        self.app.open_monitor(self.epg_path, config)

    def action_back(self) -> None:
        self.app.pop_screen()
