from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QMessageBox, QTreeWidgetItemIterator, QComboBox
from PySide6.QtCore import Qt

from BatAnnotation.QtModels import QtSequence, QtBatCall
from BatAnnotation.Tables import Recording
from BatSpec.QtUp.Builder import build_node as b

from App.TreeWidget import AnnotationTreeWidget
from App.FormWidget import PropertyForms
from App.SpectrogramWidget import SpectrogramWidget
from App.Store import AppStore

class EditorWidget(QWidget):
    """Главный виджет вкладки разметки. Оркестратор UI."""
    def __init__(self, store: AppStore):
        super().__init__()
        self.store = store
        self._prev_cb_index = -1
        self.setup_ui()
        self.load_recording_list()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        with b(main_layout, QHBoxLayout()) as toolbar_top:
            with b(toolbar_top, QComboBox()) as self.cb_recording:
                self.cb_recording.currentIndexChanged.connect(self.on_recording_changed)
            toolbar_top.addStretch()

        with b(main_layout, QHBoxLayout()) as toolbar:
            with b(toolbar, QPushButton("➕ Секвенция (Контекст)")) as btn_add_seq:
                btn_add_seq.clicked.connect(self.add_sequence)
                
            with b(toolbar, QPushButton("➕ Писк (Call)")) as btn_add_call:
                btn_add_call.clicked.connect(self.add_call)
                
            with b(toolbar, QPushButton("❌ Удалить")) as btn_del:
                btn_del.clicked.connect(self.delete_selected)
                
            toolbar.addStretch()
            
            with b(toolbar, QPushButton("💾 Сохранить в БД")) as btn_save:
                btn_save.clicked.connect(lambda: self.save_data(show_info=True))

        with b(main_layout, QSplitter(Qt.Orientation.Horizontal)) as splitter:
            with b(splitter, AnnotationTreeWidget(self.store)) as self.tree:
                self.tree.itemSelectionChanged.connect(self.on_tree_selection)

            with b(splitter, SpectrogramWidget(self.store.recording)) as self.plot:
                self.plot.itemClicked.connect(self.on_plot_click)
                self.plot.dataModified.connect(self.mark_dirty)
                
            with b(splitter, PropertyForms(self.store)) as self.forms:
                self.forms.dataModified.connect(self.mark_dirty)
                
            splitter.setSizes([250, 700, 250])

        if self.store.recording.recording_id:
            self.tree.build_from(self.store.recording)
            self.plot.set_selection("rec", self.store.recording)

    def mark_dirty(self):
        """Вызывается при любом изменении в Форме или на Графике"""
        self.store.is_dirty = True

    def load_recording_list(self):
        self.cb_recording.blockSignals(True)
        self.cb_recording.clear()
        
        recs = self.store.db.query(Recording.recording_id, Recording.filename).all()
        for rec_id, fname in recs:
            self.cb_recording.addItem(fname, rec_id)
            
        idx = self.cb_recording.findData(self.store.recording.recording_id)
        if idx >= 0:
            self.cb_recording.setCurrentIndex(idx)
            self._prev_cb_index = idx
            
        self.cb_recording.blockSignals(False)

    def on_recording_changed(self, index: int):
        if self.store.is_dirty:
            reply = QMessageBox.question(
                self, "Несохраненные изменения",
                "У вас есть несохраненные изменения.\nСохранить их перед переключением?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                self.cb_recording.blockSignals(True)
                self.cb_recording.setCurrentIndex(self._prev_cb_index)
                self.cb_recording.blockSignals(False)
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_data(show_info=False):
                    self.cb_recording.blockSignals(True)
                    self.cb_recording.setCurrentIndex(self._prev_cb_index)
                    self.cb_recording.blockSignals(False)
                    return

        rec_id = self.cb_recording.itemData(index)
        if rec_id:
            self.store.load_recording(rec_id)
            self._prev_cb_index = index
            self.tree.clearSelection()
            self.plot.set_selection("rec", self.store.recording)

    def on_tree_selection(self):
        items = self.tree.selectedItems()
        if not items:
            self.forms.load_from("", None)
            self.plot.set_selection("rec", self.store.recording)
            return
            
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        self.forms.load_from(typ, model)
        self.plot.set_selection(typ, model)

    def on_plot_click(self, typ, model):
        if not typ or not model:
            self.tree.clearSelection()
            return
            
        if typ == "rec":
            self.tree.clearSelection()
            return

        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            i_typ, i_model = item.data(0, Qt.ItemDataRole.UserRole)
            if i_model == model and i_typ == typ:
                self.tree.setCurrentItem(item)
                return
            iterator += 1

    def add_sequence(self):
        vr = self.plot.getViewBox().viewRect()
        # ОБЯЗАТЕЛЬНО передаем родителя
        seq = QtSequence(self.store.recording) 
        seq.t_start_ms = vr.center().x() - 100
        seq.t_end_ms = vr.center().x() + 100
        seq.f_min_khz = 20
        seq.f_max_khz = 60
        self.store.recording.sequences.append(seq)
        self.mark_dirty()

    def add_call(self):
        items = self.tree.selectedItems()
        if not items:
            return QMessageBox.warning(self, "Внимание", "Выберите Sequence, куда добавить Call.")
            
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # Исправлено надежное получение родительской секвенции
        seq = model if typ == "seq" else model.parent()
        
        if not seq or not isinstance(seq, QtSequence):
            return QMessageBox.warning(self, "Внимание", "Сначала выделите Sequence в дереве.")
            
        vr = self.plot.getViewBox().viewRect()
        # ОБЯЗАТЕЛЬНО передаем родителя
        call = QtBatCall(seq) 
        call.t_start_ms = vr.center().x() - 10
        call.t_end_ms = vr.center().x() + 10
        call.f_min_khz = seq.f_min_khz + 5
        call.f_max_khz = seq.f_max_khz - 5
        
        call.peak_khz = call.f_min_khz + (call.f_max_khz - call.f_min_khz)/2
        call.peak_ms = call.t_start_ms + (call.t_end_ms - call.t_start_ms)/2
        call.signal_curves = {"main": [[call.t_start_ms, call.f_max_khz], [call.t_end_ms, call.f_min_khz]]}
        
        seq.calls.append(call)
        self.mark_dirty()

    def delete_selected(self):
        items = self.tree.selectedItems()
        if not items: return
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        
        if typ == "seq":
            self.store.recording.sequences.remove(model)
        elif typ == "call":
            seq = model.parent()
            if seq and model in seq.calls:
                seq.calls.remove(model)
            else:
                # Надежный Fallback (на всякий случай)
                for s in self.store.recording.sequences:
                    if model in s.calls:
                        s.calls.remove(model)
                        break
        elif typ in ["fmaxe", "curve"]:
            if typ == "fmaxe":
                model.peak_khz = 0.0
                model.peak_ms = 0.0
            else:
                model.signal_curves = None
            model.changed.emit()
            
        self.mark_dirty()

    def save_data(self, show_info=True) -> bool:
        try:
            self.store.save_recording_to_db()
            if show_info:
                QMessageBox.information(self, "Успех", "Данные сохранены!")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")
            return False
