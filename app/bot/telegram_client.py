import logging
from telethon import TelegramClient, events
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import MessageTemplate, MessageLog
import os
from dotenv import load_dotenv
import asyncio
import signal

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()

class TelegramHandler:
    def __init__(self):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.client = None
        self.session_file = 'user_session'
        
    def _remove_session(self):
        """Session dosyasını temizle"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            if os.path.exists(f"{self.session_file}.session"):
                os.remove(f"{self.session_file}.session")
            logger.info("Session dosyası başarıyla silindi")
        except Exception as e:
            logger.error(f"Session dosyası silinirken hata oluştu: {str(e)}")

    async def disconnect(self):
        """Client'ı düzgün şekilde kapat"""
        try:
            if self.client:
                await self.client.disconnect()
                logger.info("Telegram client kapatıldı")
        except Exception as e:
            logger.error(f"Client kapatılırken hata oluştu: {str(e)}")
        finally:
            self._remove_session()

    async def start(self):
        """Telegram client'ı başlat"""
        try:
            # Client'ı oluştur ve başlat
            self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
            
            # Sinyal handler'larını ekle
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, lambda s, f: asyncio.create_task(self.disconnect()))
            
            # Mesaj handler'ını ekle
            @self.client.on(events.NewMessage())
            async def handle_new_message(event):
                # Kendi mesajlarımızı yanıtlama
                if event.is_private and not event.out:
                    await self.handle_message(event)

            # Client'ı başlat
            await self.client.start(phone=self.phone)
            logger.info("Telegram client başlatıldı")
            
            # Client'ı çalışır durumda tut
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Client başlatılırken hata oluştu: {str(e)}")
            raise
        finally:
            await self.disconnect()

    async def handle_message(self, event):
        """Gelen mesajları işle"""
        try:
            db = SessionLocal()
            
            # Mesaj bilgilerini al
            incoming_message = event.message.text
            sender = await event.get_sender()
            user_id = str(sender.id)
            
            # Mesaj şablonunu kontrol et
            template = db.query(MessageTemplate).filter(
                MessageTemplate.trigger_text.ilike(incoming_message),
                MessageTemplate.is_active == True
            ).first()
            
            # Yanıt mesajını hazırla
            if template:
                response_text = template.response_text
                template_id = template.id
            else:
                response_text = "Üzgünüm, bu mesaj için uygun bir yanıt şablonu bulamadım."
                template_id = None
            
            # Mesajı logla
            message_log = MessageLog(
                user_id=user_id,
                incoming_message=incoming_message,
                response_message=response_text,
                template_id=template_id
            )
            db.add(message_log)
            db.commit()
            
            # Yanıt gönder
            await event.reply(response_text)
            
        except Exception as e:
            logger.error(f"Mesaj işlenirken hata oluştu: {str(e)}")
            await event.reply("Üzgünüm, bir hata oluştu.")
        
        finally:
            db.close()

async def run_client():
    """Telegram client'ı çalıştır"""
    handler = TelegramHandler()
    try:
        await handler.start()
    except KeyboardInterrupt:
        await handler.disconnect()
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        await handler.disconnect() 