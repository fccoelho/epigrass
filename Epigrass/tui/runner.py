"""Async subprocess runner for Epigrass simulations.

Simulations always run as ``python -m Epigrass.manager <flags> <model.epg>``
child processes (same pattern as the Gradio builder, epigrass_gui.py), so a
crash or hung simulation never takes the TUI down with it.
"""
from __future__ import annotations

import asyncio
import os
import re
import signal
import sys
from dataclasses import dataclass
from pathlib import Path

#: Matches tqdm bar lines such as
#: ``Simulation steps (vectorized):  45%|████▌     | 23/50 [00:12<00:15]``
TQDM_RE = re.compile(
    r"^(?P<desc>.*?)\s*:\s*(?P<pct>\d+)%\|[^\|]*\|\s*(?P<cur>\d+)/(?P<total>\d+)"
)

BACKENDS = ("sqlite", "csv", "mysql")


@dataclass
class RunConfig:
    """Options mirroring the epirunner CLI flags."""

    backend: str = "sqlite"
    dbuser: str = ""
    dbpass: str = ""
    dbhost: str = "localhost"
    parallel: bool = False
    dashboard: bool = False
    gradio: bool = True  # TUI default dashboard is the Gradio one
    view_only: bool = False

    def to_args(self) -> list[str]:
        args = ["-b", self.backend]
        if self.backend == "mysql":
            args += ["-u", self.dbuser, "-p", self.dbpass, "-H", self.dbhost]
        if self.parallel:
            args.append("-P")
        if self.dashboard:
            args.append("-D")
        if self.gradio:
            args.append("-G")
        if self.view_only:
            args.append("-V")
        return args


def build_command(epg_path: str | os.PathLike, config: RunConfig) -> list[str]:
    """Full command line: manager is always run from the model's directory."""
    epg = Path(epg_path)
    return [sys.executable, "-m", "Epigrass.manager", *config.to_args(), epg.name]


def parse_progress(line: str) -> tuple[str, int, int] | None:
    """Extract ``(description, current, total)`` from a tqdm bar line."""
    m = TQDM_RE.match(line.strip())
    if not m:
        return None
    desc = m.group("desc").strip() or "Progress"
    return desc, int(m.group("cur")), int(m.group("total"))


class SimulationRunner:
    """Streams a simulation subprocess, parsing tqdm progress from stdout."""

    def __init__(
        self,
        epg_path: str | os.PathLike,
        config: RunConfig | None = None,
        cwd: str | os.PathLike | None = None,
    ):
        self.epg_path = Path(epg_path)
        self.config = config or RunConfig()
        self.cwd = str(Path(cwd) if cwd is not None else self.epg_path.parent)
        self.command = build_command(self.epg_path, self.config)
        self.proc: asyncio.subprocess.Process | None = None

    async def run(self):
        """Async generator of events.

        - ``("start", command)``
        - ``("log", line)``
        - ``("progress", description, current, total)``
        - ``("done", returncode)``
        """
        self.proc = await asyncio.create_subprocess_exec(
            *self.command,
            cwd=self.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            start_new_session=True,  # own process group, so pools die with it
        )
        yield ("start", " ".join(self.command))
        assert self.proc.stdout is not None
        buf = b""
        while True:
            chunk = await self.proc.stdout.read(2048)
            if not chunk:
                break
            buf += chunk
            # tqdm repaints the bar with \r; regular prints end with \n
            parts = re.split(rb"[\r\n]", buf)
            buf = parts.pop()
            for part in parts:
                if not part.strip():
                    continue
                text = part.decode(errors="replace")
                progress = parse_progress(text)
                if progress:
                    yield ("progress", *progress)
                else:
                    yield ("log", text)
        if buf.strip():
            text = buf.decode(errors="replace")
            progress = parse_progress(text)
            if progress:
                yield ("progress", *progress)
            else:
                yield ("log", text)
        returncode = await self.proc.wait()
        yield ("done", returncode)

    def cancel(self) -> None:
        """Terminate the whole simulation process group."""
        if self.proc is None or self.proc.returncode is not None:
            return
        try:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                self.proc.kill()
            except ProcessLookupError:
                pass
