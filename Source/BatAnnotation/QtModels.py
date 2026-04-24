from typing import Optional, Any
import uuid
from PySide6.QtCore import QObject, Signal, Property

from BatAnnotation.API import MemoryBatCall, MemorySequence, MemoryRecording, MemoryLookups, MemorySpecies, MemoryLookupItem
from BatAnnotation.Reactive.Dict import ReactiveDict
from BatAnnotation.Reactive.List import ReactiveList

# ==============================================================================
# УТИЛИТА ДЛЯ ГЕНЕРАЦИИ СВОЙСТВ
# ==============================================================================

class QtModelBase(QObject):
    changed = Signal()

    def _update_val(self, attr: str, val: Any) -> None:
        if getattr(self, attr) != val:
            setattr(self, attr, val)
            self.changed.emit()

# ... (Оставляем классы QtBatCall, QtSequence, QtRecording без изменений, как в предыдущем ответе) ...

class QtBatCall(QtModelBase):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._call_id: str = str(uuid.uuid4())
        self._shape_id: Optional[str] = None
        self._t_start_ms: float = 0.0
        self._t_end_ms: float = 0.0
        self._f_min_khz: float = 0.0
        self._f_max_khz: float = 0.0
        self._peak_khz: Optional[float] = None
        self._peak_ms: Optional[float] = None
        self._signal_curves: Optional[dict] = None
        self._notes: Optional[str] = None
        self._is_new: bool = True 

    @Property(str, notify=QtModelBase.changed)
    def call_id(self) -> str: return self._call_id
    @call_id.setter
    def call_id(self, val: str): self._update_val("_call_id", val)

    @Property(str, notify=QtModelBase.changed)
    def shape_id(self) -> Optional[str]: return self._shape_id
    @shape_id.setter
    def shape_id(self, val: Optional[str]): self._update_val("_shape_id", val)

    @Property(float, notify=QtModelBase.changed)
    def t_start_ms(self) -> float: return self._t_start_ms
    @t_start_ms.setter
    def t_start_ms(self, val: float): self._update_val("_t_start_ms", val)

    @Property(float, notify=QtModelBase.changed)
    def t_end_ms(self) -> float: return self._t_end_ms
    @t_end_ms.setter
    def t_end_ms(self, val: float): self._update_val("_t_end_ms", val)

    @Property(float, notify=QtModelBase.changed)
    def f_min_khz(self) -> float: return self._f_min_khz
    @f_min_khz.setter
    def f_min_khz(self, val: float): self._update_val("_f_min_khz", val)

    @Property(float, notify=QtModelBase.changed)
    def f_max_khz(self) -> float: return self._f_max_khz
    @f_max_khz.setter
    def f_max_khz(self, val: float): self._update_val("_f_max_khz", val)

    @Property(float, notify=QtModelBase.changed)
    def peak_khz(self) -> Optional[float]: return self._peak_khz
    @peak_khz.setter
    def peak_khz(self, val: Optional[float]): self._update_val("_peak_khz", val)

    @Property(float, notify=QtModelBase.changed)
    def peak_ms(self) -> Optional[float]: return self._peak_ms
    @peak_ms.setter
    def peak_ms(self, val: Optional[float]): self._update_val("_peak_ms", val)

    @Property(dict, notify=QtModelBase.changed)
    def signal_curves(self) -> Optional[dict]: return self._signal_curves
    @signal_curves.setter
    def signal_curves(self, val: Optional[dict]): self._update_val("_signal_curves", val)

    @Property(str, notify=QtModelBase.changed)
    def notes(self) -> Optional[str]: return self._notes
    @notes.setter
    def notes(self, val: Optional[str]): self._update_val("_notes", val)

    @Property(float, notify=QtModelBase.changed)
    def duration_ms(self) -> float:
        return self._t_end_ms - self._t_start_ms

    def load_from(self, mem: MemoryBatCall) -> None:
        self._call_id = mem.call_id
        self._shape_id = mem.shape_id
        self._t_start_ms = mem.t_start_ms
        self._t_end_ms = mem.t_end_ms
        self._f_min_khz = mem.f_min_khz
        self._f_max_khz = mem.f_max_khz
        self._peak_khz = mem.peak_khz
        self._peak_ms = mem.peak_ms
        self._signal_curves = mem.signal_curves
        self._notes = mem.notes
        self._is_new = mem.is_new 
        self.changed.emit()

    def to_memory(self) -> MemoryBatCall:
        return MemoryBatCall(
            call_id=self._call_id,
            shape_id=self._shape_id,
            t_start_ms=self._t_start_ms,
            t_end_ms=self._t_end_ms,
            f_min_khz=self._f_min_khz,
            f_max_khz=self._f_max_khz,
            peak_khz=self._peak_khz,
            peak_ms=self._peak_ms,
            signal_curves=self._signal_curves,
            notes=self._notes,
            is_new=self._is_new 
        )


