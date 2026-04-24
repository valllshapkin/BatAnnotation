from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from BatAnnotation.QtModels import QtRecording

class AnnotationTreeWidget(QTreeWidget):
    """Кастомное дерево с глобальной синхронизацией узлов"""
    def __init__(self, lookups):
        super().__init__()
        self.lookups = lookups
        self.setHeaderHidden(True)
        self.recording = None
        self._model_items = [] # Кеш для связи (QTreeWidgetItem, typ, Model)

    def build_from(self, recording: QtRecording):
        self.blockSignals(True)
        
        # 1. Отписываемся от старых моделей, чтобы не было утечек памяти
        for _, _, model in self._model_items:
            try:
                model.changed.disconnect(self.refresh_all_texts)
            except Exception:
                pass
                
        self.clear()
        self.recording = recording
        self._model_items.clear()
        
        # 2. Вспомогательная функция для регистрации узла и подписки на его изменения
        def add_node(parent_item, typ, model):
            item = QTreeWidgetItem(parent_item)
            item.setData(0, Qt.ItemDataRole.UserRole, (typ, model))
            self.update_item_text(item, typ, model)
            self._model_items.append((item, typ, model))
            # МАГИЯ РЕАКТИВНОСТИ: подписываемся на персональный сигнал КАЖДОЙ модели
            model.changed.connect(self.refresh_all_texts)
            return item

        # 3. Строим дерево
        rec_item = add_node(self, "rec", self.recording)
        
        for seq in self.recording.sequences:
            seq_item = add_node(rec_item, "seq", seq)
            
            for call in seq.calls:
                call_item = add_node(seq_item, "call", call)
                
                # Виртуальные узлы
                add_node(call_item, "fmaxe", call)
                add_node(call_item, "curve", call)
                
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
            item.setText(0, f"🔊 Писк: {model.t_start_ms:.0f}-{model.t_end_ms:.0f}")
        elif typ == "fmaxe":
            val = f"{model.peak_khz:.1f}kHz" if model.peak_khz else "Нет"
            item.setText(0, f"🎯 fmaxe: {val}")
        elif typ == "curve":
            pts = len(model.signal_curves.get("main", [])) if model.signal_curves else 0
            item.setText(0, f"〰️ Кривая ({pts} узлов)")

    def refresh_all_texts(self):
        """
        Пробегается по всем элементам и обновляет их названия.
        Вызывается при любом чихе в ЛЮБОЙ модели (даже если изменили ROI).
        """
        self.blockSignals(True)
        for item, typ, model in self._model_items:
            try:
                self.update_item_text(item, typ, model)
            except RuntimeError:
                # На случай, если C++ объект QTreeWidgetItem был удален Qt
                pass
        self.blockSignals(False)
