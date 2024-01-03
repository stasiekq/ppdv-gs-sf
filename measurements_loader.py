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
                "birthdate": data["birthdate"],
                "disabled": data["disabled"],
                "firstname": data["firstname"],
                "lastname": data["lastname"],
                "name": data["name"],
                "timestamps": [],
                "L0_values": [],
                "L0_anomalies": [],
                "L1_values": [],
                "L1_anomalies": [],
                "L2_values": [],
                "L2_anomalies": [],
                "R0_values": [],
                "R0_anomalies": [],
                "R1_values": [],
                "R1_anomalies": [],
                "R2_values": [],
                "R2_anomalies": [],
                "_expire_ts": []
            }
            storage[patient_id] = patient_data
        else:
            patient_data = storage[patient_id]

        # convert timestamp
        timestamp_str = str(data["timestamp"])
        timestamp = f"{timestamp_str[0:-12]}:{timestamp_str[-12:-10]}:{timestamp_str[-10:-8]}"
        timestamps_amount = len(patient_data["timestamps"])
        if timestamps_amount > 0 and patient_data["timestamps"][timestamps_amount - 1] == timestamp:  # Add smoothing
            patient_data["values"][timestamps_amount - 1] = \
                smooth_data(data["values"], patient_data["values"][timestamps_amount - 1])
        else:  # Add record
            patient_data["timestamps"].append(timestamp)
            patient_data["values"].append(data["values"])
            patient_data["anomalies"].append(data["anomalies"])
            patient_data["_expire_ts"].append(time.time())
    except TypeError:
        logging.warning("No data! Make sure you are connected to VPN")


def smooth_data(data1, data2):
    smoothed = [0, 0, 0, 0, 0, 0]
    for i in range(0, 6):
        smoothed[i] = (data1[i] + data2[i]) / 2
    return smoothed


def expire_data(s):
    storage = get_storage()
    for patient_id, patient_data in storage.items():
        ts = time.time()
        while len(patient_data["_expire_ts"]) > 0 and patient_data["_expire_ts"][0] < (ts - s):
            patient_data["timestamps"].pop(0)
            patient_data["values"].pop(0)
            patient_data["anomalies"].pop(0)
            patient_data["_expire_ts"].pop(0)