from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QMessageBox
from PySide6.QtCore import Qt
from BatAnnotation.Lookup import Species, DetectorModel, HabitatType, ContextType, SignalShape

class LookupsEditorWidget(QWidget):
    """Вкладка для редактирования справочников"""
    def __init__(self, db_session):
        super().__init__()
        self.db = db_session
        self.current_model = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Справочник:"))
        self.cb_tables = QComboBox()
        self.cb_tables.addItem("Виды (Species)", Species)
        self.cb_tables.addItem("Детекторы (Detectors)", DetectorModel)
        self.cb_tables.addItem("Местообитания (Habitats)", HabitatType)
        self.cb_tables.addItem("Контексты (Contexts)", ContextType)
        self.cb_tables.addItem("Формы (Shapes)", SignalShape)
        self.cb_tables.currentIndexChanged.connect(self.load_table)
        top_layout.addWidget(self.cb_tables)
        top_layout.addStretch()
        
        btn_save = QPushButton("💾 Сохранить изменения в БД")
        btn_save.clicked.connect(self.save_table)
        top_layout.addWidget(btn_save)
        
        layout.addLayout(top_layout)
        
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
