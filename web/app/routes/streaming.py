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
			await websocket.send_json({'results': {
				'image_streaming': str(process.frame_image_encoded)
			}})
			await asyncio.sleep(0.5)
	except:
		await websocket.close()