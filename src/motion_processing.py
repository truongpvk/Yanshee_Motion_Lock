from __future__ import print_function
import time
import openadk
from openadk.rest import ApiException
from pprint import pprint

robo_ip = '10.220.5.226' # Change to robot API

# create an instance of the API class
configuration = openadk.Configuration()
configuration.host = f'http://{robo_ip}:9090/v1'
api_instance = openadk.MotionsApi(openadk.ApiClient(configuration)) # Change API options

def putMotion(action: str, direction: str, repeat: int, speed='normal', operation='start', timestamp=2000):
    if repeat == 0:
        print('Robot may be had unlimited actions!')
        return 0

    body = {
        'operation': operation,
        'motion': {
            'name': action,
            'direction': direction,
            'repeat': repeat,
            'speed': speed
        },
        'timestamp': timestamp
    }

    api_response = api_instance.put_motions(body)
    return int(api_response.data.total_time)