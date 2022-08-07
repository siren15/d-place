from asyncio import ensure_future
import asyncio
import json
from fastapi import FastAPI
from starsessions import SessionMiddleware
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import database as db
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://beni2am.herokuapp.com",
    "http://beni2am.herokuapp.com",
    "https://haigb.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SESSION_SECRET = os.environ['sesh_secret']
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, max_age=7200, autoload=True)

@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})

@app.get('/api/fetch')
async def sse(request:Request):
    async def event_generator():
        px = []
        while True:
            if await request.is_disconnected():
                break
            pxs = [dict(dict(x=p.x,y=p.y,colour=p.colour)) async for p in db.PixelPlace.find_all()]
            pstr = json.dumps(pxs)
            if pxs != px:
                px = pxs
                yield {
                    "event": "new_pixels",
                    "retry": 15000,
                    "data": pstr
                }
        await asyncio.sleep(1)
    return EventSourceResponse(event_generator())

@app.post('/api/add')
async def addpixel(request: Request, position: db.PixelPosition):
    pos = await db.PixelPlace.find_one({'x':position.x, 'y':position.y})
    if pos is None:
        await db.PixelPlace(x=position.x, y=position.y, colour=position.colour).insert()
    else:
        pos.colour = position.colour
        await pos.save()
    return position

ensure_future(db.connect_db())