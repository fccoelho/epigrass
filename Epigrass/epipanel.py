import pandas as pd
import altair as alt
import networkx as NX
import nx_altair as nxa
import geopandas as gpd
import os
import panel as pn
import panel.widgets as pnw
import hvplot.pandas
import holoviews as hv
import geoviews as gv
from holoviews.operation.datashader import datashade, bundle_graph
from holoviews import opts
from bokeh.resources import INLINE
import param
import base64
from sqlalchemy import create_engine
import glob
from functools import lru_cache

enc_icon = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA3ElEQVRYhe2WWQ7DIAxEH1XvVR+dmzkfVSJngWIW0VYZKV8EZgzDmABARFkhBDxomQs8z+tFvfoxBUG8nHkBgnircAlOwlt5LzxmkN4CbgFfJeB950vSrDHxUihOwtbEKxaQScKxQTUrCU87YJE5jnEeOJJfkdkxNUcTaDCnrbb0OCJRFbavmtySer3QVcAMI/5GEmaN1utNqAIhpjwghm8/Lsg2twbTd8CsU2/AlrnTTbhDbSX/swPgr2ZIeHl6QStX8tqsi79MBqxXMNcpu+LY7Ub0i48VdOv3CSxJ9X3LgJP02QAAAABJRU5ErkJggg=='
with open('egicon.png', 'wb') as f:
    f.write(base64.b64decode(enc_icon))
material = pn.template.MaterialTemplate(title='Epigrass Dashboard', favicon='egicon.png', logo='egicon.png')

pn.config.sizing_mode = 'stretch_width'
alt.renderers.set_embed_options(actions=True)


@lru_cache(maxsize=10)
def get_sims(fname):
    """
    Get list of simulations available on SQLite database
    :param pth: Database file
    :return: List of tables. list of str
    """
    full_path = os.path.join(fname, 'Epigrass.sqlite')
    if os.path.exists(full_path):
        con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
        sims = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
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
        G = NX.read_gml(full_path)
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
def get_localities(fname, simulation_name):
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
        gpd.GeoDataFrame()
        read_map.cache_clear()


def get_subgraph(G, node):
    """
    return subgraph containing `node` and its direct neighboors
    :param G: full graph
    :param node: node defining the subgraph
    """
    nodes = [node]
    nodes.extend(list(G.neighbors(node)))
    H = G.subgraph(nodes).copy()
    return H


