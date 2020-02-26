import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.tools as tls
import sqlite3
from sqlalchemy import create_engine
import os, glob
from functools import lru_cache

is_epigrass_folder = os.path.exists('Epigrass.sqlite')

@lru_cache(2)
def load_sim(sim):
    if sim is None:
        return pd.DataFrame(data={'time': range(2), 'name':0})
    con = create_engine('sqlite:///Epigrass.sqlite?check_same_thread=False').connect()
    data = pd.read_sql_table(sim, con)
    con.close()
    return data


def get_sims():
    if is_epigrass_folder:
        con = create_engine('sqlite:///Epigrass.sqlite?check_same_thread=False').connect()
        sims = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [s[0] for s in sims if not (s[0].endswith('_meta') or s[0].endswith('e'))]
    else:
        return ['No simulations found']


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Epigrass Dashboard'),

    html.Div(children='''
        Visualize your Simulations.
    '''),
    html.H3('Simulations:'),
    dcc.Dropdown(
        id='sim-drop',
        options=[{'label': s, 'value': s} for s in get_sims()],
    ),
    html.Div(id='sim-table'),
    html.Div(children=[
        html.B('Series:'),
        dcc.Dropdown(id='columns', multi=True, searchable=True,)], style={'width': '48%', 'display': 'inline-block'}),
    html.Div(children=[
        html.B('Localities:'),
        dcc.Dropdown(id='localities', multi=True, searchable=True),
    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'},),
    html.H4('Series:'),
    dcc.Graph(id='series-plot'),
    dcc.Graph(id='bubble-map'),

])


## Callbacks

@app.callback(
    Output(component_id='sim-table', component_property='children'),
    [Input(component_id='sim-drop', component_property='value')]
)
def update_sim_table(sim_name):
    try:
        df = load_sim(sim_name)
        return generate_table(df)
    except TypeError as e:
        return html.P('No data')


@app.callback(
    Output(component_id='series-plot', component_property='figure'),
    [Input(component_id='columns', component_property='value'),
     Input(component_id='sim-drop', component_property='value'),
     Input(component_id='localities', component_property='value')]
)
def update_series_plot(columns_selected, sim_name, localities):
    df = load_sim(sim_name)
    if localities and localities[0] is not None:
        df = df[df.name.isin(localities)]
    tf = df.time.max()
    traces = []
    cols = columns_selected
    if not cols:
        cols = df.columns[5:7]
    for c in cols:
        if c in ['geocode,'    'time', 'name', 'lat', 'longit']:
            continue
        traces.append(dict(
            x=df.time,
            y=df[c],
            text=df['name'],
            mode='line',
            opacity=0.7,
            name=c
        ))
    return {
        'data': traces,
        'layout': dict(
            xaxis={'type': 'linear', 'title': 'time',
                   'range': [0, tf]},
            yaxis={'title': 'Individuals'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            transition={'duration': 500},
        )
    }


@app.callback(
    Output(component_id='columns', component_property='options'),
    [Input(component_id='sim-drop', component_property='value')]
)
def fill_columns(sim_name):
    try:
        df = load_sim(sim_name)
        return [{'label': c, 'value': c} for c in df.columns if c not in ['geocode,'    'time', 'name', 'lat', 'longit']]
    except (TypeError, ValueError) as e:
        return []

@app.callback(
    Output(component_id='localities', component_property='options'),
    [Input(component_id='sim-drop', component_property='value')]
)
def fill_localities(sim_name):
    try:
        df = load_sim(sim_name)
        return [{'label': c, 'value': c} for c in set(df.name)]
    except (TypeError, ValueError) as e:
        return []

@app.callback(
    Output(component_id='bubble-map', component_property='figure'),
    [Input(component_id='sim-drop', component_property='value')]
)
def draw_bubble_map(val):
    import json
    maps = glob.glob('*.shp')
    if maps:
        mapdf = gpd.read_file('Data.shp')
        mapjson = json.loads(mapdf.to_json())
        ax = mapdf.plot(column='prevalence', legend=True)
        mfig = ax.get_figure()
        fig_url = tls.mpl_to_plotly(mfig, resize=True)
        fig = px.choropleth(mapdf, geojson=mapjson, color='prevalence',  hover_name='name', hover_data=['prevalence'],
                            color_continuous_scale='viridis', scope='south america',
                             )

    return fig

def main():
    app.run_server(debug=True)





if __name__ == '__main__':
    main()
