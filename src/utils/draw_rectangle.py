import cv2
import base64
from .logger import asctime
from config import POSITION_CAM

def draw_rectangle(image, bbox_dict, encoded=False):
	'''
	Draw bbox detection vehicle and license plate
	Args:
		image(np.array): image for drawed
		bbox_dict(dict): {'name':value(list)}
		encoded(boolen): True/False retrun image decode
	Return:
		drawed_image(any): image drawed retrun str if decoded else np.array 
	'''
	for name in bbox_dict:
		if bbox_dict[name][1]:
			if name == 'vehicle_type':
				color_reactangle = (0, 204, 0) # Green
			elif name == 'license_plate':
				color_reactangle = (204, 102, 0) # Red
			
			x_min, y_min = bbox_dict[name][1][0], bbox_dict[name][1][1]
			x_max, y_max = bbox_dict[name][1][2], bbox_dict[name][1][3]
			# Draw rectangle
			cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color_reactangle, 1)
			# Add label
			cv2.rectangle(image, (x_min, y_min), (x_min+50, y_min+15), color_reactangle, cv2.FILLED)
			cv2.putText(image, f'{bbox_dict[name][0]}', (x_min+2,y_min+12), cv2.FONT_HERSHEY_PLAIN, 0.7, (255, 255, 255), 1)
	
	# Draw datetime in black background
	asctime_str = asctime()
	cv2.rectangle(image, (0, int((2/100)*image.shape[1])), (int((46/100)*image.shape[0]), 0), (0,0,0), cv2.FILLED)
	cv2.putText(image, f'{POSITION_CAM} | {asctime_str}', (10,15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
	if encoded:
		image_list = cv2.imencode('.jpg', image)[1]
		image_bytes = image_list.tobytes()
		image_encoded = base64.b64encode(image_bytes)
		return image_encoded
	else: return image
			