from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QMessageBox, QTreeWidgetItemIterator
from PySide6.QtCore import Qt

from BatAnnotation.QtModels import QtSequence, QtBatCall
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
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        with b(main_layout, QHBoxLayout()) as toolbar:
            with b(toolbar, QPushButton("➕ Секвенция (Контекст)")) as btn_add_seq:
                btn_add_seq.clicked.connect(self.add_sequence)
                
            with b(toolbar, QPushButton("➕ Писк (Call)")) as btn_add_call:
                btn_add_call.clicked.connect(self.add_call)
                
            with b(toolbar, QPushButton("❌ Удалить")) as btn_del:
                btn_del.clicked.connect(self.delete_selected)
                
            toolbar.addStretch()
            
            with b(toolbar, QPushButton("💾 Сохранить в БД")) as btn_save:
                btn_save.clicked.connect(self.save_data)

        with b(main_layout, QSplitter(Qt.Orientation.Horizontal)) as splitter:
            with b(splitter, AnnotationTreeWidget(self.store)) as self.tree:
                self.tree.itemSelectionChanged.connect(self.on_tree_selection)
                
            with b(splitter, PropertyForms(self.store)) as self.forms:
                pass
                
            with b(splitter, SpectrogramWidget(self.store.recording)) as self.plot:
                self.plot.itemClicked.connect(self.on_plot_click)
                
            splitter.setSizes([250, 300, 700])

        # Первичное построение дерева, если данные уже загружены
        if self.store.recording.recording_id:
            self.tree.build_from(self.store.recording)

    def on_tree_selection(self):
        items = self.tree.selectedItems()
        if not items:
            self.forms.load_from("", None)
            self.plot.set_selection("", None)
            return
            
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        self.forms.load_from(typ, model)
        self.plot.set_selection(typ, model)

    def on_plot_click(self, typ, model):
        if not typ or not model:
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
        seq = QtSequence()
        seq.t_start_ms = vr.center().x() - 100
        seq.t_end_ms = vr.center().x() + 100
        seq.f_min_khz = 20
        seq.f_max_khz = 60
        # Добавление в список автоматически сгенерирует узел в TreeWidget
        self.store.recording.sequences.append(seq)

    def add_call(self):
        items = self.tree.selectedItems()
        if not items:
            return QMessageBox.warning(self, "Внимание", "Выберите Sequence, куда добавить Call.")
            
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        seq = model if typ == "seq" else getattr(model, "parent", None) 
        if typ != "seq":
            return QMessageBox.warning(self, "Внимание", "Сначала выделите Sequence в дереве.")
            
        vr = self.plot.getViewBox().viewRect()
        call = QtBatCall()
        call.t_start_ms = vr.center().x() - 10
        call.t_end_ms = vr.center().x() + 10
        call.f_min_khz = seq.f_min_khz + 5
        call.f_max_khz = seq.f_max_khz - 5
        
        call.peak_khz = call.f_min_khz + (call.f_max_khz - call.f_min_khz)/2
        call.peak_ms = call.t_start_ms + (call.t_end_ms - call.t_start_ms)/2
        call.signal_curves = {"main": [[call.t_start_ms, call.f_max_khz], [call.t_end_ms, call.f_min_khz]]}
        
        # Добавление в список автоматически сгенерирует узел в TreeWidget
        model.calls.append(call)

    def delete_selected(self):
        items = self.tree.selectedItems()
        if not items: return
        typ, model = items[0].data(0, Qt.ItemDataRole.UserRole)
        
        if typ == "seq":
            # Удаление из списка автоматически удалит узел из TreeWidget
            self.store.recording.sequences.remove(model)
        elif typ == "call":
            for seq in self.store.recording.sequences:
                if model in seq.calls:
                    seq.calls.remove(model)
                    break
        elif typ in ["fmaxe", "curve"]:
            if typ == "fmaxe":
                model.peak_khz = None
                model.peak_ms = None
            else:
                model.signal_curves = None
            model.changed.emit()

    def save_data(self):
        try:
            self.store.save_recording_to_db()
            QMessageBox.information(self, "Успех", "Данные сохранены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")
