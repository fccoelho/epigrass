import pandas as pd
import geopandas as gpd
import os
import panel as pn
import panel.widgets as pnw
import hvplot.pandas
import param
from sqlalchemy import create_engine
import glob
from functools import lru_cache

material = pn.template.MaterialTemplate(title='Epigrass Dashboard')

pn.config.sizing_mode = 'stretch_width'


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
        return [s[0] for s in sims if not (s[0].endswith('_meta') or s[0].endswith('e'))]
    else:
        print(f'==> File {full_path} not found')
        return []


@lru_cache(maxsize=10)
def read_simulation(fname, simulation_name, locality):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        return pd.DataFrame()

    con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
    simdf = pd.read_sql_query(f"select * from {simulation_name} where name='{locality}'", con)
    simdf.fillna(0, inplace=True)
    return simdf

@lru_cache(maxsize=10)
def get_localities(fname, simulation_name):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
        return []
    con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
    locs = pd.read_sql_query(f'select distinct name from {simulation_name}', con)
    return [l[0] for l in locs.values]

@lru_cache(maxsize=10)
def read_map(fname):
    if os.path.exists(fname):
        return gpd.read_file(fname)
    else:
        gpd.GeoDataFrame()


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

    @param.depends('map_selector', 'model_path', watch=True)
    def update_sims(self):
        sims = get_sims(self.model_path)
        self.param['simulation_run'].objects = sims
        if sims:
            self.simulation_run = sims[0]

    @param.depends('simulation_run', watch=True)
    def update_localities(self):
        locs = get_localities(self.model_path, self.simulation_run)
        self.param['localities'].objects = list(locs)
        if locs:
            self.localities = locs[0]

    @param.depends('map_selector', 'simulation_run')
    def view_map(self):
        if self.map_selector:
            self.mapdf = read_map(self.map_selector)
            f = self.mapdf.hvplot.polygons(geo=True, c='prevalence',
                                           alpha=0.7,
                                           responsive=True,
                                           colorbar=True,
                                           tiles=True
                                           )

            return f
        else:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)

    @param.depends('localities', 'time_slider')
    def view_series(self):
        if self.simulation_run is None:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)
        mapdf = read_map(os.path.join(self.model_path, 'Data.gpkg'))
        df = read_simulation(self.model_path, self.simulation_run, self.localities)
        if len(df) == 0:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)
        time = df.time.min()
        self.param['time_slider'].bounds = (df.time.min(), df.time.max())
        variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]


        name_col = [c for c in mapdf if df.name[0] in list(mapdf[c])][0]
        mapa_t = pd.merge(mapdf, df[df.time == self.time_slider][['name', 'time'] + variables],
                          left_on=name_col, right_on='name')
        series = df[df.name == self.localities].hvplot.line(
            width=400,
            x='time',
            y=variables,
            responsive=True,
            subplots=True,
            shared_axes=False,
            value_label=f'Cases at {self.localities}'
        ).cols(3)
        mapa = mapa_t.hvplot.polygons(
            geo=True,
            hover_cols=variables,
            alpha=0.7,
            responsive=True,
            title=f'State at time {self.time_slider}',
            c=variables[-2],
            colorbar=True,
            tiles=True
        )
        return (mapa + series).cols(1)

    def panel(self):
        return pn.Row(self.param, self.view)


series_viewer = SeriesViewer()  # model_path=sm.output()[0], sim_run=sm.output()[1], locality=sm.output()[2])

material.sidebar.append(pn.Param(series_viewer, name='Control Panel'))

# material.sidebar.append(pn.widgets.StaticText(sm.simulation_run.path))
material.main.append(
    pn.Column(
        pn.Row(
            pn.Card(series_viewer.view_map, title='Final State')
        ),
        pn.Row(
            pn.Card(series_viewer.view_series, title='Series')
        ),

    )
)
material.servable();

def show(pth):
    series_viewer.model_path = pth
    pn.serve(material, port=5006)

if __name__ == "__main__":
    pn.serve(material, port=5006)
    # M = MetaInfo()
    # S = SimMap()
    # SV = SeriesViewer()
