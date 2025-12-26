#!/usr/bin/env python3
import gradio as gr
import pandas as pd
import os
import subprocess
import configparser
import geopandas as gpd
import matplotlib.pyplot as plt
import sys
import io

# Templates
EPG_TEMPLATE = """################################################################
#  EPIGRASS -Model Definition
################################################################

[THE WORLD]
shapefile = []
sites = sites.csv
edges = edges.csv
encoding = utf8

[EPIDEMIOLOGICAL MODEL]
modtype = SIR

[MODEL PARAMETERS]
beta = 0.5
r = 0.1
delta = 0

[INITIAL CONDITIONS]
S = N
I = 1
R = 0

[EPIDEMIC EVENTS]
seed = []
Vaccinate = []
Quarantine = []

[TRANSPORTATION MODEL]
doTransp = 1
stochastic = 0
speed = 0

[SIMULATION AND OUTPUT]
steps = 365
outdir =
sqlout = 1
report = 0
Replicas = 0
RandSeed = 0
Batch = []
"""

SITES_TEMPLATE = """lat,long,NAME,POP,geocode
-22.9068,-43.1729,Rio de Janeiro,6000000,1
-23.5505,-46.6333,Sao Paulo,12000000,2
"""

EDGES_TEMPLATE = """NOME_ORIGEM,NOME_DEST,flowOD,flowDO,Dist,COD_ORIGEM,COD_DESTINO
Rio de Janeiro,Sao Paulo,1000,1000,430,1,2
"""

def parse_epg_for_map(epg_content, project_path):
    try:
        cp = configparser.ConfigParser(inline_comment_prefixes='#')
        cp.read_string(epg_content)
        if 'THE WORLD' in cp and 'shapefile' in cp['THE WORLD']:
            shp_info = eval(cp['THE WORLD']['shapefile'])
            if shp_info and isinstance(shp_info, list) and len(shp_info) > 0:
                shp_path = os.path.join(project_path, shp_info[0])
                if os.path.exists(shp_path):
                    return shp_path
    except Exception as e:
        print(f"Error parsing EPG for map: {e}")
    return None

def load_project(project_path):
    if isinstance(project_path, list):
        if not project_path:
            return "No path selected.", "", None, None, None
        project_path = project_path[0]
    
    if not project_path or not os.path.exists(project_path):
        return "Project path does not exist.", "", None, None, None

    files = os.listdir(project_path)
    epg_file = next((f for f in files if f.endswith('.epg')), None)
    sites_file = next((f for f in files if f == 'sites.csv'), None)
    edges_file = next((f for f in files if f == 'edges.csv'), None)

    epg_content = ""
    if epg_file:
        with open(os.path.join(project_path, epg_file), 'r') as f:
            epg_content = f.read()
    
    sites_df = pd.DataFrame()
    if sites_file:
        sites_df = pd.read_csv(os.path.join(project_path, sites_file))
    
    edges_df = pd.DataFrame()
    if edges_file:
        edges_df = pd.read_csv(os.path.join(project_path, edges_file))

    status = f"Loaded project from {project_path}"
    
    # Render map if possible
    map_fig = None
    shp_path = parse_epg_for_map(epg_content, project_path)
    print(shp_path, project_path)
    if shp_path:
        try:
            gdf = gpd.read_file(shp_path)
            fig, ax = plt.subplots(figsize=(10, 8))
            gdf.plot(ax=ax)
            ax.set_title(f"Map: {os.path.basename(shp_path)}")
            map_fig = fig
        except Exception as e:
            status += f" (Map error: {e})"

    return status, epg_content, sites_df, edges_df, map_fig, project_path

def save_project(project_path, epg_content, sites_df, edges_df):
    if isinstance(project_path, list):
        if not project_path: return "Error: No path selected."
        project_path = project_path[0]

    if not project_path or not os.path.exists(project_path):
        return "Error: Invalid project path."

    files = os.listdir(project_path)
    epg_file = next((f for f in files if f.endswith('.epg')), "simulation.epg")
    
    try:
        with open(os.path.join(project_path, epg_file), 'w') as f:
            f.write(epg_content)
        
        if sites_df is not None:
            sites_df.to_csv(os.path.join(project_path, 'sites.csv'), index=False)
        
        if edges_df is not None:
            edges_df.to_csv(os.path.join(project_path, 'edges.csv'), index=False)
        
        return f"Project saved successfully at {project_path}"
    except Exception as e:
        return f"Error saving project: {e}"

def create_project(project_path):
    if isinstance(project_path, list):
        if not project_path:
            return "Error: No path selected.", "", None, None, None
        project_path = project_path[0]

    if not project_path:
        return "Error: No project path specified.", "", None, None, None
    
    try:
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        
        with open(os.path.join(project_path, 'new_simulation.epg'), 'w') as f:
            f.write(EPG_TEMPLATE)
        
        with open(os.path.join(project_path, 'sites.csv'), 'w') as f:
            f.write(SITES_TEMPLATE)
            
        with open(os.path.join(project_path, 'edges.csv'), 'w') as f:
            f.write(EDGES_TEMPLATE)
            
        return load_project(project_path)
    except Exception as e:
        return f"Error creating project: {e}", "", None, None, None

