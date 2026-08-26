"""Tests for the epirunner TUI (Epigrass.tui)."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from Epigrass.tui import epg_utils
from Epigrass.tui.runner import (BACKENDS, RunConfig, SimulationRunner,
                                 build_command, parse_progress)

TESTS_DIR = Path(__file__).parent


class TestEpgParse(unittest.TestCase):
    def setUp(self):
        self.epg = TESTS_DIR / "SEIR.epg"

    def test_parse_mirrors_manager_semantics(self):
        parsed = epg_utils.parse_epg(self.epg)
        self.assertEqual(parsed["epidemiological model.modtype"], "SEIR")
        self.assertEqual(parsed["the world.sites"], "sitios3.csv")
        self.assertEqual(parsed["the world.edges"], "edgesout.csv")
        # inline comments are preserved in raw values
        self.assertIn("# clumping", parsed["model parameters.alpha"])

    def test_overview_rows_ordered(self):
        rows = epg_utils.overview_rows(epg_utils.parse_epg(self.epg))
        sections = [r[0] for r in rows]
        self.assertIn("The World", sections)
        self.assertLess(sections.index("The World"),
                        sections.index("Simulation And Output"))
        # every row is (section, key, value)
        for sec, key, value in rows:
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)


class TestEpgValidate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.epg = Path(self.tmp) / "model.epg"
        shutil.copy(TESTS_DIR / "SEIR.epg", self.epg)
        # copy companion data files next to the model
        for name in ("sitios3.csv", "edgesout.csv"):
            shutil.copy(TESTS_DIR / name, Path(self.tmp) / name)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_valid_script(self):
        self.assertEqual(epg_utils.validate_epg(self.epg), [])

    def test_missing_sites_file(self):
        os.remove(Path(self.tmp) / "sitios3.csv")
        errors = epg_utils.validate_epg(self.epg)
        self.assertTrue(any("sites file not found" in e for e in errors))

    def test_invalid_modtype(self):
        epg_utils.set_values(self.epg, {("epidemiological model", "modtype"): "XYZ"})
        errors = epg_utils.validate_epg(self.epg)
        self.assertTrue(any("Invalid model type" in e for e in errors))

    def test_missing_required_key(self):
        text = self.epg.read_text().replace("alpha =", "alphax =")
        self.epg.write_text(text)
        errors = epg_utils.validate_epg(self.epg)
        self.assertTrue(any("Missing required entry: [model parameters] alpha"
                            in e for e in errors))

    def test_bad_expression(self):
        epg_utils.set_values(self.epg, {("simulation and output", "steps"): "50/0+"})
        errors = epg_utils.validate_epg(self.epg)
        self.assertTrue(any("steps" in e and "invalid expression" in e
                            for e in errors))

    def test_unparseable_file(self):
        bad = Path(self.tmp) / "bad.epg"
        bad.write_text("[broken\nno equals here\n")
        errors = epg_utils.validate_epg(bad)
        self.assertTrue(errors)


class TestEpgSetValues(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.epg = Path(self.tmp) / "model.epg"
        self.epg.write_text(
            "[SIMULATION AND OUTPUT]\n"
            "steps = 50\n"
            "\n"
            "[MODEL PARAMETERS]\n"
            "beta = 0.4  # transmission\n"
            "alpha = 1\n"
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_set_value_preserves_comments(self):
        changed, missing = epg_utils.set_values(
            self.epg,
            {("simulation and output", "steps"): "100",
             ("model parameters", "beta"): "0.9"},
        )
        self.assertEqual(changed, 2)
        self.assertEqual(missing, [])
        text = self.epg.read_text()
        self.assertIn("steps = 100", text)
        self.assertIn("beta = 0.9  # transmission", text)
        self.assertIn("alpha = 1", text)

    def test_set_value_reports_missing_keys(self):
        changed, missing = epg_utils.set_values(
            self.epg, {("model parameters", "nonexistent"): "1"})
        self.assertEqual(changed, 0)
        self.assertIn(("model parameters", "nonexistent"), missing)

    def test_section_scoping(self):
        # 'steps' only exists in SIMULATION AND OUTPUT, so this must miss
        changed, missing = epg_utils.set_values(
            self.epg, {("model parameters", "steps"): "100"})
        self.assertEqual(changed, 0)
        self.assertEqual(len(missing), 1)


class TestFindModels(unittest.TestCase):
    def test_finds_nested_epgs_skips_outdata_and_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.epg").touch()
            (root / "sub").mkdir()
            (root / "sub" / "b.epg").touch()
            (root / ".git").mkdir()
            (root / ".git" / "c.epg").touch()
            (root / "outdata-a").mkdir()
            (root / "outdata-a" / "d.epg").touch()
            models = epg_utils.find_models(root)
            names = [m.name for m in models]
            self.assertEqual(names, ["a.epg", "b.epg"])

    def test_max_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "x" / "y").mkdir(parents=True)
            (root / "x" / "deep.epg").touch()
            (root / "x" / "y" / "deeper.epg").touch()
            names = [m.name for m in epg_utils.find_models(root, max_depth=1)]
            self.assertEqual(names, ["deep.epg"])


class TestRunConfigAndCommand(unittest.TestCase):
    def test_defaults_match_cli_defaults(self):
        cfg = RunConfig()
        self.assertEqual(cfg.backend, "sqlite")
        self.assertEqual(cfg.to_args(), ["-b", "sqlite"])

    def test_mysql_includes_credentials(self):
        cfg = RunConfig(backend="mysql", dbuser="u", dbpass="p", dbhost="h")
        self.assertEqual(cfg.to_args(),
                         ["-b", "mysql", "-u", "u", "-p", "p", "-H", "h"])

    def test_flag_toggles(self):
        cfg = RunConfig(parallel=True, dashboard=True, gradio=True, view_only=True)
        self.assertEqual(cfg.to_args(), ["-b", "sqlite", "-P", "-D", "-G", "-V"])

    def test_build_command_uses_basename(self):
        cfg = RunConfig(parallel=True)
        cmd = build_command("/some/dir/model.epg", cfg)
        self.assertEqual(cmd[-1], "model.epg")
        self.assertIn("-P", cmd)
        self.assertIn("Epigrass.manager", cmd)

    def test_backends_ordered(self):
        self.assertEqual(BACKENDS, ("sqlite", "csv", "mysql"))


class TestParseProgress(unittest.TestCase):
    def test_tqdm_line(self):
        line = "Simulation steps (vectorized):  45%|████▌     | 23/50 [00:12<00:15,  1.89it/s]"
        self.assertEqual(parse_progress(line),
                         ("Simulation steps (vectorized)", 23, 50))

    def test_complete_line(self):
        line = "Sites: 100%|██████████| 300/300 [00:03<00:00, 85.20it/s]"
        self.assertEqual(parse_progress(line), ("Sites", 300, 300))

    def test_plain_line(self):
        self.assertIsNone(parse_progress("Simulation starting."))
        self.assertIsNone(parse_progress(""))


class TestSimulationRunner(unittest.TestCase):
    def test_runner_sets_cwd_to_model_dir(self):
        runner = SimulationRunner(Path("/some/dir/model.epg"), RunConfig())
        self.assertEqual(runner.cwd, "/some/dir")
        self.assertTrue(runner.command[-1] == "model.epg")

    def test_cancel_without_process_is_noop(self):
        runner = SimulationRunner(Path("/some/dir/model.epg"))
        runner.cancel()  # must not raise


class TestTuiApp(unittest.IsolatedAsyncioTestCase):
    async def test_browser_lists_models_and_navigates(self):
        from Epigrass.tui.app import EpigrassTui
        from Epigrass.tui.screens.browser import ModelBrowserScreen

        app = EpigrassTui()
        async with app.run_test(size=(100, 40)) as pilot:
            await pilot.pause(0.2)
            browser = app.screen
            self.assertIsInstance(browser, ModelBrowserScreen)
            await pilot.pause(0.5)
            table = browser.query_one("#model-table")
            self.assertGreater(table.row_count, 0)
            # escape from the browser is a no-op (single screen)
            await pilot.press("escape")
            self.assertIs(app.screen, browser)

    async def test_monitor_finish_success_renders(self):
        # regression: _finish must not use non-existent Screen APIs
        from textual.widgets import Static

        from Epigrass.tui.app import EpigrassTui
        from Epigrass.tui.runner import RunConfig
        from Epigrass.tui.screens.monitor import RunMonitorScreen

        app = EpigrassTui()
        epg = TESTS_DIR / "SEIR.epg"
        async with app.run_test(size=(100, 40)) as pilot:
            monitor = RunMonitorScreen(epg, RunConfig())
            monitor.run_worker = lambda *a, **k: None  # no real simulation
            await app.push_screen(monitor)
            await pilot.pause(0.2)
            monitor.running = False  # pretend the run already ended
            monitor.returncode = 0
            monitor._finish()
            await pilot.pause(0.1)
            text = monitor.query_one("#monitor-status", Static).content
            self.assertIn("Finished successfully", str(text))

    async def test_monitor_finish_failure_renders(self):
        from textual.widgets import Static

        from Epigrass.tui.app import EpigrassTui
        from Epigrass.tui.runner import RunConfig
        from Epigrass.tui.screens.monitor import RunMonitorScreen

        app = EpigrassTui()
        epg = TESTS_DIR / "SEIR.epg"
        async with app.run_test(size=(100, 40)) as pilot:
            monitor = RunMonitorScreen(epg, RunConfig())
            monitor.run_worker = lambda *a, **k: None  # no real simulation
            await app.push_screen(monitor)
            await pilot.pause(0.2)
            monitor.running = False
            monitor.returncode = 1
            monitor._finish()
            await pilot.pause(0.1)
            text = monitor.query_one("#monitor-status", Static).content
            self.assertIn("Simulation failed", str(text))


class TestManagerTuiDispatch(unittest.TestCase):
    def test_tui_dispatch_is_isolated(self):
        # the tui entry must not import manager-side effects at module import
        import Epigrass.tui.app as tui_app

        self.assertFalse(any(m.startswith("Epigrass.manager")
                             for m in vars(tui_app)))


if __name__ == "__main__":
    unittest.main()
