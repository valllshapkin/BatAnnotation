import sys
import uuid
from pathlib import Path
ScriptDir = Path(__file__).parent

# ==============================================================================
# 1. ИНИЦИАЛИЗАЦИЯ БД И СИДОВ
# ==============================================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(f"sqlite:///{ScriptDir.joinpath('test.db').as_posix()}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestBase(DeclarativeBase): pass

from BatAnnotation import config as BatAnnotationConfig
BatAnnotationConfig.BASE = TestBase

from BatAnnotation.manage import create_all
create_all(engine)

from BatAnnotation.CommonSeeds.Core import seed_all as seed_core
from BatAnnotation.CommonSeeds.EuropeGeneral import seed_all as seed_eu
from BatAnnotation.Lookup import Species, DetectorModel, HabitatType, ContextType, SignalShape
from BatAnnotation.Tables import Recording, CallSequence, BatCall
from BatAnnotation.API import AnnotationManager
from BatAnnotation.QtModels import QtRecording, QtSequence, QtBatCall, QtLookups

def setup_synthetic_data(db):
    seed_core(db)
    seed_eu(db)
    
    rec = db.query(Recording).first()
    if rec:
        return rec.recording_id
        
    print("Создаю синтетические данные...")
    new_rec = Recording(recording_id=str(uuid.uuid4()), filename="test_forest_01.wav", sample_rate_hz=384000, duration_s=10.0)
    
    # Немного расширим тестовые данные для наглядности
    seq1 = CallSequence(sequence_id=str(uuid.uuid4()), t_start_ms=1000, t_end_ms=1800, f_min_khz=35, f_max_khz=85, notes="Четкий пролет")
    seq1.calls.append(BatCall(t_start_ms=1010, t_end_ms=1030, f_min_khz=40, f_max_khz=80, fmaxe_khz=50.0, t_fmaxe_ms=1020, notes="Пик 1"))
    seq1.calls.append(BatCall(t_start_ms=1200, t_end_ms=1220, f_min_khz=38, f_max_khz=78, fmaxe_khz=48.0, t_fmaxe_ms=1210, notes="Пик 2"))
    seq1.calls.append(BatCall(t_start_ms=1400, t_end_ms=1420, f_min_khz=36, f_max_khz=75, fmaxe_khz=45.0, t_fmaxe_ms=1410, notes="Пик 3"))
    
    seq2 = CallSequence(sequence_id=str(uuid.uuid4()), t_start_ms=5000, t_end_ms=5800, f_min_khz=20, f_max_khz=50)
    seq2.calls.append(BatCall(t_start_ms=5050, t_end_ms=5070, f_min_khz=25, f_max_khz=45, fmaxe_khz=35.0, t_fmaxe_ms=5060))
    seq2.calls.append(BatCall(t_start_ms=5300, t_end_ms=5320, f_min_khz=22, f_max_khz=42, fmaxe_khz=32.0, t_fmaxe_ms=5310))
    
    new_rec.sequences.extend([seq1, seq2])
    db.add(new_rec)
    db.commit()
    
    return new_rec.recording_id

# ==============================================================================
# 2. Qt ИНТЕРФЕЙС
# ==============================================================================
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItemIterator, QWidget, QVBoxLayout, QHBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QFormLayout, 
    QDoubleSpinBox, QComboBox, QPushButton, QSplitter, QLabel, 
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt

# Импортируем наш новый виджет Спектрограммы
from SpectrogramWidget import SpectrogramWidget

