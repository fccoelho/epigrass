"""
Epigrass Interactive Dashboard with Advanced Visualizations.

This module provides a Gradio-based dashboard for visualizing and analyzing
epidemiological simulation results with animated and interactive plots.
"""

import base64
import os
import tempfile
from functools import cache, lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd
import gradio as gr
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text


def _create_icon_file() -> str:
    """Create the icon file in a temporary directory."""
    enc_icon = b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA3ElEQVRYhe2WWQ7DIAxEH1XvVR+dmzkfVSJngWIW0VYZKV8EZgzDmABARFkhBDxomQs8z+tFvfoxBUG8nHkBgnircAlOwlt5LzxmkN4CbgFfJeB950vSrDHxUihOwtbEKxaQScKxQTUrCU87YJE5jnEeOJJfkdkxNUcTaDCnrbb0OCJRFbavmtySer3QVcAMI/5GEmaN1utNqAIhpjwghm8/Lsg2twbTd8CsU2/AlrnTTbhDbSX/swPgr2ZIeHl6QStX8tqsi79MBqxXMNcpu+LY7Ub0i48VdOv3CSxJ9X3LgJP02QAAAABJRU5ErkJggg=="
    icon_path = os.path.join(tempfile.gettempdir(), "egicon.png")
    with open(icon_path, "wb") as f:
        f.write(base64.b64decode(enc_icon))
    return icon_path


ICON_PATH = _create_icon_file()


class SimulationData:
    """Class to manage simulation data loading and caching."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._engine = None
        self._cache: Dict[str, Any] = {}

    @property
    def db_path(self) -> str:
        return os.path.join(self.model_path, "Epigrass.sqlite")

    @property
    def engine(self):
        """Lazy-loaded database engine."""
        if self._engine is None and os.path.exists(self.db_path):
            self._engine = create_engine(
                f"sqlite:///{self.db_path}?check_same_thread=False"
            )
        return self._engine

    def get_simulations(self) -> List[str]:
        """Get list of available simulations."""
        if not os.path.exists(self.db_path):
            return []

        with self.engine.connect() as con:
            result = con.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            )
            return [
                row[0]
                for row in result
                if not (row[0].endswith("_meta") or row[0].endswith("e"))
            ]

    def get_localities(self, simulation: str) -> List[str]:
        """Get list of localities for a simulation."""
        if not self.engine:
            return []

        query = text(f"SELECT DISTINCT name FROM {simulation}")
        with self.engine.connect() as con:
            result = con.execute(query)
            return [row[0] for row in result]

    def get_max_time(self, simulation: str) -> int:
        """Get maximum time step for a simulation."""
        if not self.engine:
            return 0

        query = text(f"SELECT MAX(time) FROM {simulation}")
        with self.engine.connect() as con:
            result = con.execute(query)
            max_t = result.fetchone()[0]
            return max_t if max_t is not None else 0

    def read_simulation(
        self,
        simulation: str,
        locality: Optional[str] = None,
        time: Optional[int] = None,
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Read simulation data with optional filtering."""
        if not self.engine:
            return pd.DataFrame()

        col_str = "*" if not columns else ", ".join(columns)
        query = f"SELECT {col_str} FROM {simulation}"
        conditions = []

        if locality:
            conditions.append("name = :locality")
        if time is not None:
            conditions.append("time = :time")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        params = {}
        if locality:
            params["locality"] = locality
        if time is not None:
            params["time"] = time

        with self.engine.connect() as con:
            df = pd.read_sql_query(text(query), con, params=params)

        df.fillna(0, inplace=True)
        return df

    def get_meta(self, simulation: str) -> pd.DataFrame:
        """Get simulation metadata."""
        if not self.engine:
            return pd.DataFrame()

        meta_table = f"{simulation}_meta"
        with self.engine.connect() as con:
            try:
                return pd.read_sql_query(text(f"SELECT * FROM {meta_table}"), con)
            except Exception:
                return pd.DataFrame()

    def read_map(self) -> gpd.GeoDataFrame:
        """Read map data from GeoPackage."""
        map_path = os.path.join(self.model_path, "Data.gpkg")
        if not os.path.exists(map_path):
            return gpd.GeoDataFrame()

        gdf = gpd.read_file(map_path)
        if hasattr(gdf, "geometry") and hasattr(gdf.geometry, "centroid"):
            gdf["lat"] = gdf.geometry.centroid.y
            gdf["lon"] = gdf.geometry.centroid.x
        return gdf

    def get_graph(self) -> nx.MultiDiGraph:
        """Read network graph from GML file."""
        graph_path = os.path.join(self.model_path, "network.gml")
        if os.path.exists(graph_path):
            return nx.read_gml(graph_path, destringizer=int)
        return nx.MultiDiGraph()

    def read_spread_tree(self) -> pd.DataFrame:
        """Read spread tree data if available."""
        spread_path = os.path.join(self.model_path, "spread.json")
        if os.path.exists(spread_path):
            with open(spread_path, "r") as f:
                import json

                data = json.load(f)
                return pd.DataFrame(data.get("links", []))
        return pd.DataFrame()

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()