# pipeline = pn.pipeline.Pipeline()
class SeriesViewer(param.Parameterized):
    model_path = param.String(default='../demos/outdata-rio')
    map_selector = param.ObjectSelector()
    simulation_run = param.ObjectSelector()
    localities = param.ObjectSelector(default='Pick a Locality', objects=[])
    time_slider = param.Integer(default=1, bounds=(1, 300))

    def __init__(self, **params):
        self.update()
        self.update_sims()
        super(SeriesViewer, self).__init__(**params)

    @param.depends('model_path', watch=True)
    def update(self):
        maps = glob.glob(os.path.join(self.model_path, '*.gpkg'))
        self.param['map_selector'].objects = maps
        if maps:
            self.map_selector = maps[0]
        self.mapdf = read_map(os.path.join(self.model_path, 'Data.gpkg'))

    @param.depends('map_selector', 'model_path', watch=True)
    def update_sims(self):
        sims = get_sims(self.model_path)
        self.param['simulation_run'].objects = sims
        if sims:
            self.simulation_run = sims[-1]
        self.df = read_simulation(self.model_path, self.simulation_run)

    @param.depends('simulation_run', watch=True)
    def update_localities(self):
        locs = get_localities(self.model_path, self.simulation_run)
        self.param['localities'].objects = list(locs)
        if locs:
            self.localities = locs[0]

    @param.depends('map_selector', 'simulation_run')
    def view_meta(self):
        df = get_meta_table(self.model_path, self.simulation_run)
        if len(df) > 0:
            dfpars = df[[c for c in df.columns if 'parameters' in c]]
            dfpars.columns = [c.split('$')[-1] for c in dfpars.columns]
            return pn.pane.Markdown(
                f"""
## Simulation Info
### Map File
{df['the_world$shapefile'].iloc[0].split(',')[0].strip("['")}
### Sites File
{df['the_world$sites'].iloc[0]}
### Edges File
{df['the_world$sites'].iloc[0]}
### Model Type
{df['epidemiological_model$modtype'].iloc[0]}
### Epidemic Events
Seed: {df['epidemic_events$seed'].iloc[0]}

"""
            )
        else:
            return pn.pane.Markdown("")

    @param.depends('model_path', 'map_selector', 'simulation_run')
    def view_map(self):
        if self.map_selector and self.mapdf is not None:
            mapdf = self.mapdf
            map10 = mapdf.sort_values('totalcases', ascending=False).iloc[:15]
            brush = alt.selection_single(encodings=["y"], on="mouseover", empty='none')
            color = alt.Color('totalcases', scale=alt.Scale(type='pow', exponent=0.4))
            f = alt.hconcat(
                alt.Chart(map10).mark_bar().encode(
                    x=alt.X('totalcases', scale=alt.Scale(nice=True)),
                    y=alt.Y('name', sort=alt.EncodingSortField(field='totalcases',
                                                               op='sum', order='descending')),
                    tooltip=['name', 'prevalence', 'totalcases'],
                    color=alt.condition(brush, alt.value('lightgray'), color)
                ).add_selection(
                    brush
                ).properties(
                    width=200,
                    height='container'
                ),
                alt.Chart(self.mapdf).mark_geoshape(
                ).encode(
                    color=alt.condition(
                        brush,
                        alt.value('lightgray'),
                        color,
                    ),
                    tooltip=['name', 'prevalence', 'totalcases', 'arrivals']
                ).properties(
                    width=600,
                    height='container'
                )
            )
            # f = self.mapdf[self.mapdf.totalcases>0].hvplot.polygons(geo=True, c='prevalence',
            #                                alpha=0.7,
            #                                colormap='BuPu',
            #                                responsive=True,
            #                                colorbar=True,
            #                                tiles=True,
            #                                )

            return f
        else:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)

    @param.depends('model_path', 'localities')
    def view_network(self):
        if self.mapdf is None:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)
        G = get_graph(self.model_path)
        if G.order == 0:
            return pn.pane.Alert(f'## No network file found on {self.model_path}')
        nodeloc = list(filter(lambda n: n[1]['name'] == self.localities, G.nodes(data=True)))
        # print(nodeloc, self.localities)
        if nodeloc == []:
            return pn.pane.Alert(f'## Please select a locality.')
        H = get_subgraph(G, nodeloc[0][0])
        partial_map = self.mapdf[self.mapdf.geocode.isin(H.nodes)]
        partial_map = partial_map.set_crs(4326)
        partial_map = partial_map.to_crs(3857)  # Converting to web mercator
        centroids = [(c.x, c.y) for c in partial_map.centroid]
        # Draw the graph using Altair
        gcs = [str(int(gc)) for gc in partial_map.geocode]
        pos = dict(zip(gcs, centroids))

        # viz = nxa.draw_networkx(
        #     G, pos=pos,
        #     node_color='weight',
        #     cmap='viridis',
        #     width='weight',
        #     edge_color='black',
        # )

        kwargs = dict(width=800, height=800, xaxis=None, yaxis=None)
        hv.opts.defaults(opts.Nodes(**kwargs), opts.Graph(**kwargs))
        colors = ['#000000'] + hv.Cycle('Category20').values
        epi_graph = hv.Graph.from_networkx(H, positions=pos)

        epi_graph.opts(
            cmap=colors, node_size=10, edge_line_width=1,
            directed=True,
            node_line_color='gray',
            edge_color='gray',
            node_color='circle'
        )
        tiles = gv.tile_sources.Wikipedia

        f = bundle_graph(epi_graph) * tiles
        source = epi_graph.nodes.clone()
        # print(epi_graph.nodes.data.iloc[0])
        source.data = epi_graph.nodes.data[epi_graph.nodes.data.name == self.localities]

        return f * source.opts(color='red')

    @param.depends('localities', 'time_slider', 'simulation_run')
    def view_series(self):
        if self.simulation_run is None:
            return pn.pane.Alert('## No data\nPlease select a simulation from the `Simulation run` widget on the left.')
        mapdf = self.mapdf
        df = self.df = read_simulation(self.model_path, self.simulation_run)
        # df = self.df[self.df.name==self.localities]
        if len(df) == 0:
            return pn.pane.Alert(f'## No data for "{self.localities}"\nPlease select a locality.')
        time = df.time.min()
        self.param['time_slider'].bounds = (df.time.min(), df.time.max())
        variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
        if mapdf is None:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)
        name_col = [c for c in mapdf if df.name[0] in list(mapdf[c])][0]
        mapa_t = pd.merge(mapdf, df[df.time == self.time_slider][['name', 'time'] + variables],
                          left_on=name_col, right_on='name')
        # series = df[df.name == self.localities].hvplot.line(
        #     width=400,
        #     x='time',
        #     y=variables,
        #     responsive=True,
        #     subplots=True,
        #     shared_axes=False,
        #     value_label=f'Cases at {self.localities}',
        # ).cols(3)
        mapa = alt.Chart(mapa_t).mark_geoshape(
        ).encode(
            color='Infectious',
            tooltip=['name'] + variables,
        ).properties(
            width='container',
            height='container'
        )
        # mapa = mapa_t[self.mapdf.totalcases > 0].hvplot.polygons(
        #     geo=True,
        #     hover_cols=variables,
        #     alpha=0.7,
        #     colormap='BuPu',
        #     responsive=True,
        #     title=f'State at time {self.time_slider}',
        #     c=variables[-2],
        #     colorbar=True,
        #     tiles=True,
        # )
        # f = (mapa + series).cols(1)

        return mapa

    @param.depends('localities', 'time_slider', 'simulation_run')
    def altair_series(self):
        if len(self.df) == 0:
            return
        df = self.df[self.df.name == self.localities]
        variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]

        base = alt.Chart(df).mark_line(interpolate='step-after').encode(
            x='time:Q',
            y='incidence:Q'
        ).properties(
            width='container',
            height=300
        )

        chart = alt.vconcat()
        for i, y_enc in enumerate(variables[::2]):
            row = alt.hconcat()
            row |= base.encode(x='time', y=y_enc)
            if i < len(variables):
                row |= base.encode(x='time', y=variables[i + 1], tooltip=['time', 'incidence', 'Infectious'])

            chart &= row
        return chart


