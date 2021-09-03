import asyncio
import time
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from fastapi.params import Query
from pydantic.types import Json
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from .. import controllers, templates
from ..config import engine, get_session_db
from ..schemas import Vehicle
from ..utils import get_token_header, socket

import os
import glob
from config import DIRECTORY_SAVE_CAPTURE

from src import process
router = APIRouter()

router = APIRouter(
	prefix="/streaming",
	tags=["streaming"],
	# dependencies=[Depends(get_token_header)],
	responses={404: {"description": "Not found"}},
)

@router.get('/')
async def get_vehicles(
	request: Request
	):
	results = {
		'title' : 'Streaming Camera'
	}
	return templates.TemplateResponse('streaming.html', context={'request': request, 'results': results})

async def get_frame_socket(
	websocket: WebSocket,
	):
	await websocket.accept()
	
	try:
		while True:
			results_dict_list = list()

			path_image_list = [i for i in sorted(glob.glob(f'{DIRECTORY_SAVE_CAPTURE}/*.jpg'), key=os.path.getatime)]
			for i in path_image_list:
				filename = i.split('/')[-1]
				filename_list = filename.split('_')
				vehicle_type = filename_list[0]
				confidence = filename_list[1]
				image_name = filename.split('.jpg')[0]
				results_dict_list.append({
					'vehicle_type':vehicle_type,
					'conf_vehicle_type': confidence,
					'image_filename': image_name
				})
			await websocket.send_json({'results': {
				'image_streaming': str(process.frame_image_encoded),
				'results_counting': results_dict_list
			}})
			await asyncio.sleep(0.1)
	except:
		await websocket.close()