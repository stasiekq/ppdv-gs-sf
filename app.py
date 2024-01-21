from dash import Dash, html, dcc, callback, Output, Input
import time
import threading
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import storage
from api_client import fetch_data
import numpy as np
import sqlite3

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''

    CREATE TABLE IF NOT EXISTS patients (

        id INTEGER PRIMARY KEY,
        firstname TEXT,
        lastname TEXT,
        birthdate TEXT,
        disabled BOOLEAN

    )
    ''')

cursor.execute('''

    CREATE TABLE IF NOT EXISTS traces (

        id INTEGER PRIMARY KEY,
        patient_id INTEGER,
        timestamp TEXT,
        L0_value INTEGER,
        L0_anomaly BOOLEAN,
        L1_value INTEGER,
        L1_anomaly BOOLEAN,
        L2_value INTEGER,
        L2_anomaly BOOLEAN,
        R0_value INTEGER,
        R0_anomaly BOOLEAN,
        R1_value INTEGER,
        R1_anomaly BOOLEAN,
        R2_value INTEGER,
        R2_anomaly BOOLEAN,
        FOREIGN KEY(patient_id) REFERENCES patients(id)

    )
    ''')

connection.commit()

def add_trace(patient_id, data):
    id = data['trace']['timestamp']
    
    # convert timestamp
    timestamp_str = str(id)
    timestamp = f"{timestamp_str[0:-12]}:{timestamp_str[-12:-10]}:{timestamp_str[-10:-8]}"

    trace = (
        id,
        patient_id,
        timestamp,
        data['trace']['L0_value'],
        data['trace']['L0_anomaly'],
        data['trace']['L1_value'],
        data['trace']['L1_anomaly'],
        data['trace']['L2_value'],
        data['trace']['L2_anomaly'],
        data['trace']['R0_value'],
        data['trace']['R0_anomaly'],
        data['trace']['R1_value'],
        data['trace']['R1_anomaly'],
        data['trace']['R2_value'],
        data['trace']['R2_anomaly']
    )

    try:
        cursor.execute('''
            INSERT or IGNORE INTO traces (id, patient_id, timestamp, L0_value, L0_anomaly, L1_value, L1_anomaly, L2_value, L2_anomaly, R0_value, R0_anomaly, R1_value, R1_anomaly, R2_value, R2_anomaly)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', trace)
        connection.commit()

        rows_inserted = cursor.rowcount
        if rows_inserted > 0:
            print(f"Successfully added trace: {id}")
        else:
            print(f"No new row added for trace.")

    except Exception as e:
        print(f"Error adding trace: {trace}. Error: {str(e)}")

    connection.commit()

def add_patient(data):
    patient = (
        data['id'],
        data['firstname'],
        data['lastname'],
        data['birthdate'],
        data['disabled']
    )

    try:
        cursor.execute('''
            INSERT or IGNORE INTO patients (id, firstname, lastname, birthdate, disabled)
            VALUES (?, ?, ?, ?, ?)
        ''', patient)
        connection.commit()

        rows_inserted = cursor.rowcount
        if rows_inserted > 0:
            print(f"Successfully added patient: {patient}")
        else:
            print(f"No new row added for patient: {patient}. This patient might already exist in the database.")

    except Exception as e:
        print(f"Error adding patient: {patient}. Error: {str(e)}")

    connection.commit()

def get_patient_traces(patient_id):
    cursor.execute("SELECT * FROM traces WHERE patient_id = ?", [patient_id])
    return cursor.fetchall()

def get_last_trace(patient_id):
    cursor.execute("SELECT * FROM traces WHERE patient_id = ? ORDER BY timestamp DESC LIMIT 1", [patient_id])
    return cursor.fetchone()

def expire_data(seconds):
    cursor.execute("DELETE FROM traces WHERE timestamp < ?", [time.time() - seconds])
    connection.commit()

def collect_data():
    while True:
        try:
            for i in range(1, 7):
                data = fetch_data(i)
                add_trace(i, data)
            expire_data(600)

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
        # dcc.Graph(
        #     id='hm-subplots',
        #     figure={}
        # ),
        # dcc.Graph(
        #     id='hm-take2',
        #     figure={}
        # ),
    ], style={'overflowX': 'scroll', 'width': '1000px'}),
    dcc.Interval(
        id='interval-component',
        interval=100,
        n_intervals=0
    )
])

