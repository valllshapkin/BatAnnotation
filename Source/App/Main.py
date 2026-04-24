import sys
import uuid
from pathlib import Path

ScriptDir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ScriptDir.parent))
sys.path.insert(0, str(ScriptDir))

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = create_engine(f"sqlite:///{ScriptDir.joinpath('test.db').as_posix()}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestBase(DeclarativeBase): pass

from BatAnnotation import config as BatAnnotationConfig
BatAnnotationConfig.BASE = TestBase

from BatAnnotation.manage import create_all
create_all(engine)

from BatAnnotation.CommonSeeds.Core import seed_all as seed_core
from BatAnnotation.CommonSeeds.EuropeGeneral import seed_all as seed_eu
from BatAnnotation.Tables import Recording, CallSequence, BatCall

def setup_synthetic_data(db: Session):
    seed_core(db)
    seed_eu(db)
    
    count = db.query(Recording).count()
    if count >= 1000:
        print(f"Стресс-данные уже существуют ({count} записей). Загружаю первую.")
        return db.query(Recording).first().recording_id
        
    print("Генерация стресс-теста (1000 записей, 30k calls, кривые и fmaxe)... Это займет пару секунд.")
    
    recs_to_add = []
    
    for i in range(1000):
        # ДОБАВЛЕНО: duration_s = 10.0 для правильного масштаба при клике в фон!
        rec = Recording(
            recording_id=str(uuid.uuid4()), 
            filename=f"stress_test_bat_{i:04d}.wav", 
            sample_rate_hz=384000,
            duration_s=10.0 
        )
        
        for j in range(3):
            seq = CallSequence(sequence_id=str(uuid.uuid4()), t_start_ms=1000+j*2000, t_end_ms=1800+j*2000, f_min_khz=35, f_max_khz=85)
            
            for k in range(10):
                t_s = 1010 + j*2000 + k*70
                t_e = t_s + 20
                call = BatCall(
                    call_id=str(uuid.uuid4()),
                    t_start_ms=t_s, t_end_ms=t_e, 
                    f_min_khz=40, f_max_khz=80, 
                    peak_khz=50.0, peak_ms=t_s+10
                )
                call.signal_curves = {"main": [[t_s, 80], [t_s+5, 60], [t_s+10, 50], [t_s+15, 45], [t_s+20, 40]]}
                seq.calls.append(call)
                
            rec.sequences.append(seq)
            
        recs_to_add.append(rec)
        
        if len(recs_to_add) >= 100:
            db.add_all(recs_to_add)
            db.commit()
            recs_to_add = []
            
    if recs_to_add:
        db.add_all(recs_to_add)
        db.commit()
        
    print("Генерация завершена успешно!")
    return db.query(Recording).first().recording_id

# ==============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ==============================================================================
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from App.EditorWidget import EditorWidget
from App.LookupsWidget import LookupsEditorWidget
from App.Store import AppStore

class MainWindow(QMainWindow):
    def __init__(self, recording_id: str):
        super().__init__()
        self.setWindowTitle("Bat Annotation Advanced Studio v4.0 (Store Architecture)")
        self.resize(1400, 800)
        
        self.db = SessionLocal()
        
        self.store = AppStore(self.db)
        self.store.initialize(recording_id)
        
        tabs = QTabWidget()
        
        self.editor_tab = EditorWidget(self.store)
        tabs.addTab(self.editor_tab, "🦇 Интерактивная Разметка")
        
        self.lookups_tab = LookupsEditorWidget(self.store)
        tabs.addTab(self.lookups_tab, "📚 Справочники (БД)")
        
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    with SessionLocal() as db:
        test_rec_id = setup_synthetic_data(db)
        
    window = MainWindow(test_rec_id)
    window.show()
    sys.exit(app.exec())
