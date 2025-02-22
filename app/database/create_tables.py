import os
import sys
from pathlib import Path

# UTF-8 encoding'i zorla
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

try:
    # Proje kök dizinini bul ve Python path'e ekle
    current_file = os.path.abspath(__file__)
    project_root = str(Path(current_file).parent.parent)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from database.database import Base, engine
    from database.models import MessageTemplate, MessageLog

    def create_tables():
        print("Veritabanı tabloları oluşturuluyor...")
        try:
            Base.metadata.create_all(bind=engine)
            print("Tablolar başarıyla oluşturuldu!")
        except Exception as e:
            print(f"Tablo oluşturma hatası: {str(e)}")
            raise

    if __name__ == "__main__":
        create_tables()

except Exception as e:
    print(f"Genel hata: {str(e)}")
    raise 