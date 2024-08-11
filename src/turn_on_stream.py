from __future__ import print_function
import time
import openadk
from openadk.rest import ApiException
from pprint import pprint

robo_ip = '10.220.5.226'

# create an instance of the API class
configuration = openadk.Configuration()
configuration.host = f'http://{robo_ip}:9090/v1'
api_instance = openadk.VisionsApi(openadk.ApiClient(configuration))

body = {
    'resolution': '640x480'
}

try:
    response = api_instance.post_visions_streams(body=body)
    print(response)
except ApiException as e:
    print(e)