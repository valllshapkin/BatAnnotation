from collections.abc import Callable, Iterable
from typing import Any
from PySide6.QtCore import QObject, Signal, Property

class ReactiveList[T](list[T]):
    """
    Симметричная реализация реактивного списка.
    Поддерживает No-op проверки, безопасные выбросы исключений и атомарность.
    """

    class Signals(QObject):
        itemAdded = Signal(int, object)         # index, item
        itemRemoved = Signal(int, object)       # index, old_item
        itemSet = Signal(int, object, object)   # index, new_item, old_item
        cleared = Signal()
        updated = Signal()                      # Triggered on mass operations (slices, extend)
        changed = Signal()                      # Universal trigger

        def __init__(self, parent_list: 'ReactiveList[T]', parent: QObject | None = None):
            super().__init__(parent)
            self._list = parent_list

        @Property(list, notify=changed)
        def data(self) -> list[T]:
            return list(self._list)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.signals = self.Signals(self)
        super().__init__(*args, **kwargs)

    # ==================== Одиночные мутации ====================

    def append(self, item: T) -> None:
        super().append(item)
        idx = len(self) - 1
        self.signals.itemAdded.emit(idx, item)
        self.signals.changed.emit()

    def insert(self, index: int, item: T) -> None:
        super().insert(index, item)
        actual_idx = index if index < len(self) else len(self) - 1
        self.signals.itemAdded.emit(actual_idx, item)
        self.signals.changed.emit()

    def remove(self, item: T) -> None:
        # Вызовет ValueError штатно, сигналы не вылетят, если элемента нет.
        idx = self.index(item)
        super().remove(item)
        self.signals.itemRemoved.emit(idx, item)
        self.signals.changed.emit()

    def pop(self, index: int = -1) -> T:
        actual_index = index if index >= 0 else len(self) + index
        if actual_index < 0 or actual_index >= len(self):
             return super().pop(index) # native raise IndexError
        
        item = super().pop(index)
        self.signals.itemRemoved.emit(actual_index, item)
        self.signals.changed.emit()
        return item

    def __setitem__(self, key: int | slice, value: Any) -> None:
        if isinstance(key, slice):
            super().__setitem__(key, value)
            self.signals.updated.emit()
            self.signals.changed.emit()
        else:
            old_value = self[key] # native raise IndexError if invalid
            if old_value == value: # No-op optimization
                return
            super().__setitem__(key, value)
            self.signals.itemSet.emit(key, value, old_value)
            self.signals.changed.emit()

    def __delitem__(self, key: int | slice) -> None:
        if isinstance(key, slice):
            super().__delitem__(key)
            self.signals.updated.emit()
            self.signals.changed.emit()
        else:
            actual_index = key if key >= 0 else len(self) + key
            old_value = self[key] # native raise IndexError
            super().__delitem__(key)
            self.signals.itemRemoved.emit(actual_index, old_value)
            self.signals.changed.emit()

    # ==================== Массовые мутации ====================

    def extend(self, iterable: Iterable[T]) -> None:
        items = list(iterable)
        if not items:
            return
        super().extend(items)
        self.signals.updated.emit()
        self.signals.changed.emit()

    def clear(self) -> None:
        if not self: # No-op check
            return
        super().clear()
        self.signals.cleared.emit()
        self.signals.changed.emit()

    def __iadd__(self, other: Iterable[T]) -> 'ReactiveList[T]':
        self.extend(other)
        return self

    # ==================== Утилиты ====================

    def copy(self) -> 'ReactiveList[T]':
        return self.__class__(self)

    def connect_all(self, slot: Callable[..., Any]) -> None:
        self.signals.itemAdded.connect(slot)
        self.signals.itemRemoved.connect(slot)
        self.signals.itemSet.connect(slot)
        self.signals.cleared.connect(slot)
        self.signals.updated.connect(slot)
        self.signals.changed.connect(slot)

def make_reactive_list[T](l: list[T]) -> ReactiveList[T]:
    if type(l) is ReactiveList:
        return l
    return ReactiveList(l)
