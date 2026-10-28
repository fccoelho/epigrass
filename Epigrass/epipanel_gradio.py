import pandas as pd
import numpy as np
import networkx as NX
import geopandas as gpd
import os
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from functools import lru_cache 
import glob
from sqlalchemy import create_engine, text
import json

# Ícone codificado
enc_icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA3ElEQVRYhe2WWQ7DIAxEH1XvVR+dmzkfVSJngWIW0VYZKV8EZgzDmABARFkhBDxomQs8z+tFvfoxBUG8nHkBgnircAlOwlt5LzxmkN4CbgFfJeB950vSrDHxUihOwtbEKxaQScKxQTUrCU87YJE5jnEeOJJfkdkxNUcTaDCnrbb0OCJRFbavmtySer3QVcAMI/5GEmaN1utNqAIhpjwghm8/Lsg2twbTd8CsU2/AlrnTTbhDbSX/swPgr2ZIeHl6QStX8tqsi79MBqxXMNcpu+LY7Ub0i48VdOv3CSxJ9X3LgJP02QAAAABJRU5ErkJggg=='
with open('egicon.png', 'wb') as f:
    f.write(base64.b64decode(enc_icon))


@lru_cache(maxsize=1)
def get_engine(db_path):
    """
    Create a cached SQLAlchemy engine
    """
    return create_engine(f'sqlite:///{db_path}?check_same_thread=False')


@lru_cache(maxsize=10)
def get_sims(fname):
    """
    Get list of simulations available on SQLite database
    :param fname: Database file path
    :return: List of tables. list of str
    """
    full_path = os.path.join(fname, 'Epigrass.sqlite')
    if os.path.exists(full_path):
        engine = get_engine(full_path)
        with engine.connect() as con:
            sims = con.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"))
            sim_names = [s[0] for s in sims if not (s[0].endswith('_meta') or s[0].endswith('e'))]
        return sim_names
    else:
        print(f'==> File {full_path} not found')
        get_sims.cache_clear()
        return []


def get_graph(pth):
    full_path = os.path.join(os.path.abspath(pth), 'network.gml')
    if os.path.exists(full_path):
        G = NX.read_gml(full_path, destringizer=int)
    else:
        G = NX.MultiDiGraph()
    return G


@lru_cache(maxsize=10)
def get_meta_table(fname, simname):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if os.path.exists(full_path):
        mname = simname + '_meta'
        engine = get_engine(full_path)
        with engine.connect() as con:
            df = pd.read_sql_query(f"select * from {mname}", con)
    else:
        df = pd.DataFrame()
        get_meta_table.cache_clear()
    return df


@lru_cache(maxsize=20)
def read_simulation(fname, simulation_name, locality=None, time=None, columns=None):
    """
    Read simulation data with optional filtering for locality and time
    """
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        read_simulation.cache_clear()
        return pd.DataFrame()

    engine = get_engine(full_path)
    
    col_str = "*"
    if columns:
        col_str = ", ".join(columns)
        
    query = f"select {col_str} from {simulation_name}"
    conditions = []
    if locality:
        conditions.append(f"name='{locality}'")
    if time is not None:
        conditions.append(f"time={time}")
        
    if conditions:
        query += " where " + " and ".join(conditions)

    with engine.connect() as con:
        simdf = pd.read_sql_query(query, con)
    
    simdf.fillna(0, inplace=True)
    return simdf


@lru_cache(maxsize=10)
def get_localities(fname, simulation_name) -> list:
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        get_localities.cache_clear()
        return []
    engine = get_engine(full_path)
    with engine.connect() as con:
        locs = pd.read_sql_query(f'select distinct name from {simulation_name}', con)
    localities = [l[0] for l in locs.values]
    return localities


@lru_cache(maxsize=20)
def get_max_time(fname, simulation_name):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        return 0
    engine = get_engine(full_path)
    with engine.connect() as con:
        res = con.execute(text(f"SELECT max(time) FROM {simulation_name}"))
        max_t = res.fetchone()[0]
    return max_t if max_t is not None else 0


