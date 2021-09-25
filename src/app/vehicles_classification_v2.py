'''
@author     : Ali Mustofa HALOTEC
@module     : Vehicle Classification Jetson Interface
@Created on : 14 Sept 2021
'''

import jetson.inference as jetson_interface
import jetson.utils as jetson_utils

from config import CLASESS_MODEL_SSDNET, VEHICLE_CLASESS, MIN_CONFIDENCE

class VehicleClassification:
	def __init__(self):
		self.network    = 'ssd-mobilenet-v2'
		self.overlay    = 'box, labels, conf'
		self.threshold  = MIN_CONFIDENCE
		self.model      = jetson_interface.detectNet(self.network, threshold=self.threshold)

	def __np_image2_cuda_image(self, image):
		return jetson_utils.cudaFromNumpy(image)

	def filter_and_crop(self, results, min_confidence=0.0):
		'''
		Format result(
		-- ClassID: int()
		-- Confidence: float()
		-- Left:    float()
		-- Top:     float()
		-- Right:   float()
		-- Bottom:  float()
		-- Width:   float()
		-- Height:  float()
		-- Area:    float()
		-- Center:  tuple(float(), float())
		)
		Filter min confidence prediction and classes id/name
		Cropped image and get index max value confidence lavel
		Args:
			results(jetson.inference.detectNet.Detection) : results prediction ssd-mobilenet-v2
			min_confidence(float(range 0.0 - 1.0)) : minimal confidence for filter results
		Return:
			result(list) : [x_min, y_min, x_max, y_max, classes_name, confidence]
		'''
		vehicle_list = list()

		if len(results) >= 1:
			for result in results:
				classes_name    = CLASESS_MODEL_SSDNET[int(result.ClassID)]
				confidence      = result.Confidence
				if classes_name in VEHICLE_CLASESS and confidence > min_confidence:
					x_min, y_min    = int(result.Left), int(result.Top)
					x_max, y_max    = int(result.Right), int(result.Bottom)
					vehicle_list.append([x_min, y_min, x_max, y_max, classes_name, confidence])
		return vehicle_list

	def detection(self, image):
		'''
		Detection image with ssd-mobilenet-v2
		-> convert image(np.array) to CudaImage
		-> Detection 
		Args:
			img(np.array): image for prediction,
		Retrun:
			result(list): result detection ssd-mobilenet-v2(<jetson.inference.detectNet.Detection object at 0x7f9be9f090>)
		'''
		cuda_image = self.__np_image2_cuda_image(image)
		results = self.model.Detect(cuda_image, overlay=self.overlay)
		return results