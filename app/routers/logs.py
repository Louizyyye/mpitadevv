# app/routers/logs.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Log
from app.schemas.logs import LogCreate, LogResponse

router = APIRouter(
    prefix="/api/logs",
    tags=["Logs"]
)

# ------------------- CREATE LOG -------------------
@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    """
    Create a new log entry
    """
    db_log = Log(
        user_id=log.user_id,
        level=log.level,
        message=log.message
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# ------------------- GET ALL LOGS -------------------
@router.get("/", response_model=List[LogResponse])
def get_all_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all logs
    """
    logs = db.query(Log).offset(skip).limit(limit).all()
    return logs

# ------------------- GET LOG BY ID -------------------
@router.get("/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a log by its ID
    """
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# ------------------- DELETE LOG -------------------
@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    """
    Delete a log by its ID
    """
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"detail": "Log deleted successfully"}
