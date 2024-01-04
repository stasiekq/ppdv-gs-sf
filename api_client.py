import requests

def fetch_data(patient_id: int):
    url = f'http://tesla.iem.pw.edu.pl:9080/v2/monitor/{patient_id}'

    try:
        response = requests.get(url)
    except requests.ConnectionError:
        return "Connection Error"

    response_json = response.json()

    return {
        'birthdate': response_json['birthdate'],
        'disabled': response_json['disabled'],
        'firstname': response_json['firstname'],
        'lastname': response_json['lastname'],
        'trace': {
            'timestamp': response_json['trace']['id'],
            'L0_value': response_json['trace']['sensors'][0]['value'],
            'L0_anomaly': response_json['trace']['sensors'][0]['anomaly'],
            'L1_value': response_json['trace']['sensors'][1]['value'],
            'L1_anomaly': response_json['trace']['sensors'][1]['anomaly'],
            'L2_value': response_json['trace']['sensors'][2]['value'],
            'L2_anomaly': response_json['trace']['sensors'][2]['anomaly'],
            'R0_value': response_json['trace']['sensors'][3]['value'],
            'R0_anomaly': response_json['trace']['sensors'][3]['anomaly'],
            'R1_value': response_json['trace']['sensors'][4]['value'],
            'R1_anomaly': response_json['trace']['sensors'][4]['anomaly'],
            'R2_value': response_json['trace']['sensors'][5]['value'],
            'R2_anomaly': response_json['trace']['sensors'][5]['anomaly'],
        },
    }