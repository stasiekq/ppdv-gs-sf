from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import time
import threading
from plotly.subplots import make_subplots


collector_running = True
storage.init_storage()

for i in range(25):
    storage.add_measurements(1, fetch_data(1))
    storage.add_measurements(2, fetch_data(2))
    storage.add_measurements(3, fetch_data(3))
    storage.add_measurements(4, fetch_data(4))
    storage.add_measurements(5, fetch_data(5))
    storage.add_measurements(6, fetch_data(6))

    time.sleep(0.2)


app = Dash(__name__)

print(storage.get_storage()[1]['traces']['L0_values'])
print(storage.get_storage()[1]['traces']['L1_values'])
print(storage.get_storage()[1]['traces']['L2_values'])
print(storage.get_storage()[1]['traces']['R0_values'])
print(storage.get_storage()[1]['traces']['R1_values'])
print(storage.get_storage()[1]['traces']['R2_values'])


app.layout = html.Div([
    html.H1(children='PPDV Final Project', style={'textAlign':'center'}),
    dcc.Dropdown(['1', '2', '3', '4', '5', '6'], '1', id='patient-dropdown'),
    dcc.Dropdown(['L0','L1','L2','R0','R1','R2'], 'L0', id='sensor-dropdown'),
    dcc.Graph(
        id='sensor-graph',
        figure={}
    )
])

@callback(
    Output('sensor-graph', 'figure'),
    [Input('patient-dropdown', 'value'),Input('sensor-dropdown', 'value')],
)
def update_output(patient_id, sensor_id):
    return {
        'data': [
            {
                'x': storage.get_storage()[int(patient_id)]['traces']['timestamps'],
                'y': storage.get_storage()[int(patient_id)]['traces'][f'{sensor_id}_values'],
                'type': 'scatter',
                'name': f'{sensor_id} sensor'
            },
        ],
        'layout': {
            'title': f'Scatter of {sensor_id} sensor'
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)
