from dash import Dash, html, dcc, callback, Output, Input
import time
import threading
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import numpy as np

storage.init_storage()

def collect_data():
    while True:
        try:
            for i in range(1, 7):
                data = fetch_data(i)
                storage.add_measurements(i, data)
            storage.expire_data(60)

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
        dcc.Graph(
            id='hm-subplots',
            figure={}
        ),
        dcc.Graph(
            id='hm-take2',
            figure={}
        ),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=100,
        n_intervals=0
    )
])

@callback(
    [Output('sensor-graph', 'figure'), 
     Output('hm-subplots', 'figure'),
     Output('hm-take2', 'figure')],
    [Input('patient-dropdown', 'value'), 
     Input('sensor-checklist', 'value'), 
     Input('interval-component', 'n_intervals')],
)
def update_output(patient_id, sensor_ids, n_intervals):
    patient_data = storage.get_storage()[int(patient_id)]
    firstname = patient_data['firstname']
    lastname = patient_data['lastname']
    timestamps = patient_data['traces']['timestamps']
    
    last_measurement = storage.get_last_measurement(int(patient_id))

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
    
    layout = {
        'title': f'Scatter for sensors - patient {firstname} {lastname}',
        'height': 400,
        'width': 600,
    }  

    # Wykres heatmap dla ostatniego pomiaru
    l0_h = px.imshow(np.array([last_measurement['L0_value']]).reshape(1, 1), color_continuous_scale='Plasma', text_auto=True)
    l1_h = px.imshow(np.array([last_measurement['L1_value']]).reshape(1, 1), color_continuous_scale='Plasma')
    l2_h = px.imshow(np.array([last_measurement['L2_value']]).reshape(1, 1), color_continuous_scale='Plasma')
    
    to_display = [
        [last_measurement['L0_value'], last_measurement['R0_value']],
        [last_measurement['L1_value'], last_measurement['R1_value']],
        [last_measurement['L2_value'], last_measurement['R2_value']],
    ]
    
    to_display_arr = np.array(to_display)
    
    another_take = px.imshow(to_display_arr)

    # Wykres kolumnowy dla L0
    l0_values = patient_data['traces']['L0_values']
    l0_color_scale = px.colors.sequential.Plasma
    l0_chart_data = [{
        'x': ['L0'],
        'y': [l0_values[-1]],
        'type': 'bar',
        'marker': {'color': [l0_color_scale[int(l0_values[-1] / 1000 * (len(l0_color_scale) - 1))]]},
    }]
    
    #another_take = make_subplots(rows=1, cols=3, subplot_titles=['L0 Heatmap', 'L1 Heatmap', 'L2 Heatmap'])

    # Połączenie heatmap w jeden subplot
    fig_heatmaps = make_subplots(rows=1, cols=3, subplot_titles=['L0 Heatmap', 'L1 Heatmap', 'L2 Heatmap'])
    fig_heatmaps.add_trace(l0_h['data'][0], row=1, col=1)
    fig_heatmaps.add_trace(l1_h['data'][0], row=1, col=2)
    fig_heatmaps.add_trace(l2_h['data'][0], row=1, col=3)
    fig_heatmaps.update_layout(height=400, width=1200, title_text=f'Heatmaps - {firstname} {lastname}')

    return {'data': sensor_data, 'layout': layout}, fig_heatmaps, another_take


if __name__ == '__main__':
    app.run_server(debug=True)
