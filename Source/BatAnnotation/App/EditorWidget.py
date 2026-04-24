from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QMessageBox, QTreeWidgetItemIterator
from PySide6.QtCore import Qt

from BatAnnotation.API import AnnotationManager
from BatAnnotation.QtModels import QtRecording, QtLookups, QtSequence, QtBatCall

from App.TreeWidget import AnnotationTreeWidget
from App.FormWidget import PropertyForms
from App.SpectrogramWidget import SpectrogramWidget

class EditorWidget(QWidget):
    """Главный виджет вкладки разметки. Оркестратор."""
    def __init__(self, db_session, recording_id: str):
        super().__init__()
        self.api = AnnotationManager(db_session)
        self.lookups = QtLookups()
        self.recording = QtRecording()
        self.recording_id = recording_id
        
        self.lookups.load_from(self.api.load_lookups())
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # --- TOOLBAR ---
        toolbar = QHBoxLayout()
        btn_add_seq = QPushButton("➕ Секвенция (Контекст)")
        btn_add_seq.clicked.connect(self.add_sequence)
        
        btn_add_call = QPushButton("➕ Писк (Call)")
        btn_add_call.clicked.connect(self.add_call)
        
        btn_del = QPushButton("❌ Удалить")
        btn_del.setStyleSheet("background-color: #552222; color: white;")
        btn_del.clicked.connect(self.delete_selected)
        
        btn_save = QPushButton("💾 Сохранить в БД")
        btn_save.clicked.connect(self.save_data)
        
        toolbar.addWidget(btn_add_seq)
        toolbar.addWidget(btn_add_call)
        toolbar.addWidget(btn_del)
        toolbar.addStretch()
        toolbar.addWidget(btn_save)
        layout.addLayout(toolbar)

        # --- PANELS ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.tree = AnnotationTreeWidget(self.lookups)
        splitter.addWidget(self.tree)
        
        self.forms = PropertyForms(self.lookups)
        splitter.addWidget(self.forms)
        
        self.plot = SpectrogramWidget(self.recording)
        splitter.addWidget(self.plot)
        
        splitter.setSizes([250, 300, 700])
        layout.addWidget(splitter)
        
        # --- SIGNALS ---
        self.tree.itemSelectionChanged.connect(self.on_tree_selection)
        self.plot.itemClicked.connect(self.on_plot_click)
        self.recording.changed.connect(self.tree.refresh_selected_text) # Синхронизация текста при драге ROI

    def load_data(self):
        mem_rec = self.api.load_recording(self.recording_id)
        if mem_rec:
            self.recording.load_from(mem_rec)
            self.tree.build_from(self.recording)

    def on_tree_selection(self):
        items = self.tree.selectedItems()
        if not items:
            self.forms.load_from("", None)
            self.plot.set_selection("", None)
            return
            
        typ, model = items[0].data(0, Qt.UserRole)
        self.forms.load_from(typ, model)
        self.plot.set_selection(typ, model)

    def on_plot_click(self, typ, model):
        if not typ or not model:
            self.tree.clearSelection()
            return
            
        # Ищем в дереве и выделяем
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            i_typ, i_model = item.data(0, Qt.UserRole)
            if i_model == model and i_typ == typ:
                self.tree.setCurrentItem(item)
                return
            iterator += 1

    # --- ACTIONS ---
    def add_sequence(self):
        vr = self.plot.getViewBox().viewRect()
        seq = QtSequence()
        seq.t_start_ms = vr.center().x() - 100
        seq.t_end_ms = vr.center().x() + 100
        seq.f_min_khz = 20
        seq.f_max_khz = 60
        self.recording.sequences.append(seq)
        self.tree.build_from(self.recording) # Перестраиваем дерево

    def add_call(self):
        items = self.tree.selectedItems()
        if not items:
            return QMessageBox.warning(self, "Внимание", "Выберите Sequence, куда добавить Call.")
            
        typ, model = items[0].data(0, Qt.UserRole)
        seq = model if typ == "seq" else getattr(model, "parent", None) # Логика поиска родителя (упрощенно)
        if typ != "seq":
            return QMessageBox.warning(self, "Внимание", "Сначала выделите Sequence в дереве.")
            
        vr = self.plot.getViewBox().viewRect()
        call = QtBatCall()
        call.t_start_ms = vr.center().x() - 10
        call.t_end_ms = vr.center().x() + 10
        call.f_min_khz = seq.f_min_khz + 5
        call.f_max_khz = seq.f_max_khz - 5
        
        # Дефолтная точка и кривая
        call.fmaxe_khz = call.f_min_khz + (call.f_max_khz - call.f_min_khz)/2
        call.t_fmaxe_ms = call.t_start_ms + (call.t_end_ms - call.t_start_ms)/2
        call.signal_curves = {"main": [[call.t_start_ms, call.f_max_khz], [call.t_end_ms, call.f_min_khz]]}
        
        model.calls.append(call)
        self.tree.build_from(self.recording)

    def delete_selected(self):
        items = self.tree.selectedItems()
        if not items: return
        typ, model = items[0].data(0, Qt.UserRole)
        
        if typ == "seq":
            self.recording.sequences.remove(model)
        elif typ == "call":
            # Ищем родительскую Sequence (так как у QtBatCall нет ссылки на parent)
            for seq in self.recording.sequences:
                if model in seq.calls:
                    seq.calls.remove(model)
                    break
        elif typ in ["fmaxe", "curve"]:
            # Удаляем только данные, сам Call остается
            if typ == "fmaxe":
                model.fmaxe_khz = None
                model.t_fmaxe_ms = None
            else:
                model.signal_curves = None
            model.changed.emit()
            
        self.tree.build_from(self.recording)

    def save_data(self):
        try:
            self.api.save_recording(self.recording.to_memory())
            QMessageBox.information(self, "Успех", "Данные сохранены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")
