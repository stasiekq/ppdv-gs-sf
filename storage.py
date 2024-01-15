import logging
import time

global _storage


def init_storage():
    global _storage
    _storage = {}
    return _storage


def get_storage():
    global _storage
    return _storage


def add_measurements(patient_id, data):
    storage = get_storage()

    try:
        if patient_id not in storage:
            patient_data = {
                'birthdate': data['birthdate'],
                'disabled': data['disabled'],
                'firstname': data['firstname'],
                'lastname': data['lastname'],
                'traces': {
                    'timestamps': [],
                    'L0_values': [],
                    'L0_anomalies': [],
                    'L1_values': [],
                    'L1_anomalies': [],
                    'L2_values': [],
                    'L2_anomalies': [],
                    'R0_values': [],
                    'R0_anomalies': [],
                    'R1_values': [],
                    'R1_anomalies': [],
                    'R2_values': [],
                    'R2_anomalies': [],
                    '_expire_ts': []
                }
            }
            storage[patient_id] = patient_data
        else:
            patient_data = storage[patient_id]

        # convert timestamp
        timestamp_str = str(data['trace']['timestamp'])
        timestamp = f"{timestamp_str[0:-12]}:{timestamp_str[-12:-10]}:{timestamp_str[-10:-8]}"
        patient_data['traces']['timestamps'].append(timestamp)
        patient_data['traces']['L0_values'].append(data['trace']['L0_value'])
        patient_data['traces']['L0_anomalies'].append(data['trace']['L0_anomaly'])
        patient_data['traces']['L1_values'].append(data['trace']['L1_value'])
        patient_data['traces']['L1_anomalies'].append(data['trace']['L1_anomaly'])
        patient_data['traces']['L2_values'].append(data['trace']['L2_value'])
        patient_data['traces']['L2_anomalies'].append(data['trace']['L2_anomaly'])
        patient_data['traces']['R0_values'].append(data['trace']['R0_value'])
        patient_data['traces']['R0_anomalies'].append(data['trace']['R0_anomaly'])
        patient_data['traces']['R1_values'].append(data['trace']['R1_value'])
        patient_data['traces']['R1_anomalies'].append(data['trace']['R1_anomaly'])
        patient_data['traces']['R2_values'].append(data['trace']['R2_value'])
        patient_data['traces']['R2_anomalies'].append(data['trace']['R2_anomaly'])
        patient_data['traces']['_expire_ts'].append(time.time())
    except TypeError:
        logging.warning('No data! Make sure you are connected to VPN')


def expire_data(s):
    storage = get_storage()
    for patient_id, patient_data in storage.items():
        ts = time.time()
        while len(patient_data['traces']['_expire_ts']) > 0 and patient_data['traces']['_expire_ts'][0] < (ts - s):
            patient_data['traces']['timestamps'].pop(0)
            patient_data['traces']['L0_values'].pop(0)
            patient_data['traces']['L0_anomalies'].pop(0)
            patient_data['traces']['L1_values'].pop(0)
            patient_data['traces']['L1_anomalies'].pop(0)
            patient_data['traces']['L2_values'].pop(0)
            patient_data['traces']['L2_anomalies'].pop(0)
            patient_data['traces']['R0_values'].pop(0)
            patient_data['traces']['R0_anomalies'].pop(0)
            patient_data['traces']['R1_values'].pop(0)
            patient_data['traces']['R1_anomalies'].pop(0)
            patient_data['traces']['R2_values'].pop(0)
            patient_data['traces']['R2_anomalies'].pop(0)
            patient_data['traces']['_expire_ts'].pop(0)

def get_last_measurement(patient_id):
    storage = get_storage()

    if patient_id in storage:
        patient_data = storage[patient_id]
        last_index = -1  # Index for the last measurement

        if patient_data['traces']['timestamps']:
            last_index = -1  # Index for the last measurement
            last_measurement = {
                'timestamp': patient_data['traces']['timestamps'][last_index],
                'L0_value': patient_data['traces']['L0_values'][last_index],
                'L0_anomaly': patient_data['traces']['L0_anomalies'][last_index],
                'L1_value': patient_data['traces']['L1_values'][last_index],
                'L1_anomaly': patient_data['traces']['L1_anomalies'][last_index],
                'L2_value': patient_data['traces']['L2_values'][last_index],
                'L2_anomaly': patient_data['traces']['L2_anomalies'][last_index],
                'R0_value': patient_data['traces']['R0_values'][last_index],
                'R0_anomaly': patient_data['traces']['R0_anomalies'][last_index],
                'R1_value': patient_data['traces']['R1_values'][last_index],
                'R1_anomaly': patient_data['traces']['R1_anomalies'][last_index],
                'R2_value': patient_data['traces']['R2_values'][last_index],
                'R2_anomaly': patient_data['traces']['R2_anomalies'][last_index]
            }
            return last_measurement
        else:
            logging.warning(f'No measurements available for patient {patient_id}')
            return None
    else:
        logging.warning(f'Patient {patient_id} not found in storage')
        return None