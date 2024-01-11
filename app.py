from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import time
import threading
import plotly.express as px

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
    html.H1(children='PPDV Final Project', style={'textAlign': 'center'}),
    dcc.Dropdown(['1', '2', '3', '4', '5', '6'], '1', id='patient-dropdown'),
    dcc.Checklist(['L0', 'L1', 'L2', 'R0', 'R1', 'R2'], ['L0'], id='sensor-checklist', inline=True),
    html.Div([
        dcc.Graph(
            id='sensor-graph',
            figure={}
        ),
        html.Div([
            dcc.Graph(
                id='l0-column-chart',
                figure={}
            ),
            dcc.Graph(
                id='l1-column-chart',
                figure={}
            ),
            dcc.Graph(
                id='l2-column-chart',
                figure={}
            ),
        ], style={'display': 'flex', 'flexDirection': 'row'}),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=100,
        n_intervals=0
    )
])

@callback(
    [Output('sensor-graph', 'figure'), 
     Output('l0-column-chart', 'figure'), 
     Output('l1-column-chart', 'figure'), 
     Output('l2-column-chart', 'figure')],
    [Input('patient-dropdown', 'value'), 
     Input('sensor-checklist', 'value'), 
     Input('interval-component', 'n_intervals')],
)
def update_output(patient_id, sensor_ids, n_intervals):
    patient_data = storage.get_storage()[int(patient_id)]
    firstname = patient_data['firstname']
    lastname = patient_data['lastname']
    timestamps = patient_data['traces']['timestamps']

    # Wykres punktowy
    sensor_data = []
    for sensor_id in sensor_ids:
        trace = {
            'x': timestamps,
            'y': patient_data['traces'][f'{sensor_id}_values'],
            'type': 'scatter',
            'name': f'{sensor_id} sensor',
        }
        sensor_data.append(trace)

    # Wykres kolumnowy dla L0
    l0_values = patient_data['traces']['L0_values']
    l0_color_scale = px.colors.sequential.Plasma
    l0_chart_data = [{
        'x': ['L0'],
        'y': [l0_values[-1]],
        'type': 'bar',
        'marker': {'color': [l0_color_scale[int(l0_values[-1] / 1000 * (len(l0_color_scale) - 1))]]},
    }]

    layout = {
        'title': f'Scatter for sensors - patient {firstname} {lastname}',
        'height': 400,
        'width': 600,
    }

    l0_chart_layout = {
        'title': f'L0 Column Chart - {firstname} {lastname}',
        'barmode': 'group',
        'height': 400,
        'width': 600,
    }
    
    # Wykres kolumnowy dla L1
    l1_values = patient_data['traces']['L1_values']
    l1_color_scale = px.colors.sequential.Plasma
    l1_chart_data = [{
        'x': ['L1'],
        'y': [l1_values[-1]],
        'type': 'bar',
        'marker': {'color': [l1_color_scale[int(l1_values[-1] / 1000 * (len(l1_color_scale) - 1))]]},
    }]

    layout = {
        'title': f'Scatter for sensors - patient {firstname} {lastname}',
        'height': 400,
        'width': 600,
    }

    l1_chart_layout = {
        'title': f'L1 Column Chart - {firstname} {lastname}',
        'barmode': 'group',
        'height': 400,
        'width': 600,
    }
    
    # Wykres kolumnowy dla L2
    l2_values = patient_data['traces']['L2_values']
    l2_color_scale = px.colors.sequential.Plasma
    l2_chart_data = [{
        'x': ['L2'],
        'y': [l2_values[-1]],
        'type': 'bar',
        'marker': {'color': [l2_color_scale[int(l2_values[-1] / 1000 * (len(l2_color_scale) - 1))]]},
    }]

    layout = {
        'title': f'Scatter for sensors - patient {firstname} {lastname}',
        'height': 400,
        'width': 600,
    }

    l2_chart_layout = {
        'title': f'L2 Column Chart - {firstname} {lastname}',
        'barmode': 'group',
        'height': 400,
        'width': 600,
    }
    

    return {'data': sensor_data, 'layout': layout}, {'data': l0_chart_data, 'layout': l0_chart_layout}, {'data': l1_chart_data, 'layout': l1_chart_layout}, {'data': l2_chart_data, 'layout': l2_chart_layout}

if __name__ == '__main__':
    app.run_server(debug=True)
