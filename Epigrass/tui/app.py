"""Epigrass TUI application."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from textual.app import App

from .screens.browser import ModelBrowserScreen
from .screens.inspector import ModelInspectorScreen
from .screens.monitor import RunMonitorScreen
from .screens.results import ResultsBrowserScreen
from .screens.run_config import RunConfigScreen


class EpigrassTui(App):
    TITLE = "epirunner"
    SUB_TITLE = "Epigrass simulation manager"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+p", "command_palette", "Command palette"),
    ]

    def on_mount(self) -> None:
        self.push_screen(ModelBrowserScreen(Path.cwd()))

    # -- navigation helpers -------------------------------------------------
    def open_inspector(self, epg_path: Path) -> None:
        self.push_screen(ModelInspectorScreen(epg_path))

    def open_run_config(self, epg_path: Path) -> None:
        self.push_screen(RunConfigScreen(epg_path))

    def open_monitor(self, epg_path: Path, config) -> None:
        self.push_screen(RunMonitorScreen(epg_path, config))

    def open_results(self, base_dir: Path) -> None:
        self.push_screen(ResultsBrowserScreen(base_dir))

    # -- actions -------------------------------------------------------------
    def launch_dashboard(self, epg_path: Path, gradio: bool = True,
                         view_only: bool = False) -> None:
        """Open the web dashboard in a detached subprocess (serves on :5006)."""
        cmd = [sys.executable, "-m", "Epigrass.manager", "-b", "sqlite"]
        if gradio:
            cmd.append("-G")
        if view_only:
            cmd.append("-V")
        cmd.append(Path(epg_path).name)
        subprocess.Popen(cmd, cwd=str(Path(epg_path).parent))
        self.notify("Dashboard starting on http://localhost:5006 "
                    "(leave it running in the background)")


def run() -> None:
    """Entry point for ``epirunner tui``."""
    EpigrassTui().run()
