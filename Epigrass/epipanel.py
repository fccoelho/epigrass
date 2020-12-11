import pandas as pd
import altair as alt
import geopandas as gpd
import os
import panel as pn
import panel.widgets as pnw
import hvplot.pandas
import param
from sqlalchemy import create_engine
import glob
# import gpdvega
from functools import lru_cache

material = pn.template.MaterialTemplate(title='Epigrass Dashboard', favicon='../egicon.png', logo='../egicon.png')

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
        return []


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
    return df


@lru_cache(maxsize=10)
def read_simulation(fname, simulation_name, locality=None):
    full_path = os.path.join(os.path.abspath(fname), 'Epigrass.sqlite')
    if not os.path.exists(full_path):
        print(f'==> File {full_path} not found')
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


# pipeline = pn.pipeline.Pipeline()
class SeriesViewer(param.Parameterized):
    model_path = param.String()#default='../demos/outdata-rio')
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
            self.simulation_run = sims[0]
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

"""
            )
        else:
            return pn.pane.Markdown("")

    @param.depends('map_selector', 'simulation_run')
    def view_map(self):
        if self.map_selector and self.mapdf is not None:
            mapdf = self.mapdf
            map10 = mapdf.sort_values('totalcases', ascending=False).iloc[:15]
            brush = alt.selection_single(encodings=["y"], on="mouseover", empty='none')
            color = alt.Color('prevalence', scale=alt.Scale(type='pow', exponent=0.4))
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
            color='incidence',
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
            y='incidence:Q',
        ).properties(
            width='container',
            height=300
        )

        chart = alt.vconcat()
        for i, y_enc in enumerate(variables[::2]):
            row = alt.hconcat()
            row |= base.encode(x='time', y=y_enc)
            if i < len(variables):
                row |= base.encode(x='time', y=variables[i+1])

            chart &= row
        return chart


series_viewer = SeriesViewer()  # model_path=sm.output()[0], sim_run=sm.output()[1], locality=sm.output()[2])

material.sidebar.append(pn.Param(series_viewer, name='Control Panel'))
material.sidebar.append(pn.layout.Divider())
material.sidebar.append(series_viewer.view_meta)

# material.sidebar.append(pn.widgets.StaticText(sm.simulation_run.path))
material.main.append(
    pn.Column(
        pn.Row(
            pn.Card(series_viewer.view_map, title='Final State')
        ),
        pn.Row(
            pn.Card(series_viewer.view_series, title='Time Map')
        ),
        pn.Row(
            pn.Card(series_viewer.altair_series, title='Time Series')
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
