from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import MessageTemplate, MessageLog

app = FastAPI(title="AutoReplyBot API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm originlere izin veriyoruz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic modelleri
class MessageTemplateBase(BaseModel):
    trigger_text: str
    response_text: str
    is_active: bool = True

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateResponse(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True

@app.get("/")
async def root():
    return {"message": "AutoReplyBot API çalışıyor"}

@app.post("/templates/", response_model=MessageTemplateResponse)
def create_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    """Yeni mesaj şablonu oluştur"""
    db_template = MessageTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@app.get("/templates/", response_model=List[MessageTemplateResponse])
def get_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm mesaj şablonlarını listele"""
    templates = db.query(MessageTemplate).offset(skip).limit(limit).all()
    return templates

@app.get("/templates/{template_id}", response_model=MessageTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Belirli bir mesaj şablonunu getir"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    return template

@app.put("/templates/{template_id}", response_model=MessageTemplateResponse)
def update_template(template_id: int, template: MessageTemplateCreate, db: Session = Depends(get_db)):
    """Mesaj şablonunu güncelle"""
    db_template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    for key, value in template.dict().items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@app.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Mesaj şablonunu sil"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Şablon bulunamadı")
    
    db.delete(template)
    db.commit()
    return {"message": "Şablon başarıyla silindi"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 