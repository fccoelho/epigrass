"""
Spread display and analysis module.

This module handles the generation of spread trees from epidemiological
simulation data and exports them in various graph formats.
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TextIO, Tuple

import networkx as nx
import numpy as np

if TYPE_CHECKING:
    from Epigrass.base_models import Graph


class Spread:
    """
    Generates and exports spread trees from epidemic simulation data.

    A spread tree represents the transmission pathways of an epidemic,
    showing which sites infected which other sites and at what time.

    Attributes:
        g: The graph object containing epidemic simulation data.
        nxg: A NetworkX MultiDiGraph representing the spread tree.
        outdir: Output directory for exported files.
        encoding: Character encoding for file outputs.
    """

    def __init__(
        self, graphobj: "Graph", outdir: str = ".", encoding: str = "utf-8"
    ) -> None:
        """
        Initialize the Spread object and generate spread tree files.

        Args:
            graphobj: A graph object containing epidemic simulation data
                      with epipath and site_dict attributes.
            outdir: Directory where output files will be saved.
            encoding: Character encoding for output files.
        """
        self.g = graphobj
        self.nxg: nx.MultiDiGraph = nx.MultiDiGraph()
        self.outdir = Path(outdir)
        self.encoding = encoding

        self.create_tree()
        self._export_graphs()

    def create_tree(self) -> None:
        """
        Generate an unambiguous spread tree by selecting infectors for each site.

        Creates a NetworkX MultiDiGraph where nodes represent infected sites
        and edges represent transmission events with weights indicating the
        number of infectious individuals transmitted.
        """
        for n in self.g.epipath:
            infected = self.g.site_dict[n[1]]
            infectors = n[-1]

            self.nxg.add_node(n[1], name=infected.sitename, time=n[0])

            for infector, count in infectors.items():
                self.nxg.add_edge(n[1], infector.geocode, weight=float(count))

    def _export_graphs(self) -> None:
        """Export the spread tree to multiple graph formats."""
        self.outdir.mkdir(parents=True, exist_ok=True)

        # Export to GraphML
        nx.write_graphml(
            self.nxg, str(self.outdir / "spread.graphml"), encoding=self.encoding
        )

        # Export to GML
        nx.write_gml(self.nxg, str(self.outdir / "spread.gml"))

        # Export to JSON
        node_link_data = nx.node_link_data(self.nxg)
        with open(self.outdir / "spread.json", "w", encoding=self.encoding) as f:
            json.dump(node_link_data, f)

    @classmethod
    def write_gml(
        cls,
        tree: List[Tuple[Any, ...]],
        outdir: str,
        encoding: str,
        fname: str = "spreadtree.gml",
    ) -> None:
        """
        Save a spread tree in GML format with custom styling.

        This class method provides backward compatibility for custom
        GML export with visual styling attributes.

        Args:
            tree: List of tuples representing the spread tree.
                  Each tuple contains (time, target_id, source_id, ...).
            outdir: Output directory path.
            encoding: Character encoding for the output file.
            fname: Output filename (default: "spreadtree.gml").
        """
        output_path = Path(outdir)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(output_path / fname, "w", encoding=encoding) as f:
            cls._write_gml_content(f, tree)

        print(f"Wrote {fname}")

    @classmethod
    def _write_gml_content(cls, fobj: TextIO, tree: List[Tuple[Any, ...]]) -> None:
        """
        Write the edges and nodes section of a GML file.

        Args:
            fobj: File object to write to.
            tree: List of tuples representing the spread tree.
        """
        # Write header
        fobj.writelines(
            [
                'Creator "Epigrass"\n',
                'Version ""\n',
                "graph\n[\n",
                "\thierarchic\t1\n",
                '\tlabel\t"Spread Tree"\n',
                "\tdirected\t1\n",
            ]
        )

        # Create dictionary of node IDs, eliminating duplicates
        nodes: Dict[Any, int] = {}
        for idx, item in enumerate(tree):
            target_id = item[1]
            if target_id not in nodes:
                nodes[target_id] = len(nodes)

        # Write nodes
        for node_id, node_num in nodes.items():
            fobj.writelines(
                [
                    "\tnode\n",
                    "\t[\n",
                    f"\t\tid\t{node_num}\n",
                    f'\t\tlabel\t"{node_id}"\n',
                    "\t\tgraphics\n",
                    "\t\t[\n",
                    "\t\t\tw\t60\n",
                    "\t\t\th\t30\n",
                    '\t\t\ttype\t"roundrectangle"\n',
                    '\t\t\tfill\t"#FFCC00"\n',
                    '\t\t\toutline\t"#000000"\n',
                    "\t\t]\n",
                    "\t\tLabelGraphics\n",
                    "\t\t[\n",
                    f'\t\t\ttext\t"{node_id}"\n',
                    "\t\t\tfontSize\t13\n",
                    '\t\t\tfontName\t"Dialog"\n',
                    '\t\t\tanchor\t"c"\n',
                    "\t\t]\n",
                    "\t]\n",
                ]
            )

        # Write edges
        for item in tree:
            label = str(item[0])
            target_id = nodes[item[1]]

            try:
                source_id = nodes[item[2]]
            except KeyError:
                # Seed site has no source
                continue

            fobj.writelines(
                [
                    "\tedge\n",
                    "\t[\n",
                    f"\t\tsource\t{source_id}\n",
                    f"\t\ttarget\t{target_id}\n",
                    f'\t\tlabel\t"{label}"\n',
                    "\t\tgraphics\n",
                    "\t\t[\n",
                    '\t\t\tfill\t"#000000"\n',
                    '\t\t\ttargetArrow\t"standard"\n',
                    "\t\t]\n",
                    "\t]\n",
                ]
            )

        fobj.write("]")
