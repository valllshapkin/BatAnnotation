import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from BatAnnotation.QtModels import QtModelBase, QtRecording, QtSequence, QtBatCall

# ==============================================================================
# КАСТОМНЫЕ ИНТЕРАКТИВНЫЕ ROI
# ==============================================================================

class PointROI(pg.ROI):
    """ROI для точки (например fmaxe). Не меняет размер, только перемещается."""
    def __init__(self, pos, pen, brush):
        super().__init__(pos, [0, 0], movable=True, resizable=False, rotatable=False)
        self.pen = pen
        self.brush = brush

    def paint(self, p, opt, widget):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        # Рисуем кружок радиусом 5 пикселей (независимо от зума графика)
        px, py = self.pixelSize()
        rx, ry = 5 * px, 5 * py
        p.drawEllipse(QtCore.QRectF(-rx, -ry, rx * 2, ry * 2))

    def boundingRect(self):
        px, py = self.pixelSize()
        rx, ry = 6 * px, 6 * py
        return QtCore.QRectF(-rx, -ry, rx * 2, ry * 2)

# ==============================================================================
# БЫСТРЫЙ СЛОЙ ОТРИСОВКИ (ДЛЯ НЕАКТИВНЫХ ЭЛЕМЕНТОВ)
# ==============================================================================

class FastAnnotationLayer(pg.GraphicsObject):
    """
    Рисует все секвенции и писки ОДНИМ вызовом.
    Это решает проблему SegFault и обеспечивает 60 FPS при тысячах объектов.
    """
    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.active_model = None  # Модель, которую мы СЕЙЧАС редактируем (ее скрываем)
        
        # Кисти и перья (Кэшируем для скорости)
        self.pen_seq = pg.mkPen((50, 150, 255), width=1)
        self.brush_seq = pg.mkBrush(50, 150, 255, 30)
        
        self.pen_call = pg.mkPen((50, 255, 50), width=1)
        self.brush_call = pg.mkBrush(50, 255, 50, 50)
        
        self.pen_pt = pg.mkPen((255, 255, 0), width=1)
        self.brush_pt = pg.mkBrush(255, 255, 0, 200)

        # Подписываемся на изменения модели, чтобы перерисовывать слой
        self.recording.changed.connect(self.update)

    def set_active_model(self, model):
        self.active_model = model
        self.update()

    def paint(self, p, *args):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        
        # Размеры пикселя для отрисовки точек одинакового размера при любом зуме
        px = self.pixelWidth() * 4 if self.pixelWidth() else 1
        py = self.pixelHeight() * 4 if self.pixelHeight() else 1

        for seq in self.recording.sequences:
            # 1. Рисуем Sequence
            if seq != self.active_model:
                p.setPen(self.pen_seq)
                p.setBrush(self.brush_seq)
                w = seq.t_end_ms - seq.t_start_ms
                h = seq.f_max_khz - seq.f_min_khz
                p.drawRect(QtCore.QRectF(seq.t_start_ms, seq.f_min_khz, w, h))
                
            # 2. Рисуем Calls внутри Sequence
            for call in seq.calls:
                if call != self.active_model:
                    p.setPen(self.pen_call)
                    p.setBrush(self.brush_call)
                    cw = call.t_end_ms - call.t_start_ms
                    ch = call.f_max_khz - call.f_min_khz
                    p.drawRect(QtCore.QRectF(call.t_start_ms, call.f_min_khz, cw, ch))
                    
                    # 3. Рисуем точку FmaxE, если есть
                    if call.fmaxe_khz is not None and call.t_fmaxe_ms is not None:
                        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                        p.setPen(self.pen_pt)
                        p.setBrush(self.brush_pt)
                        cx, cy = call.t_fmaxe_ms, call.fmaxe_khz
                        p.drawEllipse(QtCore.QRectF(cx - px, cy - py, px * 2, py * 2))
                        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)

    def boundingRect(self):
        # Чтобы слой не отсекался, задаем глобальные рамки.
        # В реальном приложении здесь лучше брать границы аудиофайла
        return QtCore.QRectF(0, 0, 999999, 200)

# ==============================================================================
# КОНТРОЛЛЕР ГРАФИКА
# ==============================================================================

