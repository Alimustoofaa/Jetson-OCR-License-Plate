import cv2
import sys
import time
import subprocess
import numpy as np
from threading import Thread
from config import COMMAND_CAMERA_PROPERTY

from .utils import logging
from .app import LicensePlateExtract
from .schema import ResultProcess
from .utils import (detection_object, classification_vehicle, 
					resize, detect_char, read_text, encode_image,
					ArducamConfig, save_capture, request_post_api)

def __process_license_plate(image, image_detection, bbox):
	'''
	Preprocess and process ocr license plate indonesia
	Args:
		image(np.array): Original Image
		image_detection(np.array): Image crop detection
		bbox(list): bbox detection object [x_min, y_min, x_max, y_max]
	Retrun:
		text_license_plate(str): result license plate
		conf_license_plate(float): confidence level ocr
	'''
	
	if bbox and len(image_detection) >= 1:
		# Resize image if width < 150
		image_crop = resize(image_detection, 250, 255) if image_detection.shape[1] < 150 else image_detection
		# Detection character in image
		detected_char = detect_char(image_crop, output=False)
		# Handle image if detected char not found
		image_crop = resize(image, 50, 60) if not detected_char else image_crop
	else: image_crop = resize(image, 50, 60)

	# Process ocr
	results_ocr = read_text(image_crop, position_text='horizontal', clasess_name='license_plate')
	# Extract results ocr 
	text_processing = LicensePlateExtract(results_ocr)
	license_plate_dict = text_processing.license_plate_dict
	print(license_plate_dict)
	try:
		text_license_plate = (f"{license_plate_dict['area_code'][0]} "
							f"{license_plate_dict['license_number'][0]} "
							f"{license_plate_dict['unique_are'][0]}")

		conf_license_plate = round((license_plate_dict['area_code'][1]+
									license_plate_dict['license_number'][1]+
									license_plate_dict['unique_are'][1]
							)/len(license_plate_dict), 2)
	except:
		text_license_plate = ' '.join([i for i,_ in license_plate_dict.values()])
		conf_license_plate = round(sum([i for _,i in license_plate_dict.values()])/len(license_plate_dict), 2)

	logging.info(f'License Plate : {text_license_plate}')
	logging.info(f'Confidence : {conf_license_plate*100} %')
	return text_license_plate, conf_license_plate

def main_ocr_license_plate(image_vehicle, result_vehicle_type):
	'''
	Detection license plate and process ocr license plate
	Args:
		image_vehicle(np.array): Image crop vehicle
		result_vehicle_type(list): [id_timestamp, crop_image, classes, confidence]
	Return:
		result(dict): {
			id : timestamp(int),
			process_time : float,
			vehicle_classification : {
				image: bytes,
				vehicle_type: str
			},
			license_plate : {
				bbox : list([x_min, y_min, x_max, y_max]),
				license_plate: str,
				confidence: float,
				image: bytes
			}
		}
	'''
	start_time 			= time.time()
	timestamp			= result_vehicle_type[0]
	image				= result_vehicle_type[1]
	vehicle_type		= result_vehicle_type[2]
	confidence_vehicle	= result_vehicle_type[3]
	logging.info(f'========== Process LPR id {timestamp} ==========')
	logging.info(f'Vehiecle Type : {vehicle_type}')
	# Detection object
	try: license_plate = detection_object(image)
	except: license_plate = (np.array([], dtype=np.uint8), 0, list())

	# Get image crop and bbox detection (license plate) and handle mis detection
	if len(license_plate[0]) >=1 and\
		license_plate[1] > 0 and\
		len(license_plate[2]) == 4:
		image_license_plate, bbox_license_plate, confidence_license_plate = license_plate[0], license_plate[2], license_plate[1]
	else:
		# Get manual crop container characteristic with detect char and filter bbox character\
		image_license_plate, bbox_license_plate, confidence_license_plate = image, list(), 0
	text_license_plate, conf_license_plate = __process_license_plate(
		image, image_license_plate, bbox_license_plate
	)
	# Encode image vehicle and license plate
	image_vehicle_type_encoded	= encode_image(image_vehicle)
	image_license_plate_encoded	= encode_image(image_license_plate)
 
	end_time = round((time.time() - start_time),2)
	logging.info(f'Time Processing : {end_time} s')
	# result = (vehicle_type, text_license_plate, conf_license_plate, end_time)
	result = ResultProcess(
		id 						= timestamp,
		processing_time 		= end_time,
		vehicle_classification 	= {
			'vehicle_type'		: vehicle_type,
			'confidence'		: confidence_vehicle,
			'image'				: image_vehicle_type_encoded
		},
		license_plate 			= {
			'bbox'				: bbox_license_plate,
			'license_plate'		: text_license_plate,
			'confidence'		: conf_license_plate,
			'image'				: image_license_plate_encoded
		}
	)
	# HANDLE POST TO SERVER
	Thread(target=request_post_api, args=(result, )).start()
	return result.dict()