def run_simulation_proc(project_path):
    if isinstance(project_path, list):
        if not project_path:
            yield "Error: No path selected."
            return
        project_path = project_path[0]

    if not project_path or not os.path.exists(project_path):
        yield "Error: Invalid project path."
        return

    files = os.listdir(project_path)
    epg_file = next((f for f in files if f.endswith('.epg')), None)
    
    if not epg_file:
        yield "Error: No .epg file found in project."
        return

    epg_path = os.path.join(project_path, epg_file)
    cmd = [sys.executable, "-m", "Epigrass.manager", epg_path]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   text=True, bufsize=1, universal_newlines=True, cwd=project_path)
        
        yield f"Starting simulation: {' '.join(cmd)}\n"
        for line in process.stdout:
            yield line
        
        process.wait()
        if process.returncode == 0:
            yield "\nSimulation finished successfully."
        else:
            yield f"\nSimulation failed with return code {process.returncode}"
    except Exception as e:
        yield f"Error running simulation: {e}"

with gr.Blocks(title="Epigrass Simulation Builder") as demo:
    gr.Markdown("# Epigrass Simulation Builder")
    
    project_action = gr.State("") # "load" or "create"
    current_project_path = gr.State("")

    with gr.Row():
        path_display = gr.Textbox(label="Current Project Path", interactive=False, scale=4)
        load_btn = gr.Button("📂 Load Project", scale=1)
        create_btn = gr.Button("➕ Create New Project", scale=1)

    ROOT_DIR = os.getcwd()

    with gr.Group(visible=False) as explorer_group:
        gr.Markdown("## Select Project Directory")
        explorer = gr.FileExplorer(root_dir=ROOT_DIR, file_count="single", glob="**/*")
        with gr.Row():
            confirm_btn = gr.Button("Confirm Selection", variant="primary")
            cancel_btn = gr.Button("Cancel")

    with gr.Tabs() as tabs:
        with gr.Tab("Configuration"):
            epg_editor = gr.Code(label="Simulation (.epg)", language="python", lines=20)
        
        with gr.Tab("Sites"):
            sites_table = gr.DataFrame(label="sites.csv", interactive=True)
            
        with gr.Tab("Edges"):
            edges_table = gr.DataFrame(label="edges.csv", interactive=True)
            
        with gr.Tab("Map"):
            map_plot = gr.Plot(label="Geographic Map")

    with gr.Row():
        save_btn = gr.Button("💾 Save Project", variant="primary")
        run_btn = gr.Button("🚀 Run Simulation", variant="secondary")

    status_output = gr.Textbox(label="Status/Output", lines=10, interactive=False)

    # Event handlers
    def open_explorer(action):
        return gr.update(visible=True), action

    load_btn.click(lambda: open_explorer("load"), outputs=[explorer_group, project_action])
    create_btn.click(lambda: open_explorer("create"), outputs=[explorer_group, project_action])
    cancel_btn.click(lambda: gr.update(visible=False), outputs=[explorer_group])

    def handle_selection(action, selected_path):
        
        if not selected_path:
            return gr.update(visible=False), "No path selected.", gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
        print(selected_path,os.path.isdir(selected_path), type(selected_path))
        path = selected_path
        # selected_path is a list from gr.FileExplorer
        # original_path = selected_path[0]
        # path = original_path
        # # Resolve to absolute path relative to ROOT_DIR
        # # FileExplorer paths often start with / but are relative to root_dir
        # if not os.path.isabs(path) or path.startswith('/'):
        #     path = os.path.abspath(os.path.join(ROOT_DIR, path.lstrip('/')))
            
        debug_msg = f"Original: {selected_path} | Resolved: {path}"
        # If user picked a file, get its directory
        if os.path.isfile(path):
            path = os.path.dirname(path)
        
        if action == "load":
            status, epg, sites, edges, map_fig, final_path = load_project(path)
            return gr.update(visible=False), f"{status} | {debug_msg}", epg, sites, edges, map_fig, final_path
        elif action == "create":
            status, epg, sites, edges, map_fig, final_path = create_project(path)
            return gr.update(visible=False), status, epg, sites, edges, map_fig, final_path
        
        return gr.update(visible=False), "Invalid action.", gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()

    confirm_btn.click(
        fn=handle_selection,
        inputs=[project_action, explorer],
        outputs=[explorer_group, status_output, epg_editor, sites_table, edges_table, map_plot, path_display]
    ).then(
        fn=lambda p: p,
        inputs=[path_display],
        outputs=[current_project_path]
    )
    
    save_btn.click(
        fn=save_project,
        inputs=[current_project_path, epg_editor, sites_table, edges_table],
        outputs=[status_output]
    )
    
    run_btn.click(
        fn=run_simulation_proc,
        inputs=[current_project_path],
        outputs=[status_output]
    )

def main():
    demo.launch(favicon_path="egicon.png", 
                theme=gr.themes.Soft(), 
                title="Epigrass Simulation Builder"
                )

if __name__ == "__main__":
    main()