@lru_cache(maxsize=20)
def last_data_time(fname, simulation_name):
    """
    Last time step for which the majority of sites still have
    epidemiological data. Models that go extinct keep writing rows with
    NULL values until the configured number of steps, so max(time) alone
    is misleading.
    """
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        return None
    engine = get_engine(full_path)
    with engine.connect() as con:
        cols = [r[1] for r in con.execute(
            text(f'PRAGMA table_info("{simulation_name}")'))]
    epi = [c for c in cols
           if c not in ('geocode', 'time', 'name', 'lat', 'longit')]
    if not epi:
        return None
    sentinel = epi[0]
    with engine.connect() as con:
        counts = con.execute(text(
            f'SELECT "time", COUNT("{sentinel}") FROM "{simulation_name}" '
            f'GROUP BY "time" ORDER BY "time"')).fetchall()
        if not counts:
            return None
        n_sites = con.execute(
            text(f'SELECT COUNT(*) FROM "{simulation_name}" '
                 f'WHERE "time" = (SELECT MIN("time") FROM "{simulation_name}")')
        ).fetchone()[0]
    threshold = max(1, n_sites // 2)
    good = [t for (t, c) in counts if c >= threshold]
    if good:
        return int(good[-1])
    any_data = [t for (t, c) in counts if c > 0]
    return int(any_data[-1]) if any_data else None


@lru_cache(maxsize=5)
def read_map(fname):
    if os.path.exists(fname):
        gdf = gpd.read_file(fname)
        if hasattr(gdf, 'geometry') and hasattr(gdf.geometry, 'centroid'):
            gdf['lat'] = gdf.geometry.centroid.y
            gdf['lon'] = gdf.geometry.centroid.x
        return gdf
    else:
        read_map.cache_clear()
        return gpd.GeoDataFrame()


#: Pseudo map entry used when the model has no shapefile (no Data.gpkg)
NO_MAP_SENTINEL = "Sites (lat/lon) — sem Data.gpkg"


@lru_cache(maxsize=10)
def get_sites_frame(model_path, simulation_run):
    """
    Final-time site table (name, lat, longit + epi variables) read from the
    simulation SQLite database. Used as a fallback to draw maps when the model
    has no shapefile and Data.gpkg was never created.
    """
    if not simulation_run:
        return pd.DataFrame()
    df = read_simulation(model_path, simulation_run)
    if df.empty or not {'lat', 'longit'}.issubset(df.columns):
        return pd.DataFrame()
    t = last_data_time(model_path, simulation_run)
    max_t = t if t is not None else int(df['time'].max())
    return df[df['time'] == max_t].copy()


def pick_main_var(columns):
    """Choose the epidemiological variable to display on fallback maps."""
    for cand in ('totalcases', 'Infectious', 'incidence', 'Incidência',
                 'Arrivals'):
        if cand in columns:
            return cand
    epi = [c for c in columns
           if c not in ('name', 'time', 'geocode', 'lat', 'longit')]
    return epi[0] if epi else None


def _finite(values):
    """Clamp inf and NaN to the finite range (models can diverge)."""
    values = np.asarray(values, dtype=float)
    fin = values[np.isfinite(values)]
    if fin.size:
        values = np.clip(values, fin.min(), fin.max())
    return np.nan_to_num(values, nan=0.0)


def _bubble_sizes(values, lo=5, hi=30):
    """Scale values into marker sizes within [lo, hi]."""
    values = _finite(values)
    vmin, vmax = values.min(), values.max()
    if vmax <= vmin:
        return np.full(len(values), (lo + hi) / 2)
    return lo + (hi - lo) * (values - vmin) / (vmax - vmin)


def _geo_bounds(lat, lon, pad_frac=0.2, min_pad=0.5):
    """Compute center/ranges for a geo layout from coordinate arrays."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    lat_pad = max((lat.max() - lat.min()) * pad_frac, min_pad)
    lon_pad = max((lon.max() - lon.min()) * pad_frac, min_pad)
    return dict(
        center=dict(lat=float(lat.mean()), lon=float(lon.mean())),
        lataxis_range=[float(lat.min() - lat_pad), float(lat.max() + lat_pad)],
        lonaxis_range=[float(lon.min() - lon_pad), float(lon.max() + lon_pad)],
    )


@lru_cache(maxsize=5)
def get_map_geojson(fname):
    gdf = read_map(fname)
    if not gdf.empty:
        return gdf.__geo_interface__
    return None


def get_subgraph(G, node):
    """
    return subgraph containing `node` and its direct neighbors
    :param G: full graph
    :param node: node defining the subgraph
    """
    nodes = [node]
    nodes.extend([int(n) for n in G.neighbors(node)])
    H = G.subgraph(nodes).copy()
    return H


def refresh_data(model_path):
    """Refresh all cached data"""
    get_sims.cache_clear()
    get_localities.cache_clear()
    read_map.cache_clear()
    read_simulation.cache_clear()
    get_meta_table.cache_clear()
    
    # Get updated data
    maps = glob.glob(os.path.join(model_path, '*.gpkg'))
    if not maps:
        # Model without a shapefile: no Data.gpkg exists. Offer the site
        # coordinates from the simulation database so map tabs still render.
        maps = [NO_MAP_SENTINEL]
    sims = get_sims(model_path)
    
    map_choices = maps if maps else []
    sim_choices = sims if sims else []
    
    map_value = maps[0] if maps else None
    sim_value = sims[-1] if sims else None
    
    return (
        gr.Dropdown(choices=map_choices, value=map_value),
        gr.Dropdown(choices=sim_choices, value=sim_value),
        gr.Dropdown(choices=[], value=None),
        ""
    )


def update_localities(model_path, simulation_run):
    """Update localities dropdown based on selected simulation"""
    if not simulation_run:
        return gr.Dropdown(choices=[], value=None)
    
    locs = get_localities(model_path, simulation_run)
    return gr.Dropdown(choices=locs, value=locs[0] if locs else None)


def get_meta_info(model_path, simulation_run):
    """Get simulation metadata as markdown"""
    if not simulation_run:
        return ""
    
    df = get_meta_table(model_path, simulation_run)
    if len(df) > 0:
        return f"""
## Informações da Simulação
### Arquivo de Mapa
{df['the_world$shapefile'].iloc[0].split(',')[0].strip("['")}
### Arquivo de Sites
{df['the_world$sites'].iloc[0]}
### Tipo de Modelo
{df['epidemiological_model$modtype'].iloc[0]}
### Eventos Epidêmicos
Seed: {df['epidemic_events$seed'].iloc[0]}
"""
    else:
        return "## Nenhuma informação de metadados disponível"


def create_simulation_table(model_path, simulation_run):
    """Create a paginated table with simulation data"""
    if not simulation_run:
        return pd.DataFrame()
    
    max_time = last_data_time(model_path, simulation_run)
    if max_time is None:
        max_time = get_max_time(model_path, simulation_run)
    df = read_simulation(model_path, simulation_run, time=max_time)
    if df.empty:
        return pd.DataFrame()
    
    # Get final time step data for summary
    max_time = df['time'].max()
    final_data = df[df['time'] == max_time].copy()
    
    # Select relevant columns for the table
    display_columns = ['name', 'geocode']
    

    
    # Add epidemiological variables
    epi_vars = [c for c in df.columns if c not in ['name', 'time','geocode', 'lat', 'longit']]
    display_columns.extend(epi_vars)
    
    # Filter and format the data
    table_data = final_data[display_columns].copy()
    
    # Round numeric columns to 2 decimal places
    numeric_columns = table_data.select_dtypes(include=[np.number]).columns
    table_data[numeric_columns] = table_data[numeric_columns].round(2)
    
    # Rename columns for better display
    column_mapping = {
        'name': 'Localidade',
        'geocode': 'Código',
        'incidence': 'Incidência',
        'arrivals': 'Chegadas',
        'Susceptible': 'Suscetíveis',
        'Exposed': 'Expostos',
        'Infectious': 'Infecciosos',
        'Recovered': 'Recuperados',
        'totalcases': 'Casos Totais',
    }
    
    # Apply column mapping where columns exist
    existing_mapping = {k: v for k, v in column_mapping.items() if k in table_data.columns}
    table_data = table_data.rename(columns=existing_mapping)
    
    return table_data


@lru_cache(maxsize=10)
def zoom_to_location(model_path, location_name):
    """Create a zoomed version of the map focused on a specific location"""
    if not location_name:
        return go.Figure().add_annotation(
            text="Selecione uma localidade para focar no mapa",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16)
        )
    
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    if mapdf.empty:
        # No Data.gpkg (model without shapefile): zoom on site coordinates
        sims = get_sims(model_path)
        sites = get_sites_frame(model_path, sims[-1] if sims else None)
        if sites.empty:
            return go.Figure()
        var = pick_main_var(sites.columns)
        selected = sites[sites['name'] == location_name]
        if selected.empty:
            return go.Figure().add_annotation(
                text=f"Localidade '{location_name}' não encontrada",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=True, font=dict(size=16)
            )
        sel_lat = float(selected['lat'].iloc[0])
        sel_lon = float(selected['longit'].iloc[0])
        fig = go.Figure()
        if var:
            z = _finite(sites[var])
            fig.add_trace(go.Scattergeo(
                lon=sites['longit'], lat=sites['lat'],
                mode='markers',
                marker=dict(
                    size=_bubble_sizes(sites[var]),
                    color=z, colorscale='YlOrRd',
                    colorbar=dict(title=var, x=1.02),
                    line=dict(width=0.5, color='gray'),
                ),
                text=sites['name'],
                hovertemplate='<b>%{text}</b><br>' + var + ': %{marker.color}<extra></extra>',
                showlegend=False,
            ))
        fig.add_trace(go.Scattergeo(
            lon=[sel_lon], lat=[sel_lat],
            mode='markers',
            marker=dict(size=22, color='red', symbol='star',
                        line=dict(width=2, color='white')),
            text=[location_name],
            hovertemplate='<b>🎯 %{text}</b><br>Localidade Selecionada<extra></extra>',
            showlegend=False,
        ))
        zoom = 3.0
        fig.update_geos(
            projection_type="natural earth",
            showland=True, landcolor="lightgray",
            showocean=True, oceancolor="lightblue",
            center=dict(lat=sel_lat, lon=sel_lon),
            lataxis_range=[sel_lat - zoom, sel_lat + zoom],
            lonaxis_range=[sel_lon - zoom, sel_lon + zoom],
        )
        fig.update_layout(
            title=f"🎯 Mapa Focado em: {location_name} (coordenadas dos sites)",
            height=600, showlegend=False,
        )
        return fig

    # Find the selected location
    selected_location = mapdf[mapdf['name'] == location_name]
    if selected_location.empty:
        return go.Figure().add_annotation(
            text=f"Localidade '{location_name}' não encontrada",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=True, font=dict(size=16)
        )
    
    # selected_location already has lat/lon from read_map
    selected_lat = selected_location['lat'].iloc[0]
    selected_lon = selected_location['lon'].iloc[0]
    
    # Create focused map with both choropleth and highlighted location
    fig = go.Figure()
    
    # Get cached GeoJSON
    mapdf_json = get_map_geojson(os.path.join(model_path, 'Data.gpkg'))
    
    # Add choropleth trace
    fig.add_trace(
        go.Choropleth(
            geojson=mapdf_json,
            locations=mapdf.index,
            z=mapdf['totalcases'],
            colorscale='YlOrRd',
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Casos Totais: %{z}<br>' +
                         'Prevalência: %{customdata[1]:.4f}<br>' +
                         'Chegadas: %{customdata[2]}<extra></extra>',
            customdata=np.column_stack((mapdf['name'], mapdf['prevalence'], mapdf['arrivals'])),
            colorbar=dict(
                title="Casos Totais",
                x=1.02
            ),
            showlegend=False
        )
    )
    
    # Add a marker to highlight the selected location
    fig.add_trace(
        go.Scattergeo(
            lon=[selected_lon],
            lat=[selected_lat],
            mode='markers',
            marker=dict(
                size=20,
                color='red',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=[location_name],
            hovertemplate='<b>🎯 %{text}</b><br>Localidade Selecionada<extra></extra>',
            showlegend=False
        )
    )
    
    # Calculate zoom bounds around selected location
    zoom_range = 1.0  # degrees - increased for better visibility
    
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue",
        showlakes=True,
        lakecolor="lightblue",
        center=dict(lat=selected_lat, lon=selected_lon),
        lataxis_range=[selected_lat - zoom_range, selected_lat + zoom_range],
        lonaxis_range=[selected_lon - zoom_range, selected_lon + zoom_range],
        projection_scale=2  # Moderate zoom level
    )
    
    fig.update_layout(
        title=f"🎯 Mapa Focado em: {location_name}",
        height=600,
        showlegend=False,
        annotations=[
            dict(
                text=f"📍 Casos Totais: {int(selected_location['totalcases'].iloc[0])}<br>"
                     f"📊 Prevalência: {selected_location['prevalence'].iloc[0]:.4f}",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.02, y=0.02,
                xanchor="left", yanchor="bottom",
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="red",
                borderwidth=2,
                font=dict(size=12)
            )
        ]
    )
    
    return fig


@lru_cache(maxsize=5)
def create_final_map(model_path, map_selector, simulation_run):
    """Create final state map visualization with interactive bar chart and zoomable choropleth"""
    if not map_selector or not simulation_run:
        return go.Figure()
    
    map_path = os.path.join(model_path, 'Data.gpkg')
    mapdf = read_map(map_path)
    if mapdf.empty:
        # No Data.gpkg (model without shapefile): bubble map from site coords
        sites = get_sites_frame(model_path, simulation_run)
        if sites.empty:
            return go.Figure().add_annotation(
                text="Sem Data.gpkg nem coordenadas (lat/longit) nos dados da simulação",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14)
            )
        var = pick_main_var(sites.columns)
        top = sites.assign(_z=_finite(sites[var]) if var else 0)
        top = top.sort_values('_z', ascending=False).iloc[:15]
        
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.3, 0.7],
            specs=[[{"type": "bar"}, {"type": "geo"}]],
            subplot_titles=("🏆 Top 15 Localidades",
                            f"🗺️ Mapa de Sites ({var})")
        )
        fig.add_trace(
            go.Bar(
                x=top['_z'],
                y=top['name'],
                orientation='h',
                marker=dict(color=top['_z'],
                            colorscale='YlOrRd', showscale=False),
                hovertemplate='<b>%{y}</b><br>' + (var or 'valor') +
                              ': %{x:,.0f}<extra></extra>',
                showlegend=False
            ),
            row=1, col=1
        )
        z = _finite(sites[var]) if var else None
        fig.add_trace(
            go.Scattergeo(
                lon=sites['longit'], lat=sites['lat'],
                mode='markers',
                marker=dict(
                    size=_bubble_sizes(sites[var]) if var else 8,
                    color=z if var else 'darkorange',
                    colorscale='YlOrRd',
                    colorbar=dict(title=var or '', x=1.02, len=0.8),
                    line=dict(width=0.5, color='gray'),
                ),
                text=sites['name'],
                hovertemplate='<b>%{text}</b><br>' +
                              (var or 'valor') + ': %{marker.color:,.0f}<extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )
        fig.update_geos(
            projection_type="natural earth",
            showland=True, landcolor="lightgray",
            showocean=True, oceancolor="lightblue",
            **_geo_bounds(sites['lat'], sites['longit']),
            row=1, col=2
        )
        fig.update_layout(
            title="Estado Final da Epidemia (coordenadas dos sites)",
            height=600, showlegend=False
        )
        return fig
    
    # Get top 15 locations by total cases
    map10 = mapdf.sort_values('totalcases', ascending=False).iloc[:15]
    
    # mapdf already has lat/lon from read_map
    
    # Create subplot with bar chart and choropleth map
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.3, 0.7],
        specs=[[{"type": "bar"}, {"type": "geo"}]],
        subplot_titles=("🏆 Top 15 Localidades", "🗺️ Mapa Coroplético")
    )
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=map10['totalcases'],
            y=map10['name'],
            orientation='h',
            marker=dict(
                color=map10['totalcases'],
                colorscale='YlOrRd',
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>Casos Totais: %{x:,.0f}<br><i>Use o seletor à direita para focar</i><extra></extra>',
            name="Top Localidades",
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Create choropleth map using the geometry data
    if hasattr(mapdf, 'geometry') and not mapdf.empty:
        # Get cached GeoJSON
        mapdf_json = get_map_geojson(map_path)
        
        # Add choropleth trace
        fig.add_trace(
            go.Choropleth(
                geojson=mapdf_json,
                locations=mapdf.index,
                z=mapdf['totalcases'],
                colorscale='YlOrRd',
                hovertemplate='<b>%{customdata[0]}</b><br>' +
                             'Casos Totais: %{z}<br>' +
                             'Prevalência: %{customdata[1]:.4f}<br>' +
                             'Chegadas: %{customdata[2]}<extra></extra>',
                customdata=np.column_stack((mapdf['name'], mapdf['prevalence'], mapdf['arrivals'])),
                colorbar=dict(
                    title="Casos Totais",
                    x=1.02,
                    len=0.8
                ),
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Calculate initial bounds for centering the map
        if len(mapdf) > 0:
            lat_center = mapdf['lat'].mean()
            lon_center = mapdf['lon'].mean()
            lat_range = mapdf['lat'].max() - mapdf['lat'].min()
            lon_range = mapdf['lon'].max() - mapdf['lon'].min()
            
            # Add padding (20% of range)
            lat_padding = lat_range * 0.2
            lon_padding = lon_range * 0.2
            
            # Update geo layout with zoom and pan capabilities
            fig.update_geos(
                projection_type="natural earth",
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="lightblue",
                showlakes=True,
                lakecolor="lightblue",
                center=dict(lat=lat_center, lon=lon_center),
                lataxis_range=[mapdf['lat'].min() - lat_padding, mapdf['lat'].max() + lat_padding],
                lonaxis_range=[mapdf['lon'].min() - lon_padding, mapdf['lon'].max() + lon_padding],
                projection_scale=1
            )
    
    # Update layout
    fig.update_layout(
        title="Estado Final da Epidemia",
        height=600,
        showlegend=False
    )
    
    return fig


@lru_cache(maxsize=10)
def create_network_viz(model_path, localities):
    """Create network visualization around selected locality using geographic coordinates"""
    if not localities:
        return go.Figure()
    
    G = get_graph(model_path)
    if G.order() == 0:
        return go.Figure().add_annotation(text="Nenhum arquivo de rede encontrado", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Find the selected node
    nodeloc = list(filter(lambda n: n[1]['name'] == localities, G.nodes(data=True)))
    if not nodeloc:
        return go.Figure().add_annotation(text="Localidade não encontrada na rede", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    H = get_subgraph(G, nodeloc[0][0])
    
    # Load map data to get geographic coordinates; fall back to the site
    # coordinates stored in the simulation database when there is no
    # Data.gpkg (model without a shapefile).
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    has_geometry = False
    if not mapdf.empty:
        # Extract coordinates from geometry
        if hasattr(mapdf.geometry, 'centroid'):
            mapdf['lat'] = mapdf.geometry.centroid.y
            mapdf['lon'] = mapdf.geometry.centroid.x
            has_geometry = True
    if not has_geometry:
        sims = get_sims(model_path)
        mapdf = get_sites_frame(model_path, sims[-1] if sims else None)
        if mapdf.empty or not {'lat', 'longit'}.issubset(mapdf.columns):
            return go.Figure().add_annotation(
                text="Sem Data.gpkg nem coordenadas (lat/longit) nos dados da simulação",
                xref="paper", yref="paper", x=0.5, y=0.5)
        mapdf = mapdf.rename(columns={'longit': 'lon'})
    
    # Create position dictionary using geographic coordinates
    pos = {}
    for node in H.nodes(data=True):
        node_name = node[1].get('name', str(node[0]))
        # Find coordinates for this node in the coordinate frame
        node_coords = mapdf[mapdf['name'] == node_name]
        if not node_coords.empty:
            pos[node[0]] = (node_coords['lon'].iloc[0], node_coords['lat'].iloc[0])
        else:
            # Fallback: use a default position if coordinates not found
            pos[node[0]] = (0, 0)
    
    # Prepare edge traces using geographic coordinates
    edge_lon = []
    edge_lat = []
    selected_node_id = nodeloc[0][0]
    for edge in H.edges(selected_node_id):
        if edge[0] in pos and edge[1] in pos:
            lon0, lat0 = pos[edge[0]]
            lon1, lat1 = pos[edge[1]]
            edge_lon.extend([lon0, lon1, None])
            edge_lat.extend([lat0, lat1, None])
    
    edge_trace = go.Scattergeo(
        lon=edge_lon, lat=edge_lat,
        line=dict(width=1, color='gray'),
        hoverinfo='none',
        mode='lines',
        name='Conexões'
    )
    
    # Prepare node traces using geographic coordinates
    node_lon = []
    node_lat = []
    node_text = []
    node_colors = []
    node_info = []
    
    for node in H.nodes(data=True):
        if node[0] in pos:
            lon, lat = pos[node[0]]
            node_lon.append(lon)
            node_lat.append(lat)
            node_name = node[1].get('name', str(node[0]))
            node_text.append(node_name)
            node_info.append(f"<b>{node_name}</b><br>Lon: {lon:.4f}<br>Lat: {lat:.4f}")
            # Highlight selected node
            node_colors.append('red' if node[0] == nodeloc[0][0] else 'lightblue')
    
    node_trace = go.Scattergeo(
        lon=node_lon, lat=node_lat,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hovertemplate='%{customdata}<extra></extra>',
        customdata=node_info,
        marker=dict(
            size=10,
            color=node_colors,
            line=dict(width=1, color='black')
        ),
        name='Localidades'
    )
    
    # Choropleth base layer, only when real map polygons are available
    traces = []
    if has_geometry:
        mapdf_json = get_map_geojson(os.path.join(model_path, 'Data.gpkg'))
        traces.append(go.Choropleth(
            geojson=mapdf_json,
            locations=mapdf.index,
            z=mapdf['totalcases'] if 'totalcases' in mapdf.columns else [0]*len(mapdf),
            colorscale='YlOrRd',
            showscale=False,
            hoverinfo='skip',
            marker=dict(opacity=0.5, line=dict(width=0.5, color='gray'))
        ))
    traces.extend([edge_trace, node_trace])
    fig = go.Figure(data=traces)
    
    # Calculate bounds
    lat_center = mapdf['lat'].mean()
    lon_center = mapdf['lon'].mean()
    lat_range = mapdf['lat'].max() - mapdf['lat'].min()
    lon_range = mapdf['lon'].max() - mapdf['lon'].min()
    lat_padding = lat_range * 0.2 if lat_range > 0 else 0.5
    lon_padding = lon_range * 0.2 if lon_range > 0 else 0.5

    fig.update_layout(
        title=(f'🕸️ Rede Geográfica - {localities}'
               + (' (sobre mapa coroplético)' if has_geometry
                  else ' (coordenadas dos sites)')),
        showlegend=False,
        height=600,
        margin=dict(b=0,l=0,r=0,t=40)
    )
    
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue",
        center=dict(lat=lat_center, lon=lon_center),
        lataxis_range=[mapdf['lat'].min() - lat_padding, mapdf['lat'].max() + lat_padding],
        lonaxis_range=[mapdf['lon'].min() - lon_padding, mapdf['lon'].max() + lon_padding],
        projection_scale=1.2
    )
    
    return fig


@lru_cache(maxsize=20)
def create_temporal_map(model_path, simulation_run, time_slider):
    """Create temporal choropleth map at specific time"""
    if not simulation_run:
        return go.Figure()
    
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    df_time = read_simulation(model_path, simulation_run, time=time_slider)
    
    if mapdf.empty:
        # No Data.gpkg (model without shapefile): bubble map at time t
        if df_time.empty or not {'lat', 'longit'}.issubset(df_time.columns):
            return go.Figure().add_annotation(
                text="Sem Data.gpkg nem coordenadas (lat/longit) nos dados da simulação",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14)
            )
        var = pick_main_var(df_time.columns)
        if not var:
            return go.Figure()
        z = _finite(df_time[var])
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lon=df_time['longit'], lat=df_time['lat'],
            mode='markers',
            marker=dict(
                size=_bubble_sizes(df_time[var]),
                color=z, colorscale='YlOrRd',
                colorbar=dict(title=var, x=1.02),
                line=dict(width=0.5, color='gray'),
            ),
            text=df_time['name'],
            customdata=np.column_stack((df_time['name'], z)),
            hovertemplate=('<b>%{customdata[0]}</b><br>Tempo: ' +
                           str(time_slider) + '<br>' + var +
                           ': %{customdata[1]:.2f}<extra></extra>'),
            showlegend=False,
        ))
        fig.update_geos(
            projection_type="natural earth",
            showland=True, landcolor="lightgray",
            showocean=True, oceancolor="lightblue",
            showlakes=True, lakecolor="lightblue",
            **_geo_bounds(df_time['lat'], df_time['longit']),
        )
        fig.update_layout(
            title=f'🌍 Mapa de Sites - Tempo {time_slider} ({var}, sem polígonos)',
            height=600, showlegend=False
        )
        return fig
    
    if df_time.empty:
        return go.Figure()
    
    # df_time is already filtered to time_slider
    
    variables = [c for c in df_time.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
    
    # Merge with map data
    name_col = [c for c in mapdf.columns if df_time.name.iloc[0] in list(mapdf[c])][0] if len(df_time) > 0 else 'name'
    mapa_t = pd.merge(mapdf, df_time[['name', 'time'] + variables], 
                      left_on=name_col, right_on='name', how='left')
    
    # Fill NaN values with 0 for visualization
    for var in variables:
        if var in mapa_t.columns:
            mapa_t[var] = mapa_t[var].fillna(0)
    
    # Choose the main variable to display (prefer 'Infectious', then first available variable)
    main_var = 'Infectious' if 'Infectious' in variables else (variables[0] if variables else 'incidence')
    if main_var not in mapa_t.columns:
        main_var = variables[0] if variables else 'incidence'
    
    # mapa_t already has lat/lon from read_map (via mapdf merge)
    
    # Create choropleth map
    fig = go.Figure()
    
    # Convert geometry to GeoJSON format for choropleth
    mapa_t_json = mapa_t.__geo_interface__
    
    # Prepare hover data with all available variables
    hover_data = []
    for idx, row in mapa_t.iterrows():
        hover_info = f"<b>{row['name']}</b><br>Tempo: {time_slider}<br>"
        for var in variables:
            if var in row and pd.notna(row[var]):
                hover_info += f"{var}: {row[var]:.2f}<br>"
        hover_data.append(hover_info)
    
    # Add choropleth trace
    fig.add_trace(
        go.Choropleth(
            geojson=mapa_t_json,
            locations=mapa_t.index,
            z=mapa_t[main_var],
            colorscale='YlOrRd',
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_data,
            colorbar=dict(
                title=main_var.capitalize(),
                x=1.02
            ),
            showlegend=False
        )
    )
    
    # Calculate bounds for centering the map
    if len(mapa_t) > 0 and 'lat' in mapa_t.columns and 'lon' in mapa_t.columns:
        lat_center = mapa_t['lat'].mean()
        lon_center = mapa_t['lon'].mean()
        lat_range = mapa_t['lat'].max() - mapa_t['lat'].min()
        lon_range = mapa_t['lon'].max() - mapa_t['lon'].min()
        
        # Add padding (20% of range)
        lat_padding = lat_range * 0.2 if lat_range > 0 else 1
        lon_padding = lon_range * 0.2 if lon_range > 0 else 1
        
        # Update geo layout
        fig.update_geos(
            projection_type="natural earth",
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            showlakes=True,
            lakecolor="lightblue",
            center=dict(lat=lat_center, lon=lon_center),
            lataxis_range=[mapa_t['lat'].min() - lat_padding, mapa_t['lat'].max() + lat_padding],
            lonaxis_range=[mapa_t['lon'].min() - lon_padding, mapa_t['lon'].max() + lon_padding],
            projection_scale=1
        )
    
    fig.update_layout(
        title=f'🌍 Mapa Coroplético - Tempo {time_slider} ({main_var.capitalize()})',
        height=600,
        showlegend=False
    )
    
    return fig


@lru_cache(maxsize=10)
def create_time_series(model_path, simulation_run, localities):
    """Create time series plots for selected locality"""
    if not simulation_run or not localities:
        return go.Figure()
    
    df_loc = read_simulation(model_path, simulation_run, locality=localities)
    if df_loc.empty:
        return go.Figure()
    
    variables = [c for c in df_loc.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
    
    # Create subplots for different variables
    n_vars = len(variables)
    n_cols = 2
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=variables,
        vertical_spacing=0.1
    )
    
    for i, var in enumerate(variables):
        row = i // n_cols + 1
        col = i % n_cols + 1
        
        fig.add_trace(
            go.Scatter(
                x=df_loc['time'],
                y=df_loc[var],
                mode='lines',
                name=var,
                line=dict(shape='hv'),  # step-after equivalent
                showlegend=False
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        title=f'Séries Temporais - {localities}',
        height=400 * n_rows,
        showlegend=False
    )
    
    return fig


def update_time_bounds(model_path, simulation_run):
    """Update time slider bounds based on simulation data"""
    if not simulation_run:
        return gr.Slider()
    
    df = read_simulation(model_path, simulation_run)
    if df.empty:
        return gr.Slider()
    
    min_time = int(df.time.min())
    t = last_data_time(model_path, simulation_run)
    max_time = t if t is not None else int(df.time.max())
    
    return gr.Slider(minimum=min_time, maximum=max_time, value=min_time)


def export_geolibre(model_path, simulation_run):
    """Write a .geolibre.json project for the selected simulation and hand
    it to the DownloadButton. Raises gr.Error on failure (shown as toast)."""
    from Epigrass import geolibre_export
    try:
        return str(geolibre_export.export_project(model_path,
                                                  sim=simulation_run))
    except Exception as exc:
        raise gr.Error(f"Falha ao exportar projeto GeoLibre: {exc}")


def create_dashboard(pth:str):
    """
     Create the main Gradio dashboard
    :param pth: Path to the model data
    :return: Gradio interface
    """
    
    with gr.Blocks() as demo:
        gr.HTML("""<img src="https://github.com/fccoelho/epigrass/blob/master/Epigrass/egicon.png?raw=true"> <h1 align="center">Epigrass Dashboard</h1>""")
        gr.Markdown("## Dashboard interativo para visualização de Simulações")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🎛️ Controles")
                
                model_path = gr.Textbox(
                    value=pth,
                    label="Caminho do Modelo",
                    placeholder="Digite o caminho para os dados do modelo"
                )
                
                refresh_btn = gr.Button("🔄 Atualizar Dados", variant="primary")

                geolibre_btn = gr.DownloadButton(
                    "📤 Exportar projeto GeoLibre", variant="secondary")
                
                map_selector = gr.Dropdown(
                    label="📁 Arquivo de Mapa",
                    choices=[],
                    value=None
                )
                
                simulation_run = gr.Dropdown(
                    label="🎯 Simulação",
                    choices=[],
                    value=None
                )
                
                localities = gr.Dropdown(
                    label="📍 Localidades",
                    choices=[],
                    value=None
                )
                
                time_slider = gr.Slider(
                    minimum=1,
                    maximum=300,
                    value=1,
                    step=1,
                    label="⏰ Tempo"
                )
                
                gr.Markdown("---")
                meta_info = gr.Markdown("## ℹ️ Informações da Simulação")
            
            with gr.Column(scale=3):
                with gr.Tabs():
                    with gr.Tab("🗺️ Estado Final"):
                        final_map = gr.Plot(label="Mapa do Estado Final")
                        
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 📊 Dados da Simulação (Estado Final)")
                                simulation_table = gr.Dataframe(
                                    label="Tabela de Dados",
                                    interactive=False,
                                    wrap=True,
                                    row_count=10,

                                )
                    
                    with gr.Tab("🕸️ Rede"):
                        network_plot = gr.Plot(label="Visualização da Rede")
                    
                    with gr.Tab("🌍 Mapa Temporal"):
                        temporal_map = gr.Plot(label="Mapa no Tempo")
                    
                    with gr.Tab("📈 Séries Temporais"):
                        time_series = gr.Plot(label="Gráficos de Séries Temporais")
        
        # Event handlers
        refresh_btn.click(
            fn=refresh_data,
            inputs=[model_path],
            outputs=[map_selector, simulation_run, localities, meta_info]
        )

        geolibre_btn.click(
            fn=export_geolibre,
            inputs=[model_path, simulation_run],
            outputs=[geolibre_btn]
        )
        
        # Auto-refresh on load
        demo.load(
            fn=refresh_data,
            inputs=[model_path],
            outputs=[map_selector, simulation_run, localities, meta_info]
        )
        
        # Update table on load
        demo.load(
            fn=create_simulation_table,
            inputs=[model_path, simulation_run],
            outputs=[simulation_table]
        )
        
        simulation_run.change(
            fn=update_localities,
            inputs=[model_path, simulation_run],
            outputs=[localities]
        )
        
        simulation_run.change(
            fn=update_time_bounds,
            inputs=[model_path, simulation_run],
            outputs=[time_slider]
        )
        
        simulation_run.change(
            fn=get_meta_info,
            inputs=[model_path, simulation_run],
            outputs=[meta_info]
        )
        
        # Update simulation table when simulation changes
        simulation_run.change(
            fn=create_simulation_table,
            inputs=[model_path, simulation_run],
            outputs=[simulation_table]
        )
        
        # Auto-zoom when locality is selected from left column
        localities.change(
            fn=zoom_to_location,
            inputs=[model_path, localities],
            outputs=[final_map]
        )
        
        # Update plots when inputs change
        # Final Map update
        for inp in [model_path, map_selector, simulation_run]:
            inp.change(
                fn=create_final_map,
                inputs=[model_path, map_selector, simulation_run],
                outputs=[final_map]
            )
            
        # Network Viz update
        for inp in [model_path, localities]:
            inp.change(
                fn=create_network_viz,
                inputs=[model_path, localities],
                outputs=[network_plot]
            )
            
        # Temporal Map update
        for inp in [model_path, simulation_run, time_slider]:
            inp.change(
                fn=create_temporal_map,
                inputs=[model_path, simulation_run, time_slider],
                outputs=[temporal_map]
            )
            
        # Time Series update
        for inp in [model_path, simulation_run, localities]:
            inp.change(
                fn=create_time_series,
                inputs=[model_path, simulation_run, localities],
                outputs=[time_series]
            )
        
        # Update table when relevant inputs change
        for inp in [model_path, simulation_run]:
            inp.change(
                fn=create_simulation_table,
                inputs=[model_path, simulation_run],
                outputs=[simulation_table]
            )
    
    return demo


#: preferred dashboard port; the next free one is used when it is taken
DEFAULT_PORT = 5006
PORT_TRIES = 25


def find_free_port(start: int = DEFAULT_PORT, tries: int = PORT_TRIES) -> int | None:
    """Return the first bindable port from ``start``, or None if all busy."""
    import socket
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return None


def launch_dashboard(demo, **kwargs):
    """
    Launch a Gradio Blocks app on the first free port from DEFAULT_PORT.
    Falls back to Gradio's automatic port selection if the range is busy.
    """
    port = find_free_port()
    if port is None:
        print(f"==> Ports {DEFAULT_PORT}-{DEFAULT_PORT + PORT_TRIES - 1} busy; "
              "letting Gradio pick a port automatically", flush=True)
    else:
        print(f"==> Epigrass Dashboard starting on http://localhost:{port}",
              flush=True)
    kwargs.setdefault("share", False)
    try:
        demo.launch(server_port=port, **kwargs)
    except OSError:
        print(f"==> Port {port} was taken during startup; "
              "retrying on an automatic port", flush=True)
        demo.launch(**kwargs)


def show(pth):
    """Launch the dashboard with a specific path"""
    demo = create_dashboard(pth)
    launch_dashboard(demo, root_path='/Epigrass',
                     allowed_paths=['/assets', pth])


if __name__ == "__main__":
    demo = create_dashboard()
    launch_dashboard(demo, title="Epigrass Dashboard", theme=gr.themes.Soft())
