from server import Server
from uvicorn.config import Config

from src.process import vehicle_detection_and_counting

config = Config("server:app", host="127.0.0.1", port=8001, loop="asyncio", reload=True)
server = Server(config=config)

with server.run_in_thread():
	while True:
		vehicle_detection_and_counting()