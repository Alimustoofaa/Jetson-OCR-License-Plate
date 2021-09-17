import cv2
import subprocess

from config import COMMAND_CAMERA_PROPERTY

class CameraCSI:
	def __init__(self, num_device):
		self.camera = cv2.VideoCapture(num_device, cv2.CAP_V4L2)
		self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))
		# self.cap.set(cv2.CAP_PROP_CONVERT_RGB, self.cap.convert2rgb)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		self.camera.set(cv2.CAP_PROP_FPS, 30)
		self.__run_config_arducam()

	def __run_config_arducam(self):
		for _ in range(7):
			subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)
			ret, frame = self.camera.read()

	def camera_arducam(self):
		return self.camera