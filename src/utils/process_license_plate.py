import cv2

from .logger import logging
from src.schema import ConfigOcr
from src.app import LicensePlateDetection
from src.app import OpticalCharacterRecognition
from src.app import VehicleClassification_V2

from config import MIN_CONFIDENCE

classification  = VehicleClassification_V2()
model           = LicensePlateDetection()
ocr             = OpticalCharacterRecognition()

def detection_object(image):
	'''
	Detection license plate
	and filter clasess, confidence
	Args:
		image(np.array): image for cropped
	return:
		result(tuple): (
				image_cropped(np.array): image croped,
				confidence(float): confidence level,
				bbox(list): bbox detection [x_min, y_min, x_max, y_max]
			)

	'''
	result_detection = model.prediction(image)
	license_plate = model.filter_and_crop(
		img=image, results=result_detection, min_confidence=MIN_CONFIDENCE
	)
	if len(license_plate[0]) >=1 and license_plate[1] > 0 and len(license_plate[2]) == 4:
		logging.info(f'Got license plate detection confidence : {round(license_plate[1], 2)*100} %')
	else: logging.info(f'License plate not found')
	return license_plate

def classification_vehicle(image, log=True):
	'''
	Classification vehicle
	and filter clasess, confidence
	Args:
		image(np.array): image for classification
	Return:
		result(tuple): (
			clasess(str): clases name
			confidence(float): confidence level
			bbox(list): bbox object [x_min, y_min, x_max, y_max]
		)
	'''
	result_classification = classification.detection(image)
	results_vehicle_list = classification.filter_and_crop(
		results=result_classification, min_confidence=MIN_CONFIDENCE+0.2
	)
	# if log:
	# 	if vehicle_type[0] and vehicle_type[1] and vehicle_type[2]:
	# 		logging.info(f'Got classification {vehicle_type[2]} confidence : {round(vehicle_type[0], 2)*100} %')
	# 	else: logging.info(f'Not found object classification')
	return results_vehicle_list
	
def resize(image, height_percent=180, width_percent=180):
	'''
	resize image by percent
	Args:
		image(np.array): image
		height_percent(int): percentage height
		width_percent(int): percentage width
	Return:
		image(np.array): image resized
	'''
	height = int(image.shape[0] * height_percent / 100)
	width = int(image.shape[1] * width_percent / 100)
	dim = (width, height)
	try: new_img = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
	except cv2.error: new_img = image
	logging.info(f'Resize image to : {new_img.shape}')
	return new_img

def detect_char(image, output=False):
	'''
	Detection charcters text in image
	Args:
		image(np.array): image.
		output(boolean): output detection default (output=False)
	Return:
		result(boolean|list): result detection character
	'''
	try: detected_char = ocr.detect_char(image)
	except: detected_char = [[],[]]
	if detected_char[0]:
		logging.info(f'Found text in image : {" ".join([str(i) for i in detected_char[0]])}')
	else:
		logging.info(f'Not found text in image')

	if output:
		results = detected_char[0][0]
	else: 
		if detected_char[0]: results = True
		else: results = False
	return results

def read_text(image, position_text='horizontal', clasess_name='license_plate'):
	'''
	Set methods and value config ocr
	methods view schema/config_ocr.py
	Args:
		image(np.array): image for read text
		position_text(str): position text vertical/horizontal (default=vertical)
		clasess_name(str): clasess name read text (default=license_plate)
	Retrun:
		result(list): [([[28, 32], [52, 32], [52, 64], [28, 64]], 'text', 0.9846626687831872)]
	'''
	if position_text == 'horizontal':
		config = ConfigOcr(
			beam_width      = 8,
			batch_size      = 10,
			text_threshold  = 0.4,
			link_threshold  = 0.7,
			low_text        = 0.4,
			slope_ths       = 0.9,
			mag_ratio 		= 1,
			add_margin		= 0.5,
			width_ths       = 0.2
		)
	elif position_text == 'vertical':
		config = ConfigOcr(
			batch_size  	= 10,
			text_threshold 	= 0.2,
			link_threshold 	= 0.9,
			low_text 		= 0.4,
			add_margin		= 0
		)
	results = ocr.ocr_image(image=image, config=config)
	if position_text == 'horizontal': results.sort(reverse=False)
	else : results = results
	logging.info(f'Ocr {clasess_name} : {" ".join([i[1] for i in results])}')
	return results