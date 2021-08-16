import os
import sys
import cv2
import time
import glob
import subprocess
from adam_io import Adam6050D
from threading import Thread

from config import ADAM_CONFIG
from config import DIRECTORY_SAVE_CAPTURE
from config import COMMAND_CAMERA_PROPERTY
from src.utils import ArducamConfig, save_capture

from src.process import main_ocr_license_plate

# Connect to Adam
adam = Adam6050D(ADAM_CONFIG['ip'], ADAM_CONFIG['username'], ADAM_CONFIG['password'])

def process_license_plate():
    while True:
        path_image_list = [i for i in glob.glob(f'{DIRECTORY_SAVE_CAPTURE}/*.jpg')]
        if path_image_list:
            for path_image in path_image_list:
                if os.path.isfile(path_image):
                    print(f'========{path_image.split("/")[-1]}========')
                    image   = cv2.imread(path_image)
                    result  = main_ocr_license_plate(image)
                    if result: 
                        path_image_list.remove(path_image)
                        os.remove(path_image)
                time.sleep(1)
        time.sleep(1)

def capture_image():
    # open camera
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

    for i in range(7):
        subprocess.call([COMMAND_CAMERA_PROPERTY], shell=True)
        _, frame = camera.read()

    while True:
        ret, frame = camera.read()
        if not ret: print('Error Camera Module'); sys.exit(1)
        # if condition sensor detector
        di = adam.input(0)
        # Sensor digital output
        A1, A2 = di[0], di[1]
        B1, B2 = di[2], di[3]
        if A2 == 1:
            frame = arducam_conf.convert(frame=frame)
            save_capture(frame)
    
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