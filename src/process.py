import cv2
import sys
import time
import subprocess
import numpy as np

from config import COMMAND_CAMERA_PROPERTY

from .utils import logging
from .app import LicensePlateExtract
from .schema import ResultProcess
from .utils import (detection_object, classification_vehicle, 
					resize, detect_char, read_text, draw_rectangle,
					ArducamConfig, save_capture)
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
	try: confidence_vehicle ,bbox_vehicle, vehicle_type = classification_vehicle(image)
	except: confidence_vehicle ,bbox_vehicle, vehicle_type = 0,'', [0,0,0,0]

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
		image_license_plate, bbox_license_plate = image, list()
	text_license_plate, conf_license_plate = __process_license_plate(
		image, image_license_plate, bbox_license_plate
	)
	# Draw bbox rectangle
	image_encoded = draw_rectangle(
		image,
		{
			'license_plate': ['plate',bbox_license_plate], 
			'vehicle_type': [vehicle_type, bbox_vehicle]
		}, 
		encoded=True
	)
 
	end_time = round((time.time() - start_time),2)
	logging.info(f'Time Processing : {end_time} s')
	# result = (vehicle_type, text_license_plate, conf_license_plate, end_time)
	result = ResultProcess(
		vehicle_classification = {
			'bbox': bbox_vehicle,
			'confidence': confidence_vehicle,
			'clases': vehicle_type
		},
		license_plate = {
			'bbox': bbox_license_plate,
			'result_ocr': text_license_plate,
			'confidence': conf_license_plate
		},
		processing_time = end_time,
		image = image_encoded
	)
	return result.dict()


frame_image_encoded = np.array([])

def vehicle_detection_and_counting():
	'''
	Procesing live detection vehicle in camera video
	-> Run Camera
	-> Classification Vehicle
	-> Processing bbox
	-> Vehicle Counting

	'''
	global frame_image_encoded

	PREDICTION_BORDER_Y = [550, 550]
	PREDICTION_BORDER_X = [700, 1400]

	try:
		# camera = cv2.VideoCapture("filesrc location=/home/ocr/Halotec/Jetson-OCR-License-Plate/captures/3.mp4 ! qtdemux ! h264parse ! omxh264dec ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink", cv2.CAP_GSTREAMER)
		camera			= cv2.VideoCapture(0, cv2.CAP_V4L2)
		arducam_conf	= ArducamConfig(0)
	except:
		print('Reconnect camera..')
		camera			= cv2.VideoCapture(0, cv2.CAP_V4L2)
		arducam_conf	= ArducamConfig(0)
		time.sleep(1)

	camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
	camera.set(cv2.CAP_PROP_CONVERT_RGB, arducam_conf.convert2rgb)
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
	camera.set(cv2.CAP_PROP_FPS, 15)

	# Run shell v4l2-ctl, worked with 7 loop
	for _ in range(7):
		subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)
		ret, frame = camera.read()
	
	while True:
		ret, frame = camera.read()
		if ret: #print('Error Camera Module'); sys.exit(1)
			image = frame.copy()
			# Draw line
			# frame = cv2.resize(frame, (300, 300), interpolation = cv2.INTER_AREA)
			
			# Vehicle Detection
			start_time = time.time()
			try: confidence_vehicle ,bbox_vehicle, vehicle_type = classification_vehicle(cv2.resize(frame, (300, 300), interpolation = cv2.INTER_AREA), log=False)
			except: confidence_vehicle, vehicle_type, bbox_vehicle = 0,'', [0,0,0,0] 

			if confidence_vehicle and len(bbox_vehicle)>1 and len(vehicle_type)>2:
				# Calculate Centroid
				x, y = int((bbox_vehicle[0] + bbox_vehicle[2])/2), int((bbox_vehicle[1] + bbox_vehicle[3])/2)
				cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

				# Process counting
				if x in range(PREDICTION_BORDER_X[0], PREDICTION_BORDER_X[1]) and y in range(PREDICTION_BORDER_Y[1], PREDICTION_BORDER_Y[1]+10):
					cv2.line(frame, (PREDICTION_BORDER_X[0],PREDICTION_BORDER_Y[0]), (PREDICTION_BORDER_X[1], PREDICTION_BORDER_Y[1]), (0, 0, 255), 2)
					save_capture(image, name=f'{vehicle_type}_{round(confidence_vehicle, 2)}')
					# save_db(bbox_vehicle, confidence_vehicle, vehicle_type)
			# Draw ractangle image
			cv2.line(frame, (PREDICTION_BORDER_X[0],PREDICTION_BORDER_Y[0]), (PREDICTION_BORDER_X[1], PREDICTION_BORDER_Y[1]), (255, 0, 0), 2)
			image_encoded = draw_rectangle(
				frame,
				{'vehicle_type': [vehicle_type, bbox_vehicle]}, 
				encoded=True
			)
			frame_image_encoded = image_encoded
		else:  break