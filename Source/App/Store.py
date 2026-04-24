from PySide6.QtCore import QObject
from sqlalchemy.orm import Session
from BatAnnotation.API import AnnotationManager
from BatAnnotation.QtModels import QtLookups, QtRecording

class AppStore(QObject):
    """
    Единый источник истины (Single Source of Truth).
    Содержит в себе менеджер БД, справочники и текущую активную запись.
    Любой виджет, у которого есть ссылка на store, получает доступ ко всему приложению.
    """
    def __init__(self, db_session: Session):
        super().__init__()
        self.db = db_session
        self.api = AnnotationManager(db_session)
        
        # Реактивное состояние
        self.lookups = QtLookups()
        self.recording = QtRecording()

    def initialize(self, recording_id: str):
        """Загружает исходные данные из БД при запуске."""
        self.sync_lookups_from_db()
        mem_rec = self.api.load_recording(recording_id)
        if mem_rec:
            self.recording.load_from(mem_rec)

    def sync_lookups_from_db(self):
        """Запрашивает актуальные справочники из БД и обновляет реактивные словари."""
        mem_lookups = self.api.load_lookups()
        self.lookups.load_from(mem_lookups)

    def save_recording_to_db(self):
        """Сохраняет текущую разметку в БД и сбрасывает флаги 'нового' элемента."""
        mem_rec_to_save = self.recording.to_memory()
        self.api.save_recording(mem_rec_to_save)
        
        # Сбрасываем флаги
        for seq in self.recording.sequences:
            seq._is_new = False
            for call in seq.calls:
                call._is_new = False
