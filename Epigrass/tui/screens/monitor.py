"""Live simulation monitor: progress bar, log stream, cancel/dashboard."""
from __future__ import annotations

import time
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import (Footer, Label, ProgressBar, RichLog, Static)

from ..runner import SimulationRunner

#: files listed after a successful run
INTERESTING_OUTPUTS = ("epistats.csv", "sitestats.csv", "epipath.csv",
                       "adjmat.csv", "Epigrass.sqlite", "Data.gpkg",
                       "network.gexf", "spread.json", "spread.graphml")


class RunMonitorScreen(Screen):
    BINDINGS = [
        Binding("c", "cancel", "Cancel"),
        Binding("d", "dashboard", "Dashboard", show=False),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, epg_path: str | Path, config) -> None:
        super().__init__()
        self.epg_path = Path(epg_path)
        self.config = config
        self.runner = SimulationRunner(self.epg_path, self.config)
        self.running = False
        self.returncode: int | None = None
        self._start_time = 0.0
        self._progress_value = 0

    def compose(self) -> ComposeResult:
        yield Static("", id="monitor-title")
        with Vertical(id="monitor-body"):
            yield ProgressBar(id="sim-progress", show_eta=False, total=100)
            yield Label("", id="progress-label")
            yield RichLog(id="sim-log", highlight=False, markup=False, wrap=True,
                          max_lines=5000)
        yield Static("", id="monitor-status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#monitor-title", Static).update(
            f"Running [b]{self.epg_path.name}[/b] "
            f"(backend: {self.config.backend}"
            f"{', parallel' if self.config.parallel else ''})"
        )
        self.running = True
        self._start_time = time.time()
        self.set_interval(1.0, self._tick)
        self.run_worker(self._run_sim, exclusive=True)

    def _tick(self) -> None:
        if self.running:
            elapsed = int(time.time() - self._start_time)
            self.query_one("#monitor-status", Static).update(
                f"[b]Running[/b] · {elapsed // 60:02d}:{elapsed % 60:02d} "
                "· [b]c[/b] cancels"
            )

    async def _run_sim(self) -> None:
        log = self.query_one("#sim-log", RichLog)
        bar = self.query_one("#sim-progress", ProgressBar)
        label = self.query_one("#progress-label", Label)
        async for event in self.runner.run():
            kind = event[0]
            if kind == "start":
                log.write(f"$ {event[1]}")
            elif kind == "log":
                log.write(event[1])
            elif kind == "progress":
                _, desc, current, total = event
                bar.total = total
                bar.update(progress=current)
                self._progress_value = current
                label.update(f"{desc}: {current}/{total}")
            elif kind == "done":
                self.returncode = event[1]
        self._finish()

    def _finish(self) -> None:
        self.running = False
        elapsed = int(time.time() - self._start_time)
        status = self.query_one("#monitor-status", Static)
        if self.returncode == 0:
            outdir = self.epg_path.parent / f"outdata-{self.epg_path.stem}"
            files = [f.name for f in sorted(outdir.glob("*"))
                     if f.name in INTERESTING_OUTPUTS] if outdir.is_dir() else []
            listing = ("\nOutput files in [b]"
                       f"{outdir}[/b]:\n  " + "\n  ".join(files)) if files else ""
            status.update(
                f"[b green]Finished successfully[/b green] in "
                f"{elapsed // 60:02d}:{elapsed % 60:02d}"
                f"{listing}\n[b]d[/b] opens the dashboard · [b]esc[/b] returns"
            )
            self.screen.set_binding_display("d", True)
            self.notify("Simulation finished successfully", severity="information")
        else:
            status.update(
                f"[b red]Simulation failed[/b red] (exit code {self.returncode}) "
                f"after {elapsed // 60:02d}:{elapsed % 60:02d} — "
                "see the log above · [b]esc[/b] returns"
            )
            self.notify("Simulation failed", severity="error")

    def action_cancel(self) -> None:
        if not self.running:
            return
        self.runner.cancel()
        self.query_one("#sim-log", RichLog).write("— cancel requested —")

    def action_dashboard(self) -> None:
        if self.running or self.returncode != 0:
            return
        self.app.launch_dashboard(self.epg_path, self.config.gradio)

    def action_back(self) -> None:
        if self.running:
            self.notify("Simulation still running — press [b]c[/b] to cancel first",
                        severity="warning")
            return
        self.app.pop_screen()
