import requests
import pandas as pd
import re
import datetime
import time as tm
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as pe

url = 'https://api.coincap.io/v2/assets'
payload = {}
headers = {}

response = requests.get(url, headers=headers, data=payload)
currency = re.findall(r'"id":"(.*?)",', response.text)

bar = pe.bar()

date_from_widget = html.Div([
    html.Div('Дата начала периода (DD.MM.YYYY)', className="text-primary",),
    dcc.Input(
        id='DateFrom',
        type='text',
        style={'width': '140px', 'height': '40px'}
    )
])

date_to_widget = html.Div([
    html.Div('Дата конца периода (DD.MM.YYYY)', className="text-primary",),
    dcc.Input(
        id='DateTo',
        type='text',
        style={'width': '140px', 'height': '40px'}
    )
])

select_currency = html.Div([
    html.Div(''),
    dcc.Dropdown(currency, id='assets_dropdown', style={
        'width': '140px'
    })
])

gist = html.Div([
    dcc.Graph(id='value_graph', figure=bar, style={
        'height': '600px'
    })
])

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row(select_currency, style={'margin-top': '200px', 'margin-left': '60px',}),
            dbc.Row([
                dbc.Col(date_from_widget, style={'margin-top': '20px', 'margin-left': '10px'}),
                dbc.Col(date_to_widget, style={'margin-top': '20px', 'margin-left': '10px'})
            ])
        ], width=3),
        dbc.Col(gist, width=8)])
])


@app.callback(
    Output('value_graph', 'figure'),
    [Input('assets_dropdown', 'value'),
     Input('DateFrom', 'value'),
     Input('DateTo', 'value')]
)
def get_new_graph(curency, date_from_value, date_to_value):
    date_from = datetime.datetime.strptime(date_from_value, "%d.%m.%Y").date()
    date_from_unix = (tm.mktime(date_from.timetuple())) * 1000

    date_to = datetime.datetime.strptime(date_to_value, "%d.%m.%Y").date()
    date_to_unix = (tm.mktime(date_to.timetuple())) * 1000

    url = f'https://api.coincap.io/v2/assets/{curency}/history?interval=d1&start={date_from_unix}&end={date_to_unix}'
    headers = {}
    payload = {}
    response2 = requests.get(url, headers=headers, data=payload)

    history = re.findall(r'"priceUsd":"(.*?)",', response2.text)

    prices = []
    for price in history:
        prices.append(round(float(price), 2))

    times = re.findall(r'"time":(.*?),', response2.text)
    date = []
    for time in times:
        date.append(datetime.datetime.fromtimestamp(int(time) / 1000).date())

    df = pd.DataFrame({'price': prices, 'time': date})

    bar = pe.bar(df, x='time', y='price')
    return bar


if __name__ == '__main__':
    app.run_server(debug=False)