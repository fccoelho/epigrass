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
from sqlalchemy import create_engine, text
import glob
from functools import lru_cache
import json

# Ícone codificado
enc_icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA3ElEQVRYhe2WWQ7DIAxEH1XvVR+dmzkfVSJngWIW0VYZKV8EZgzDmABARFkhBDxomQs8z+tFvfoxBUG8nHkBgnircAlOwlt5LzxmkN4CbgFfJeB950vSrDHxUihOwtbEKxaQScKxQTUrCU87YJE5jnEeOJJfkdkxNUcTaDCnrbb0OCJRFbavmtySer3QVcAMI/5GEmaN1utNqAIhpjwghm8/Lsg2twbTd8CsU2/AlrnTTbhDbSX/swPgr2ZIeHl6QStX8tqsi79MBqxXMNcpu+LY7Ub0i48VdOv3CSxJ9X3LgJP02QAAAABJRU5ErkJggg=='
with open('egicon.png', 'wb') as f:
    f.write(base64.b64decode(enc_icon))


@lru_cache(maxsize=10)
def get_sims(fname):
    """
    Get list of simulations available on SQLite database
    :param fname: Database file path
    :return: List of tables. list of str
    """
    full_path = os.path.join(fname, 'Epigrass.sqlite')
    if os.path.exists(full_path):
        con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
        sims = con.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"))
        sim_names = [s[0] for s in sims if not (s[0].endswith('_meta') or s[0].endswith('e'))]
        con.close()
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
        con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
        df = pd.read_sql_query(f"select * from {mname}", con)
        con.close()
    else:
        df = pd.DataFrame()
        get_meta_table.cache_clear()
    return df


@lru_cache(maxsize=10)
def read_simulation(fname, simulation_name, locality=None):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        read_simulation.cache_clear()
        return pd.DataFrame()

    con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
    if locality is None:
        simdf = pd.read_sql_query(f"select * from {simulation_name}", con)
    else:
        simdf = pd.read_sql_query(f"select * from {simulation_name} where name='{locality}'", con)
    simdf.fillna(0, inplace=True)
    con.close()
    return simdf


@lru_cache(maxsize=10)
def get_localities(fname, simulation_name) -> list:
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        get_localities.cache_clear()
        return []
    con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
    locs = pd.read_sql_query(f'select distinct name from {simulation_name}', con)
    localities = [l[0] for l in locs.values]
    con.close()
    return localities


@lru_cache(maxsize=10)
def read_map(fname):
    if os.path.exists(fname):
        return gpd.read_file(fname)
    else:
        read_map.cache_clear()
        return gpd.GeoDataFrame()


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


def zoom_to_location(model_path, location_name):
    """Create a zoomed version of the map focused on a specific location"""
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    if mapdf.empty:
        return go.Figure()
    
    # Find the selected location
    selected_location = mapdf[mapdf['name'] == location_name]
    if selected_location.empty:
        return create_final_map(model_path, 'Data.gpkg', None)
    
    # Extract coordinates from geometry
    if hasattr(mapdf.geometry, 'centroid'):
        mapdf['lat'] = mapdf.geometry.centroid.y
        mapdf['lon'] = mapdf.geometry.centroid.x
        selected_lat = selected_location.geometry.centroid.y.iloc[0]
        selected_lon = selected_location.geometry.centroid.x.iloc[0]
    else:
        return create_final_map(model_path, 'Data.gpkg', None)
    
    # Create focused map
    fig = go.Figure()
    
    # Convert geometry to GeoJSON format for choropleth
    mapdf_json = mapdf.__geo_interface__
    
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
            )
        )
    )
    
    # Calculate zoom bounds around selected location
    zoom_range = 0.5  # degrees
    
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
        projection_scale=3  # Zoom in more
    )
    
    fig.update_layout(
        title=f"Mapa Focado em: {location_name}",
        height=600,
        showlegend=False
    )
    
    return fig