class QtSequence(QtModelBase):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._sequence_id: str = str(uuid.uuid4())
        self._context_id: Optional[str] = None
        self._species_id: Optional[str] = None
        self._t_start_ms: float = 0.0
        self._t_end_ms: float = 0.0
        self._f_min_khz: float = 0.0
        self._f_max_khz: float = 0.0
        self._notes: Optional[str] = None
        self._is_new: bool = True 
        
        self.calls = ReactiveList[QtBatCall]()
        self.calls.signals.changed.connect(self.changed)

    @Property(str, notify=QtModelBase.changed)
    def sequence_id(self) -> str: return self._sequence_id
    @sequence_id.setter
    def sequence_id(self, val: str): self._update_val("_sequence_id", val)

    @Property(str, notify=QtModelBase.changed)
    def context_id(self) -> Optional[str]: return self._context_id
    @context_id.setter
    def context_id(self, val: Optional[str]): self._update_val("_context_id", val)

    @Property(str, notify=QtModelBase.changed)
    def species_id(self) -> Optional[str]: return self._species_id
    @species_id.setter
    def species_id(self, val: Optional[str]): self._update_val("_species_id", val)

    @Property(float, notify=QtModelBase.changed)
    def t_start_ms(self) -> float: return self._t_start_ms
    @t_start_ms.setter
    def t_start_ms(self, val: float): self._update_val("_t_start_ms", val)

    @Property(float, notify=QtModelBase.changed)
    def t_end_ms(self) -> float: return self._t_end_ms
    @t_end_ms.setter
    def t_end_ms(self, val: float): self._update_val("_t_end_ms", val)

    @Property(float, notify=QtModelBase.changed)
    def f_min_khz(self) -> float: return self._f_min_khz
    @f_min_khz.setter
    def f_min_khz(self, val: float): self._update_val("_f_min_khz", val)

    @Property(float, notify=QtModelBase.changed)
    def f_max_khz(self) -> float: return self._f_max_khz
    @f_max_khz.setter
    def f_max_khz(self, val: float): self._update_val("_f_max_khz", val)

    @Property(str, notify=QtModelBase.changed)
    def notes(self) -> Optional[str]: return self._notes
    @notes.setter
    def notes(self, val: Optional[str]): self._update_val("_notes", val)

    def load_from(self, mem: MemorySequence) -> None:
        self._sequence_id = mem.sequence_id
        self._context_id = mem.context_id
        self._species_id = mem.species_id
        self._t_start_ms = mem.t_start_ms
        self._t_end_ms = mem.t_end_ms
        self._f_min_khz = mem.f_min_khz
        self._f_max_khz = mem.f_max_khz
        self._notes = mem.notes
        self._is_new = mem.is_new 

        self.calls.clear()
        qt_calls = []
        for c in mem.calls:
            qt_call = QtBatCall(self)
            qt_call.load_from(c)
            qt_calls.append(qt_call)
        self.calls.extend(qt_calls)
        
        self.changed.emit()

    def to_memory(self) -> MemorySequence:
        mem_seq = MemorySequence(
            sequence_id=self._sequence_id,
            context_id=self._context_id,
            species_id=self._species_id,
            t_start_ms=self._t_start_ms,
            t_end_ms=self._t_end_ms,
            f_min_khz=self._f_min_khz,
            f_max_khz=self._f_max_khz,
            notes=self._notes,
            is_new=self._is_new 
        )
        mem_seq.calls = [c.to_memory() for c in self.calls]
        return mem_seq


