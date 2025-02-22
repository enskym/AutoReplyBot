import asyncio
import os
import signal
from dotenv import load_dotenv
import uvicorn
from api.main import app
from bot.telegram_client import run_client
from concurrent.futures import ThreadPoolExecutor
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Application:
    def __init__(self):
        self.executor = None
        self.api_task = None
        self.should_exit = False

    def run_api(self):
        """API sunucusunu çalıştır"""
        config = uvicorn.Config(
            "api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True
        )
        server = uvicorn.Server(config)
        server.run()

    async def shutdown(self, sig=None):
        """Uygulamayı düzgün şekilde kapat"""
        if sig:
            logger.info(f'Received exit signal {sig.name}...')
        
        self.should_exit = True
        
        # Executor'ı kapat
        if self.executor:
            self.executor.shutdown(wait=False)
        
        # Event loop'u temizle
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info('Shutdown complete.')

    async def main(self):
        """Ana uygulama"""
        # Sinyal handler'larını ekle
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: asyncio.create_task(self.shutdown(s)))

        # API ve Telegram client'ı aynı anda çalıştır
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.api_task = asyncio.get_event_loop().run_in_executor(self.executor, self.run_api)
        
        try:
            # Telegram client'ı ana thread'de çalıştır
            await run_client()
        except Exception as e:
            logger.error(f"Uygulama hatası: {str(e)}")
        finally:
            await self.shutdown()

if __name__ == "__main__":
    app = Application()
    try:
        asyncio.run(app.main())
    except KeyboardInterrupt:
        logger.info("Uygulama kullanıcı tarafından kapatıldı.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
    finally:
        logger.info("Uygulama kapatıldı.")