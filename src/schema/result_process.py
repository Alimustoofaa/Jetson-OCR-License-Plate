from typing import List
from pydantic import BaseModel

class VehicleClassification(BaseModel):
	bbox: List
	confidence: float
	clases: str

class LicensePlate(BaseModel):
	bbox: List
	confidence: float
	result_ocr: str
	
class ResultProcess(BaseModel):
	vehicle_classification: VehicleClassification
	license_plate: LicensePlate
	processing_time: float
	image: bytes