@callback(
    Output('sensor-graph', 'figure'),
    [Input('patient-dropdown', 'value'),
    Input('sensor-checklist', 'value'),
    # Input('interval-component', 'n_intervals')
    ],
)
def update_output(patient_id, sensor_ids):
    firstname = cursor.execute("SELECT firstname FROM patients WHERE id = ?", [patient_id]).fetchone()[0]
    lastname = cursor.execute("SELECT lastname FROM patients WHERE id = ?", [patient_id]).fetchone()[0]
    patient_data = {
        'traces': {
            'L0_values': [],
            'L1_values': [],
            'L2_values': [],
            'R0_values': [],
            'R1_values': [],
            'R2_values': [],
        },
        'timestamps': [],
    }

    for trace in get_patient_traces(patient_id):
        patient_data['traces']['L0_values'].append(trace[3])
        patient_data['traces']['L1_values'].append(trace[5])
        patient_data['traces']['L2_values'].append(trace[7])
        patient_data['traces']['R0_values'].append(trace[9])
        patient_data['traces']['R1_values'].append(trace[11])
        patient_data['traces']['R2_values'].append(trace[13])
        patient_data['timestamps'].append(trace[2])

    #Generate scatter plot
    sensor_data = []
    for sensor_id in sensor_ids:
        p = {
            'x': patient_data['timestamps'],
            'y': patient_data['traces'][f'{sensor_id}_values'],
            'name': f'{sensor_id} values',
            'type': 'scatter',
        }

        sensor_data.append(p)

    width_per_timestamp = 100
    total_width = max(len(patient_data['timestamps']) * width_per_timestamp, 1000)

    layout = {
        'title': f'Scatter for sensors - patient {firstname} {lastname}',
        'height': 400,
        'width': total_width,  # Increase the width to enable scrolling for 15 timestamps
    }  

    return {
        'data': sensor_data,
        'layout': layout
        }

    # Wykres heatmap dla ostatniego pomiaru
    # l0_h = px.imshow(np.array([last_measurement['L0_value']]).reshape(1, 1), color_continuous_scale='Plasma', text_auto=True)
    # l1_h = px.imshow(np.array([last_measurement['L1_value']]).reshape(1, 1), color_continuous_scale='Plasma')
    # l2_h = px.imshow(np.array([last_measurement['L2_value']]).reshape(1, 1), color_continuous_scale='Plasma')
    
    # to_display = [
    #     [last_measurement['L0_value'], last_measurement['R0_value']],
    #     [last_measurement['L1_value'], last_measurement['R1_value']],
    #     [last_measurement['L2_value'], last_measurement['R2_value']],
    # ]
    
    # to_display_arr = np.array(to_display)
    
    # another_take = px.imshow(to_display_arr)

    # Wykres kolumnowy dla L0
    # l0_values = patient_data['traces']['L0_values']
    # l0_color_scale = px.colors.sequential.Plasma
    # l0_chart_data = [{
    #     'x': ['L0'],
    #     'y': [l0_values[-1]],
    #     'type': 'bar',
    #     'marker': {'color': [l0_color_scale[int(l0_values[-1] / 1000 * (len(l0_color_scale) - 1))]]},
    # }]
    
    #another_take = make_subplots(rows=1, cols=3, subplot_titles=['L0 Heatmap', 'L1 Heatmap', 'L2 Heatmap'])

    # Połączenie heatmap w jeden subplot
    # fig_heatmaps = make_subplots(rows=1, cols=3, subplot_titles=['L0 Heatmap', 'L1 Heatmap', 'L2 Heatmap'])
    # fig_heatmaps.add_trace(l0_h['data'][0], row=1, col=1)
    # fig_heatmaps.add_trace(l1_h['data'][0], row=1, col=2)
    # fig_heatmaps.add_trace(l2_h['data'][0], row=1, col=3)
    # fig_heatmaps.update_layout(height=400, width=1200, title_text=f'Heatmaps - {firstname} {lastname}')


if __name__ == '__main__':
    app.run_server(debug=True)
