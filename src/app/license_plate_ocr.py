'''
@author     : Ali Mustofa HALOTEC
@module     : OCR License Plate Indonesia
@Created on : 7 Agust 2021
'''

import cv2
import torch
import easyocr
from PIL import Image, ImageDraw

class OpticalCharacterRecognition:
    '''
    Load model library Ocr
    '''
    def __init__(self):
        self.device         = True if torch.cuda.is_available() else False
        self.list_langs     = ['en', 'id', 'la']
        self.recog_network  = 'latin_g2'
        self.reader         = easyocr.Reader(self.list_langs, gpu = self.device, recog_network = self.recog_network)

    def detect_char(self, image):
        '''
        Detection character in image
        Args:
            image(np.array): image for detect character
        Retrun:
            result(list): [[x_min, x_max, y_min, y_max]], []
        '''
        return self.reader.detect(image)

    def ocr_image(self, image, config):
        '''
        Read text in image with library easy ocr
        with configuration in param config
        Args:
            image(np.array): image for ocr
            config(schema.config_ocr): configuration library ocr
        Retrun:
            result(list): [([[28, 32], [52, 32], [52, 64], [28, 64]], 'text', confidence(float))]
        '''
        results = self.reader.readtext(
            image,
            detail          = config.detail,
            decoder         = config.decoder,
            beamWidth       = config.beam_width,
            batch_size      = config.batch_size,
            workers         = config.workers,
            allowlist       = config.allow_list,
            blocklist       = config.blocklist,
            paragraph       = config.paragraph,
            min_size        = config.min_size,
            rotation_info   = config.rotation_info,
            # Contrast
            contrast_ths    = config.contrast_ths,
            adjust_contrast = config.adjust_contrast,
            # Text detection
            text_threshold  = config.text_threshold + 0.1 if self.device else config.text_threshold,
            low_text        = config.low_text,
            link_threshold  = config.link_threshold,
            canvas_size     = config.canvas_size,
            mag_ratio       = config.mag_ratio
        )
        return results
    
    def draw_boxes(self, image, bounds, color='yellow', width=2):
        text = []
        confidence = []
        image = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)

        for bound in bounds:
            if bound[2] > 0.0:
                confidence.append(bound[2])
                text.append(bound[1])
                p0, p1, p2, p3 = bound[0]
                draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)
        
        # Calculate AVG confidence level
        avgConf = sum(confidence)/len(confidence)
        return image, text, avgConf