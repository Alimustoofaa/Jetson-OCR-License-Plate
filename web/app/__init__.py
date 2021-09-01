from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .utils import get_query_token
from fastapi.templating import Jinja2Templates


app = FastAPI()

def mount_static_directory():
    app.mount("/dist", StaticFiles(directory="assets/dist"), name="dist")
    return app

def templates_enggine():
    templates = Jinja2Templates(directory="pages/")
    return templates

app.mount("/dist", StaticFiles(directory="web/assets/dist"), name="dist")
templates = Jinja2Templates(directory="web/pages/")
# @app.get("/")
# def form_post(request: Request):
#     result = "Type a number"
#     return templates.TemplateResponse('index.html', context={'request': request, 'result': result})
