from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

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
	
class Vehicle(BaseModel):
	vehicle_classification: VehicleClassification
	license_plate: LicensePlate
	processing_time: float
	image: bytes
	filename: str