class Visualizations:
    """Class containing all visualization functions."""

    def __init__(self, data: SimulationData):
        self.data = data

    def _get_map_bounds(self, mapdf: gpd.GeoDataFrame, padding: float = 0.15) -> dict:
        """
        Calculate zoom bounds for a map to show only the network region.

        Args:
            mapdf: GeoDataFrame with lat/lon columns.
            padding: Padding as fraction of range (default 15%).

        Returns:
            Dict with center, lataxis_range, lonaxis_range, and projection_scale.
        """
        if mapdf.empty or "lat" not in mapdf.columns or "lon" not in mapdf.columns:
            return {
                "center": dict(lat=0, lon=0),
                "lataxis_range": [-90, 90],
                "lonaxis_range": [-180, 180],
                "projection_scale": 1,
            }

        lat_min, lat_max = mapdf["lat"].min(), mapdf["lat"].max()
        lon_min, lon_max = mapdf["lon"].min(), mapdf["lon"].max()

        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min

        # Add padding
        lat_padding = lat_range * padding if lat_range > 0 else 0.5
        lon_padding = lon_range * padding if lon_range > 0 else 0.5

        lat_center = (lat_min + lat_max) / 2
        lon_center = (lon_min + lon_max) / 2

        # Calculate projection scale based on range
        # Larger range = smaller scale (more zoomed out)
        max_range = max(lat_range, lon_range)
        if max_range > 50:
            projection_scale = 1
        elif max_range > 20:
            projection_scale = 2
        elif max_range > 10:
            projection_scale = 3
        elif max_range > 5:
            projection_scale = 5
        elif max_range > 2:
            projection_scale = 8
        elif max_range > 1:
            projection_scale = 12
        else:
            projection_scale = 20

        return {
            "center": dict(lat=lat_center, lon=lon_center),
            "lataxis_range": [lat_min - lat_padding, lat_max + lat_padding],
            "lonaxis_range": [lon_min - lon_padding, lon_max + lon_padding],
            "projection_scale": projection_scale,
        }

    def _apply_map_zoom(self, fig: go.Figure, bounds: dict) -> go.Figure:
        """Apply zoom bounds to a figure's geo layout."""
        fig.update_geos(
            projection_type="natural earth",
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            showlakes=True,
            lakecolor="lightblue",
            center=bounds["center"],
            lataxis_range=bounds["lataxis_range"],
            lonaxis_range=bounds["lonaxis_range"],
            projection_scale=bounds["projection_scale"],
        )
        return fig

    # ==================== ANIMATED CHOROPLETH MAP (Gradio-compatible) ====================

    def create_map_at_time(
        self,
        simulation: str,
        time: int,
        variable: str = "Infectious",
        colorscale: str = "YlOrRd",
    ) -> go.Figure:
        """
        Create choropleth map at a specific time step.

        This method is designed to work with Gradio's slider - no Plotly animations.

        Args:
            simulation: Name of the simulation to visualize.
            time: Time step to display.
            variable: Epidemiological variable to display.
            colorscale: Plotly colorscale name.

        Returns:
            Plotly Figure showing the map at the specified time.
        """
        if not simulation:
            return self._empty_figure("Selecione uma simulação")

        mapdf = self.data.read_map()
        if mapdf.empty:
            return self._empty_figure("Arquivo de mapa não encontrado")

        # Load data at specific time
        time_data = self.data.read_simulation(simulation, time=time)
        if time_data.empty:
            return self._empty_figure(f"Sem dados para tempo {time}")

        # Get available variables
        variables = [
            c
            for c in time_data.columns
            if c not in ["name", "time", "geocode", "lat", "longit"]
        ]

        if variable not in variables:
            variable = variables[0] if variables else "incidence"

        # Merge with map
        merged = mapdf.merge(time_data[["name", variable]], on="name", how="left")
        merged[variable] = merged[variable].fillna(0)

        # Calculate statistics
        total_cases = merged[variable].sum()
        max_val = merged[variable].max()
        infected_count = (merged[variable] > 0).sum()

        fig = go.Figure(
            go.Choropleth(
                geojson=merged.__geo_interface__,
                locations=merged.index,
                z=merged[variable],
                colorscale=colorscale,
                marker=dict(opacity=0.85, line=dict(width=0.5, color="gray")),
                colorbar=dict(title=variable, x=1.02),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    f"{variable}: %{{z:.2f}}<extra></extra>"
                ),
                customdata=[[name] for name in merged["name"]],
            )
        )

        # Calculate zoom bounds
        bounds = self._get_map_bounds(mapdf)
        fig = self._apply_map_zoom(fig, bounds)

        fig.update_layout(
            title=f"🎬 Dispersão Epidêmica - Tempo: {time} | {variable}",
            height=600,
            annotations=[
                dict(
                    text=f"Total: {total_cases:.0f} | Locais afetados: {infected_count} | Máx: {max_val:.0f}",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.02,
                    xanchor="left",
                    bgcolor="rgba(255,255,255,0.8)",
                    font=dict(size=11),
                )
            ],
        )

        return fig

    # ==================== SPREAD TREE (Gradio-compatible) ====================

    def create_spread_tree_at_time(self, simulation: str, time: int) -> go.Figure:
        """
        Create spread tree visualization at a specific time.

        Args:
            simulation: Name of the simulation.
            time: Time step to display.

        Returns:
            Plotly Figure showing infected locations up to the specified time.
        """
        if not simulation:
            return self._empty_figure("Selecione uma simulação")

        all_data = self.data.read_simulation(simulation)
        if all_data.empty:
            return self._empty_figure("Dados de simulação não encontrados")

        mapdf = self.data.read_map()
        if mapdf.empty:
            return self._empty_figure("Arquivo de mapa não encontrado")

        # Find infection times for each locality
        infection_times = {}

        for locality in all_data["name"].unique():
            loc_data = all_data[all_data["name"] == locality]
            infected = (
                loc_data[loc_data["Infectious"] > 0]
                if "Infectious" in loc_data.columns
                else loc_data[loc_data["incidence"] > 0]
            )

            if not infected.empty:
                infection_times[locality] = infected["time"].min()

        if not infection_times:
            return self._empty_figure("Nenhuma infecção detectada")

        # Nodes infected by this time
        infected_now = {
            loc: inf_t for loc, inf_t in infection_times.items() if inf_t <= time
        }

        if not infected_now:
            return self._empty_figure(f"Nenhuma infecção até o tempo {time}")

        # Create coordinate lookup
        coords = {}
        for _, row in mapdf.iterrows():
            coords[row["name"]] = (row["lon"], row["lat"])

        # Node positions
        node_data = [
            (loc, coords[loc][0], coords[loc][1], inf_t)
            for loc, inf_t in infected_now.items()
            if loc in coords
        ]

        if not node_data:
            return self._empty_figure("Coordenadas não encontradas")

        node_lons = [d[1] for d in node_data]
        node_lats = [d[2] for d in node_data]
        node_names = [d[0] for d in node_data]
        node_times = [d[3] for d in node_data]

        fig = go.Figure()

        # Add base choropleth
        fig.add_trace(
            go.Choropleth(
                geojson=mapdf.__geo_interface__,
                locations=mapdf.index,
                z=[
                    1 if mapdf.iloc[i]["name"] in infected_now else 0
                    for i in range(len(mapdf))
                ],
                colorscale=[[0, "lightgray"], [1, "lightyellow"]],
                showscale=False,
                hoverinfo="skip",
                marker=dict(opacity=0.3, line=dict(width=0.3, color="gray")),
            )
        )

        # Add infected nodes
        fig.add_trace(
            go.Scattergeo(
                lon=node_lons,
                lat=node_lats,
                mode="markers+text",
                text=node_names,
                textposition="top center",
                textfont=dict(size=8),
                marker=dict(
                    size=15,
                    color=node_times,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Tempo de Infecção", x=1.02),
                    line=dict(width=1, color="black"),
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Tempo de Infecção: %{marker.color}<extra></extra>"
                ),
                name="Locais Infectados",
            )
        )

        # Apply zoom bounds
        bounds = self._get_map_bounds(mapdf)
        fig = self._apply_map_zoom(fig, bounds)

        fig.update_layout(
            title=f"🌳 Árvore de Dispersão - Tempo: {time} | Locais infectados: {len(infected_now)}",
            height=600,
            showlegend=False,
        )

        return fig

    # ==================== R(t) VISUALIZATION ====================

    def calculate_rt(
        self, simulation: str, serial_interval: float = 7.0
    ) -> Tuple[go.Figure, pd.DataFrame]:
        """
        Calculate and visualize effective reproduction number R(t).

        Uses the exponential growth method for R(t) estimation.

        Args:
            simulation: Name of the simulation.
            serial_interval: Mean serial interval (default 7 days).

        Returns:
            Tuple of (Plotly Figure, R(t) DataFrame).
        """
        if not simulation:
            return self._empty_figure("Selecione uma simulação"), pd.DataFrame()

        all_data = self.data.read_simulation(simulation)
        if all_data.empty:
            return self._empty_figure("Dados não encontrados"), pd.DataFrame()

        # Aggregate new cases by time
        if "incidence" in all_data.columns:
            daily_cases = all_data.groupby("time")["incidence"].sum().reset_index()
        elif "Infectious" in all_data.columns:
            daily_cases = all_data.groupby("time")["Infectious"].sum().reset_index()
            daily_cases.rename(columns={"Infectious": "incidence"}, inplace=True)
        else:
            return self._empty_figure(
                "Variável de incidência não encontrada"
            ), pd.DataFrame()

        # Calculate R(t) using exponential growth method
        # R = exp(r * T), where r is growth rate and T is serial interval

        times = daily_cases["time"].values
        cases = daily_cases["incidence"].values

        rt_values = []
        ci_lower = []
        ci_upper = []

        window = 5  # Rolling window for smoothing

        for i in range(len(times)):
            if i < window - 1:
                rt_values.append(np.nan)
                ci_lower.append(np.nan)
                ci_upper.append(np.nan)
                continue

            # Calculate growth rate from rolling window
            window_cases = cases[i - window + 1 : i + 1]
            window_times = times[i - window + 1 : i + 1]

            # Avoid log(0)
            window_cases = np.maximum(window_cases, 1e-10)

            # Linear regression on log(cases)
            log_cases = np.log(window_cases)
            slope, _ = np.polyfit(window_times, log_cases, 1)

            # Calculate R(t)
            r = slope
            R = np.exp(r * serial_interval)

            # Simple confidence interval (assuming Poisson variation)
            var_r = 1 / np.sum(window_cases)
            R_lower = np.exp((r - 1.96 * np.sqrt(var_r)) * serial_interval)
            R_upper = np.exp((r + 1.96 * np.sqrt(var_r)) * serial_interval)

            rt_values.append(R)
            ci_lower.append(max(0, R_lower))
            ci_upper.append(R_upper)

        # Create DataFrame
        rt_df = pd.DataFrame(
            {
                "time": times,
                "Rt": rt_values,
                "CI_lower": ci_lower,
                "CI_upper": ci_upper,
                "cases": cases,
            }
        )

        # Remove NaN values for plotting
        rt_df_clean = rt_df.dropna()

        # Create figure
        fig = make_subplots(
            rows=2,
            cols=1,
            row_heights=[0.6, 0.4],
            subplot_titles=("R(t) - Número de Reprodução Efetivo", "Casos Novos"),
        )

        # R(t) line with confidence interval
        fig.add_trace(
            go.Scatter(
                x=rt_df_clean["time"],
                y=rt_df_clean["Rt"],
                mode="lines",
                name="R(t)",
                line=dict(color="blue", width=2),
            ),
            row=1,
            col=1,
        )

        # Confidence interval
        fig.add_trace(
            go.Scatter(
                x=list(rt_df_clean["time"]) + list(rt_df_clean["time"][::-1]),
                y=list(rt_df_clean["CI_upper"]) + list(rt_df_clean["CI_lower"][::-1]),
                fill="toself",
                fillcolor="rgba(0,100,255,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                showlegend=False,
                name="IC 95%",
            ),
            row=1,
            col=1,
        )

        # Threshold line at R=1
        fig.add_hline(
            y=1,
            line_dash="dash",
            line_color="red",
            annotation_text="R=1 (Limiar Epidêmico)",
            row=1,
            col=1,
        )

        # Cases bar chart
        fig.add_trace(
            go.Bar(
                x=rt_df["time"],
                y=rt_df["cases"],
                name="Casos Novos",
                marker_color="orange",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="📊 Número de Reprodução Efetivo R(t)",
            height=700,
            showlegend=True,
            hovermode="x unified",
        )

        fig.update_xaxes(title_text="Tempo", row=2, col=1)
        fig.update_yaxes(title_text="R(t)", row=1, col=1)
        fig.update_yaxes(title_text="Casos", row=2, col=1)

        # Autoscale y-axis based on R(t) values only (not confidence interval)
        if not rt_df_clean.empty and "Rt" in rt_df_clean.columns:
            rt_min = rt_df_clean["Rt"].min()
            rt_max = rt_df_clean["Rt"].max()
            # Add 20% padding, ensure 0 to at least 2 is shown for context
            y_min = max(0, rt_min * 0.8 - 0.2)
            y_max = max(2, rt_max * 1.2 + 0.2)
            fig.update_yaxes(range=[y_min, y_max], row=1, col=1)

        return fig, rt_df_clean

    # ==================== SIMULATION COMPARISON ====================

    def compare_simulations(
        self, simulations: List[str], variable: str = "Infectious"
    ) -> go.Figure:
        """
        Compare multiple simulation runs.

        Args:
            simulations: List of simulation names to compare.
            variable: Variable to compare.

        Returns:
            Plotly Figure with comparison plots.
        """
        if not simulations or len(simulations) < 2:
            return self._empty_figure("Selecione pelo menos 2 simulações")

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Curvas Epidêmicas Comparadas",
                "Casos Totais Acumulados",
                "Pico de Infecção",
                "Duração da Epidemia",
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}],
            ],
        )

        colors = px.colors.qualitative.Plotly
        summary_data = []

        for i, sim in enumerate(simulations):
            all_data = self.data.read_simulation(sim)
            if all_data.empty:
                continue

            # Aggregate by time
            if variable in all_data.columns:
                time_series = all_data.groupby("time")[variable].sum()
            elif "incidence" in all_data.columns:
                time_series = all_data.groupby("time")["incidence"].sum()
            else:
                continue

            color = colors[i % len(colors)]

            # Epidemic curve
            fig.add_trace(
                go.Scatter(
                    x=time_series.index,
                    y=time_series.values,
                    mode="lines",
                    name=sim,
                    line=dict(color=color, width=2),
                ),
                row=1,
                col=1,
            )

            # Cumulative cases
            cumulative = time_series.cumsum()
            fig.add_trace(
                go.Scatter(
                    x=time_series.index,
                    y=cumulative.values,
                    mode="lines",
                    name=sim,
                    line=dict(color=color, width=2),
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

            # Summary statistics
            summary_data.append(
                {
                    "simulation": sim,
                    "peak": time_series.max(),
                    "peak_time": time_series.idxmax(),
                    "total": time_series.sum(),
                    "duration": len(time_series),
                }
            )

        if not summary_data:
            return self._empty_figure("Nenhum dado encontrado para comparação")

        summary_df = pd.DataFrame(summary_data)

        # Peak comparison bar
        fig.add_trace(
            go.Bar(
                x=summary_df["simulation"],
                y=summary_df["peak"],
                marker_color=colors[: len(summary_df)],
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Duration comparison bar
        fig.add_trace(
            go.Bar(
                x=summary_df["simulation"],
                y=summary_df["duration"],
                marker_color=colors[: len(summary_df)],
                showlegend=False,
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            title=f"📈 Comparação de Simulações - {variable}",
            height=800,
            showlegend=True,
        )

        fig.update_xaxes(title_text="Tempo", row=1, col=1)
        fig.update_xaxes(title_text="Tempo", row=1, col=2)
        fig.update_yaxes(title_text=variable, row=1, col=1)
        fig.update_yaxes(title_text="Casos Acumulados", row=1, col=2)
        fig.update_yaxes(title_text="Pico", row=2, col=1)
        fig.update_yaxes(title_text="Duração", row=2, col=2)

        return fig

    # ==================== ANIMATED NETWORK ====================

    def create_animated_network(self, simulation: str, time: int) -> go.Figure:
        """
        Create network visualization showing epidemic state at specific time.

        Args:
            simulation: Name of the simulation.
            time: Time step to visualize.

        Returns:
            Plotly Figure with network visualization.
        """
        if not simulation:
            return self._empty_figure("Selecione uma simulação")

        G = self.data.get_graph()
        if G.order() == 0:
            return self._empty_figure("Arquivo de rede não encontrado")

        mapdf = self.data.read_map()
        if mapdf.empty:
            return self._empty_figure("Arquivo de mapa não encontrado")

        # Get simulation data at this time
        time_data = self.data.read_simulation(simulation, time=time)
        if time_data.empty:
            return self._empty_figure(f"Sem dados para tempo {time}")

        # Create coordinate lookup
        coords = {}
        for _, row in mapdf.iterrows():
            coords[row["name"]] = (row["lon"], row["lat"])

        # Create state lookup
        states = {}
        for _, row in time_data.iterrows():
            states[row["name"]] = {
                "Susceptible": row.get("Susceptible", 0),
                "Exposed": row.get("Exposed", 0),
                "Infectious": row.get("Infectious", 0),
                "Recovered": row.get("Recovered", 0),
            }

        # State colors
        state_colors = {
            "Susceptible": "blue",
            "Exposed": "orange",
            "Infectious": "red",
            "Recovered": "green",
        }

        def get_dominant_state(name):
            if name not in states:
                return "Susceptible"
            s = states[name]
            return max(s, key=s.get)

        # Prepare edge traces
        edge_lons = []
        edge_lats = []

        for edge in G.edges():
            source_data = G.nodes[edge[0]]
            target_data = G.nodes[edge[1]]

            source_name = source_data.get("name", str(edge[0]))
            target_name = target_data.get("name", str(edge[1]))

            if source_name in coords and target_name in coords:
                edge_lons.extend([coords[source_name][0], coords[target_name][0], None])
                edge_lats.extend([coords[source_name][1], coords[target_name][1], None])

        # Prepare node traces
        node_lons = []
        node_lats = []
        node_names = []
        node_colors = []
        node_sizes = []
        node_hover = []

        for node in G.nodes(data=True):
            node_name = node[1].get("name", str(node[0]))

            if node_name in coords:
                lon, lat = coords[node_name]
                state = get_dominant_state(node_name)

                node_lons.append(lon)
                node_lats.append(lat)
                node_names.append(node_name)
                node_colors.append(state_colors[state])

                # Size based on infectious count
                inf_count = states.get(node_name, {}).get("Infectious", 0)
                node_sizes.append(10 + min(inf_count / 10, 20))

                # Hover text
                if node_name in states:
                    s = states[node_name]
                    hover = (
                        f"<b>{node_name}</b><br>"
                        + f"S: {s['Susceptible']:.0f}<br>"
                        + f"E: {s['Exposed']:.0f}<br>"
                        + f"I: {s['Infectious']:.0f}<br>"
                        + f"R: {s['Recovered']:.0f}"
                    )
                else:
                    hover = f"<b>{node_name}</b><br>Sem dados"
                node_hover.append(hover)

        # Create figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(
            go.Scattergeo(
                lon=edge_lons,
                lat=edge_lats,
                mode="lines",
                line=dict(width=1, color="gray"),
                hoverinfo="none",
                showlegend=False,
            )
        )

        # Add nodes
        fig.add_trace(
            go.Scattergeo(
                lon=node_lons,
                lat=node_lats,
                mode="markers+text",
                text=node_names,
                textposition="top center",
                textfont=dict(size=8),
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=1, color="black"),
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=node_hover,
                showlegend=False,
            )
        )

        # Add legend for states
        for state, color in state_colors.items():
            fig.add_trace(
                go.Scattergeo(
                    lon=[None],
                    lat=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=state,
                    showlegend=True,
                )
            )

        # Apply zoom bounds
        bounds = self._get_map_bounds(mapdf)
        fig = self._apply_map_zoom(fig, bounds)

        fig.update_layout(
            title=f"🕸️ Rede Epidêmica - Tempo {time}",
            height=600,
            showlegend=True,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        )

        return fig

    # ==================== WAVEFRONT VISUALIZATION ====================

    def create_wavefront_visualization(self, simulation: str) -> go.Figure:
        """
        Visualize epidemic wavefront propagation.

        Args:
            simulation: Name of the simulation.

        Returns:
            Plotly Figure with wavefront analysis.
        """
        if not simulation:
            return self._empty_figure("Selecione uma simulação")

        all_data = self.data.read_simulation(simulation)
        if all_data.empty:
            return self._empty_figure("Dados não encontrados")

        mapdf = self.data.read_map()
        if mapdf.empty:
            return self._empty_figure("Arquivo de mapa não encontrado")

        # Find infection times
        infection_times = {}
        seed_location = None

        for locality in all_data["name"].unique():
            loc_data = all_data[all_data["name"] == locality]
            infected = (
                loc_data[loc_data["Infectious"] > 0]
                if "Infectious" in loc_data.columns
                else loc_data[loc_data["incidence"] > 0]
            )

            if not infected.empty:
                inf_time = infected["time"].min()
                infection_times[locality] = inf_time

                if seed_location is None or inf_time < infection_times.get(
                    seed_location, float("inf")
                ):
                    seed_location = locality

        if not infection_times or not seed_location:
            return self._empty_figure("Nenhuma infecção detectada")

        # Get seed coordinates
        seed_coords = mapdf[mapdf["name"] == seed_location]
        if seed_coords.empty:
            return self._empty_figure("Localização semente não encontrada")

        seed_lon = seed_coords["lon"].iloc[0]
        seed_lat = seed_coords["lat"].iloc[0]

        # Calculate distances from seed
        distances = []
        arrival_times = []
        names = []

        for locality, arr_time in infection_times.items():
            loc_coords = mapdf[mapdf["name"] == locality]
            if not loc_coords.empty:
                loc_lon = loc_coords["lon"].iloc[0]
                loc_lat = loc_coords["lat"].iloc[0]

                # Haversine distance (simplified)
                dist = (
                    np.sqrt((loc_lon - seed_lon) ** 2 + (loc_lat - seed_lat) ** 2) * 111
                )  # km approximation

                distances.append(dist)
                arrival_times.append(arr_time)
                names.append(locality)

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Distância vs Tempo de Chegada",
                "Velocidade de Dispersão",
                "Histograma de Tempos de Chegada",
                "Mapa de Isochrones",
            ),
        )

        # Scatter plot: Distance vs Arrival Time
        fig.add_trace(
            go.Scatter(
                x=arrival_times,
                y=distances,
                mode="markers+text",
                text=names,
                textposition="top center",
                textfont=dict(size=7),
                marker=dict(
                    size=10,
                    color=arrival_times,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Tempo", x=0.45),
                ),
                name="Localidades",
            ),
            row=1,
            col=1,
        )

        # Fit line for velocity
        if len(distances) > 1:
            z = np.polyfit(arrival_times, distances, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(arrival_times), max(arrival_times), 100)

            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=p(x_line),
                    mode="lines",
                    line=dict(color="red", dash="dash"),
                    name=f"Velocidade: {z[0]:.2f} km/tempo",
                ),
                row=1,
                col=1,
            )

        # Velocity over time (rolling)
        if len(arrival_times) > 5:
            sorted_data = sorted(zip(arrival_times, distances))
            times_sorted = [x[0] for x in sorted_data]
            dists_sorted = [x[1] for x in sorted_data]

            velocities = []
            times_vel = []
            for i in range(1, len(times_sorted)):
                dt = times_sorted[i] - times_sorted[i - 1]
                dd = dists_sorted[i] - dists_sorted[i - 1]
                if dt > 0:
                    velocities.append(dd / dt)
                    times_vel.append(times_sorted[i])

            fig.add_trace(
                go.Scatter(
                    x=times_vel,
                    y=velocities,
                    mode="lines",
                    line=dict(color="green"),
                    name="Velocidade",
                ),
                row=1,
                col=2,
            )

        # Histogram of arrival times
        fig.add_trace(
            go.Histogram(
                x=arrival_times, nbinsx=20, marker_color="purple", name="Distribuição"
            ),
            row=2,
            col=1,
        )

        # Isochrone map
        for locality, arr_time in infection_times.items():
            loc_coords = mapdf[mapdf["name"] == locality]
            if not loc_coords.empty:
                loc_lon = loc_coords["lon"].iloc[0]
                loc_lat = loc_coords["lat"].iloc[0]

                fig.add_trace(
                    go.Scatter(
                        x=[loc_lon],
                        y=[loc_lat],
                        mode="markers",
                        marker=dict(size=8, color=arr_time, colorscale="Viridis"),
                        showlegend=False,
                    ),
                    row=2,
                    col=2,
                )

        fig.update_layout(
            title="🌊 Análise de Wavefront Epidêmico", height=800, showlegend=True
        )

        fig.update_xaxes(title_text="Tempo de Chegada", row=1, col=1)
        fig.update_yaxes(title_text="Distância do Seed (km)", row=1, col=1)
        fig.update_xaxes(title_text="Tempo", row=1, col=2)
        fig.update_yaxes(title_text="Velocidade (km/tempo)", row=1, col=2)
        fig.update_xaxes(title_text="Tempo de Chegada", row=2, col=1)
        fig.update_yaxes(title_text="Frequência", row=2, col=1)
        fig.update_xaxes(title_text="Longitude", row=2, col=2)
        fig.update_yaxes(title_text="Latitude", row=2, col=2)

        return fig

    # ==================== EXISTING VISUALIZATIONS (IMPROVED) ====================

    def create_final_map(self, simulation: str) -> go.Figure:
        """Create final state map with bar chart."""
        if not simulation:
            return self._empty_figure("Selecione uma simulação")

        mapdf = self.data.read_map()
        max_time = self.data.get_max_time(simulation)
        time_data = self.data.read_simulation(simulation, time=max_time)

        if mapdf.empty or time_data.empty:
            return self._empty_figure("Dados não encontrados")

        # Merge data
        merged = mapdf.merge(time_data, on="name", how="left")

        # Get top 15 locations
        var = "totalcases" if "totalcases" in merged.columns else "Infectious"
        top15 = merged.nlargest(15, var)

        # Create subplot
        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.3, 0.7],
            specs=[[{"type": "bar"}, {"type": "geo"}]],
            subplot_titles=("🏆 Top 15 Localidades", "🗺️ Mapa Final"),
        )

        # Bar chart
        fig.add_trace(
            go.Bar(
                x=top15[var],
                y=top15["name"],
                orientation="h",
                marker=dict(color=top15[var], colorscale="YlOrRd"),
            ),
            row=1,
            col=1,
        )

        # Choropleth
        fig.add_trace(
            go.Choropleth(
                geojson=merged.__geo_interface__,
                locations=merged.index,
                z=merged[var],
                colorscale="YlOrRd",
                colorbar=dict(title=var, x=1.02),
            ),
            row=1,
            col=2,
        )

        # Calculate zoom bounds
        bounds = self._get_map_bounds(mapdf)

        fig.update_geos(
            projection_type="natural earth",
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            center=bounds["center"],
            lataxis_range=bounds["lataxis_range"],
            lonaxis_range=bounds["lonaxis_range"],
            projection_scale=bounds["projection_scale"],
            row=1,
            col=2,
        )

        fig.update_layout(
            title="🗺️ Estado Final da Epidemia", height=600, showlegend=False
        )

        return fig

    def create_time_series(self, simulation: str, locality: str) -> go.Figure:
        """Create time series plots for a locality."""
        if not simulation or not locality:
            return self._empty_figure("Selecione simulação e localidade")

        df_loc = self.data.read_simulation(simulation, locality=locality)
        if df_loc.empty:
            return self._empty_figure("Dados não encontrados")

        variables = [
            c
            for c in df_loc.columns
            if c not in ["name", "time", "geocode", "lat", "longit"]
        ]

        n_vars = len(variables)
        n_cols = 2
        n_rows = (n_vars + n_cols - 1) // n_cols

        fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=variables)

        for i, var in enumerate(variables):
            row = i // n_cols + 1
            col = i % n_cols + 1

            fig.add_trace(
                go.Scatter(
                    x=df_loc["time"],
                    y=df_loc[var],
                    mode="lines",
                    line=dict(shape="hv"),
                    showlegend=False,
                ),
                row=row,
                col=col,
            )

        fig.update_layout(
            title=f"📈 Séries Temporais - {locality}", height=300 * n_rows
        )

        return fig

    def create_simulation_table(self, simulation: str) -> pd.DataFrame:
        """Create summary table for simulation."""
        if not simulation:
            return pd.DataFrame()

        max_time = self.data.get_max_time(simulation)
        df = self.data.read_simulation(simulation, time=max_time)

        if df.empty:
            return pd.DataFrame()

        display_cols = ["name", "geocode"]
        epi_vars = [
            c
            for c in df.columns
            if c not in ["name", "time", "geocode", "lat", "longit"]
        ]
        display_cols.extend(epi_vars)

        table = df[display_cols].copy()

        # Rename columns
        rename_map = {
            "name": "Localidade",
            "geocode": "Código",
            "incidence": "Incidência",
            "Susceptible": "Suscetíveis",
            "Exposed": "Expostos",
            "Infectious": "Infecciosos",
            "Recovered": "Recuperados",
            "totalcases": "Casos Totais",
        }
        table = table.rename(
            columns={k: v for k, v in rename_map.items() if k in table.columns}
        )

        # Round numeric columns
        numeric_cols = table.select_dtypes(include=[np.number]).columns
        table[numeric_cols] = table[numeric_cols].round(2)

        return table

    def _empty_figure(self, message: str = "Sem dados") -> go.Figure:
        """Create an empty figure with a message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16),
        )
        fig.update_layout(height=400)
        return fig


def create_dashboard(pth: str) -> gr.Blocks:
    """
    Create the main Gradio dashboard.

    Args:
        pth: Path to the model data directory.

    Returns:
        Gradio Blocks interface.
    """
    data = SimulationData(pth)
    viz = Visualizations(data)

    with gr.Blocks(title="Epigrass Dashboard", theme=gr.themes.Soft()) as demo:
        gr.HTML(f"""
        <div style="display: flex; align-items: center; justify-content: center;">
            <img src="file/{ICON_PATH}" width="50" height="50">
            <h1 style="margin-left: 20px;">Epigrass Dashboard</h1>
        </div>
        """)
        gr.Markdown(
            "### Dashboard Interativo para Visualização de Simulações Epidemiológicas"
        )

        # State for multi-select comparison
        selected_sims = gr.State([])

        with gr.Row():
            # Control Panel
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("## 🎛️ Controles")

                model_path = gr.Textbox(
                    value=pth, label="📁 Caminho do Modelo", interactive=True
                )

                refresh_btn = gr.Button("🔄 Atualizar Dados", variant="primary")

                simulation = gr.Dropdown(
                    label="🎯 Simulação", choices=[], value=None, interactive=True
                )

                localities = gr.Dropdown(
                    label="📍 Localidades", choices=[], value=None, interactive=True
                )

                time_slider = gr.Slider(
                    minimum=1,
                    maximum=300,
                    value=1,
                    step=1,
                    label="⏰ Tempo",
                    interactive=True,
                )

                # Variable selector
                variable = gr.Dropdown(
                    label="📊 Variável",
                    choices=[
                        "Infectious",
                        "Exposed",
                        "Recovered",
                        "Susceptible",
                        "incidence",
                        "totalcases",
                    ],
                    value="Infectious",
                    interactive=True,
                )

                # Colorscale selector
                colorscale = gr.Dropdown(
                    label="🎨 Escala de Cores",
                    choices=[
                        "YlOrRd",
                        "Viridis",
                        "Plasma",
                        "Inferno",
                        "Blues",
                        "Greens",
                    ],
                    value="YlOrRd",
                    interactive=True,
                )

                gr.Markdown("---")
                meta_info = gr.Markdown("## ℹ️ Informações da Simulação")

            # Visualization Tabs
            with gr.Column(scale=3):
                with gr.Tabs():
                    # Tab 1: Animated Map
                    with gr.Tab("🎬 Animação"):
                        with gr.Row():
                            play_btn = gr.Button(
                                "▶️ Auto Play", size="sm", variant="secondary"
                            )
                            stop_btn = gr.Button("⏹️ Stop", size="sm")
                        animated_map = gr.Plot(label="Mapa Animado")
                        gr.Markdown(
                            "Use o slider **⏰ Tempo** no painel esquerdo para navegar ou clique em Auto Play."
                        )

                    # Tab 2: Spread Tree
                    with gr.Tab("🌳 Árvore de Spread"):
                        spread_tree = gr.Plot(label="Árvore de Transmissão")
                        gr.Markdown(
                            "Visualização dos locais infectados até o tempo selecionado no slider."
                        )

                    # Tab 3: R(t)
                    with gr.Tab("📊 R(t)"):
                        rt_plot = gr.Plot(label="Número de Reprodução Efetivo")
                        rt_table = gr.Dataframe(
                            label="Dados de R(t)", interactive=False
                        )
                        gr.Markdown(
                            """
                        **Interpretação:**
                        - R(t) > 1: Epidemia em crescimento
                        - R(t) = 1: Epidemia estável
                        - R(t) < 1: Epidemia em declínio
                        """
                        )

                    # Tab 4: Comparison
                    with gr.Tab("📈 Comparação"):
                        sim_multiselect = gr.Dropdown(
                            label="Selecione Simulações (múltiplas)",
                            choices=[],
                            multiselect=True,
                            interactive=True,
                        )
                        compare_btn = gr.Button(
                            "Comparar Simulações", variant="secondary"
                        )
                        comparison_plot = gr.Plot(label="Comparação")
                        gr.Markdown("Selecione 2 ou mais simulações para comparar.")

                    # Tab 5: Animated Network
                    with gr.Tab("🕸️ Rede Dinâmica"):
                        network_plot = gr.Plot(label="Rede Epidêmica")
                        gr.Markdown(
                            """
                        **Legenda de Cores:**
                        - 🔵 Azul: Suscetíveis
                        - 🟠 Laranja: Expostos
                        - 🔴 Vermelho: Infecciosos
                        - 🟢 Verde: Recuperados
                        
                        Use o slider **⏰ Tempo** no painel esquerdo para navegar.
                        """
                        )

                    # Tab 6: Wavefront
                    with gr.Tab("🌊 Wavefront"):
                        wavefront_plot = gr.Plot(label="Análise de Wavefront")
                        gr.Markdown(
                            "Análise da velocidade e direção de propagação da epidemia."
                        )

                    # Tab 7: Final State
                    with gr.Tab("🗺️ Estado Final"):
                        final_map = gr.Plot(label="Estado Final")
                        simulation_table = gr.Dataframe(
                            label="📊 Dados da Simulação",
                            interactive=False,
                            wrap=True,
                        )

                    # Tab 8: Time Series
                    with gr.Tab("📉 Séries Temporais"):
                        time_series = gr.Plot(label="Séries Temporais")

        # ==================== EVENT HANDLERS ====================

        def refresh_all(model_path_val):
            data.model_path = model_path_val
            data.clear_cache()

            sims = data.get_simulations()
            locs = data.get_localities(sims[-1]) if sims else []

            return (
                gr.Dropdown(choices=sims, value=sims[-1] if sims else None),
                gr.Dropdown(choices=locs, value=locs[0] if locs else None),
                gr.Dropdown(choices=sims, value=[]),
                "",
            )

        def update_localities_fn(sim):
            if not sim:
                return gr.Dropdown(choices=[], value=None)
            locs = data.get_localities(sim)
            return gr.Dropdown(choices=locs, value=locs[0] if locs else None)

        def update_time_bounds_fn(sim):
            if not sim:
                return gr.Slider(minimum=1, maximum=300, value=1)
            max_t = data.get_max_time(sim)
            return gr.Slider(minimum=1, maximum=max(max_t, 1), value=1)

        def get_meta_fn(sim):
            if not sim:
                return ""
            meta = data.get_meta(sim)
            if meta.empty:
                return "## Nenhuma informação disponível"
            return f"""
            ## Informações da Simulação
            - **Tipo de Modelo:** {meta.get("epidemiological_model$modtype", ["N/A"])[0] if len(meta) > 0 else "N/A"}
            - **Seed:** {meta.get("epidemic_events$seed", ["N/A"])[0] if len(meta) > 0 else "N/A"}
            """

        # Refresh button
        refresh_btn.click(
            fn=refresh_all,
            inputs=[model_path],
            outputs=[simulation, localities, sim_multiselect, meta_info],
        )

        # Load on startup
        demo.load(
            fn=refresh_all,
            inputs=[model_path],
            outputs=[simulation, localities, sim_multiselect, meta_info],
        )

        # Update localities when simulation changes
        simulation.change(
            fn=update_localities_fn, inputs=[simulation], outputs=[localities]
        )

        # Update main time slider when simulation changes
        simulation.change(
            fn=update_time_bounds_fn,
            inputs=[simulation],
            outputs=[time_slider],
        )

        # Update meta info
        simulation.change(fn=get_meta_fn, inputs=[simulation], outputs=[meta_info])

        # ==================== ANIMATED MAP ====================
        # Update when simulation, time, variable, or colorscale changes
        for inp in [simulation, time_slider, variable, colorscale]:
            inp.change(
                fn=viz.create_map_at_time,
                inputs=[simulation, time_slider, variable, colorscale],
                outputs=[animated_map],
            )

        # ==================== SPREAD TREE ====================
        # Update when simulation or time changes
        for inp in [simulation, time_slider]:
            inp.change(
                fn=viz.create_spread_tree_at_time,
                inputs=[simulation, time_slider],
                outputs=[spread_tree],
            )

        # ==================== R(t) ====================
        simulation.change(
            fn=viz.calculate_rt, inputs=[simulation], outputs=[rt_plot, rt_table]
        )

        # ==================== COMPARISON ====================
        def update_comparison(sim):
            return gr.Dropdown(choices=data.get_simulations())

        simulation.change(
            fn=update_comparison, inputs=[simulation], outputs=[sim_multiselect]
        )

        compare_btn.click(
            fn=viz.compare_simulations,
            inputs=[sim_multiselect, variable],
            outputs=[comparison_plot],
        )

        # ==================== NETWORK ====================
        # Uses main time slider
        for inp in [simulation, time_slider]:
            inp.change(
                fn=viz.create_animated_network,
                inputs=[simulation, time_slider],
                outputs=[network_plot],
            )

        # ==================== WAVEFRONT ====================
        simulation.change(
            fn=viz.create_wavefront_visualization,
            inputs=[simulation],
            outputs=[wavefront_plot],
        )

        # ==================== FINAL MAP ====================
        simulation.change(
            fn=viz.create_final_map, inputs=[simulation], outputs=[final_map]
        )

        # ==================== TIME SERIES ====================
        for inp in [simulation, localities]:
            inp.change(
                fn=viz.create_time_series,
                inputs=[simulation, localities],
                outputs=[time_series],
            )

        # ==================== TABLE ====================
        simulation.change(
            fn=viz.create_simulation_table,
            inputs=[simulation],
            outputs=[simulation_table],
        )

        # ==================== AUTO PLAY FUNCTIONALITY ====================
        # Python-based auto-play that increments the main time slider

        def get_new_time(current_time, max_time):
            """Get next time step."""
            new_time = current_time + 1
            if new_time > max_time:
                new_time = 1
            return new_time

        # Animation state
        animation_state = gr.State(False)

        def toggle_animation(is_playing):
            """Toggle animation state."""
            return not is_playing

        # Use timer for animation (Gradio 4.x+)
        try:
            anim_timer = gr.Timer(0.5, active=False)

            def tick_anim(current, sim):
                if not sim:
                    return current
                max_t = data.get_max_time(sim)
                return get_new_time(current, max_t)

            anim_timer.tick(
                fn=tick_anim,
                inputs=[time_slider, simulation],
                outputs=[time_slider],
            )

            play_btn.click(
                fn=lambda: gr.Timer(active=True),
                inputs=None,
                outputs=[anim_timer],
            )

            stop_btn.click(
                fn=lambda: gr.Timer(active=False),
                inputs=None,
                outputs=[anim_timer],
            )

        except AttributeError:
            # Fallback for older Gradio versions - manual stepping
            play_btn.click(
                fn=lambda t, sim: get_new_time(
                    t, data.get_max_time(sim) if sim else 300
                ),
                inputs=[time_slider, simulation],
                outputs=[time_slider],
            )

            stop_btn.click(
                fn=lambda t: t,
                inputs=[time_slider],
                outputs=[time_slider],
            )

    return demo


def show(pth: str):
    """
    Launch the dashboard.

    Args:
        pth: Path to the model data directory.
    """
    demo = create_dashboard(pth)
    demo.launch(
        server_port=5006, share=False, inbrowser=True, allowed_paths=[ICON_PATH, pth]
    )


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    show(path)
