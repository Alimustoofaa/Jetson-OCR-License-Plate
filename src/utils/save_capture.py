import cv2
from pathlib import Path
from config import DIRECTORY_SAVE_CAPTURE
from .logger import datetime_format

def save_capture(image):
    '''
    Save image in directory captues
    Args:
        image(np.array) : image for save
    Retrun:
        saved(boolen) : save success(True)/save failed(False)
    '''
    # Checking directory
    Path(DIRECTORY_SAVE_CAPTURE).mkdir(parents=True, exist_ok=True)
    # Get date time for filename
    date_time_tuple = datetime_format()
    date_time_str   = ''.join(map(str, date_time_tuple))
    # Save image
    dir_filename = f'{DIRECTORY_SAVE_CAPTURE}/{date_time_str}.jpg'
    saved_image = cv2.imwrite(dir_filename, image)
    if saved_image: print(f'Done saved capture filename : {date_time_str}.jpg')
    else: print(f'Failed saved capture filename : {date_time_str}.jpg')
    return saved_image