import time
import uvicorn
import threading
import contextlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from web.app.routes import list_vehicles, streaming

class Server(uvicorn.Server):
	def install_signal_handlers(self):
		pass

	@contextlib.contextmanager
	def run_in_thread(self):
		thread = threading.Thread(target=self.run)
		thread.start()
		try:
			while not self.started:
				time.sleep(1e-3)
			yield
		finally:
			self.should_exit = True
			thread.join()

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.mount("/dist", StaticFiles(directory="web/assets/dist"), name="dist")
app.mount("/captures", StaticFiles(directory="captures"), name="captures")
templates = Jinja2Templates(directory="web/pages/")

app.include_router(list_vehicles.router)
app.include_router(streaming.router)
app.add_websocket_route('/ws/list_vehicles', list_vehicles.get_vehicle_socket)
app.add_websocket_route('/ws/streaming', streaming.get_frame_socket)