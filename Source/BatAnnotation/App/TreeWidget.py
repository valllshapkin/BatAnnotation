from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from BatAnnotation.QtModels import QtRecording

class AnnotationTreeWidget(QTreeWidget):
    """Кастомное дерево с поддержкой виртуальных узлов (fmaxe, curve)"""
    def __init__(self, lookups):
        super().__init__()
        self.lookups = lookups
        self.setHeaderHidden(True)
        self.recording = None

    def build_from(self, recording: QtRecording):
        self.blockSignals(True)
        self.clear()
        self.recording = recording
        
        rec_item = QTreeWidgetItem(self)
        rec_item.setData(0, Qt.UserRole, ("rec", self.recording))
        self.update_item_text(rec_item, "rec", self.recording)
        
        for seq in self.recording.sequences:
            seq_item = QTreeWidgetItem(rec_item)
            seq_item.setData(0, Qt.UserRole, ("seq", seq))
            self.update_item_text(seq_item, "seq", seq)
            
            for call in seq.calls:
                call_item = QTreeWidgetItem(seq_item)
                call_item.setData(0, Qt.UserRole, ("call", call))
                self.update_item_text(call_item, "call", call)
                
                # Виртуальные узлы
                pt_item = QTreeWidgetItem(call_item)
                pt_item.setData(0, Qt.UserRole, ("fmaxe", call))
                self.update_item_text(pt_item, "fmaxe", call)
                
                crv_item = QTreeWidgetItem(call_item)
                crv_item.setData(0, Qt.UserRole, ("curve", call))
                self.update_item_text(crv_item, "curve", call)
                
        self.expandAll()
        self.blockSignals(False)

    def update_item_text(self, item: QTreeWidgetItem, typ: str, model):
        if typ == "rec":
            item.setText(0, f"🎵 {model.filename}")
        elif typ == "seq":
            sp = self.lookups.species.get(model.species_id)
            sp_name = sp.latin_name if sp else "Неизвестно"
            item.setText(0, f"🦇 Секвенция: {model.t_start_ms:.0f}-{model.t_end_ms:.0f} [{sp_name}]")
        elif typ == "call":
            item.setText(0, f"  🔊 Писк: {model.t_start_ms:.0f}-{model.t_end_ms:.0f}")
        elif typ == "fmaxe":
            val = f"{model.fmaxe_khz:.1f}kHz" if model.fmaxe_khz else "Нет"
            item.setText(0, f"    🎯 fmaxe: {val}")
        elif typ == "curve":
            pts = len(model.signal_curves.get("main", [])) if model.signal_curves else 0
            item.setText(0, f"    〰️ Кривая ({pts} узлов)")

    def refresh_selected_text(self):
        """Обновляет текст выбранного элемента и его виртуальных детей, если мы тянем ROI"""
        items = self.selectedItems()
        if not items: return
        item = items[0]
        typ, model = item.data(0, Qt.UserRole)
        self.update_item_text(item, typ, model)
        
        # Если это call, обновим текст и у его детей (fmaxe, curve)
        if typ == "call":
            for i in range(item.childCount()):
                child = item.child(i)
                c_typ, c_model = child.data(0, Qt.UserRole)
                self.update_item_text(child, c_typ, c_model)
