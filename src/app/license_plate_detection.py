'''
@Author     : Ali Mustofa HALOTEC
@Module     : Detection License Plate Indonesia
@Created on : 7 Agust 2021
'''

import os
import torch
import requests
import numpy as np
from tqdm import tqdm
from pathlib import Path

from config import DIRECTORY_MODEL, DETECTION_MODEL, CLASESS_MODEL_LICENSE_PLATE

class LicensePlateDetection:
    '''
    Load custom model Yolo v5
    in directory model/model_license_plate.pt
    '''
    def __init__(self):
        self.model_path = os.path.join(DIRECTORY_MODEL, DETECTION_MODEL['license_plate']['filename'])
        self.check_model()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path_or_model=self.model_path)
        self.model.to(self.device)

    def check_model(self):
        '''
        Checking model in model_path
        download model if file not found
        '''
        Path(DIRECTORY_MODEL).mkdir(parents=True, exist_ok=True)
        if not os.path.isfile(self.model_path):
            print('Downloading license plate detection model, please wait.')
            response = requests.get(DETECTION_MODEL['license_plate']['url'], stream=True)
            progress = tqdm(response.iter_content(1024), 
                        f'Downloading {DETECTION_MODEL["license_plate"]["filename"]}', 
                        total=DETECTION_MODEL['license_plate']['file_size'], unit='B', 
                        unit_scale=True, unit_divisor=1024)
            with open(self.model_path, 'wb') as f:
                for data in progress:
                    f.write(data)
                    progress.update(len(data))
                print(f'Done downloaded {DETECTION_MODEL["license_plate"]["filename"]} detection model.')
        else:
            print(f'Load {DETECTION_MODEL["license_plate"]["filename"]} detection model.')

    def filter_and_crop(self, img, results, min_confidence=0.0):
        '''
        Format result([tensor([[151.13147, 407.76913, 245.91382, 454.27802,   0.89075,   0.00000]])])
        Filter min confidence prediction and classes id/name
        Cropped image and get index max value confidence lavel
        Args:
            img(np.array): image for cropped,
            result(models.common.Detections): result detection YoloV5
            min_confidence(float): minimal confidence detection in range 0-1
        Return:
            result(tuple): (
                image_cropped(np.array): image croped,
                confidence(float): confidence level,
                bbox(list): bbox detection [x_min, y_min, x_max, y_max]
            )
        '''
        max_conf_license_plate, img_license_plate, bbox_license_plate  = 0, np.array([], dtype=np.uint8), list()

        results_format = results.xyxy

        if len(results_format[0]) >= 1:
            for i in range(len(results_format[0])):
                classes_name = CLASESS_MODEL_LICENSE_PLATE[int(results_format[0][i][-1])]
                confidence = float(results_format[0][i][-2])
                if classes_name == 'license_plate' and confidence >= min_confidence:
                    if confidence > max_conf_license_plate:
                        max_conf_license_plate = confidence
                        x1, y1 = int(results_format[0][i][0]), int(results_format[0][i][1])
                        x2, y2 = int(results_format[0][i][2]), int(results_format[0][i][3])
                        cropped_img = img[y1-10 : y2+10, x1-10 : x2+10]
                        bbox_license_plate = [x1-10, y1-10, x2+10, y2+10]
                        img_license_plate = cropped_img
                    else:
                        max_conf_license_plate  = max_conf_license_plate
                        bbox_license_plate      = bbox_license_plate
                        img_license_plate       = img_license_plate

        else:
            max_conf_license_plate, img_license_plate, bbox_license_plate = 0, np.array([], dtype=np.uint8), list()

        license_plate = (img_license_plate, max_conf_license_plate, bbox_license_plate)
        return license_plate

    def prediction(self, image):
        '''
        Prediction image object detectionn YoloV5
        Args:
            img(np.array): image for prediction,
        Retrun:
            result(models.common.Detections): result detection YoloV5(convert to result xyxy)
        '''
        results = self.model(image)
        return results