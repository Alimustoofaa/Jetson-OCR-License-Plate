import os
import json
import numpy as np

POSITION_CAM = 'RA 88A'
# Config
ROOT = os.path.normpath(os.path.dirname(__file__))

DIRECTORY_MODEL         = os.path.expanduser('~/.Halotec-LPR/Model')

DIRECTORY_LOGGER        = os.path.expanduser('~/.Halotec-LPR/Logger')

DIRECTORY_SAVE_CAPTURE  = os.path.join(ROOT, 'captures')

GSTREAMER_PIPELINE = {
    'resolutions': {
        'high'      : (720, 1280),
        'medium'    : (640, 480),
        'low'       : (320, 240) },
    'framerate'     : 21,
    'flip_method'   : 0
}

RESOLUTIONS = {
    'high': (1280, 720),
    'medium': (640, 480),
    'low': (320, 240)
}
URL_VEHICLE_API = 'http://192.168.0.168:8765/list_vehicles/add'

PORT = 8001

'''
Area Detection
    D------------C
    |            |
    |            |
    A------------B
'''
A = (816, 848)
B = (1918, 735)
C = (1336, 598)
D = (615, 606)
AREA_DETECTION = np.array([A, B, C, D], np.int32)

CLASESS_MODEL_SSDNET = [
    'unlabeled', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 
    'traffic light', 'fire hydrant', 'street sign', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'hat', 'backpack', 'umbrella', 
    'shoe', 'eye glasses', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'plate', 
    'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 
    'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'mirror', 
    'dining table', 'window', 'desk', 'toilet', 'door', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 
    'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'blender', 'book', 'clock', 'vase',
    'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

VEHICLE_CLASESS = ['car', 'bus', 'truck']

COLOR = {
	'car'	: (0, 153, 0),
	'truck'	: (204,0,102),
	'bus'	: (204, 102, 0)
}

CLASESS_MODEL_LICENSE_PLATE = ['license_plate']

MIN_CONFIDENCE = 0.2

DETECTION_MODEL = {
    'license_plate' : {
        'filename': 'model_license_plate_iso_code.pt',
        'url' : 'https://github.com/Alimustoofaa/1-PlateDetection/releases/download/model_yolov5/license_plat_indonesia_best.pt',
        'file_size' : 14753191
    },
    'yolov5s': {
        'filename': 'model_yolov5s.pt',
        'url' : 'https://github.com/Alimustoofaa/1-PlateDetection/releases/download/model_yolov5/yolov5s.pt',
        'file_size' : 14796495
    }
}

REPLACE_NUMBER2ABJAD_DICT = {
    '7': 'T',
    '8': 'B',
    '5': 'S',
    '0': 'O',
    '4': 'C'
}

REPLACE_ABJAD2NUMBER_DICT = {
    'A': '4',
    'O': '0',
    'T': '7'
}

__file_kd_wilayah = open(os.path.join(os.getcwd(),'./kode_wilayah.json'))
KODE_WILAYAH_JSON = json.loads(__file_kd_wilayah.read())
KODE_WILAYAH_LIST = [i for i in KODE_WILAYAH_JSON.keys()]

# V4l2 Camera control
'''
exposure_auto 0x009a0901 (bool)   			: default=1 value=1
zoom 0x009a090d (int)    					: min=1 max=9 step=1 default=1 value=1
bypass_mode 0x009a2064 (intmenu)			: min=0 max=1 default=0 value=0
override_enable 0x009a2065 (intmenu)		: min=0 max=1 default=0 value=0
height_align 0x009a2066 (int)    			: min=1 max=16 step=1 default=1 value=1
size_align 0x009a2067 (intmenu)				: min=0 max=2 default=0 value=0
write_isp_format 0x009a2068 (bool)   		: default=0 value=0
sensor_signal_properties 0x009a2069 (u32)   : min=0 max=4294967295 step=1 default=0 [30][18] flags=read-only, has-payload
sensor_image_properties 0x009a206a (u32)    : min=0 max=4294967295 step=1 default=0 [30][16] flags=read-only, has-payload
sensor_control_properties 0x009a206b (u32)  : min=0 max=4294967295 step=1 default=0 [30][36] flags=read-only, has-payload
sensor_dv_timings 0x009a206c (u32)    		: min=0 max=4294967295 step=1 default=0 [30][16] flags=read-only, has-payload
low_latency_mode 0x009a206d (bool)   		: default=0 value=0
preferred_stride 0x009a206e (int)    		: min=0 max=65535 step=1 default=0 value=0
sensor_modes 0x009a2082 (int)    			: min=0 max=30 step=1 default=30 value=5 flags=read-only
'''
# v4l2-ctl -d 0 --set-ctrl vertical_flip=1 -c exposure=50000 -c saturation=5000
COMMAND_CAMERA_PROPERTY = 'v4l2-ctl -d 0 -c exposure=500000  -c saturation=5500'

# Straming camera
FPS = 30
# -> Lounch string
LAUNCH_STRING = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                f'caps=video/x-raw,format=BGR,width=640,height=480,framerate={FPS}/1 ' \
                '! videoconvert ! video/x-raw,format=I420 ' \
                '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                '! rtph264pay config-interval=1 name=pay0 pt=96'