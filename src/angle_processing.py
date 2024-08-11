from __future__ import print_function
import time
import openadk
from openadk.rest import ApiException
from pprint import pprint

robo_ip = '10.220.5.226' # Change to robot API

# create an instance of the API class
configuration = openadk.Configuration()
configuration.host = f'http://{robo_ip}:9090/v1'
api_instance = openadk.SensorsApi(openadk.ApiClient(configuration)) # Change API options

angle_offset = 20.0

#angle per step
turn_right = 36.2
turn_left = 15.5

def getSensorResponse(api_instance):
    api_response = api_instance.get_sensors_gyro()
    return api_response

def getAngle(response):
    return float(response.data.gyro[0].euler_z)

def isAccept(z, origin_z):
    global angle_offset

    offset = abs(z - origin_z)

    response = {
        'isAccept': False,
    }

    if offset <= 180:
        if offset <= angle_offset:
            response['isAccept'] = True
        else:
            if z < origin_z:
                response['direction'] = 'left'
            else:
                response['direction'] = 'right'
    else:
        if 360 - offset <= angle_offset:
            response['isAccept'] = True
        else:
            if z > origin_z:
                response['direction'] = 'left'
            else:
                response['direction'] = 'right'

    return response

def getRepeat(z, origin_z):
    global angle_offset
    global turn_left
    global turn_right

    offset = abs(z - origin_z)

    if offset <= 180:
        if z > origin_z:
            repeat = int(offset / turn_left)
        else:
            repeat = int(offset / turn_right)
    else:
        if z < origin_z:
            repeat = int((360 - offset) / turn_left)
        else:
            repeat = int((360 - offset) / turn_right)

    return repeat if repeat > 1 else 1
