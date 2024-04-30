from fastapi import FastAPI
from db.engine import get_db

app = FastAPI()

def init_app(app: FastAPI):
    from .api.endpoints.channel import router as channel_router
    from .api.endpoints.search import router as search_router
    app.include_router(channel_router)
    app.include_router(search_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}