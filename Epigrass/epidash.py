import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3
import os

is_epigrass_folder = os.path.exists('Epigrass.sqlite')

def load_sim(sim):
    con = sqlite3.connect("Epigrass.sqlite")
    data = pd.read_sql_table(sim, con)
    return data

def get_sims():
    if is_epigrass_folder:
        con = sqlite3.connect("Epigrass.sqlite")
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        sims = (cur.fetchall())
        return [s[0] for s in sims if not s.endswith('_meta')]
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
        EpiDash: visualize your Simulations.
    '''),
    html.H3('Simulations:'),
    dcc.Dropdown(
        id='sim-drop',
        options=[{'label': s, 'value': s} for s in get_sims()],
    ),
    html.Div(id='sim-table'),

    ])

@app.callback(
    Output(component_id='sim-table', component_property='children'),
    [Input(component_id='sim-drop', component_property='value')]
)
def update_sim_table(sim_name):
    df = load_sim(sim_name)
    return generate_table(df)

def main():
    app.run_server(debug=True)

if __name__ == '__main__':
    main()