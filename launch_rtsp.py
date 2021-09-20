
import cv2
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from gi.repository import Gst, GstRtspServer, GObject
from src.utils import classification_vehicle, draw_rectangle

from src.utils import CameraCSI
from config import LAUNCH_STRING, FPS

class SensorFactory(GstRtspServer.RTSPMediaFactory):
	def __init__(self, **properties):
		super(SensorFactory, self).__init__(**properties)
		self.device_cam 	= CameraCSI(num_device=0)
		self.cap 			= self.device_cam.camera_arducam()
		self.number_frames 	= 0
		self.fps	 		= FPS
		self.duration 		= 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
		self.launch_string 	= LAUNCH_STRING

	def on_need_data(self, src, lenght):
		if self.cap.isOpened():
			ret, frame 	= self.cap.read()
			if ret:
				# Vehicle detection and classification
				try: confidence_vehicle ,bbox_vehicle, vehicle_type = classification_vehicle(frame, log=False)
				except: confidence_vehicle ,bbox_vehicle, vehicle_type = 0,'', [0,0,0,0]
				# Draw rectangle
				fram_rec = draw_rectangle(
					frame,	
					{'vehicle_type': [vehicle_type, bbox_vehicle, confidence_vehicle]}, 
					encoded=False, datetime_watermark=True
				)
				data 			= cv2.resize(fram_rec, (640, 480), interpolation = cv2.INTER_AREA).tostring()
				buf 			= Gst.Buffer.new_allocate(None, len(data), None); buf.fill(0, data)
				buf.duration 	= self.duration
				timestamp 		= self.number_frames * self.duration
				buf.pts 		= buf.dts = int(timestamp)
				buf.offset 		= timestamp
				self.number_frames += 1
				retval 			= src.emit('push-buffer', buf)
				# print(f'pushed buffer, frame {self.number_frames}, duration {self.duration} ns, durations {self.duration / Gst.SECOND} s')
				if retval != Gst.FlowReturn.OK:
					print(retval)

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
		self.get_mount_points().add_factory("/test", self.factory)
		self.attach(None)


GObject.threads_init()
Gst.init(None)
server = GstServer()
loop = GObject.MainLoop()
loop.run()