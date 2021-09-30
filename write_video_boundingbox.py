import cv2
import time
import subprocess
from datetime import datetime

from numpy.lib.type_check import imag

from config import (
	COMMAND_CAMERA_PROPERTY, POSITION_CAM, 
	AREA_DETECTION, A, B, C, D
)

from src.utils import (
	classification_vehicle,
	draw_rectangle_list,
	EuclideanDistTracker,
	logging
)

class CameraCSI:
	'''
	Read camera module cv2 and
	run command v4l2 config
	Args:
		num_device(int): number device camera
	'''
	def __init__(self, num_device):
		self.num_device = num_device
		if POSITION_CAM.split(" ")[1] != '88A':
			self.camera = cv2.VideoCapture(self.num_device, cv2.CAP_V4L2)
			self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))
			# self.cap.set(cv2.CAP_PROP_CONVERT_RGB, self.cap.convert2rgb)
			self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
			self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
			self.camera.set(cv2.CAP_PROP_FPS, 30)
			self.__run_config_arducam()
		else:
			self.camera = cv2.VideoCapture(self._gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
			
	def __run_config_arducam(self):
		for _ in range(7):
			subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)
			ret, frame = self.camera.read()

	def _gstreamer_pipeline(
		capture_width=1280,
		capture_height=720,
		display_width=1280,
		display_height=720,
		framerate=30,
		flip_method=0,
	):
		return (
			"nvarguscamerasrc ! "
			"video/x-raw(memory:NVMM), "
			"width=(int)%d, height=(int)%d, "
			"format=(string)NV12, framerate=(fraction)%d/1 ! "
			"nvvidconv flip-method=%d ! "
			"video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
			"videoconvert ! "
			"video/x-raw, format=(string)BGR ! appsink"
			% (
				capture_width,
				capture_height,
				framerate,
				flip_method,
				display_width,
				display_height,
			)
		)

	def camera_arducam(self):
		if not self.camera.isOpened(): self.__init__(self.num_device)
		return self.camera



def process_trigger_vehicle(frame):
	tracker 	= EuclideanDistTracker()
	unique_id 	= list()

	image = frame.copy()
	# Crop image area detection
	image_area = frame.copy()
	image_area = image_area[A[1]+20:D[1]-20, A[0]-20, frame.shape]
	cv2.imwrite(f'captures/classes.jpg', image)
	# Vehicle detection and classification
	try: vehicle_classification_list	= classification_vehicle(frame, log=False)
	except: vehicle_classification_list = list()

	# Draw line
	cv2.line(image, (D[0], D[1]), (C[0], C[1]), (0, 128, 255), thickness=2) #TOP
	
	if len(vehicle_classification_list):
		# Object Tracking
		boxes_ids = tracker.update(vehicle_classification_list)
		for i in boxes_ids:
			x_min, y_min, x_max, y_max, classes, conf, id = i
			# Calculate Centroid
			x, y = int((x_min + x_max)/2), int((y_min + y_max)/2)
			# Condition Count Object
			if x in range(A[0], C[0]+50) and y in range(C[1],C[1]+50):
				if not id in unique_id:
					crop_img 		= frame[y_min-15:y_max+15, x_min-15:x_max+15]
					timestamp_id 	= int(datetime.timestamp(datetime.now()))
					# cv2.imwrite(f'captures/{classes}_{str(timestamp_id)}.jpg', image)
					result_vehicle	= [timestamp_id, crop_img, classes, conf]
					# Thread(target=main_ocr_license_plate, args=(crop_img, result_vehicle, ), daemon = True).start()
					# Change color line
					cv2.line(image, (D[0], D[1]), (C[0], C[1]), (0, 0, 225), thickness=2) #TOP
					# Reset value unique_id
					if len(unique_id) > 100: unique_id = list()
					unique_id.append(id)
			# Draw circle in centroid rectangle
			cv2.circle(frame, (x,y), 2, (0, 0, 255), -1)

	# Reset value trakcer id
	if tracker.id_count > 200: tracker.id_count = 0

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

device_cam 	= CameraCSI(num_device=0)
camera      = device_cam.camera_arducam()
out 		= cv2.VideoWriter('result_video_379.avi', cv2.VideoWriter_fourcc(*"XVID"), 60.0, (1280, 720))

print('Startt')
while True:
	ret, frame = camera.read()
	if not ret: print('error')
	image = process_trigger_vehicle(frame)
	# cv2.imwrite('aa.jpg', frame); break
	out.write(image)
	
# camera.release()
out.release()


#KURANG CROP DIAREA TERTENTU