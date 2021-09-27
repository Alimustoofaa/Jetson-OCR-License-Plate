import cv2
import subprocess

from config import COMMAND_CAMERA_PROPERTY, POSITION_CAM

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