def create_final_map(model_path, map_selector, simulation_run):
    """Create final state map visualization with interactive bar chart and zoomable choropleth"""
    if not map_selector or not simulation_run:
        return go.Figure()
    
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    if mapdf.empty:
        return go.Figure()
    
    # Get top 15 locations by total cases
    map10 = mapdf.sort_values('totalcases', ascending=False).iloc[:15]
    
    # Extract coordinates from geometry
    if hasattr(mapdf.geometry, 'centroid'):
        mapdf['lat'] = mapdf.geometry.centroid.y
        mapdf['lon'] = mapdf.geometry.centroid.x
    else:
        mapdf['lat'] = 0
        mapdf['lon'] = 0
    
    # Create figure with custom subplot configuration
    fig = go.Figure()
    
    # Create choropleth map using the geometry data
    if hasattr(mapdf, 'geometry') and not mapdf.empty:
        # Convert geometry to GeoJSON format for choropleth
        mapdf_json = mapdf.__geo_interface__
        
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
                name="Mapa"
            )
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
                # Enable zoom and pan
                projection_scale=1
            )
    
    # Add bar chart as a separate subplot using domain
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
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<br>Clique para focar no mapa<extra></extra>',
            name="Top Localidades",
            yaxis="y2",
            xaxis="x2",
            # Add custom data for click events
            customdata=map10['name']
        )
    )
    
    # Update layout with dual axis configuration
    fig.update_layout(
        title="Estado Final da Epidemia - Clique nas barras para focar no mapa",
        height=600,
        showlegend=False,
        # Configure the map (main plot)
        geo=dict(
            domain=dict(x=[0.4, 1.0], y=[0, 1])
        ),
        # Configure the bar chart
        xaxis2=dict(
            domain=[0, 0.35],
            anchor="y2",
            title="Casos Totais"
        ),
        yaxis2=dict(
            domain=[0.3, 0.7],
            anchor="x2",
            title="Localidades"
        ),
        # Add click event handling instructions
        annotations=[
            dict(
                text="💡 Clique nas barras para focar no mapa<br>🔍 Use os controles do mapa para navegar",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                xanchor="left", yanchor="top",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
                font=dict(size=10)
            )
        ]
    )
    
    # Add JavaScript callback for bar click events (this would need to be handled in Gradio)
    # For now, we'll add the infrastructure for future enhancement
    fig.update_traces(
        selector=dict(type="bar"),
        # This creates the foundation for click interactivity
        meta={"click_action": "zoom_to_location"}
    )
    
    return fig


def create_network_viz(model_path, localities):
    """Create network visualization around selected locality"""
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
    
    # Create layout
    pos = NX.spring_layout(H, seed=42)
    
    # Prepare edge traces
    edge_x = []
    edge_y = []
    for edge in H.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='gray'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Prepare node traces
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    
    for node in H.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node[1].get('name', str(node[0])))
        # Highlight selected node
        node_colors.append('red' if node[0] == nodeloc[0][0] else 'lightblue')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        hoverinfo='text',
        marker=dict(
            size=20,
            color=node_colors,
            line=dict(width=2, color='black')
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=f'Rede ao redor de {localities}',
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002 ) ],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )
    
    return fig


