from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from web.app.routes import list_vehicles, streaming

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.mount("/dist", StaticFiles(directory="web/assets/dist"), name="dist")
templates = Jinja2Templates(directory="web/pages/")

app.include_router(list_vehicles.router)
app.include_router(streaming.router)
app.add_websocket_route('/ws/list_vehicles', list_vehicles.get_vehicle_socket)
app.add_websocket_route('/ws/streaming', streaming.get_frame_socket)