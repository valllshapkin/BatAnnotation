from PySide6.QtCore import QObject
from sqlalchemy.orm import Session
from BatAnnotation.API import AnnotationManager
from BatAnnotation.QtModels import QtLookups, QtRecording

class AppStore(QObject):
    def __init__(self, db_session: Session):
        super().__init__()
        self.db = db_session
        self.api = AnnotationManager(db_session)
        
        self.lookups = QtLookups()
        self.recording = QtRecording()
        
        # Флаг наличия несохраненных изменений
        self.is_dirty = False

    def initialize(self, recording_id: str):
        self.sync_lookups_from_db()
        self.load_recording(recording_id)

    def load_recording(self, recording_id: str):
        """Загружает новую запись из БД (Используется при выборе в Combobox)"""
        mem_rec = self.api.load_recording(recording_id)
        if mem_rec:
            self.recording.load_from(mem_rec)
            # При загрузке данные свежие, сбрасываем флаг
            self.is_dirty = False

    def sync_lookups_from_db(self):
        mem_lookups = self.api.load_lookups()
        self.lookups.load_from(mem_lookups)

    def save_recording_to_db(self):
        mem_rec_to_save = self.recording.to_memory()
        self.api.save_recording(mem_rec_to_save)
        
        for seq in self.recording.sequences:
            seq._is_new = False
            for call in seq.calls:
                call._is_new = False
                
        # После сохранения изменения зафиксированы
        self.is_dirty = False
