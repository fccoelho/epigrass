"""
Report generation module for Epigrass simulations.

This module generates markdown reports with embedded plots for
epidemiological network simulation models.
"""

import base64
import datetime
import io
import os
import re
import sys
from pathlib import Path
from time import time as timer
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from Epigrass.simulation import Simulation


class ReportError(Exception):
    """Custom exception for report generation errors."""

    pass


class PlotHelper:
    """
    Helper class for generating plots in reports.

    Provides predefined plot functions that can be safely called
    instead of using exec() on arbitrary code.
    """

    @staticmethod
    def bar_plot(
        x: List[int],
        y: List[Union[int, float]],
        xlabel: str = "",
        ylabel: str = "",
        title: str = "",
    ) -> plt.Figure:
        """Create a bar plot and return the figure."""
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        return fig

    @staticmethod
    def histogram(
        data: np.ndarray, bins: int = 10, density: bool = True, title: str = ""
    ) -> plt.Figure:
        """Create a histogram and return the figure."""
        fig, ax = plt.subplots()
        flat_data = data.flat if hasattr(data, "flat") else data
        if flat_data is None or (hasattr(flat_data, "size") and flat_data.size == 0):
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_title(title)
            return fig
        ax.hist(flat_data, bins=bins, density=density)
        ax.set_title(title)
        return fig

    @staticmethod
    def pcolor_plot(
        matrix: np.ndarray, title: str = "", colorbar: bool = True
    ) -> plt.Figure:
        """Create a pseudocolor plot and return the figure."""
        fig, ax = plt.subplots()

        def no_data_msg(msg: str = "No data"):
            ax.text(0.5, 0.5, msg, ha="center", va="center", transform=ax.transAxes)
            ax.set_title(title)

        try:
            if matrix is None:
                no_data_msg()
                return fig

            # Convert sparse matrix to dense if needed
            if hasattr(matrix, "toarray"):
                matrix = matrix.toarray()

            if not hasattr(matrix, "shape"):
                no_data_msg()
                return fig

            if len(matrix.shape) < 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
                no_data_msg("Insufficient data for matrix plot")
                return fig

            c = ax.pcolor(matrix)
            ax.set_title(title)
            if colorbar:
                fig.colorbar(c, ax=ax)
            return fig

        except Exception:
            no_data_msg("Unable to render matrix")
            return fig
        if hasattr(matrix, "shape") and (
            len(matrix.shape) < 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0
        ):
            ax.text(
                0.5, 0.5, "Insufficient data for matrix plot", ha="center", va="center"
            )
            ax.set_title(title)
            return fig
        c = ax.pcolor(matrix)
        ax.set_title(title)
        if colorbar:
            fig.colorbar(c, ax=ax)
        return fig


