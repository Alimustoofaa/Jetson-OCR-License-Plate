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
	LAUNCH_STRING, FPS,
	A, B, C, D, 
	AREA_DETECTION,
	X_MIN_CROP, Y_MIN_CROP, X_MAX_CROP, Y_MAX_CROP,
	COMMAND_FFMPEG
)

class Run_Application:
	def __init__(self):
		self.device_cam 	= CameraCSI(num_device=0)
		self.cap 			= self.device_cam.camera_arducam()
		# Tracker
		self.tracker		= EuclideanDistTracker()
		self.unique_id		= list()
		self.current_timestamp = 0
		# RTMP Stream
		self.ffmepg_command = subprocess.Popen(COMMAND_FFMPEG, stdin=subprocess.PIPE)

	def process_trigger_vehicle(self, frame):
		image, image_process = frame.copy(), frame.copy()
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
				if x in range(D[0]-300, B[0]) and (y in range(C[1],C[1]+60) or y in range(D[1],D[1]+50)):
					if not id in self.unique_id:
						timestamp_id 	= int(datetime.timestamp(datetime.now()))
						if self.current_timestamp != timestamp_id+1 and self.current_timestamp != timestamp_id:
							self.current_timestamp = timestamp_id
							crop_img 		= image_process[y_min:y_max, x_min:x_max]
							result_vehicle	= [timestamp_id, crop_img, classes, conf]
							# cv2.imwrite(f'captures/{classes}_{str(timestamp_id)}.jpg', image)
							Thread(target=main_ocr_license_plate, args=(crop_img, result_vehicle, )).start()
							# Change color line
							cv2.line(image, (D[0], D[1]), (C[0], C[1]), (0, 0, 225), thickness=2) #TOP
							# Reset value unique_id
							if len(self.unique_id) > 200: self.unique_id = list()
							self.unique_id.append(id)
						else: self.current_timestamp = self.current_timestamp
				# Draw circle in centroid rectangle
				cv2.circle(frame, (x,y), 2, (0, 0, 255), -1)

		# Reset value trakcer id
		if self.tracker.id_count > 1000: self.tracker.id_count = 0

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
				frame_crop = frame[Y_MIN_CROP:Y_MAX_CROP, X_MIN_CROP:X_MAX_CROP]
				frame 	= self.process_trigger_vehicle(frame_crop)
				frame	= cv2.resize(frame, (600, 400), interpolation = cv2.INTER_AREA)
				try: self.ffmepg_command.stdin.write(frame.tobytes())
				except: pass
				finally: self.ffmepg_command.stdin.write(frame.tobytes())

aplication = Run_Application()
aplication.running_camera()