from typing import Type
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, 
    QTableView, QLabel, QMessageBox, QHeaderView, QAbstractItemView
)
# Сигнал нам больше не нужен!
from sqlalchemy.orm import DeclarativeBase

from BatSpec.QtUp.Builder import build_node as b
from BatSpec.QtUp.ModelSQLA import SqlAlchemyTableModel, SqlAlchemyDelegate
from BatAnnotation.Lookup import Species, DetectorModel, HabitatType, ContextType, SignalShape
from App.Store import AppStore # Импортируем тип для аннотации


class LookupsEditorWidget(QWidget):
    """Вкладка для редактирования справочников."""

    def __init__(self, store: AppStore):
        super().__init__()
        self.store = store          # Сохраняем ссылку на Store
        self.db = self.store.db     # Берем сессию БД для таблицы
        self.table_model = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        with b(main_layout, QHBoxLayout()) as top_layout:
            with b(top_layout, QLabel("Справочник:")):
                pass 
            
            with b(top_layout, QComboBox()) as self.cb_tables:
                self.cb_tables.addItem("Виды (Species)", Species)
                self.cb_tables.addItem("Детекторы (Detectors)", DetectorModel)
                self.cb_tables.addItem("Местообитания (Habitats)", HabitatType)
                self.cb_tables.addItem("Контексты (Contexts)", ContextType)
                self.cb_tables.addItem("Формы (Shapes)", SignalShape)
                self.cb_tables.currentIndexChanged.connect(self.load_table)
            
            with b(top_layout, QPushButton("➕ Добавить")) as btn_add:
                btn_add.clicked.connect(self.add_row)
                
            with b(top_layout, QPushButton("❌ Удалить")) as btn_del:
                btn_del.clicked.connect(self.delete_row)
                
            top_layout.addStretch()
            
            with b(top_layout, QPushButton("💾 Сохранить изменения в БД")) as btn_save:
                btn_save.clicked.connect(self.save_table)

        with b(main_layout, QTableView()) as self.table:
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        if self.cb_tables.count() > 0:
            self.load_table()

    def load_table(self):
        current_sqla_model: Type[DeclarativeBase] = self.cb_tables.currentData()
        if not current_sqla_model:
            return

        self.table_model = SqlAlchemyTableModel(self.db, current_sqla_model)
        self.table.setModel(self.table_model)
        
        delegate = SqlAlchemyDelegate(current_sqla_model, self.table)
        self.table.setItemDelegate(delegate)

    def add_row(self):
        if not self.table_model: return
        row = self.table_model.rowCount()
        if self.table_model.insertRows(row, 1):
            self.table.selectRow(row)

    def delete_row(self):
        if not self.table_model: return
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите строку для удаления.")
            return
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.table_model.removeRows(index.row(), 1)

    def save_table(self) -> bool:
        try:
            self.db.commit() # 1. Физически сохраняем в БД
            
            # 2. НАПРЯМУЮ ПРИКАЗЫВАЕМ СТОРУ ОБНОВИТЬСЯ!
            self.store.sync_lookups_from_db() 
            
            QMessageBox.information(self, "Успех", "Справочники обновлены!")
            self.table_model.refresh()
            return True
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось сохранить.\n\nПодробности:\n{e}")
            return False
