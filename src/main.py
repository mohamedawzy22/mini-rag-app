from fastapi import FastAPI
from routes import base ,data
from pymongo import AsyncMongoClient
from helpers.config import get_setting

app = FastAPI()


async def startup_db_client():
    settings = get_setting()
    app.mongodb_conn = AsyncMongoClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]
    


async def shutdown_db_client():
    
    app.mongodb_conn.close()
    
app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

app.include_router(base.base_router)
app.include_router(data.data_router)

