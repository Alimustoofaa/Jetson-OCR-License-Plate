import cv2
import time
import numpy as np

from .utils import logging
from .app import LicensePlateExtract
from .utils import (detection_object, classification_vehicle, 
					resize, detect_char, read_text)

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

def main_ocr_license_plate(image):
	'''
	Detection license plate and process ocr license plate
	Args:
		image(np.array): Image for process license plate
	Return:
		vehicle_type(str): type vehicle classification
		text_license_plate(str): result license plate
		conf_license_plate(float): confidence level ocr
		end_time(float): Processing time
	'''
	start_time = time.time()
	# Clasification vehicle
	try: _,_, vehicle_type = classification_vehicle(image)
	except: vehicle_type = ''

	# Detection object
	try: license_plate = detection_object(image)
	except: license_plate = (np.array([], dtype=np.uint8), 0, list())

	# Get image crop and bbox detection (license plate) and handle mis detection
	if len(license_plate[0]) >=1 and\
		license_plate[1] > 0 and\
		len(license_plate[2]) == 4:
		image_license_plate, bbox_license_plate = license_plate[0], license_plate[2]
	else:
		# Get manual crop container characteristic with detect char and filter bbox character\
		image_license_plate, bbox_license_plate = image, None
	text_license_plate, conf_license_plate = __process_license_plate(
		image, image_license_plate, bbox_license_plate
	)
	
	end_time = round((time.time() - start_time),2)
	logging.info(f'Time Processing : {end_time} s')
	result = (vehicle_type, text_license_plate, conf_license_plate, end_time)
	return result