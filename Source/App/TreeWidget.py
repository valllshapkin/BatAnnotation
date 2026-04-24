from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
from PySide6.QtCore import Qt
from BatAnnotation.QtModels import QtRecording, QtSequence, QtBatCall

# ==============================================================================
# РЕАКТИВНЫЕ УЗЛЫ ДЕРЕВА
# Каждый узел сам следит за своей моделью и отписывается при удалении
# ==============================================================================

class ReactiveTreeItem(QTreeWidgetItem):
    def __init__(self, parent, typ: str, model, lookups):
        super().__init__(parent)
        self.typ = typ
        self.model = model
        self.lookups = lookups
        
        # Сохраняем типизацию для хиттестов и UI
        self.setData(0, Qt.ItemDataRole.UserRole, (self.typ, self.model))
        
        # Подписываемся НА КОНКРЕТНУЮ модель
        self.model.changed.connect(self.update_text)
        
        # Если это секвенция, подписываемся ЕЩЕ И на изменение справочника видов!
        if self.typ == "seq":
            self.lookups.species.signals.changed.connect(self.update_text)
            
        self.update_text()

    def update_text(self):
        if self.typ == "rec":
            self.setText(0, f"🎵 {self.model.filename}")
            
        elif self.typ == "seq":
            sp = self.lookups.species.get(self.model.species_id)
            sp_name = sp.latin_name if sp else "Неизвестно"
            self.setText(0, f"🦇 Секвенция: {self.model.t_start_ms:.0f}-{self.model.t_end_ms:.0f} [{sp_name}]")
            
        elif self.typ == "call":
            self.setText(0, f"🔊 Писк: {self.model.t_start_ms:.0f}-{self.model.t_end_ms:.0f}")
            
        elif self.typ == "fmaxe":
            val = f"{self.model.peak_khz:.1f}kHz" if self.model.peak_khz else "Нет"
            self.setText(0, f"🎯 fmaxe: {val}")
            
        elif self.typ == "curve":
            pts = len(self.model.signal_curves.get("main", [])) if self.model.signal_curves else 0
            self.setText(0, f"〰️ Кривая ({pts} узлов)")

    def cleanup(self):
        """Отписываемся от сигналов перед удалением"""
        try: self.model.changed.disconnect(self.update_text)
        except Exception: pass
        
        if self.typ == "seq":
            try: self.lookups.species.signals.changed.disconnect(self.update_text)
            except Exception: pass


class AnnotationTreeWidget(QTreeWidget):
    """Кастомное дерево. Управляет подписками на коллекции (добавление/удаление)."""
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.lookups = store.lookups
        self.setHeaderHidden(True)
        
        # Подписываемся на глобальную смену записи (загрузка файла)
        self.store.recording.changed.connect(self._rebuild_if_new_recording)
        self._current_recording_id = None

    def _rebuild_if_new_recording(self):
        """Перестраиваем дерево только если загрузили новый файл, а не просто потянули ROI"""
        rec = self.store.recording
        if rec.recording_id != self._current_recording_id:
            self.build_from(rec)

    def build_from(self, recording: QtRecording):
        self._cleanup_all_items()
        self.clear()
        
        self._current_recording_id = recording.recording_id
        
        # 1. Корневой узел (Запись)
        rec_item = ReactiveTreeItem(self, "rec", recording, self.lookups)
        
        # 2. Подписываемся на коллекцию Sequences
        recording.sequences.signals.itemAdded.connect(lambda idx, seq: self._add_sequence_node(rec_item, seq))
        recording.sequences.signals.itemRemoved.connect(lambda idx, seq: self._remove_node_by_model(seq))
        
        # 3. Строим начальные Sequences
        for seq in recording.sequences:
            self._add_sequence_node(rec_item, seq)
            
        self.expandAll()

    def _add_sequence_node(self, parent_item, seq: QtSequence):
        seq_item = ReactiveTreeItem(parent_item, "seq", seq, self.lookups)
        
        # Подписываемся на коллекцию Calls этой конкретной секвенции
        seq.calls.signals.itemAdded.connect(lambda idx, call: self._add_call_node(seq_item, call))
        seq.calls.signals.itemRemoved.connect(lambda idx, call: self._remove_node_by_model(call))
        
        # Строим начальные Calls
        for call in seq.calls:
            self._add_call_node(seq_item, call)

    def _add_call_node(self, parent_item, call: QtBatCall):
        call_item = ReactiveTreeItem(parent_item, "call", call, self.lookups)
        # Виртуальные узлы
        ReactiveTreeItem(call_item, "fmaxe", call, self.lookups)
        ReactiveTreeItem(call_item, "curve", call, self.lookups)
        parent_item.setExpanded(True)

    def _remove_node_by_model(self, model):
        """Ищет узел по модели, делает ему cleanup и удаляет из дерева"""
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            typ, item_model = item.data(0, Qt.ItemDataRole.UserRole)
            if item_model == model and typ in ["seq", "call"]:
                # Очищаем детей (в случае call это fmaxe и curve)
                for i in range(item.childCount()):
                    child = item.child(i)
                    if isinstance(child, ReactiveTreeItem):
                        child.cleanup()
                        
                if isinstance(item, ReactiveTreeItem):
                    item.cleanup()
                item.parent().removeChild(item)
                return
            iterator += 1

    def _cleanup_all_items(self):
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if isinstance(item, ReactiveTreeItem):
                item.cleanup()
            iterator += 1
