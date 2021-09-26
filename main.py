'''
API OCR License Plate Indonesia
@Author     : Ali Mustofa HALOTEC
@Created on : 19 Agust 2021
'''

import io

import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from fastapi import FastAPI, File

from src.utils import logging
from src.process import main_ocr_license_plate

app = FastAPI(title='OCR License Plate Indonesiar',
			  description='''Container number detection and read text in image with open source
			  library easyocr https://github.com/JaidedAI/EasyOCR''',
			  version='1.0')

@app.get('/')
def index():
	return {'title': 'OCR License Plate Indonesia'}

@app.post('/v1/lpn-service')
async def input_image_for_predictions(file: bytes = File(...)):
	image = Image.open(io.BytesIO(file)).convert("RGB")
	image = np.array(image)
	image = image[:,:,::-1].copy()
	timestamp			= int(datetime.timestamp(datetime.now()))
	vehicle_type		= 'car'
	confidence_vehicle	= 0.8
	result_vehicle	= [timestamp, image, vehicle_type, confidence_vehicle]
	logging.info('================= processing image =================')
	results = main_ocr_license_plate(image, result_vehicle)
	return results