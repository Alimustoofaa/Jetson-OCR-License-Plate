import glob
import os
import cv2
from pathlib import Path
from config import DIRECTORY_SAVE_CAPTURE
from .logger import datetime_format

cur_date_time_str = str()

def save_capture(image, name):
    '''
    Save image in directory captues
    Args:
        image(np.array) : image for save
    Retrun:
        saved(boolen) : save success(True)/save failed(False)
    '''
    global cur_date_time_str
    # Checking directory
    Path(DIRECTORY_SAVE_CAPTURE).mkdir(parents=True, exist_ok=True)
    # Get date time for filename
    date_time_tuple = datetime_format()
    date_time_str   = ''.join(map(str, date_time_tuple))[:14]
    # Save image
    dir_filename = f'{DIRECTORY_SAVE_CAPTURE}/{name}_{date_time_str}.jpg'
    # log = True if not os.path.isfile(dir_filename) else False
    if cur_date_time_str != date_time_str:
        saved_image = cv2.imwrite(dir_filename, image)
        cur_date_time_str = date_time_str
        print(f'Done saved capture filename : {date_time_str}.jpg')
    else: saved_image = False
    # if not saved_image: print(f'Failed saved capture filename : {date_time_str}.jpg')
    return saved_image