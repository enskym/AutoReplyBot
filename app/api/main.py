from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import sys
from pathlib import Path

# Proje kök dizinini Python path'e ekle
current_file = Path(__file__).resolve()
project_root = str(current_file.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database.database import get_db
from database.models import MessageTemplate, MessageLog
from .schemas import (
    MessageTemplate as MessageTemplateSchema,
    MessageTemplateCreate,
    MessageTemplateUpdate,
    MessageLog as MessageLogSchema,
    DashboardStats,
    ApiResponse
)

app = FastAPI(title="AutoReplyBot API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm originlere izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_response(data=None, success=True, message=None):
    return {
        "success": success,
        "message": message,
        "data": data
    }

def serialize_template(template: MessageTemplate) -> dict:
    return {
        "id": template.id,
        "trigger_text": template.trigger_text,
        "response_text": template.response_text,
        "is_active": template.is_active,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat() if template.updated_at else None
    }

def serialize_message_log(log: MessageLog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "incoming_message": log.incoming_message,
        "response_message": log.response_message,
        "template_id": log.template_id,
        "created_at": log.created_at.isoformat()
    }

@app.get("/")
async def root():
    return create_response(message="AutoReplyBot API çalışıyor")

# Mesaj Şablonları
@app.get("/templates/", response_model=ApiResponse)
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(MessageTemplate).all()
    return create_response(data=[serialize_template(t) for t in templates])

@app.get("/templates/{template_id}", response_model=ApiResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    return create_response(data=serialize_template(template))

@app.post("/templates/", response_model=ApiResponse)
def create_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    db_template = MessageTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return create_response(data=serialize_template(db_template), message="Şablon başarıyla oluşturuldu")

@app.put("/templates/{template_id}", response_model=ApiResponse)
def update_template(template_id: int, template: MessageTemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    
    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return create_response(data=serialize_template(db_template), message="Şablon başarıyla güncellendi")

@app.delete("/templates/{template_id}", response_model=ApiResponse)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    db.delete(template)
    db.commit()
    return create_response(message="Şablon başarıyla silindi")

# Mesaj Geçmişi
@app.get("/logs/", response_model=ApiResponse)
def get_message_logs(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    logs = db.query(MessageLog).order_by(MessageLog.created_at.desc()).offset(skip).limit(limit).all()
    return create_response(data=[serialize_message_log(log) for log in logs])

# Dashboard İstatistikleri
@app.get("/stats/", response_model=ApiResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        # Son 24 saatteki mesajları al
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_messages = db.query(MessageLog).filter(
            MessageLog.created_at >= last_24h
        ).order_by(MessageLog.created_at.desc()).limit(10).all()

        # Toplam mesaj sayısı
        total_messages = db.query(func.count(MessageLog.id)).scalar() or 0

        # Aktif şablon sayısı
        active_templates = db.query(func.count(MessageTemplate.id)).filter(
            MessageTemplate.is_active == True
        ).scalar() or 0

        # Yanıt oranı (şablon kullanılan mesajlar / toplam mesajlar)
        messages_with_template = db.query(func.count(MessageLog.id)).filter(
            MessageLog.template_id.isnot(None)
        ).scalar() or 0
        response_rate = (messages_with_template / total_messages * 100) if total_messages > 0 else 0

        stats = {
            "total_messages": total_messages,
            "active_templates": active_templates,
            "response_rate": response_rate,
            "recent_messages": [serialize_message_log(msg) for msg in recent_messages]
        }
        
        return create_response(data=stats)
    except Exception as e:
        logger.error(f"Stats endpoint error: {str(e)}")
        return create_response(success=False, message=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 