import os
import torch
import requests
import numpy as np
from tqdm import tqdm
from pathlib import Path

from config import DIRECTORY_MODEL, DETECTION_MODEL, CLASESS_MODEL_YOLOV5, VEHICLE_CLASESS

class VehicleClassification:
	'''
	Load custom model Yolo v5
	in directory ultralytics/yolov5
	'''
	def __init__(self):
		self.model_path = os.path.join(DIRECTORY_MODEL, DETECTION_MODEL['yolov5s']['filename'])
		self.check_model()
		self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
		self.model = torch.hub.load('ultralytics/yolov5', 'custom', path_or_model=self.model_path)
		self.model.to(self.device)
	
	def check_model(self):
		'''
		Checking model in model_path
		download model if file not found
		'''
		Path(DIRECTORY_MODEL).mkdir(parents=True, exist_ok=True)
		if not os.path.isfile(self.model_path):
			print('Downloading license plate detection model, please wait.')
			response = requests.get(DETECTION_MODEL['yolov5s']['url'], stream=True)
			progress = tqdm(response.iter_content(1024), 
						f'Downloading {DETECTION_MODEL["yolov5s"]["filename"]}', 
						total=DETECTION_MODEL['yolov5s']['file_size'], unit='B', 
						unit_scale=True, unit_divisor=1024)
			with open(self.model_path, 'wb') as f:
				for data in progress:
					f.write(data)
					progress.update(len(data))
				print(f'Done downloaded {DETECTION_MODEL["yolov5s"]["filename"]} detection model.')
		else:
			print(f'Load {DETECTION_MODEL["yolov5s"]["filename"]} detection model.')
			
	def filter_and_crop(self, results, min_confidence=0.0):
		'''
		Format result([tensor([[151.13147, 407.76913, 245.91382, 454.27802,   0.89075,   0.00000]])])
		Filter min confidence prediction and classes id/name
		Cropped image and get index max value confidence lavel
		Args:
			results(models.common.Detections) : results prediction YoloV5
			min_confidence(float(range 0.0 - 1.0)) : minimal confidence for filter results
		Return:
			result(tuple) : (confidence, bbox, clases_name)
		'''
		max_conf, bbox, clases = 0.0, list(), str()

		results_format = results.xyxy
		if len(results_format[0]) >= 1:
			for i in range(len(results_format[0])):
				classes_name = CLASESS_MODEL_YOLOV5[int(results_format[0][i][-1])]
				confidence	= float(results_format[0][i][-2])
				if classes_name in VEHICLE_CLASESS and confidence > min_confidence:
					if confidence > max_conf:
						max_conf	 = confidence
						x_min, y_min = int(results_format[0][i][0]), int(results_format[0][i][1])
						x_max, y_max = int(results_format[0][i][2]), int(results_format[0][i][3])
						bbox, clases = [x_min, y_min, x_max, y_max], classes_name
					else:
						max_conf 	= max_conf
						bbox		= bbox
						clases		= clases
		else:
			max_conf, bbox, clases = 0.0, list(), str()
		
		vehicles_classification = (max_conf, bbox, clases)
		return vehicles_classification

	def prediction(self, image):
		'''
		Prediction image object detectionn YoloV5
		Args:
			image(numpy.ndarray) : image/frame
		Return:
			results_prediction(models.common.Detections) : results -> convert to (results.xyxy/resultsxywh)
		'''
		results = self.model(image)
		return results