def create_temporal_map(model_path, simulation_run, time_slider):
    """Create temporal map at specific time"""
    if not simulation_run:
        return go.Figure()
    
    mapdf = read_map(os.path.join(model_path, 'Data.gpkg'))
    df = read_simulation(model_path, simulation_run)
    
    if mapdf.empty or df.empty:
        return go.Figure()
    
    # Get data for specific time
    df_time = df[df.time == time_slider]
    if df_time.empty:
        return go.Figure()
    
    variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
    
    # Merge with map data
    name_col = [c for c in mapdf.columns if df.name.iloc[0] in list(mapdf[c])][0] if len(df) > 0 else 'name'
    mapa_t = pd.merge(mapdf, df_time[['name', 'time'] + variables], 
                      left_on=name_col, right_on='name', how='left')
    
    # Create scatter plot on map coordinates
    fig = go.Figure()
    
    if hasattr(mapdf.geometry, 'centroid'):
        fig.add_trace(go.Scatter(
            x=mapa_t.geometry.centroid.x,
            y=mapa_t.geometry.centroid.y,
            mode='markers',
            marker=dict(
                size=np.nan_to_num(mapa_t.get('Infectious', mapa_t.get(variables[0] if variables else 'totalcases', 0)) /
                     mapa_t.get('Infectious', mapa_t.get(variables[0] if variables else 'totalcases', 1)).max() * 30 + 5),
                color=mapa_t.get('Infectious', mapa_t.get(variables[0] if variables else 'totalcases', 0)),
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Casos")
            ),
            text=mapa_t['name'],
            hovertemplate='<b>%{text}</b><br>Tempo: ' + str(time_slider) + '<br>Casos: %{marker.color}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'Estado no Tempo {time_slider}',
        height=500,
        xaxis_title="Longitude",
        yaxis_title="Latitude"
    )
    
    return fig


def create_time_series(model_path, simulation_run, localities):
    """Create time series plots for selected locality"""
    if not simulation_run or not localities:
        return go.Figure()
    
    df = read_simulation(model_path, simulation_run)
    if df.empty:
        return go.Figure()
    
    df_loc = df[df.name == localities]
    if df_loc.empty:
        return go.Figure()
    
    variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
    
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
    max_time = int(df.time.max())
    
    return gr.Slider(minimum=min_time, maximum=max_time, value=min_time)


def create_dashboard(pth:str):
    """
     Create the main Gradio dashboard
    :param pth: Path to the model data
    :return: Gradio interface
    """
    
    with gr.Blocks(title="Epigrass Dashboard", theme=gr.themes.Soft()) as demo:
        gr.HTML("""<img src="assets/egicon.png> <h1 align="center">Epigrass Dashboard</h1>""")
        gr.Markdown("Dashboard interativo para visualização de Simulações")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🎛️ Controles")
                
                model_path = gr.Textbox(
                    value=pth,
                    label="Caminho do Modelo",
                    placeholder="Digite o caminho para os dados do modelo"
                )
                
                refresh_btn = gr.Button("🔄 Atualizar Dados", variant="primary")
                
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
                        with gr.Row():
                            with gr.Column(scale=4):
                                final_map = gr.Plot(label="Mapa do Estado Final")
                            with gr.Column(scale=1):
                                gr.Markdown("### 🎯 Foco no Mapa")
                                location_selector = gr.Dropdown(
                                    label="Selecionar Localidade",
                                    choices=[],
                                    value=None,
                                    info="Selecione para focar no mapa"
                                )
                                zoom_btn = gr.Button("🔍 Focar no Mapa", variant="secondary")
                    
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
        
        # Auto-refresh on load
        demo.load(
            fn=refresh_data,
            inputs=[model_path],
            outputs=[map_selector, simulation_run, localities, meta_info]
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
        
        # Update location selector when simulation changes
        simulation_run.change(
            fn=lambda mp, sr: gr.Dropdown(choices=get_localities(mp, sr) if sr else []),
            inputs=[model_path, simulation_run],
            outputs=[location_selector]
        )
        
        # Zoom functionality
        zoom_btn.click(
            fn=zoom_to_location,
            inputs=[model_path, location_selector],
            outputs=[final_map]
        )
        
        # Update plots when inputs change
        inputs_list = [model_path, map_selector, simulation_run, localities, time_slider]
        
        for inp in inputs_list:
            inp.change(
                fn=create_final_map,
                inputs=[model_path, map_selector, simulation_run],
                outputs=[final_map]
            )
            
            inp.change(
                fn=create_network_viz,
                inputs=[model_path, localities],
                outputs=[network_plot]
            )
            
            inp.change(
                fn=create_temporal_map,
                inputs=[model_path, simulation_run, time_slider],
                outputs=[temporal_map]
            )
            
            inp.change(
                fn=create_time_series,
                inputs=[model_path, simulation_run, localities],
                outputs=[time_series]
            )
    
    return demo


def show(pth):
    """Launch the dashboard with a specific path"""
    demo = create_dashboard(pth)
    demo.launch(server_port=5006,
                allowed_paths=['assets/egicon.png', pth],
                share=False,
                )


if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch(server_port=5006, share=False)
