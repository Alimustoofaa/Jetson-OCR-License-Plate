import os
import sys
import cv2
import time
import glob
import subprocess
import Jetson.GPIO as GPIO
from threading import Thread
from src.utils import logging

from config import DIRECTORY_SAVE_CAPTURE
from config import COMMAND_CAMERA_PROPERTY
from src.utils import ArducamConfig, save_capture

from src.process import main_ocr_license_plate

# GPIO Setup
TRIGGER_PIN = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIGGER_PIN, GPIO.IN)

def process_license_plate():
	'''
	Processing ocr plate and vehicle classification
	-> Get directory all image*.jpg saved in DIRECTORY_SAVE_CAPTURE
	-> read image in DIRECTORY_SAVE_CAPTURE
	-> Processing in function main_ocr_license_plate(image)
	-> Delete image if processing success
	'''
	while True:
		path_image_list = [i for i in glob.glob(f'{DIRECTORY_SAVE_CAPTURE}/*.jpg')]
		if path_image_list:
			for path_image in path_image_list:
				if os.path.isfile(path_image):
					logging.info(f'========{path_image.split("/")[-1]}========')
					image   = cv2.imread(path_image)
					result  = main_ocr_license_plate(image)
					if result: 
						path_image_list.remove(path_image)
						os.remove(path_image)
				time.sleep(1)
		time.sleep(1)

def capture_image():
	'''
	Run camera arducam and save image with GPIO trigger
	'''
	try:
		camera          = cv2.VideoCapture(0, cv2.CAP_V4L2)
		arducam_conf    = ArducamConfig(0)
	except:
		print('Error Camera Module')
		sys.exit(1)

	camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))
	camera.set(cv2.CAP_PROP_CONVERT_RGB, arducam_conf.convert2rgb)
	camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
	camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

	# Run shell v4l2-ctl, worked with 7 loop
	for _ in range(7):
		subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)
		ret, frame = camera.read()

	try:
		while True:
			ret, frame = camera.read()
			if not ret: print('Error Camera Module'); sys.exit(1)
				
			# GPIO wait input
			# if GPIO.input(TRIGGER_PIN):
			# 	print('Capture image')
			# 	frame = arducam_conf.convert(frame=frame)
			# 	save_capture(frame)
			# else: continue

			GPIO.wait_for_edge(TRIGGER_PIN, GPIO.FALLING)
			print('Capture image')
			frame = arducam_conf.convert(frame=frame)
			save_capture(frame)
			
	finally: GPIO.cleanup()
		
	
if __name__ == '__main__':
	# Process thred
	processing_license_plate = Thread(
		target=process_license_plate
	)

	processing_capture_image = Thread(
		target=capture_image
	)

	processing_license_plate.start()
	processing_capture_image.start()