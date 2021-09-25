from typing import List
from pydantic import BaseModel

class VehicleClassification(BaseModel):
	vehicle_type: str
	image: bytes

class LicensePlate(BaseModel):
	bbox: List
	license_plate: str
	confidence: float
	image: bytes
	
class ResultProcess(BaseModel):
	id: int
	processing_time: float
	vehicle_classification: VehicleClassification
	license_plate: LicensePlate