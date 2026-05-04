from collections.abc import Callable, Hashable
from typing import Any
from PySide6.QtCore import QObject, Signal, Property

class ReactiveDict[K: Hashable, V](dict[K, V]):
    """
    Индустриальная реализация реактивного словаря.
    - Оптимизировано от холостых обновлений (No-op check).
    - Атомарные массовые операции (update, |=).
    - Exception-safe (если базовая операция падает, сигналы не летят).
    """

    class Signals(QObject):
        itemSet = Signal(object, object, object)      # key, new_value, old_value
        itemRemoved = Signal(object, object)          # key, old_value
        cleared = Signal()
        updated = Signal(list)                        # list of changed keys
        changed = Signal()                            # Universal trigger

        def __init__(self, parent_dict: 'ReactiveDict[K, V]', parent: QObject | None = None):
            super().__init__(parent)
            self._dict = parent_dict

        @Property("QVariantMap", notify=changed)
        def data(self) -> dict[K, V]:
            return dict(self._dict)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.signals = self.Signals(self)
        super().__init__(*args, **kwargs)

    # ==================== Одиночные мутации ====================

    def __setitem__(self, key: K, value: V) -> None:
        is_existing = key in self
        old_value = self.get(key)
        
        # No-op optimization
        if is_existing and old_value == value:
            return

        super().__setitem__(key, value)
        self.signals.itemSet.emit(key, value, old_value)
        self.signals.changed.emit()

    def __delitem__(self, key: K) -> None:
        old_value = super().pop(key) 
        self.signals.itemRemoved.emit(key, old_value)
        self.signals.changed.emit()

    def pop(self, key: K, *args: Any) -> Any:
        try:
            value = super().pop(key)
            self.signals.itemRemoved.emit(key, value)
            self.signals.changed.emit()
            return value
        except KeyError:
            if args:
                return args[0]
            raise 

    def popitem(self) -> tuple[K, V]:
        key, value = super().popitem()
        self.signals.itemRemoved.emit(key, value)
        self.signals.changed.emit()
        return key, value

    def setdefault(self, key: K, default: V | None = None) -> V:
        if key not in self:
            self[key] = default  # type: ignore
        return self[key]

    # ==================== Массовые мутации ====================

    def clear(self) -> None:
        if not self:  
            return
            
        super().clear()
        self.signals.cleared.emit()
        self.signals.changed.emit()

    def update(self, *args: Any, **kwargs: Any) -> None:
        new_data = dict(*args, **kwargs)
        if not new_data:
            return

        changed_keys: list[K] = []
        
        for k, v in new_data.items():
            is_existing = k in self
            old_value = self.get(k)
            
            if not is_existing or old_value != v:
                super().__setitem__(k, v)
                changed_keys.append(k)
                self.signals.itemSet.emit(k, v, old_value)

        if changed_keys:
            self.signals.updated.emit(changed_keys)
            self.signals.changed.emit()

    def __ior__(self, other: Any) -> 'ReactiveDict[K, V]':
        self.update(other)
        return self

    # ==================== Утилиты ====================

    def copy(self) -> 'ReactiveDict[K, V]':
        return self.__class__(self)

    def connect_all(self, slot: Callable[..., Any]) -> None:
        self.signals.itemSet.connect(slot)
        self.signals.itemRemoved.connect(slot)
        self.signals.cleared.connect(slot)
        self.signals.updated.connect(slot)
        self.signals.changed.connect(slot)

def make_reactive_dict[K, V](d: dict[K, V]) -> ReactiveDict[K, V]:
    if type(d) is ReactiveDict:
        return d
    return ReactiveDict(d)
