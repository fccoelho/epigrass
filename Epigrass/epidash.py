import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os

is_epigrass_folder = os.path.exists('Epigrass.sqlite')


def load_sim(sim):
    if sim is None:
        return pd.DataFrame(data={'time': range(100), 'name':0})
    con = create_engine('sqlite:///Epigrass.sqlite').connect()
    data = pd.read_sql_table(sim, con)
    con.close()
    return data


def get_sims():
    if is_epigrass_folder:
        con = sqlite3.connect("Epigrass.sqlite")
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        sims = (cur.fetchall())
        con.close()
        return [s[0] for s in sims if not s[0].endswith('_meta')]
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
    dcc.Graph(id='series-plot'),
    dcc.Dropdown(id='columns', multi=True, searchable=True,),

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
     Input(component_id='sim-drop', component_property='value')]
)
def update_series_plot(columns_selected, sim_name):
    df = load_sim(sim_name)
    tf = df.time.max()
    traces = []
    for c in df.columns:
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
            yaxis={'title': 'Individuals', 'range': [0, 90]},
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
    except TypeError as e:
        return []


def main():
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
