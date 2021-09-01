import os
import cv2
import base64
import numpy as np
from datetime import datetime
from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from ..models import Vehicle as M_Vehicle
from ..schemas import Vehicle as S_Vehicle

ROOT = os.getcwd()
DIRECTORY_SAVE_IMAGE = os.path.join(ROOT, 'assets/dist/results_ocr')

def __decode_sting2image(image_encoded, filename):
    jpg_original = base64.b64decode(image_encoded)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)

    # Save image
    print(DIRECTORY_SAVE_IMAGE)
    dir_filename = f'{DIRECTORY_SAVE_IMAGE}/{filename}'
    cv2.imwrite(dir_filename, image)
    pass

def __extract_filename2_timestamp(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, '%y%m%d%H%M%S%f')
    return datetime_obj

def add_vehicle(db: Session, vehicle: S_Vehicle):
    __decode_sting2image(vehicle.image, vehicle.filename)
    db_vehicle = M_Vehicle(
        timestamp           = __extract_filename2_timestamp(vehicle.filename.split('.')[0]),
        license_plate       = vehicle.license_plate.result_ocr,
        conf_license_plate  = vehicle.license_plate.confidence,
        vehicle_type        = vehicle.vehicle_classification.clases,
        conf_vehicle_type   = vehicle.vehicle_classification.confidence,
        processing_time     = vehicle.processing_time,
        image_filename      = vehicle.filename,
    )
    
    db.add(db_vehicle); db.commit(); db.refresh(db_vehicle)
    return db_vehicle

def get_vehicles(db: Session, skip: int = 0, limit: int = 50) -> List[S_Vehicle]:
    return db.query(M_Vehicle).order_by(M_Vehicle.id.desc()).offset(skip).limit(limit).all()