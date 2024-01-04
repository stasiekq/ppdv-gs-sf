from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import time
import threading

collector_running = True
storage.init_storage()

for i in range(5):
    storage.add_measurements(1, fetch_data(1))
    storage.add_measurements(2, fetch_data(2))
    storage.add_measurements(3, fetch_data(3))
    storage.add_measurements(4, fetch_data(4))
    storage.add_measurements(5, fetch_data(5))
    storage.add_measurements(6, fetch_data(6))

    time.sleep(3)


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='PPDV Final Project', style={'textAlign':'center'}),
    html.Div(id='patients-figures')
])

if __name__ == '__main__':
    app.run_server(debug=True)