class LookupsEditorWidget(QWidget):
    """Вкладка для прямого редактирования справочников в БД"""
    def __init__(self, db_session):
        super().__init__()
        self.db = db_session
        self.current_model = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Выбор справочника
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Справочник:"))
        self.cb_tables = QComboBox()
        self.cb_tables.addItem("Виды (Species)", Species)
        self.cb_tables.addItem("Детекторы (Detectors)", DetectorModel)
        self.cb_tables.addItem("Местообитания (Habitats)", HabitatType)
        self.cb_tables.addItem("Контексты (Contexts)", ContextType)
        self.cb_tables.addItem("Формы сигналов (Shapes)", SignalShape)
        self.cb_tables.currentIndexChanged.connect(self.load_table)
        top_layout.addWidget(self.cb_tables)
        top_layout.addStretch()
        
        btn_save = QPushButton("💾 Сохранить изменения в БД")
        btn_save.clicked.connect(self.save_table)
        top_layout.addWidget(btn_save)
        
        layout.addLayout(top_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_table()

    def load_table(self):
        self.current_model = self.cb_tables.currentData()
        records = self.db.query(self.current_model).all()
        
        columns = [c.name for c in self.current_model.__table__.columns]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(records))
        
        for row_idx, record in enumerate(records):
            for col_idx, col_name in enumerate(columns):
                val = getattr(record, col_name)
                item = QTableWidgetItem(str(val) if val is not None else "")
                if "id" in col_name.lower():
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col_idx == 0:
                    item.setData(Qt.UserRole, record)
                self.table.setItem(row_idx, col_idx, item)

    def save_table(self):
        columns = [c.name for c in self.current_model.__table__.columns]
        for row_idx in range(self.table.rowCount()):
            record = self.table.item(row_idx, 0).data(Qt.UserRole)
            for col_idx, col_name in enumerate(columns):
                if "id" in col_name.lower(): continue
                new_val = self.table.item(row_idx, col_idx).text()
                col_type = self.current_model.__table__.columns[col_name].type.python_type
                try:
                    if new_val == "": setattr(record, col_name, None)
                    elif col_type is bool: setattr(record, col_name, new_val.lower() == "true")
                    else: setattr(record, col_name, col_type(new_val))
                except ValueError: pass
        self.db.commit()
        QMessageBox.information(self, "Успех", "Справочники обновлены!")


