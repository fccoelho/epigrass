import pandas as pd
import geopandas as gpd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import panel as pn
import panel.widgets as pnw
import hvplot.pandas
import holoviews as hv
import geoviews as gv
import param
from sqlalchemy import create_engine
import glob
from functools import lru_cache

material = pn.template.MaterialTemplate(title='Epigrass Dashboard')

pn.config.sizing_mode = 'stretch_width'

xs = np.linspace(0, np.pi)
freq = pn.widgets.FloatSlider(name="Frequency", start=0, end=10, value=2)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=np.pi)


@pn.depends(freq=freq, phase=phase)
def sine(freq, phase):
    return hv.Curve((xs, np.sin(xs * freq + phase))).opts(
        responsive=True, min_height=400)


@pn.depends(freq=freq, phase=phase)
def cosine(freq, phase):
    return hv.Curve((xs, np.cos(xs * freq + phase))).opts(
        responsive=True, min_height=400)


pth = pn.widgets.TextInput(name='Directory', default='./demos/outdata-rio')


def get_sims(pth):
    """
    Get list of simulations available on SQLite database
    :param pth: Database file
    :return: List of tables. list of str
    """
    full_path = os.path.join(pth, 'Epigrass.sqlite')
    if os.path.exists(full_path):
        con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
        sims = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [s[0] for s in sims if not (s[0].endswith('_meta') or s[0].endswith('e'))]
    else:
        return []


# @lru_cache(maxsize=10)
def read_simulation(pth, simulation_name):
    full_path = os.path.join(os.path.abspath(pth), 'Epigrass.sqlite')
    # print(f'sqlite:///{full_path}?check_same_thread=False', simulation_name)
    con = create_engine(f'sqlite:///{full_path}?check_same_thread=False').connect()
    # con = create_engine('sqlite:///Epigrass.sqlite?check_same_thread=False').connect()
    simdf = pd.read_sql_query(f'select * from {simulation_name}', con)
    simdf.fillna(0, inplace=True)
    # print(simdf.head())
    return simdf


# @lru_cache(maxsize=10)
def read_map(pth):
    return gpd.read_file(pth)


pipeline = pn.pipeline.Pipeline()


class SimMap(param.Parameterized):
    name = 'Simulation Map'
    pth = './demos/outdata-rio'
    model_path = param.String(pth)
    maps = glob.glob(os.path.join(pth, '*.gpkg'))
    selector = param.ObjectSelector(default=None if not maps else maps[0], objects=maps)
    sims = get_sims(pth)
    simulation_run = param.ObjectSelector(default=None if not sims else sims[-1], objects=sims)
    localities = param.ObjectSelector(default='Locality', objects=[])
    df = None
    mapdf = None

    @param.depends('model_path', watch=True)
    def _dir_update(self):
        maps = glob.glob(os.path.join(self.model_path, '*.gpkg'))
        self.param['selector'].objects = maps
        self.selector = maps[0]
        sims = get_sims(self.model_path)
        self.param['simulation_run'].objects = sims
        if sims:
            self.simulation_run = sims[0]

    @param.depends('simulation_run', watch=True)
    def _sim_update(self):
        self.df = read_simulation(self.model_path, self.simulation_run)
        locs = self.df.name.unique()
        # print(locs)
        self.param['localities'].objects = list(locs)
        if locs.any():
            self.localities = locs[0]

    @param.depends('selector', 'localities')
    def view(self):
        # print(self.selector, type(self.selector), self.sims, os.getcwd())
        if self.selector:
            self.mapdf = read_map(self.selector)
            f = self.mapdf.hvplot.polygons(geo=True, c='prevalence',
                                           width=800,
                                           colorbar=True,
                                           clabel='Prevalence'
                                           )

            return f
        else:
            return hv.DynamicMap(sine)

    @param.output(model_path=param.String, sim_run=param.String, locality=param.String)
    def output(self):
        return self.model_path, self.simulation_run, self.localities

    def panel(self):
        return pn.Row(self.param, self.view)


sm = SimMap()

pipeline.add_stage('SimMap', sm)


class SeriesViewer(param.Parameterized):
    model_path = param.String(precedence=-1)
    sim_run = param.String(precedence=-1)
    locality = param.String(default='Rodoviaria')
    time_slider = param.Integer(default=1, bounds=(1, 300))

    @param.depends('sim_run', 'locality', 'time_slider')
    def view(self):
        mapdf = read_map(os.path.join(self.model_path, 'Data.gpkg'))
        df = read_simulation(self.model_path, self.sim_run)
        # print('==>mapdf: ', df.name[0], mapdf['name'], self.sim_run)
        if len(df) == 0:
            return pn.indicators.LoadingSpinner(value=True, width=100, height=100)
        time = df.time.min()
        # self.time_slider.bounds = (1, df.time.max())
        variables = [c for c in df.columns if c not in ['name', 'time', 'geocode', 'lat', 'longit']]
        # values = self.df[(self.df.name == locality) & (self.df.time == time)][variables].iloc[0]
        print('==> ', mapdf.columns)
        name_col = [c for c in mapdf if df.name[0] in list(mapdf[c])][0]
        mapa_t = pd.merge(mapdf, df[df.time == self.time_slider][['name', 'time'] + variables],
                          left_on=name_col, right_on='name')
        series = df[df.name == self.locality].hvplot.line(
            width=400,
            x='time',
            y=variables,
            subplots=True,
            value_label='Cases'
        ).cols(3)
        mapa = mapa_t.hvplot.polygons(
            geo=True,
            hover_cols=variables,
            title=f'State at time {self.time_slider}',
            c=variables[-2],
            colorbar=True
        )
        return (series + mapa).cols(1)

    def panel(self):
        return pn.Row(self.param, self.view)


series_viewer = SeriesViewer(model_path=sm.output()[0], sim_run=sm.output()[1], locality=sm.output()[2])
pipeline.add_stage('Series Viewer', series_viewer)
# print(pipeline)

material.sidebar.append(pn.Param(sm, name='Simulation Parameters'))

# material.sidebar.append(pn.widgets.StaticText(sm.simulation_run.path))
material.main.append(
    pn.Column(
        pn.Row(
            pn.Card(sm.view)
        ),
        pn.Row(
            pn.Card(series_viewer.view, title='Series')
        ),
        pn.Row(
            pn.Card(pn.Param(series_viewer), title='Controls')
        )
    )
)
material.servable();
