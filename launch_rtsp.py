
import cv2
import gi
from datetime import datetime
from threading import Thread
from src.process import main_ocr_license_plate

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from gi.repository import Gst, GstRtspServer, GObject

from src.utils import (
	classification_vehicle,
	draw_rectangle_list,
	CameraCSI,
	EuclideanDistTracker,
	logging
)

from config import LAUNCH_STRING, FPS, A, B, C, D, AREA_DETECTION

class SensorFactory(GstRtspServer.RTSPMediaFactory):
	def __init__(self, **properties):
		super(SensorFactory, self).__init__(**properties)
		self.device_cam 	= CameraCSI(num_device=0)
		self.cap 			= self.device_cam.camera_arducam()
		self.number_frames 	= 0
		self.fps	 		= FPS
		self.duration 		= 1 / self.fps * Gst.SECOND
		self.launch_string 	= LAUNCH_STRING

		# Tracker
		self.tracker		= EuclideanDistTracker()
		self.unique_id		= list()

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
						Thread(target=main_ocr_license_plate, args=(crop_img, classes, timestamp_id)).start()
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

	def on_need_data(self, src, lenght):
		if self.cap.isOpened():
			ret, frame 	= self.cap.read()
			if ret:
				frame = self.process_trigger_vehicle(frame)
				data 			= cv2.resize(frame, (640, 480), interpolation = cv2.INTER_AREA).tostring()
				buf 			= Gst.Buffer.new_allocate(None, len(data), None); buf.fill(0, data)
				buf.duration 	= self.duration
				timestamp 		= self.number_frames * self.duration
				buf.pts 		= buf.dts = int(timestamp)
				buf.offset 		= timestamp
				self.number_frames += 1
				retval 			= src.emit('push-buffer', buf)

	def do_create_element(self, url):
		return Gst.parse_launch(self.launch_string)

	def do_configure(self, rtsp_media):
		self.number_frames = 0
		appsrc = rtsp_media.get_element().get_child_by_name('source')
		appsrc.connect('need-data', self.on_need_data)


class GstServer(GstRtspServer.RTSPServer):
	def __init__(self, **properties):
		super(GstServer, self).__init__(**properties)
		self.factory = SensorFactory()
		self.factory.set_shared(True)
		self.get_mount_points().add_factory("/streaming", self.factory)
		self.attach(None)
		logging.info('Server running in : rtsp://127.0.0.1:8554/streaming')


GObject.threads_init()
Gst.init(None)
server = GstServer()
loop = GObject.MainLoop()
loop.run()