class RecordingEditorWidget(QWidget):
    """Мощный срез данных (Дерево + Динамические формы + Спектрограмма)"""
    def __init__(self, db_session, recording_id: str):
        super().__init__()
        self.api = AnnotationManager(db_session)
        
        self.lookups = QtLookups()
        self.recording = QtRecording()
        self.recording_id = recording_id
        
        self.current_tree_item = None 
        self._block_tree_signal = False
        
        self.setup_ui()
        self.load_data()
        
        # Подписываем спектрограмму на клики, чтобы выделять элементы в дереве
        self.plot.itemClicked.connect(self.select_item_from_plot)
        
        # Подписываем модель записи на глобальное обновление (чтобы текст в дереве менялся)
        self.recording.changed.connect(self.refresh_current_tree_text)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- ЛЕВАЯ ПАНЕЛЬ: Дерево Иерархии ---
        left_panel = QWidget()
        l_layout = QVBoxLayout(left_panel)
        l_layout.setContentsMargins(0,0,0,0)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection)
        l_layout.addWidget(self.tree)
        main_splitter.addWidget(left_panel)
        
        # --- ЦЕНТРАЛЬНАЯ ПАНЕЛЬ: Формы свойств ---
        self.stack = QStackedWidget()
        self.setup_forms()
        main_splitter.addWidget(self.stack)
        
        # --- ПРАВАЯ ПАНЕЛЬ: Спектрограмма (PyQtGraph) ---
        self.plot = SpectrogramWidget(self.recording)
        main_splitter.addWidget(self.plot)
        
        # Настройка пропорций
        main_splitter.setSizes([250, 300, 700])
        layout.addWidget(main_splitter)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Сохранить срез в БД")
        btn_save.clicked.connect(self.save_data)
        
        btn_refresh = QPushButton("🔄 Перерисовать график")
        btn_refresh.clicked.connect(self.plot.fast_layer.update)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_refresh)
        layout.addLayout(btn_layout)

    def setup_forms(self):
        # --- ФОРМА 1: Recording ---
        w_rec = QWidget(); f_rec = QFormLayout(w_rec)
        self.rec_filename = QLineEdit()
        self.rec_detector = QComboBox()
        self.rec_habitat = QComboBox()
        f_rec.addRow("Файл:", self.rec_filename)
        f_rec.addRow("Детектор:", self.rec_detector)
        f_rec.addRow("Среда:", self.rec_habitat)
        self.stack.addWidget(w_rec)
        
        # --- ФОРМА 2: Sequence ---
        w_seq = QWidget(); f_seq = QFormLayout(w_seq)
        self.seq_species = QComboBox()
        self.seq_context = QComboBox()
        self.seq_t_start = QDoubleSpinBox(); self.seq_t_start.setMaximum(999999)
        self.seq_t_end = QDoubleSpinBox(); self.seq_t_end.setMaximum(999999)
        self.seq_f_min = QDoubleSpinBox(); self.seq_f_min.setMaximum(200)
        self.seq_f_max = QDoubleSpinBox(); self.seq_f_max.setMaximum(200)
        self.seq_notes = QLineEdit()
        
        f_seq.addRow("Вид (Species):", self.seq_species)
        f_seq.addRow("Поведение:", self.seq_context)
        f_seq.addRow("T Start (ms):", self.seq_t_start)
        f_seq.addRow("T End (ms):", self.seq_t_end)
        f_seq.addRow("F Min (kHz):", self.seq_f_min)
        f_seq.addRow("F Max (kHz):", self.seq_f_max)
        f_seq.addRow("Заметки:", self.seq_notes)
        self.stack.addWidget(w_seq)
        
        # --- ФОРМА 3: BatCall ---
        w_call = QWidget(); f_call = QFormLayout(w_call)
        self.call_shape = QComboBox()
        self.call_t_start = QDoubleSpinBox(); self.call_t_start.setMaximum(999999)
        self.call_t_end = QDoubleSpinBox(); self.call_t_end.setMaximum(999999)
        self.call_f_min = QDoubleSpinBox(); self.call_f_min.setMaximum(200)
        self.call_f_max = QDoubleSpinBox(); self.call_f_max.setMaximum(200)
        self.call_fmaxe_khz = QDoubleSpinBox(); self.call_fmaxe_khz.setMaximum(200)
        self.call_t_fmaxe_ms = QDoubleSpinBox(); self.call_t_fmaxe_ms.setMaximum(999999)
        self.call_notes = QLineEdit()
        
        f_call.addRow("Форма (Shape):", self.call_shape)
        f_call.addRow("T Start (ms):", self.call_t_start)
        f_call.addRow("T End (ms):", self.call_t_end)
        f_call.addRow("F Min (kHz):", self.call_f_min)
        f_call.addRow("F Max (kHz):", self.call_f_max)
        f_call.addRow("FmaxE (kHz):", self.call_fmaxe_khz)
        f_call.addRow("T FmaxE (ms):", self.call_t_fmaxe_ms)
        f_call.addRow("Заметки:", self.call_notes)
        self.stack.addWidget(w_call)
        
        self.stack.addWidget(QLabel("Выберите элемент для редактирования", alignment=Qt.AlignmentFlag.AlignCenter))
        self.stack.setCurrentIndex(3)
        self.bind_form_signals()

    def bind_form_signals(self):
        # Recording
        self.rec_filename.textChanged.connect(lambda v: self.update_model_field('filename', v))
        self.rec_detector.currentIndexChanged.connect(lambda: self.update_model_combobox(self.rec_detector, 'detector_id'))
        self.rec_habitat.currentIndexChanged.connect(lambda: self.update_model_combobox(self.rec_habitat, 'habitat_id'))
        # Sequence
        self.seq_species.currentIndexChanged.connect(lambda: self.update_model_combobox(self.seq_species, 'species_id'))
        self.seq_context.currentIndexChanged.connect(lambda: self.update_model_combobox(self.seq_context, 'context_id'))
        self.seq_t_start.valueChanged.connect(lambda v: self.update_model_field('t_start_ms', v))
        self.seq_t_end.valueChanged.connect(lambda v: self.update_model_field('t_end_ms', v))
        self.seq_f_min.valueChanged.connect(lambda v: self.update_model_field('f_min_khz', v))
        self.seq_f_max.valueChanged.connect(lambda v: self.update_model_field('f_max_khz', v))
        self.seq_notes.textChanged.connect(lambda v: self.update_model_field('notes', v))
        # Call
        self.call_shape.currentIndexChanged.connect(lambda: self.update_model_combobox(self.call_shape, 'shape_id'))
        self.call_t_start.valueChanged.connect(lambda v: self.update_model_field('t_start_ms', v))
        self.call_t_end.valueChanged.connect(lambda v: self.update_model_field('t_end_ms', v))
        self.call_f_min.valueChanged.connect(lambda v: self.update_model_field('f_min_khz', v))
        self.call_f_max.valueChanged.connect(lambda v: self.update_model_field('f_max_khz', v))
        self.call_fmaxe_khz.valueChanged.connect(lambda v: self.update_model_field('fmaxe_khz', v))
        self.call_t_fmaxe_ms.valueChanged.connect(lambda v: self.update_model_field('t_fmaxe_ms', v))
        self.call_notes.textChanged.connect(lambda v: self.update_model_field('notes', v))

    def update_model_field(self, field: str, value):
        if not self.current_tree_item: return
        typ, model = self.current_tree_item.data(0, Qt.UserRole)
        setattr(model, field, value)

    def update_model_combobox(self, combo: QComboBox, field: str):
        if not self.current_tree_item: return
        typ, model = self.current_tree_item.data(0, Qt.UserRole)
        setattr(model, field, combo.currentData())

    def load_data(self):
        self.lookups.load_from(self.api.load_lookups())
        self.populate_comboboxes()
        
        mem_rec = self.api.load_recording(self.recording_id)
        if mem_rec:
            self.recording.load_from(mem_rec)
            self.build_tree()
            # Устанавливаем фокус на запись при первоначальной загрузке
            self.plot.set_selection("rec", self.recording)

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

    def build_tree(self):
        self.tree.clear()
        
        rec_item = QTreeWidgetItem(self.tree)
        rec_item.setData(0, Qt.UserRole, ("rec", self.recording))
        self.set_tree_item_text(rec_item, "rec", self.recording)
        
        for seq in self.recording.sequences:
            seq_item = QTreeWidgetItem(rec_item)
            seq_item.setData(0, Qt.UserRole, ("seq", seq))
            self.set_tree_item_text(seq_item, "seq", seq)
            
            for call in seq.calls:
                call_item = QTreeWidgetItem(seq_item)
                call_item.setData(0, Qt.UserRole, ("call", call))
                self.set_tree_item_text(call_item, "call", call)
                
        self.tree.expandAll()

    def set_tree_item_text(self, item: QTreeWidgetItem, typ: str, model):
        if typ == "rec":
            item.setText(0, f"🎵 Файл: {model.filename}")
        elif typ == "seq":
            sp = self.lookups.species.get(model.species_id)
            sp_name = sp.latin_name if sp else "Неизвестно"
            item.setText(0, f"🦇 Seq: {model.t_start_ms:.0f}-{model.t_end_ms:.0f}ms [{sp_name}]")
        elif typ == "call":
            item.setText(0, f"   🔊 Call: {model.t_start_ms:.0f}-{model.t_end_ms:.0f}ms")

    def refresh_current_tree_text(self):
        """Вызывается когда QtModel сообщает об изменениях (перемещение ROI или ввод в форму)"""
        if self.current_tree_item:
            typ, model = self.current_tree_item.data(0, Qt.UserRole)
            self.set_tree_item_text(self.current_tree_item, typ, model)
            self.fill_form_from_model(typ, model) # Обновляем цифры в форме, если мы тянули ROI

    def on_tree_selection(self):
        if self._block_tree_signal: return
        
        selected = self.tree.selectedItems()
        if not selected:
            self.stack.setCurrentIndex(3)
            self.current_tree_item = None
            self.plot.set_selection("", None)
            return
            
        self.current_tree_item = selected[0]
        typ, model = self.current_tree_item.data(0, Qt.UserRole)
        
        self.fill_form_from_model(typ, model)
        self.plot.set_selection(typ, model)

    def select_item_from_plot(self, typ, model):
        """Вызывается при клике на спектрограмму"""
        if not typ or not model:
            self.tree.clearSelection()
            return
            
        # Ищем элемент в дереве
        self._block_tree_signal = True
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            i_typ, i_model = item.data(0, Qt.UserRole)
            if i_model == model:
                self.tree.setCurrentItem(item)
                self.current_tree_item = item
                self.fill_form_from_model(typ, model)
                self.plot.set_selection(typ, model)
                break
            iterator += 1
        self._block_tree_signal = False

    def fill_form_from_model(self, typ, model):
        # Загружаем данные из модели в UI (с блокировкой сигналов, чтобы не зациклить)
        if typ == "rec":
            self.stack.setCurrentIndex(0)
            self.set_val(self.rec_filename, model.filename)
            self.set_cb(self.rec_detector, model.detector_id)
            self.set_cb(self.rec_habitat, model.habitat_id)
            
        elif typ == "seq":
            self.stack.setCurrentIndex(1)
            self.set_cb(self.seq_species, model.species_id)
            self.set_cb(self.seq_context, model.context_id)
            self.set_val(self.seq_t_start, model.t_start_ms)
            self.set_val(self.seq_t_end, model.t_end_ms)
            self.set_val(self.seq_f_min, model.f_min_khz)
            self.set_val(self.seq_f_max, model.f_max_khz)
            self.set_val(self.seq_notes, model.notes or "")
            
        elif typ == "call":
            self.stack.setCurrentIndex(2)
            self.set_cb(self.call_shape, model.shape_id)
            self.set_val(self.call_t_start, model.t_start_ms)
            self.set_val(self.call_t_end, model.t_end_ms)
            self.set_val(self.call_f_min, model.f_min_khz)
            self.set_val(self.call_f_max, model.f_max_khz)
            self.set_val(self.call_fmaxe_khz, model.fmaxe_khz or 0.0)
            self.set_val(self.call_t_fmaxe_ms, model.t_fmaxe_ms or 0.0)
            self.set_val(self.call_notes, model.notes or "")

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

    def save_data(self):
        try:
            mem_rec = self.recording.to_memory()
            self.api.save_recording(mem_rec)
            QMessageBox.information(self, "Успех", "Синхронизировано с БД!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")


class MainWindow(QMainWindow):
    def __init__(self, recording_id: str):
        super().__init__()
        self.setWindowTitle("Bat Annotation Advanced Studio v2.0 (With Fast Spectrogram)")
        self.resize(1400, 800)
        
        self.db = SessionLocal()
        
        tabs = QTabWidget()
        
        self.editor_tab = RecordingEditorWidget(self.db, recording_id)
        tabs.addTab(self.editor_tab, "🦇 Интерактивная Разметка")
        
        self.lookups_tab = LookupsEditorWidget(self.db)
        tabs.addTab(self.lookups_tab, "📚 Справочники (БД)")
        
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    with SessionLocal() as db:
        test_rec_id = setup_synthetic_data(db)
        
    window = MainWindow(test_rec_id)
    window.show()
    
    sys.exit(app.exec())