class QtRecording(QtModelBase):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._recording_id: str = str(uuid.uuid4())
        self._filename: str = ""
        self._detector_id: Optional[str] = None
        self._habitat_id: Optional[str] = None
        
        self.sequences = ReactiveList[QtSequence]()
        # Мы больше не пробрасываем changed от sequences наверх!
        # Каждому свое: кто слушает sequences - тот и молодец.

    @Property(str, notify=QtModelBase.changed)
    def recording_id(self) -> str: return self._recording_id
    @recording_id.setter
    def recording_id(self, val: str): self._update_val("_recording_id", val)

    @Property(str, notify=QtModelBase.changed)
    def filename(self) -> str: return self._filename
    @filename.setter
    def filename(self, val: str): self._update_val("_filename", val)

    @Property(str, notify=QtModelBase.changed)
    def detector_id(self) -> Optional[str]: return self._detector_id
    @detector_id.setter
    def detector_id(self, val: Optional[str]): self._update_val("_detector_id", val)

    @Property(str, notify=QtModelBase.changed)
    def habitat_id(self) -> Optional[str]: return self._habitat_id
    @habitat_id.setter
    def habitat_id(self, val: Optional[str]): self._update_val("_habitat_id", val)

    def load_from(self, mem: MemoryRecording) -> None:
        self._recording_id = mem.recording_id
        self._filename = mem.filename
        self._detector_id = mem.detector_id
        self._habitat_id = mem.habitat_id
        
        self.sequences.clear()
        qt_seqs = []
        for s in mem.sequences:
            qt_seq = QtSequence(self)
            qt_seq.load_from(s)
            qt_seqs.append(qt_seq)
        self.sequences.extend(qt_seqs)
        
        self.changed.emit()

    def to_memory(self) -> MemoryRecording:
        mem_rec = MemoryRecording(
            recording_id=self._recording_id,
            filename=self._filename,
            detector_id=self._detector_id,
            habitat_id=self._habitat_id
        )
        mem_rec.sequences = [s.to_memory() for s in self.sequences]
        return mem_rec


class QtLookups(QtModelBase):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.species = ReactiveDict[str, MemorySpecies]()
        self.detectors = ReactiveDict[str, MemoryLookupItem]()
        self.habitats = ReactiveDict[str, MemoryLookupItem]()
        self.contexts = ReactiveDict[str, MemoryLookupItem]()
        self.shapes = ReactiveDict[str, MemoryLookupItem]()

    def _sync_dict(self, reactive_dict: ReactiveDict, new_data: dict):
        """
        ИСПРАВЛЕНИЕ: Строгая синхронизация. 
        Удаляет ключи, которых больше нет, и обновляет/добавляет новые.
        """
        keys_to_delete = set(reactive_dict.keys()) - set(new_data.keys())
        for k in keys_to_delete:
            del reactive_dict[k]
        reactive_dict.update(new_data)

    def load_from(self, mem: MemoryLookups) -> None:
        self._sync_dict(self.species, mem.species)
        self._sync_dict(self.detectors, mem.detectors)
        self._sync_dict(self.habitats, mem.habitats)
        self._sync_dict(self.contexts, mem.contexts)
        self._sync_dict(self.shapes, mem.shapes)
