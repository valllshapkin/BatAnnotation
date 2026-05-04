from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

# Импортируем модели БД
from BatAnnotation.Lookup import Species, DetectorModel, HabitatType, ContextType, SignalShape
from BatAnnotation.Tables import Recording, CallSequence, BatCall

# ==============================================================================
# СТРУКТУРЫ ДАННЫХ ДЛЯ ОПЕРАТИВНОЙ ПАМЯТИ
# ==============================================================================

@dataclass
class MemorySpecies:
    species_id: str
    latin_name: str
    family: Optional[str] = None
    genus: Optional[str] = None

@dataclass
class MemoryLookupItem:
    id: str
    code: Optional[str] = None
    name: Optional[str] = None

@dataclass
class MemoryLookups:
    species: Dict[str, MemorySpecies] =field(default_factory=dict) # type: ignore[reportUnknownVariableType]
    detectors: Dict[str, MemoryLookupItem] = field(default_factory=dict) # type: ignore[reportUnknownVariableType]
    habitats: Dict[str, MemoryLookupItem] = field(default_factory=dict) # type: ignore[reportUnknownVariableType]
    contexts: Dict[str, MemoryLookupItem] = field(default_factory=dict) # type: ignore[reportUnknownVariableType]
    shapes: Dict[str, MemoryLookupItem] = field(default_factory=dict) # type: ignore[reportUnknownVariableType]

@dataclass
class MemoryBatCall:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    shape_id: Optional[str] = None
    t_start_ms: float = 0.0
    t_end_ms: float = 0.0
    f_min_khz: float = 0.0
    f_max_khz: float = 0.0
    peak_khz: Optional[float] = None
    peak_ms: Optional[float] = None
    signal_curves: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    
    is_new: bool = field(default=True, repr=False)
    
    @property
    def duration_ms(self) -> float:
        return self.t_end_ms - self.t_start_ms

@dataclass
class MemorySequence:
    sequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_id: Optional[str] = None
    species_id: Optional[str] = None
    t_start_ms: float = 0.0
    t_end_ms: float = 0.0
    f_min_khz: float = 0.0
    f_max_khz: float = 0.0
    notes: Optional[str] = None
    calls: List[MemoryBatCall] = field(default_factory=list) # type: ignore[reportUnknownVariableType]
    
    is_new: bool = field(default=True, repr=False)

@dataclass
class MemoryRecording:
    recording_id: str
    filename: str
    sample_rate_hz: Optional[int] = None
    duration_s: Optional[float] = None
    detector_id: Optional[str] = None
    habitat_id: Optional[str] = None
    sequences: List[MemorySequence] = field(default_factory=list) # type: ignore[reportUnknownVariableType]


# ==============================================================================
# МЕНЕДЖЕР АННОТАЦИЙ (API для работы с БД)
# ==============================================================================

