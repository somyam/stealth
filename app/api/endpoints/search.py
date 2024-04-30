from fastapi import FastAPI, HTTPException, APIRouter, Header, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from db.engine import get_db
from sqlalchemy import func
from db.models import Channel, Message, User, UserRole, Role, Guild
from typing import List
import logging
import subprocess
import json
from sqlalchemy import or_, case
import os

router = APIRouter()

@router.get("/keyword/{keyword}", response_model=None)
async def search_by_keyword(keyword: str, db: Session = Depends(get_db)) -> List[Message]:
    """API endpoint to search for messages using keyword input."""
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword must not be empty")
    try:
        messages = db.query(Message).filter(func.lower(Message.content).like(f"%{keyword}%")).all()
        print(len(messages), type(messages))
        return messages
    except SQLAlchemyError as e:
        logging.error(f"Database error during search by keyword: {e}")
        raise HTTPException(status_code=788, detail=f"An error occurred while searching for messages: {e}")
    finally:
        db.close()
        
@router.get("/date/{start_date}/{end_date}", response_model=None)
async def search_by_date(start_date: datetime, end_date: datetime, db: Session = Depends(get_db)) -> List[Message]:
    try:
        messages = db.query(Message).filter(
            or_(
                case(
                        (Message.timestamp_edited != None, Message.timestamp_edited),
                    else_=Message.timestamp
                ).between(start_date, end_date)
            )
        ).order_by(Message.timestamp).all()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
