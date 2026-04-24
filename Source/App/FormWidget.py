from PySide6.QtWidgets import QWidget, QStackedWidget, QFormLayout, QDoubleSpinBox, QComboBox, QLineEdit, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from BatSpec.QtUp.Builder import build_node as b

class PropertyForms(QStackedWidget):
    """Набор форм для свойств (Recording, Sequence, Call)"""
    def __init__(self, lookups):
        super().__init__()
        self.lookups = lookups
        self.current_model = None
        self.current_typ = None
        
        self.setup_ui()
        self.populate_comboboxes()

    def setup_ui(self):
        # 0: Recording
        with b(self, QWidget()) as w_rec:
            with b(w_rec, QVBoxLayout()) as l_rec:
                with b(l_rec, QFormLayout()) as f_rec:
                    self.rec_filename = QLineEdit()
                    self.rec_detector = QComboBox()
                    self.rec_habitat = QComboBox()
                    f_rec.addRow("Файл:", self.rec_filename)
                    f_rec.addRow("Детектор:", self.rec_detector)
                    f_rec.addRow("Среда:", self.rec_habitat)
                l_rec.addStretch()
        
        # 1: Sequence
        with b(self, QWidget()) as w_seq:
            with b(w_seq, QVBoxLayout()) as l_seq:
                with b(l_seq, QFormLayout()) as f_seq:
                    self.seq_species = QComboBox()
                    self.seq_context = QComboBox()
                    self.seq_t_start = QDoubleSpinBox(); self.seq_t_start.setMaximum(999999)
                    self.seq_t_end = QDoubleSpinBox(); self.seq_t_end.setMaximum(999999)
                    self.seq_f_min = QDoubleSpinBox(); self.seq_f_min.setMaximum(200)
                    self.seq_f_max = QDoubleSpinBox(); self.seq_f_max.setMaximum(200)
                    self.seq_notes = QLineEdit()
                    
                    f_seq.addRow("Вид:", self.seq_species)
                    f_seq.addRow("Контекст:", self.seq_context)
                    f_seq.addRow("T Start:", self.seq_t_start)
                    f_seq.addRow("T End:", self.seq_t_end)
                    f_seq.addRow("F Min:", self.seq_f_min)
                    f_seq.addRow("F Max:", self.seq_f_max)
                    f_seq.addRow("Заметки:", self.seq_notes)
                l_seq.addStretch()
        
        # 2: Call
        with b(self, QWidget()) as w_call:
            with b(w_call, QVBoxLayout()) as l_call:
                with b(l_call, QFormLayout()) as f_call:
                    self.call_shape = QComboBox()
                    self.call_t_start = QDoubleSpinBox(); self.call_t_start.setMaximum(999999)
                    self.call_t_end = QDoubleSpinBox(); self.call_t_end.setMaximum(999999)
                    self.call_f_min = QDoubleSpinBox(); self.call_f_min.setMaximum(200)
                    self.call_f_max = QDoubleSpinBox(); self.call_f_max.setMaximum(200)
                    self.call_peak_khz = QDoubleSpinBox(); self.call_peak_khz.setMaximum(200)
                    self.call_peak_ms = QDoubleSpinBox(); self.call_peak_ms.setMaximum(999999)
                    self.call_notes = QLineEdit()
                    
                    f_call.addRow("Форма:", self.call_shape)
                    f_call.addRow("T Start:", self.call_t_start)
                    f_call.addRow("T End:", self.call_t_end)
                    f_call.addRow("F Min:", self.call_f_min)
                    f_call.addRow("F Max:", self.call_f_max)
                    f_call.addRow("FmaxE:", self.call_peak_khz)
                    f_call.addRow("T FmaxE:", self.call_peak_ms)
                    f_call.addRow("Заметки:", self.call_notes)
                l_call.addStretch()
        
        # 3: Empty (or virtual node)
        with b(self, QLabel("Ничего не выбрано", alignment=Qt.AlignmentFlag.AlignCenter)):
            pass
            
        self.setCurrentIndex(3)
        self.bind_signals()

    def populate_comboboxes(self):
        def fill(cb: QComboBox, items_dict: dict, label_attr: str):
            cb.blockSignals(True)
            cb.clear()
            cb.addItem("--- Не выбрано ---", None)
            for k, v in items_dict.items(): cb.addItem(getattr(v, label_attr) or getattr(v, "name", "N/A"), k)
            cb.blockSignals(False)

        fill(self.seq_species, self.lookups.species, "latin_name")
        fill(self.rec_detector, self.lookups.detectors, "name")
        fill(self.rec_habitat, self.lookups.habitats, "name")
        fill(self.seq_context, self.lookups.contexts, "name")
        fill(self.call_shape, self.lookups.shapes, "name")

    def refresh_lookups(self):
        """Пересобирает списки и восстанавливает текущие выбранные значения."""
        self.populate_comboboxes()
        # Вызов on_model_changed автоматически раскидает ID текущей модели по обновленным комбобоксам
        self.on_model_changed()

    def bind_signals(self):
        self.rec_filename.textChanged.connect(lambda v: self.update_model('filename', v))
        self.rec_detector.currentIndexChanged.connect(lambda: self.update_cb(self.rec_detector, 'detector_id'))
        self.rec_habitat.currentIndexChanged.connect(lambda: self.update_cb(self.rec_habitat, 'habitat_id'))
        
        self.seq_species.currentIndexChanged.connect(lambda: self.update_cb(self.seq_species, 'species_id'))
        self.seq_context.currentIndexChanged.connect(lambda: self.update_cb(self.seq_context, 'context_id'))
        self.seq_t_start.valueChanged.connect(lambda v: self.update_model('t_start_ms', v))
        self.seq_t_end.valueChanged.connect(lambda v: self.update_model('t_end_ms', v))
        self.seq_f_min.valueChanged.connect(lambda v: self.update_model('f_min_khz', v))
        self.seq_f_max.valueChanged.connect(lambda v: self.update_model('f_max_khz', v))
        
        self.call_shape.currentIndexChanged.connect(lambda: self.update_cb(self.call_shape, 'shape_id'))
        self.call_t_start.valueChanged.connect(lambda v: self.update_model('t_start_ms', v))
        self.call_t_end.valueChanged.connect(lambda v: self.update_model('t_end_ms', v))
        self.call_f_min.valueChanged.connect(lambda v: self.update_model('f_min_khz', v))
        self.call_f_max.valueChanged.connect(lambda v: self.update_model('f_max_khz', v))
        self.call_peak_khz.valueChanged.connect(lambda v: self.update_model('peak_khz', v))
        self.call_peak_ms.valueChanged.connect(lambda v: self.update_model('peak_ms', v))

    def update_model(self, field: str, value):
        if self.current_model: setattr(self.current_model, field, value)

    def update_cb(self, combo: QComboBox, field: str):
        if self.current_model: setattr(self.current_model, field, combo.currentData())

    def load_from(self, typ: str, model):
        if self.current_model and hasattr(self.current_model, 'changed'):
            try: self.current_model.changed.disconnect(self.on_model_changed)
            except Exception: pass

        self.current_model = model
        self.current_typ = typ

        if not model:
            self.setCurrentIndex(3)
            return
            
        self.current_model.changed.connect(self.on_model_changed)
        self.on_model_changed()

    def on_model_changed(self):
        model = self.current_model
        if not model: return
        
        if self.current_typ == "rec":
            self.setCurrentIndex(0)
            self.set_val(self.rec_filename, model.filename)
            self.set_cb(self.rec_detector, model.detector_id)
            self.set_cb(self.rec_habitat, model.habitat_id)
        elif self.current_typ == "seq":
            self.setCurrentIndex(1)
            self.set_cb(self.seq_species, model.species_id)
            self.set_cb(self.seq_context, model.context_id)
            self.set_val(self.seq_t_start, model.t_start_ms)
            self.set_val(self.seq_t_end, model.t_end_ms)
            self.set_val(self.seq_f_min, model.f_min_khz)
            self.set_val(self.seq_f_max, model.f_max_khz)
        elif self.current_typ in ["call", "fmaxe", "curve"]:
            self.setCurrentIndex(2)
            self.set_cb(self.call_shape, model.shape_id)
            self.set_val(self.call_t_start, model.t_start_ms)
            self.set_val(self.call_t_end, model.t_end_ms)
            self.set_val(self.call_f_min, model.f_min_khz)
            self.set_val(self.call_f_max, model.f_max_khz)
            self.set_val(self.call_peak_khz, model.peak_khz or 0.0)
            self.set_val(self.call_peak_ms, model.peak_ms or 0.0)

    def set_val(self, widget, value):
        widget.blockSignals(True)
        if isinstance(widget, QDoubleSpinBox): widget.setValue(float(value))
        elif isinstance(widget, QLineEdit): widget.setText(str(value))
        widget.blockSignals(False)
        
    def set_cb(self, combo: QComboBox, data_val):
        combo.blockSignals(True)
        idx = combo.findData(data_val)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)
