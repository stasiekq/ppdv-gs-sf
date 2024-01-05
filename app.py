from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import time
import threading
from plotly.subplots import make_subplots

storage.init_storage()

def collect_data():
    while True:
        try:
            for i in range(1, 7):
                data = fetch_data(i)
                storage.add_measurements(i, data)
            storage.expire_data(600)

            time.sleep(0.2)
        except Exception as e:
            print(f"Error collecting data: {e}")

thread = threading.Thread(target=collect_data)
thread.daemon = True
thread.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='PPDV Final Project', style={'textAlign':'center'}),
    dcc.Dropdown(['1', '2', '3', '4', '5', '6'], '1', id='patient-dropdown'),
    dcc.Checklist(['L0','L1','L2','R0','R1','R2'], ['L0'], id='sensor-checklist', inline=True),
    dcc.Graph(
        id='sensor-graph',
        figure={}
    ),
    dcc.Interval(
        id='interval-component',
        interval=100,
        n_intervals=0
    )
])

@callback(
    Output('sensor-graph', 'figure'),
    [Input('patient-dropdown', 'value'), Input('sensor-checklist', 'value'), Input('interval-component', 'n_intervals')],
)
def update_output(patient_id, sensor_ids, n_intervals):
    patient_data = storage.get_storage()[int(patient_id)]
    firstname = patient_data['firstname']
    lastname = patient_data['lastname']
    timestamps = patient_data['traces']['timestamps']

    data = []

    for sensor_id in sensor_ids:
        p = {
            'x': patient_data['traces']['timestamps'],
            'y': patient_data['traces'][f'{sensor_id}_values'],
            'type': 'scatter',
            'name': f'{sensor_id} sensor',
        }

        data.append(p)


    return {
        'data': data,
        'layout': {
            'title': f'Scatter for sensors - patient {firstname} {lastname}',
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)