class Report:
    """
    Generates markdown reports in PDF format from simulation data.

    Takes a simulation object as input and produces reports containing
    network analysis statistics, epidemiological statistics, and
    site-specific analyses.

    Attributes:
        sim: The simulation object to generate reports from.
        workdir: Working directory for report output.
        encoding: Character encoding for output files.
    """

    def __init__(self, simulation: "Simulation") -> None:
        """
        Initialize the Report generator.

        Args:
            simulation: A simulation object containing model data and results.
        """
        self.workdir = Path.cwd()
        self.sim = simulation
        self.encoding = getattr(self.sim, "encoding", "utf-8")
        self.header = ""
        self.plotter = PlotHelper()

        self.title_template = """# Epigrass Report

Model {modname} Network Report

{author}

{date}


## Abstract
Edit the report.md file and add your model's description here.

"""

    def _gen_title(
        self, title_type: str = "full", author: str = "Epigrass User"
    ) -> str:
        """
        Generate title section from simulation data.

        Args:
            title_type: Type of report ('network', 'epi', or 'full').
            author: Author name for the report.

        Returns:
            Formatted title string.
        """
        modname = self.sim.modelName
        return self.title_template.format(
            modname=modname, author=author, date=datetime.date.today()
        )

    def gen_net_title(self) -> str:
        """Generate title for network-only report."""
        return self._gen_title("network")

    def gen_epi_title(self) -> str:
        """Generate title for epidemiological report."""
        return self._gen_title("epi")

    def gen_full_title(self) -> str:
        """Generate title for full report."""
        return self._gen_title("full")

    def _figure_to_base64(self, fig: plt.Figure) -> str:
        """
        Convert a matplotlib figure to a base64-encoded image tag.

        Args:
            fig: Matplotlib figure to convert.

        Returns:
            Markdown image tag with embedded base64 image.
        """
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        return f"\n![Plot](data:image/png;base64,{img_base64})\n"

    def gen_graph_desc(self) -> str:
        """
        Generate the graph description section with network statistics.

        Returns:
            Markdown string containing network analysis and statistics.
        """
        stats = tuple(self.sim.g.doStats())
        nodd = sum(1 for i in self.sim.g.site_list if len(i.neighbors) % 2 != 0)

        # Check if Graph is Eulerian and/or traversable
        trav = "No"
        eul = "No"
        if nodd:
            if nodd == 2:
                trav = "Yes"
        else:
            eul = "Yes"

        nnodes = len(self.sim.g.site_list)
        nedges = len(self.sim.g.edge_list)
        deglist = [len(i.neighbors) for i in self.sim.g.site_list]

        # Check if graph is Hamiltonian
        if nnodes >= 3:
            if min(deglist) >= nnodes / 2.0:
                ham = "Yes"
            else:
                ham = "Possibly"
        else:
            ham = "Yes"

        # Generate plots
        plots_md = []

        # Shortest paths distribution
        fig = self.plotter.histogram(
            stats[0], bins=20, title="Shortest paths distribution"
        )
        plots_md.append(self._figure_to_base64(fig))

        # Adjacency Matrix
        fig = self.plotter.pcolor_plot(stats[12], title="Adjacency Matrix")
        plots_md.append(self._figure_to_base64(fig))

        matrix = f"""## General Network Analyses
The figure below contains a simple drawing of your graph. If your network 
is not very complex, it can help you to verify if the topology specified corresponds to
your expectations.

```python
self.sim.g.drawGraph()
```

## Network Descriptive Statistics
In this section you will find quantitative descriptors and plots 
that will help you analyze your network.

### Basic statistics

 - **Order (Number of Nodes):** {nnodes}
 - **Size (Number of Edges):** {nedges}
 - **Eulerian:** {eul}
 - **Traversable:** {trav}
 - **Hamiltonian:** {ham}

## Distance matrix
The distance Matrix represents the number of edges separating any
pair of nodes via the shortest path between them.

{plots_md[0]}

## Adjacency Matrix
The most basic measure of accessibility involves network connectivity
where a network is represented as a connectivity matrix (below), which 
expresses the connectivity of each node with its adjacent nodes.

The number of columns and rows in this matrix is equal to the number 
of nodes in the network and a value of 1 is given for each cell where 
there is a connected pair and a value of 0 for each cell where there 
is an unconnected pair.

{plots_md[1]}
"""

        indices = f"""
## Number of Cycles
The maximum number of independent cycles in a graph.
This number ($u$) is estimated by knowing the number of nodes ($v$), 
links ($e$) and of sub-graphs ($p$); $u = e-v+p$.

Trees and simple networks will have a value of 0 since they have no cycles.
The more complex a network is, the higher the value of u, so it can be used 
as an indicator of the level of development of a transport system.

**Cycles(u) = {stats[1]}**

## Wiener Distance
The Wiener distance is the sum of all the shortest distances in the network.

**Wiener's D = {stats[2]}**

## Mean Distance
The mean distance of a network is the mean of the set of shortest paths, 
excluding the 0-length paths.

$\\bar{{D}} = {stats[3]}$

## Network Diameter
The diameter of a network is the longest element of the shortest paths set.

$D(N) = {stats[4]}$

## Length of the Network
The length of a network is the sum in metric units (e.g., km) of all edges.

$L(N) = {stats[5]}$

## Weight of the Network
The weight of a network is the weight of all nodes in the graph ($W(N)$), 
which is the summation of each node's order ($o$) multiplied by 2 for all 
orders above 1.

$W(N) = {stats[6]}$

## Iota ($\\iota$) Index
The Iota index measures the ratio between the network and its weighted vertices.
It considers the structure, the length and the function of a network.

$\\iota = \\frac{{L(N)}}{{W(N)}} = {stats[7]}$

## Pi ($\\Pi$) Index
The Pi index represents the relationship between the total length of the 
network L(N) and the distance along the diameter D(d).

$\\Pi = L(N)/D(d) = {stats[8]}$

## Beta ($\\beta$) Index
The Beta index measures the level of connectivity in a network.

$\\beta = {stats[10]}$
"""
        return matrix + indices

    def site_report(self, geoc: Union[int, str]) -> Optional[str]:
        """
        Generate a report for a specific site.

        Args:
            geoc: Geocode identifying the site.

        Returns:
            Markdown string with site statistics, or None if site not found.
        """
        site = None
        for i in self.sim.g.site_list:
            if int(i.geocode) == int(geoc):
                site = i
                break

        if not site:
            print(f"Warning: Geocode {geoc} not found in site list, skipping.")
            return None

        stats = site.doStats()
        name = site.sitename

        return f"""
# {name}

## Centrality
$$C = {stats[0]}$$

## Degree
$$D = {stats[1]}$$

## Theta Index
$$\\theta = {stats[2]}$$

## Betweenness
$$B = {stats[3]}$$
"""

    def gen_site_epi(self, geoc: Union[int, str]) -> Optional[str]:
        """
        Generate epidemiological report for a specific site.

        Args:
            geoc: Geocode identifying the site.

        Returns:
            Markdown string with site epidemiological statistics, or None if not found.
        """
        site = None
        for i in self.sim.g.site_list:
            if int(i.geocode) == int(geoc):
                site = i
                break

        if not site:
            print(f"Warning: Geocode {geoc} not found in site list, skipping.")
            return None

        name = site.sitename
        incidence = site.incidence
        infc = site.thetahist
        cuminc = [sum(incidence[:i]) for i in range(len(incidence))]

        # Generate incidence plot
        fig = self.plotter.bar_plot(
            list(range(len(cuminc))),
            cuminc,
            xlabel="Time",
            ylabel="Incidence",
            title="Incidence per unit of time",
        )
        inc_plot = self._figure_to_base64(fig)

        # Generate infectious arrivals plot
        fig = self.plotter.bar_plot(
            list(range(len(infc))),
            infc,
            xlabel="Time",
            ylabel="Infectious individuals",
            title="Number of infectious individuals arriving per unit of time",
        )
        infc_plot = self._figure_to_base64(fig)

        return f"""
# {name}

## Incidence
{inc_plot}

## Infectious Arrivals
{infc_plot}
"""

    def gen_epi(self) -> str:
        """
        Generate epidemiological statistics section.

        Returns:
            Markdown string containing epidemiological statistics.
        """
        epistats = self.sim.g.getEpistats()
        cumcities = [sum(epistats[1][:i]) for i in range(len(epistats[1]))]

        # Generate epidemic spread plot
        fig = self.plotter.bar_plot(
            list(range(len(cumcities))),
            cumcities,
            xlabel="Time",
            ylabel="Number of infected cities",
        )
        spread_plot = self._figure_to_base64(fig)

        mean_speed = np.mean(epistats[1]) if epistats[1] else 0

        return f"""
# Epidemiological Statistics

## Network-wide Epidemiological Statistics
In the table below, we present epidemiological statistics about this simulation.

| Metric | Value |
|--------|-------|
| Size (people) | {epistats[0]} |
| Speed | {mean_speed} |
| Size (sites) | {epistats[2]} |
| Duration | {epistats[3]} |
| Survival | {epistats[4]} |
| Total vaccines | {epistats[5]} |
| Total Quarantined | {epistats[6]} |

{spread_plot}
"""

    def assemble(self, report_type: int, save: bool = True) -> Optional[str]:
        """
        Assemble the specified type of report.

        Args:
            report_type: Type of report to generate:
                - 0: None
                - 1: Network only
                - 2: Epidemiological only
                - 3: Both (full report)
            save: Whether to save the report to disk.

        Returns:
            Markdown string of the report, or None if report_type is 0.
        """
        print("Starting report generation...")

        sitehead = """
# Site Specific Analyses

 - **Centrality:** Also known as closeness. A measure of global centrality, 
   is the inverse of the sum of the shortest paths to all other nodes.
 - **Degree:** The order (degree) of a node is the number of its attached links.
 - **Theta Index:** Measures the function of a node, that is the average
   amount of traffic per intersection.
 - **Betweenness:** Is the number of times any node figures in the shortest path
   between any other pair of nodes.
"""

        tail = ""

        if report_type == 1:
            start = timer()
            markdown_src = self.header + self.gen_net_title() + self.gen_graph_desc()

            if self.sim.siteRep:
                markdown_src += sitehead
                for site in self.sim.siteRep:
                    result = self.site_report(site)
                    if result:
                        markdown_src += result

            markdown_src += tail
            elapsed = timer() - start
            print(f"Time to generate Network report: {elapsed:.2f} seconds.")
            repname = "net_report"

        elif report_type == 2:
            start = timer()
            markdown_src = self.header + self.gen_epi_title() + self.gen_epi()

            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    result = self.gen_site_epi(site)
                    if result:
                        markdown_src += result

            markdown_src += tail
            elapsed = timer() - start
            print(f"Time to generate Epidemiological report: {elapsed:.2f} seconds.")
            repname = "epi_report"

        elif report_type == 3:
            start = timer()
            markdown_src = self.header + self.gen_full_title() + self.gen_graph_desc()

            if self.sim.siteRep:
                markdown_src += sitehead
                for site in self.sim.siteRep:
                    result = self.site_report(site)
                    if result:
                        markdown_src += result

            markdown_src += self.gen_epi()

            if self.sim.siteRep:
                for site in self.sim.siteRep:
                    result = self.gen_site_epi(site)
                    if result:
                        markdown_src += result

            markdown_src += tail
            elapsed = timer() - start
            print(f"Time to generate full report: {elapsed:.2f} seconds.")
            repname = "full_report"

        else:
            return None

        if save:
            self.save_and_build(repname, markdown_src)

        return markdown_src

    def say(self, message: str) -> None:
        """
        Output a message to console.

        Args:
            message: The message to output.
        """
        print(message)

    def save_and_build(self, name: str, src: str) -> str:
        """
        Save the report in markdown format.

        Args:
            name: Base name for the report file.
            src: Markdown content to save.

        Returns:
            Path to the saved report file.
        """
        dirname = f"{self.sim.modelName}-report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        path = self.workdir / dirname
        path.mkdir(parents=True, exist_ok=True)

        md_file = path / f"{name}.md"
        print(f"Saving {md_file}")

        with open(md_file, "w", encoding=self.encoding) as f:
            f.write(src)

        print(f"Successfully generated markdown report at: {md_file}")
        return str(md_file)
