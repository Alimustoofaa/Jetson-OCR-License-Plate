import time
import json
import requests
from config import URL_VEHICLE_API

headers = { 'Content-Type': 'application/json'}

error_post_list = []

def request_post_api(result):
	result_json = result.json()
	try:
        response = requests.request("POST", URL_VEHICLE_API, headers=headers, data=result_json)
        if response.status_code >= 226: error_post_list.append(result_json)
        if error_post_list:
           for result_error in error_post_list:
               response = requests.request("POST", URL_VEHICLE_API, headers=headers, data=result_json)
               if response.status_code <= 226:
                   error_post_list.remove(result_error)
                time.sleep(0.5)
	except requests.exceptions.RequestException:
        error_post_list.append(result_json)