class AnnotationManager:
    def __init__(self, db_session: Session):
        self.session: Session = db_session

    def load_lookups(self) -> MemoryLookups:
        lookups = MemoryLookups()
        for sp in self.session.query(Species).filter_by(is_active=True).all():
            lookups.species[sp.species_id] = MemorySpecies(
                species_id=sp.species_id, latin_name=sp.latin_name, family=sp.family, genus=sp.genus
            )
        for d in self.session.query(DetectorModel).filter_by(is_active=True).all():
            name = f"{d.manufacturer} {d.model}"
            lookups.detectors[d.detector_id] = MemoryLookupItem(id=d.detector_id, name=name)
        for h in self.session.query(HabitatType).filter_by(is_active=True).all():
            lookups.habitats[h.habitat_id] = MemoryLookupItem(id=h.habitat_id, code=h.code, name=h.name)
        for c in self.session.query(ContextType).filter_by(is_active=True).all():
            lookups.contexts[c.context_id] = MemoryLookupItem(id=c.context_id, code=c.code, name=c.name)
        for s in self.session.query(SignalShape).filter_by(is_active=True).all():
            lookups.shapes[s.shape_id] = MemoryLookupItem(id=s.shape_id, code=s.code, name=s.name)
        return lookups

    def load_recording(self, recording_id: str) -> Optional[MemoryRecording]:
        db_rec = self.session.query(Recording)\
            .options(joinedload(Recording.sequences).joinedload(CallSequence.calls))\
            .filter_by(recording_id=recording_id).first()
            
        if not db_rec:
            return None
        
        mem_rec = MemoryRecording(
            recording_id=db_rec.recording_id, 
            filename=db_rec.filename,
            sample_rate_hz=db_rec.sample_rate_hz,
            duration_s=db_rec.duration_s,
            detector_id=db_rec.detector_id,
            habitat_id=db_rec.habitat_id
        )
        
        for db_seq in db_rec.sequences:
            mem_seq = MemorySequence(
                sequence_id=db_seq.sequence_id,
                context_id=db_seq.context_id,
                species_id=db_seq.species_id,
                t_start_ms=db_seq.t_start_ms,
                t_end_ms=db_seq.t_end_ms,
                f_min_khz=db_seq.f_min_khz,
                f_max_khz=db_seq.f_max_khz,
                notes=db_seq.notes,
                is_new=False  
            )
            
            for db_call in db_seq.calls:
                mem_call = MemoryBatCall(
                    call_id=db_call.call_id,
                    shape_id=db_call.shape_id,
                    t_start_ms=db_call.t_start_ms,
                    t_end_ms=db_call.t_end_ms,
                    f_min_khz=db_call.f_min_khz,
                    f_max_khz=db_call.f_max_khz,
                    peak_khz=db_call.peak_khz,
                    peak_ms=db_call.peak_ms,
                    signal_curves=db_call.signal_curves,
                    notes=db_call.notes,
                    is_new=False 
                )
                mem_seq.calls.append(mem_call)
                
            mem_rec.sequences.append(mem_seq)
            
        return mem_rec

    def save_recording(self, mem_rec: MemoryRecording) -> None:
        try:
            db_rec = self.session.query(Recording).filter_by(recording_id=mem_rec.recording_id).first()
            if not db_rec:
                raise ValueError(f"Recording с ID {mem_rec.recording_id} не найден в БД.")
            
            db_rec.habitat_id = mem_rec.habitat_id
            db_rec.detector_id = mem_rec.detector_id
            db_rec.sample_rate_hz = mem_rec.sample_rate_hz
            db_rec.duration_s = mem_rec.duration_s
            
            existing_db_seq_ids = {seq.sequence_id for seq in db_rec.sequences}
            existing_db_call_ids = {call.call_id for seq in db_rec.sequences for call in seq.calls}
            
            current_mem_seq_ids = set()
            current_mem_call_ids = set()
            
            for mem_seq in mem_rec.sequences:
                current_mem_seq_ids.add(mem_seq.sequence_id)
                
                if mem_seq.is_new:
                    new_seq = CallSequence(
                        sequence_id=mem_seq.sequence_id,
                        recording_id=mem_rec.recording_id,
                        context_id=mem_seq.context_id,
                        species_id=mem_seq.species_id,
                        t_start_ms=mem_seq.t_start_ms,
                        t_end_ms=mem_seq.t_end_ms,
                        f_min_khz=mem_seq.f_min_khz,
                        f_max_khz=mem_seq.f_max_khz,
                        notes=mem_seq.notes
                    )
                    self.session.add(new_seq)
                else:
                    db_seq = self.session.query(CallSequence).filter_by(sequence_id=mem_seq.sequence_id).first()
                    if db_seq:
                        db_seq.context_id = mem_seq.context_id
                        db_seq.species_id = mem_seq.species_id
                        db_seq.t_start_ms = mem_seq.t_start_ms
                        db_seq.t_end_ms = mem_seq.t_end_ms
                        db_seq.f_min_khz = mem_seq.f_min_khz
                        db_seq.f_max_khz = mem_seq.f_max_khz
                        db_seq.notes = mem_seq.notes
                
                for mem_call in mem_seq.calls:
                    current_mem_call_ids.add(mem_call.call_id)
                    
                    if mem_call.is_new:
                        new_call = BatCall(
                            call_id=mem_call.call_id,
                            sequence_id=mem_seq.sequence_id,
                            shape_id=mem_call.shape_id,
                            t_start_ms=mem_call.t_start_ms,
                            t_end_ms=mem_call.t_end_ms,
                            f_min_khz=mem_call.f_min_khz,
                            f_max_khz=mem_call.f_max_khz,
                            peak_khz=mem_call.peak_khz,
                            peak_ms=mem_call.peak_ms,
                            signal_curves=mem_call.signal_curves,
                            notes=mem_call.notes
                        )
                        self.session.add(new_call)
                    else:
                        db_call = self.session.query(BatCall).filter_by(call_id=mem_call.call_id).first()
                        if db_call:
                            db_call.shape_id = mem_call.shape_id
                            db_call.t_start_ms = mem_call.t_start_ms
                            db_call.t_end_ms = mem_call.t_end_ms
                            db_call.f_min_khz = mem_call.f_min_khz
                            db_call.f_max_khz = mem_call.f_max_khz
                            db_call.peak_khz = mem_call.peak_khz
                            db_call.peak_ms = mem_call.peak_ms
                            db_call.signal_curves = mem_call.signal_curves
                            db_call.notes = mem_call.notes

            calls_to_delete = existing_db_call_ids - current_mem_call_ids
            if calls_to_delete:
                self.session.query(BatCall).filter(BatCall.call_id.in_(calls_to_delete)).delete(synchronize_session=False)
                
            seqs_to_delete = existing_db_seq_ids - current_mem_seq_ids
            if seqs_to_delete:
                self.session.query(CallSequence).filter(CallSequence.sequence_id.in_(seqs_to_delete)).delete(synchronize_session=False)

            self.session.commit()
            
            for mem_seq in mem_rec.sequences:
                mem_seq.is_new = False
                for mem_call in mem_seq.calls:
                    mem_call.is_new = False

        except Exception as e:
            self.session.rollback()
            raise e
