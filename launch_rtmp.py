import cv2
import gi
import time
import subprocess
from datetime import datetime
from threading import Thread
from src.process import main_ocr_license_plate

from src.utils import (
	classification_vehicle,
	draw_rectangle_list,
	CameraCSI,
	EuclideanDistTracker,
	logging
)

from config import (
	LAUNCH_STRING,
	A, B, C, D, 
	AREA_DETECTION, COMMAND_FFMPEG
)

class Run_Application:
	def __init__(self):
		self.device_cam 	= CameraCSI(num_device=0)
		self.cap 			= self.device_cam.camera_arducam()
		# Tracker
		self.tracker		= EuclideanDistTracker()
		self.unique_id		= list()

		# RTMP Stream
		self.ffmepg_command = subprocess.Popen(COMMAND_FFMPEG, stdin=subprocess.PIPE)

	def process_trigger_vehicle(self, frame):
		image = frame.copy()
		# Vehicle detection and classification
		try: vehicle_classification_list	= classification_vehicle(frame, log=False)
		except: vehicle_classification_list = list()

		# Draw line
		cv2.line(image, (D[0], D[1]), (C[0], C[1]), (0, 128, 255), thickness=2) #TOP
		
		if len(vehicle_classification_list):
			# Object Tracking
			boxes_ids = self.tracker.update(vehicle_classification_list)
			for i in boxes_ids:
				x_min, y_min, x_max, y_max, classes, conf, id = i
				# Calculate Centroid
				x, y = int((x_min + x_max)/2), int((y_min + y_max)/2)
				# Condition Count Object
				if x in range(A[0], C[0]+50) and y in range(C[1],C[1]+50):
					if not id in self.unique_id:
						crop_img 		= frame[y_min-15:y_max+15, x_min-15:x_max+15]
						timestamp_id 	= int(datetime.timestamp(datetime.now()))
						result_vehicle	= [timestamp_id, crop_img, classes, conf]
						Thread(target=main_ocr_license_plate, args=(crop_img, result_vehicle, )).start()
						# Change color line
						cv2.line(image, (D[0], D[1]), (C[0], C[1]), (0, 0, 225), thickness=2) #TOP
						# Reset value unique_id
						if len(self.unique_id) > 100: self.unique_id = list()
						self.unique_id.append(id)
				# Draw circle in centroid rectangle
				cv2.circle(frame, (x,y), 2, (0, 0, 255), -1)

		# Reset value trakcer id
		if self.tracker.id_count > 200: self.tracker.id_count = 0

		# Color Block
		cv2.fillPoly(frame, [AREA_DETECTION],  (51, 153, 255))
		# Add Transparant Color
		cv2.addWeighted(frame, 0.2, image, 1 - 0.2, 0, image)
		# Add line in bottom
		cv2.line(image, (A[0], A[1]), (B[0], B[1]), (0, 128, 255), thickness=2) #BOTTON

		# Draw rectangle
		return draw_rectangle_list(
			image, vehicle_classification_list, 
			encoded=False, datetime_watermark=True
		)

	def running_camera(self):
		while True:
			ret, frame 	= self.cap.read()
			if ret:
				frame 	= self.process_trigger_vehicle(frame)
				frame	= cv2.resize(frame, (640, 480), interpolation = cv2.INTER_AREA)
				self.ffmepg_command.stdin.write(frame.tobytes())

aplication = Run_Application()
aplication.running_camera()