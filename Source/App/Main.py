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
    
    rec = db.query(Recording).first()
    if rec:
        return rec.recording_id
        
    print("Создаю синтетические данные (с кривыми)...")
    new_rec = Recording(recording_id=str(uuid.uuid4()), filename="test_forest_01.wav", sample_rate_hz=384000)
    
    seq1 = CallSequence(sequence_id=str(uuid.uuid4()), t_start_ms=1000, t_end_ms=1800, f_min_khz=35, f_max_khz=85)
    
    c1 = BatCall(t_start_ms=1010, t_end_ms=1030, f_min_khz=40, f_max_khz=80, peak_khz=50.0, peak_ms=1020)
    c1.signal_curves = {"main": [[1010, 80], [1015, 60], [1020, 50], [1025, 45], [1030, 40]]}
    
    c2 = BatCall(t_start_ms=1200, t_end_ms=1220, f_min_khz=38, f_max_khz=78, peak_khz=48.0, peak_ms=1210)
    c2.signal_curves = {"main": [[1200, 78], [1205, 58], [1210, 48], [1215, 43], [1220, 38]]}
    
    seq1.calls.extend([c1, c2])
    new_rec.sequences.append(seq1)
    
    db.add(new_rec)
    db.commit()
    
    return new_rec.recording_id

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
        
        # 1. Инициализация единого источника истины (Store)
        self.store = AppStore(self.db)
        self.store.initialize(recording_id)
        
        tabs = QTabWidget()
        
        # 2. Передаем Store в обе вкладки. 
        # Теперь вкладки сами знают, как общаться со Стором.
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
