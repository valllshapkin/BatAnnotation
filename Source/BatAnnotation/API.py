from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class MemoryBatCall:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    shape_id: Optional[str] = None
    t_start_ms: float = 0.0
    t_end_ms: float = 0.0
    f_min_khz: float = 0.0
    f_max_khz: float = 0.0
    
    # Вычисляемое свойство! В базе его нет, а в оперативке пользоваться удобно
    @property
    def duration_ms(self) -> float:
        return self.t_end_ms - self.t_start_ms

@dataclass
class MemorySequence:
    sequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_id: Optional[str] = None
    species_prediction_id: Optional[str] = None
    notes: Optional[str] = None
    # Вложенная структура!
    calls: List[MemoryBatCall] = field(default_factory=list)

@dataclass
class MemoryRecording:
    recording_id: str
    filename: str
    sample_rate_hz: Optional[int] = None
    # Вложенная структура!
    sequences: List[MemorySequence] = field(default_factory=list)


class AnnotationManager:
    def __init__(self, db_session):
        self.session = db_session

    # === ЗАГРУЗКА ИЗ БД В ПАМЯТЬ ===
    def load_recording(self, recording_id: str) -> MemoryRecording:
        # 1. Достаем тяжелые объекты из базы (желательно через joinedload для скорости)
        db_rec = self.session.query(Recording).filter_by(recording_id=recording_id).first()
        
        # 2. Собираем легкую иерархию в памяти
        mem_rec = MemoryRecording(recording_id=db_rec.recording_id, filename=db_rec.filename)
        
        for db_seq in db_rec.sequences:
            mem_seq = MemorySequence(sequence_id=db_seq.sequence_id, notes=db_seq.notes)
            
            for db_call in db_seq.calls:
                mem_call = MemoryBatCall(
                    call_id=db_call.call_id,
                    t_start_ms=db_call.t_start_ms,
                    t_end_ms=db_call.t_end_ms,
                    f_min_khz=db_call.f_min_khz,
                    f_max_khz=db_call.f_max_khz
                )
                mem_seq.calls.append(mem_call)
                
            mem_rec.sequences.append(mem_seq)
            
        return mem_rec

    # === СОХРАНЕНИЕ ИЗ ПАМЯТИ В БД ===
    def save_recording(self, mem_rec: MemoryRecording):
        # 1. Находим запись в БД
        db_rec = self.session.query(Recording).filter_by(recording_id=mem_rec.recording_id).first()
        
        # Получаем все текущие ID коллов из БД, чтобы понять, что удалили
        existing_db_call_ids = {call.call_id for seq in db_rec.sequences for call in seq.calls}
        current_mem_call_ids = set()
        
        # 2. Обновляем или добавляем коллы
        for mem_seq in mem_rec.sequences:
            # (Тут логика синхронизации секвенций)
            
            for mem_call in mem_seq.calls:
                current_mem_call_ids.add(mem_call.call_id)
                
                # Ищем колл в базе
                db_call = self.session.query(BatCall).filter_by(call_id=mem_call.call_id).first()
                
                if db_call:
                    # ОБНОВЛЕНИЕ (UPDATE)
                    db_call.t_start_ms = mem_call.t_start_ms
                    db_call.t_end_ms = mem_call.t_end_ms
                    # ...
                else:
                    # ДОБАВЛЕНИЕ (INSERT) - UUID гарантирует, что коллизии не будет
                    new_call = BatCall(
                        call_id=mem_call.call_id,
                        sequence_id=mem_seq.sequence_id,
                        t_start_ms=mem_call.t_start_ms,
                        t_end_ms=mem_call.t_end_ms,
                        # ...
                    )
                    self.session.add(new_call)

        # 3. УДАЛЕНИЕ (DELETE) - то, что есть в БД, но пропало из оперативки
        calls_to_delete = existing_db_call_ids - current_mem_call_ids
        for call_id in calls_to_delete:
            self.session.query(BatCall).filter_by(call_id=call_id).delete()

        # 4. Фиксируем транзакцию
        self.session.commit()