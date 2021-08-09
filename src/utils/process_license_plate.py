import cv2

from src.schema.config_ocr import ConfigOcr
from src.app import LicensePlateDetection
from src.app import OpticalCharacterRecognition

model   = LicensePlateDetection()
ocr     = OpticalCharacterRecognition()

def detection_object(image):
    '''
    Detection license plate
    and filter clasess, confidence
    Args:
        image(np.array): image for cropped
    return:
        result(tuple): (
                image_cropped(np.array): image croped,
                confidence(float): confidence level,
                bbox(list): bbox detection [x_min, y_min, x_max, y_max]
            )

    '''
    result_detection = model.prediction(image)
    license_plate = model.filter_and_crop(
        img=image, results=result_detection, min_confidence=0.0
    )
    if len(license_plate[0]) >=1 and license_plate[1] > 0 and len(license_plate[2]) == 4:
        print(f'Got license plate detection confidence : {round(license_plate[1], 2)} %')
    else: print(f'License plate not found')
    return license_plate

def resize(image, height_percent=180, width_percent=180):
	'''
	resize image by percent
    Args:
        image(np.array): image
        height_percent(int): percentage height
        width_percent(int): percentage width
    Return:
        image(np.array): image resized
	'''
	height = int(image.shape[0] * height_percent / 100)
	width = int(image.shape[1] * width_percent / 100)
	dim = (width, height)
	new_img = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
	print(f'Resize image to : {new_img.shape}')
	return new_img

def detect_char(image, output=False):
    '''
    Detection charcters text in image
    Args:
        image(np.array): image.
        output(boolean): output detection default (output=False)
    Return:
        result(boolean|list): result detection character
    '''
    detected_char = ocr.detect_char(image)
    if detected_char[0]:
        print(f'Found text in image : {" ".join([str(i) for i in detected_char[0]])}')
    else:
        print(f'Not found text in image')

    if output:
        results = detected_char[0][0]
    else: 
        if detected_char[0]: results = True
        else: results = False
    return results

def read_text(image, position_text='horizontal', clasess_name='license_plate'):
    '''
    Set methods and value config ocr
    methods view schema/config_ocr.py
    Args:
        image(np.array): image for read text
        position_text(str): position text vertical/horizontal (default=vertical)
        clasess_name(str): clasess name read text (default=license_plate)
    Retrun:
        result(list): [([[28, 32], [52, 32], [52, 64], [28, 64]], 'text', 0.9846626687831872)]
    '''
    if position_text == 'horizontal':
        config = ConfigOcr(
            beam_width      = 8,
            batch_size      = 10,
            text_threshold  = 0.5,
            link_threshold  = 0.9,
            low_text        = 0.4,
            slope_ths       = 0.9,
            mag_ratio 		= 1,
            add_margin		= 0.5,
            width_ths       = 0.5
        )
    elif position_text == 'vertical':
        config = ConfigOcr(
            batch_size  	= 10,
            text_threshold 	= 0.2,
            link_threshold 	= 0.9,
            low_text 		= 0.4,
            add_margin		= 0
        )

    results = ocr.ocr_image(image=image, config=config)
    if position_text == 'horizontal': results.sort(reverse=False)
    else : results = results
    print(f'Ocr {clasess_name} : {" ".join([i[1] for i in results])}')
    return results