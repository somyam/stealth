from fastapi import FastAPI, HTTPException, APIRouter, Header, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import subprocess
import json
import os
from db.engine import get_db
from db.models import Channel, Message, User, UserRole, Role, Guild
from fastapi.responses import JSONResponse
from .exporter import export_to_json
from .data_handler import insert_data

router = APIRouter()

@router.post("/export-channel/{channel_id}")
async def export_channel_to_json(channel_id: int, user_token: str = Header(...), db: Session = Depends(get_db)) -> JSONResponse:
    try:
        export_to_json(channel_id, user_token)
        with open('my_channel.json', 'r') as file:
            data = json.load(file)

        insert_data(data,db)
        return JSONResponse(content={"status": "success", "message": "Channel data exported and saved to database"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