def refresh(e):
    # Clear caches
    get_sims.cache_clear()
    get_localities.cache_clear()
    read_map.cache_clear()
    read_simulation.cache_clear()
    # Update the Panel
    series_viewer.update()
    series_viewer.update_sims()
    series_viewer.update_localities()


def main():
    global series_viewer
    series_viewer = SeriesViewer()  # model_path=sm.output()[0], sim_run=sm.output()[1], locality=sm.output()[2])
    button = pnw.Button(name='Refresh', button_type='primary')
    button.on_click(refresh)
    # Assembling the panel
    material.sidebar.append(pn.Param(series_viewer, name='Control Panel'))
    # material.sidebar.append(button)
    material.sidebar.append(pn.layout.Divider())
    material.sidebar.append(series_viewer.view_meta)
    # material.sidebar.append(pn.Row(save_fname, save_button))
    # material.sidebar.append(pn.widgets.StaticText(sm.simulation_run.path))
    material.main.append(
        pn.Column(
            pn.Row(
                pn.Card(series_viewer.view_map, title='Final State')
            ),
            pn.Row(
                pn.Card(series_viewer.view_network, title='Network')
            ),
            pn.Row(
                pn.Card(series_viewer.view_series, title='Time Map')
            ),
            pn.Row(
                pn.Card(series_viewer.altair_series, title='Time Series')
            ),

        )
    )
    return material, series_viewer


# material.servable();


def show(pth):
    material, series_viewer = main()
    series_viewer.model_path = pth
    pn.serve(material, port=5006)


if __name__ == "__main__":
    material, series_viewer = main()
    series_viewer.model_path = '../demos/outdata-rio'
    refresh(None)
    pn.serve(material, port=5006, threaded=False)
