from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import storage
from api_client import fetch_data
import time

collector_running = True

class DataAccumulator(threading.Thread):
    def run():
        while collector_running:
            storage.add_measurements(1, fetch_data(1))
            storage.add_measurements(2, fetch_data(2))
            storage.add_measurements(3, fetch_data(3))
            storage.add_measurements(4, fetch_data(4))
            storage.add_measurements(5, fetch_data(5))
            storage.add_measurements(6, fetch_data(6))

            storage.expire_data(600)
            time.sleep(0.2)


app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='PPDV Final Project', style={'textAlign':'center'}),
])

if __name__ == '__main__':
    storage.init_storage()
    app.run_server(debug=True)
