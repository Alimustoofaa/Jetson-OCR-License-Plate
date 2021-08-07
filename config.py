import os
import json

# Config
ROOT = os.path.normpath(os.path.dirname(__file__))
DIRECTORY_MODEL = 'src/models'

CAMERA_URL = {
    'url' : [
        'http://119.2.50.116:83/mjpg/video.mjpg?camera=1&timestamp=1617707000118',
        'rtsp://root:halotec@192.168.0.11/axis-media/media.amp',
        'http://192.168.0.11:9080/mjpg/video.mjpg'
    ]
}

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

ADAM_CONFIG = {
    'ip' : '192.168.0.126',
    'username' : 'root',
    'password' : '00000000'
}

PORT = 8004

CLASESS = ['license_plate']

DETECTION_MODEL = {
    'filename': 'model_license_plate_iso_code.pt',
    'url' : 'https://github.com/Alimustoofaa/1-PlateDetection/releases/download/model_yolov5/license_plat_indonesia_best.pt',
    'file_size' : 14753191
}

WORD_FOR_REPLACE = {
    # Number to text
    '0' : 'U',
	'6' : 'G',
	'O' : '0',
	# Text to number
	'F' : '0',
	'H' : '0',
    'M' : '0',
    'A' : '4',
    'D' : '0',
    'B' : '8',
	'E' : '0',
    'R' : '3',
    'S' : '3',
	# Number to number
	'1' : '4'
}

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

COMMAND_CAMERA_PROPERTY = 'v4l2-ctl -d 0 --set-ctrl vertical_flip=1 -c exposure=50000 -c saturation=5000'