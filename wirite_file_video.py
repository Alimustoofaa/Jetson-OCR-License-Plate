import cv2
import time
import subprocess
from src.utils import ArducamConfig
from config import COMMAND_CAMERA_PROPERTY

camera			= cv2.VideoCapture(0, cv2.CAP_V4L2)
arducam_conf	= ArducamConfig(0)

# Configuration Camera
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))
camera.set(cv2.CAP_PROP_CONVERT_RGB, arducam_conf.convert2rgb)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

out =  cv2.VideoWriter('result_test_videoa.avi', cv2.VideoWriter_fourcc(*"XVID"), 30.0, (640, 480))
for _ in range(7):
	subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)

start = time.time()

while True:
	ret, frame = camera.read()
	if not ret: print('error'); break
	# cv2.imwrite('aa.jpg', frame); break
	out.write(frame)
	
	current_time = int((time.time() - start))
# camera.release()
out.release()

