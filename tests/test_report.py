import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from datetime import date

from Epigrass.report import Report

class TestReport(unittest.TestCase):
    def setUp(self):
        # Create a mock simulation object
        self.mock_sim = MagicMock()
        self.mock_sim.modelName = "TestModel"
        self.mock_sim.encoding = "utf-8"
        self.mock_sim.siteRep = []
        self.mock_sim.g = MagicMock()
        self.mock_sim.g.site_list = []
        self.mock_sim.g.edge_list = []
        self.mock_sim.g.doStats.return_value = (
            [1, 2, 3],  # stats[0] - distance matrix
            5,          # stats[1] - cycles
            10,         # stats[2] - wiener distance
            2.5,        # stats[3] - mean distance
            5,          # stats[4] - diameter
            100,        # stats[5] - length
            50,        # stats[6] - weight
            2.0,       # stats[7] - iota index
            20.0,      # stats[8] - pi index
            1.5,       # stats[10] - beta index
            None, None, None  # Placeholders for other stats
        )
        self.mock_sim.g.getEpistats.return_value = (
            1000,       # epistats[0] - size people
            [10, 20, 30], # epistats[1] - incidence per time
            50,         # epistats[2] - size sites
            30,        # epistats[3] - duration
            15,        # epistats[4] - survival time
            200,       # epistats[5] - total vaccines
            100        # epistats[6] - total quarantined
        )

        self.report = Report(self.mock_sim)

    def test_init(self):
        self.assertEqual(self.report.sim, self.mock_sim)
        self.assertEqual(self.report.encoding, "utf-8")
        self.assertTrue(hasattr(self.report, "workdir"))

    def test_genNetTitle(self):
        title = self.report.genNetTitle()
        self.assertIn("TestModel", title)
        self.assertIn(str(date.today()), title)

    def test_graphDesc(self):
        desc = self.report.graphDesc()
        self.assertIn("General Network Analyses", desc)
        self.assertIn("Basic statistics", desc)
        self.assertGreaterEqual(desc.find("Order (Number of Nodes):** 0"), 1)  # From empty site_list
        self.assertGreaterEqual(desc.find("Wiener's $D =10"), 1)

    def test_genEpi(self):
        epi = self.report.genEpi()
        self.assertGreaterEqual(epi.find("Epidemiological Statistics"), 1)
        self.assertGreaterEqual(epi.find("Size (people) | 1000"), 1)
        # self.assertGreaterEqual(epi.find("Duration       | 30"), 1)

    @patch('os.makedirs')
    @patch('os.chdir')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_savenBuild(self, mock_open, mock_chdir, mock_makedirs):
        test_content = "# Test Report"
        test_name = "test_report"
        
        self.report.savenBuild(test_name, test_content)
        
        # Verify directory was created
        mock_makedirs.assert_called_once()
        mock_chdir.assert_called_once()
        
        # Verify file was written
        mock_open.assert_called_once_with(f"{test_name}.md", 'w', encoding='utf8')
        mock_open().write.assert_called_once_with(test_content)

    def test_Assemble_type1(self):
        with patch.object(self.report, 'savenBuild') as mock_save:
            self.report.Assemble(1)
            mock_save.assert_called_once()
            args, _ = mock_save.call_args
            self.assertIn("Network Descriptive Statistics", args[1])

    def test_Assemble_type2(self):
        with patch.object(self.report, 'savenBuild') as mock_save:
            self.report.Assemble(2)
            mock_save.assert_called_once()
            args, _ = mock_save.call_args
            self.assertIn("Epidemiological Statistics", args[1])

    def test_Assemble_type3(self):
        with patch.object(self.report, 'savenBuild') as mock_save:
            self.report.Assemble(3)
            mock_save.assert_called_once()
            args, _ = mock_save.call_args
            self.assertIn("Network Descriptive Statistics", args[1])
            self.assertIn("Epidemiological Statistics", args[1])

if __name__ == '__main__':
    unittest.main()