class SpectrogramWidget(pg.PlotWidget):
    """
    Основной виджет. Управляет фоном, FastLayer'ом и интерактивными ROI.
    """
    # Сигнал испускается, когда пользователь кликает на график (для выделения в дереве)
    itemClicked = QtCore.Signal(str, object) # typ ("seq", "call"), model

    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.view = self.getViewBox()
        self.view.setLimits(yMin=0, yMax=200, xMin=0) # Ограничения по осям
        self.setLabel('bottom', 'Time', units='ms')
        self.setLabel('left', 'Frequency', units='kHz')
        
        # 1. Демо-фон (Синтетическая "Спектрограмма")
        self.setup_dummy_background()
        
        # 2. Слой быстрой отрисовки
        self.fast_layer = FastAnnotationLayer(self.recording)
        self.view.addItem(self.fast_layer)
        
        # 3. Состояние
        self.active_roi = None
        self.active_fmaxe_roi = None
        self.active_model = None
        self.active_type = None
        self._updating_from_code = False # Защита от рекурсии сигналов
        
        # 4. События
        self.scene().sigMouseClicked.connect(self.on_mouse_click)

    def setup_dummy_background(self):
        """Создает шумовой фон, чтобы было похоже на спектрограмму"""
        img = pg.ImageItem()
        # Шум 1000x200
        noise = np.random.normal(size=(10000, 200), loc=50, scale=20).astype(np.uint8)
        img.setImage(noise)
        img.setRect(QtCore.QRectF(0, 0, 10000, 200)) # 10 секунд, 200 кГц
        # Градиент как в Sonobat/BatExplorer
        colormap = pg.colormap.get('magma')
        img.setColorMap(colormap)
        self.view.addItem(img)

    # --- ИНТЕГРАЦИЯ: Установка активного элемента извне (например, из Дерева) ---
    def set_selection(self, typ: str, model: QtModelBase):
        self._updating_from_code = True
        
        # Удаляем старые ROI
        if self.active_roi:
            self.view.removeItem(self.active_roi)
            self.active_roi = None
        if self.active_fmaxe_roi:
            self.view.removeItem(self.active_fmaxe_roi)
            self.active_fmaxe_roi = None
            
        self.active_model = model
        self.active_type = typ
        self.fast_layer.set_active_model(model)
        
        if not model:
            self._updating_from_code = False
            return

        # Создаем новые интерактивные ROI
        pen = pg.mkPen((50, 150, 255) if typ == "seq" else (50, 255, 50), width=2)
        hover_pen = pg.mkPen('w', width=3)
        
        pos = (model.t_start_ms, model.f_min_khz)
        size = (max(1, model.t_end_ms - model.t_start_ms), max(1, model.f_max_khz - model.f_min_khz))
        
        self.active_roi = pg.RectROI(pos, size, pen=pen, hoverPen=hover_pen)
        self.active_roi.addScaleHandle([1, 1], [0, 0])
        self.active_roi.addScaleHandle([0, 0], [1, 1])
        self.active_roi.addTranslateHandle([0.5, 0.5])
        self.active_roi.sigRegionChanged.connect(self.on_roi_changed)
        self.active_roi.setZValue(100)
        self.view.addItem(self.active_roi)

        # Если это Писк (call), добавляем точку для пиковой частоты
        if typ == "call":
            cx = model.t_fmaxe_ms if model.t_fmaxe_ms else model.t_start_ms + size[0]/2
            cy = model.fmaxe_khz if model.fmaxe_khz else model.f_min_khz + size[1]/2
            
            pt_pen = pg.mkPen('y', width=2)
            pt_brush = pg.mkBrush(255, 255, 0, 150)
            self.active_fmaxe_roi = PointROI([cx, cy], pt_pen, pt_brush)
            self.active_fmaxe_roi.sigRegionChanged.connect(self.on_roi_changed)
            self.active_fmaxe_roi.setZValue(101)
            self.view.addItem(self.active_fmaxe_roi)

        # Фокусируем камеру
        self.view.autoRange(items=[self.active_roi], padding=0.2)
        self._updating_from_code = False

    # --- СИНХРОНИЗАЦИЯ: Обновление модели при перетаскивании ROI ---
    def on_roi_changed(self):
        if self._updating_from_code or not self.active_model: return
        
        # Временно блокируем сигналы у самой модели, чтобы UI не мерцал, 
        # но вызываем model.changed в конце, чтобы обновить Дерево и Форму
        
        if self.active_roi:
            pos = self.active_roi.pos()
            size = self.active_roi.size()
            self.active_model.t_start_ms = pos.x()
            self.active_model.f_min_khz = pos.y()
            self.active_model.t_end_ms = pos.x() + size.x()
            self.active_model.f_max_khz = pos.y() + size.y()
            
        if self.active_fmaxe_roi and self.active_type == "call":
            pt_pos = self.active_fmaxe_roi.pos()
            self.active_model.t_fmaxe_ms = pt_pos.x()
            self.active_model.fmaxe_khz = pt_pos.y()
            
        # FastLayer обновляется автоматически по сигналу changed от модели

    # --- ИНТЕРАКЦИЯ: Хит-тест по клику мыши ---
    def on_mouse_click(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton: return
        
        # Если кликнули по самому ROI, игнорируем (даем ему перемещаться)
        for item in self.scene().items(ev.scenePos()):
            if isinstance(item, pg.ROI) or (hasattr(item, 'parentItem') and isinstance(item.parentItem(), pg.ROI)):
                return

        pos = self.view.mapSceneToView(ev.scenePos())
        px, py = pos.x(), pos.y()

        hit_typ, hit_model = None, None

        # Проверяем снизу вверх (сначала самые маленькие - Calls)
        for seq in self.recording.sequences:
            for call in seq.calls:
                # Хит-тест для прямоугольника писка
                if (call.t_start_ms <= px <= call.t_end_ms) and (call.f_min_khz <= py <= call.f_max_khz):
                    hit_typ, hit_model = "call", call
                    break
            if hit_model: break

        # Если не попали в писк, проверяем Sequences
        if not hit_model:
            for seq in self.recording.sequences:
                if (seq.t_start_ms <= px <= seq.t_end_ms) and (seq.f_min_khz <= py <= seq.f_max_khz):
                    hit_typ, hit_model = "seq", seq
                    break

        # Отправляем сигнал главному окну
        self.itemClicked.emit(hit_typ or "", hit_model)
