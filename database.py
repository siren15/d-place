from bson.int64 import Int64 as int64
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document as BeanieDocument, TimeSeriesConfig, Granularity, init_beanie
import motor
import os

database_url = os.environ['pt_mongo_url']

class Document(BeanieDocument):
    def __hash__(self):
        return hash(self.id)

class PixelPosition(BaseModel):
    x:int64 = 0
    y:int64 = 0
    colour:str = '#000000'

class ssedata(BaseModel):
    event:str 
    retry: int64
    data: List

class PixelPlace(Document):
    user: int64 = None
    date: datetime = datetime.now()
    x: int64 = 0
    y: int64 = 0
    colour: str = '#000000'

class logs(Document):
    guild_id: Optional[int64] = None
    channel_id: Optional[int64] = None

class prefixes(Document):
    guildid: Optional[int64] = None
    prefix: Optional[str] = None

class users(Document):
    id: int64
    position:PixelPosition
    time: datetime = datetime.now()
    pixels_placed: int64 = 0
    
async def connect_db():
    dburl = motor.motor_asyncio.AsyncIOMotorClient(database_url)
    await init_beanie(database=dburl.hackathon, document_models=[
        PixelPlace,
        logs,
        prefixes,
        users
    ])