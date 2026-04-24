import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PySide6.QtCore import Qt

from BatAnnotation.QtModels import QtRecording
from App.CustomROIs import PointROI, SmoothPolyLineROI
from App.Utils import point_line_distance, chaikin_smooth

class FastAnnotationLayer(pg.GraphicsObject):
    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.active_model = None
        self.active_sub_type = None # "fmaxe" или "curve" или None
        
        self.pen_seq = pg.mkPen((50, 150, 255), width=1)
        self.brush_seq = pg.mkBrush(50, 150, 255, 30)
        
        self.pen_call = pg.mkPen((50, 255, 50), width=1)
        self.brush_call = pg.mkBrush(50, 255, 50, 50)
        
        self.pen_pt = pg.mkPen((255, 255, 0), width=2)
        self.brush_pt = pg.mkBrush(255, 255, 0, 150)
        
        self.pen_curve = pg.mkPen((255, 100, 255), width=2)

        self.recording.changed.connect(self.update)

    def set_active(self, model, sub_type):
        self.active_model = model
        self.active_sub_type = sub_type
        self.update()

    def paint(self, p, *args):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        px = self.pixelWidth() * 4 if self.pixelWidth() else 1
        py = self.pixelHeight() * 4 if self.pixelHeight() else 1

        for seq in self.recording.sequences:
            # 1. Sequences
            if seq != self.active_model or self.active_sub_type:
                p.setPen(self.pen_seq)
                p.setBrush(self.brush_seq)
                p.drawRect(QtCore.QRectF(seq.t_start_ms, seq.f_min_khz, seq.t_end_ms - seq.t_start_ms, seq.f_max_khz - seq.f_min_khz))
                
            # 2. Calls
            for call in seq.calls:
                is_active_call = (call == self.active_model and not self.active_sub_type)
                if not is_active_call:
                    p.setPen(self.pen_call)
                    p.setBrush(self.brush_call)
                    p.drawRect(QtCore.QRectF(call.t_start_ms, call.f_min_khz, call.t_end_ms - call.t_start_ms, call.f_max_khz - call.f_min_khz))
                    
                p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                
                # 3. FmaxE (Point)
                if call.fmaxe_khz is not None and call.t_fmaxe_ms is not None:
                    if not (call == self.active_model and self.active_sub_type == "fmaxe"):
                        p.setPen(self.pen_pt)
                        p.setBrush(self.brush_pt)
                        p.drawEllipse(QtCore.QRectF(call.t_fmaxe_ms - px, call.fmaxe_khz - py, px * 2, py * 2))

                # 4. Curves
                if call.signal_curves and "main" in call.signal_curves:
                    if not (call == self.active_model and self.active_sub_type == "curve"):
                        pts = call.signal_curves["main"]
                        if len(pts) >= 2:
                            smooth_pts = chaikin_smooth(pts, 2)
                            path = pg.arrayToQPath(smooth_pts[:, 0], smooth_pts[:, 1], connect='finite')
                            p.setPen(self.pen_curve)
                            p.drawPath(path)
                            
                p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 999999, 200)


class SpectrogramWidget(pg.PlotWidget):
    itemClicked = QtCore.Signal(str, object) # typ, model

    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.view = self.getViewBox()
        self.view.setLimits(yMin=0, yMax=200, xMin=0)
        self.setLabel('bottom', 'Time', units='ms')
        self.setLabel('left', 'Frequency', units='kHz')
        
        self.setup_dummy_background()
        
        self.fast_layer = FastAnnotationLayer(self.recording)
        self.view.addItem(self.fast_layer)
        
        self.active_roi = None
        self.active_model = None
        self.active_type = None
        self._updating_from_code = False
        
        self._prev_roi_pos = None
        self._prev_roi_size = None
        
        self.scene().sigMouseClicked.connect(self.on_mouse_click)

    def setup_dummy_background(self):
        img = pg.ImageItem()
        noise = np.random.normal(size=(10000, 200), loc=50, scale=20).astype(np.uint8)
        img.setImage(noise)
        img.setRect(QtCore.QRectF(0, 0, 10000, 200))
        img.setColorMap(pg.colormap.get('magma'))
        self.view.addItem(img)

    def set_selection(self, typ: str, model):
        self._updating_from_code = True
        
        if self.active_roi:
            self.view.removeItem(self.active_roi)
            self.active_roi = None
            
        sub_type = typ if typ in ["fmaxe", "curve"] else None
        self.fast_layer.set_active(model, sub_type)
        self.active_model = model
        self.active_type = typ
        
        if not model:
            self._updating_from_code = False
            return

        # 1. Sequence / Call (Прямоугольник)
        if typ in ["seq", "call"]:
            pen = pg.mkPen((50, 150, 255) if typ == "seq" else (50, 255, 50), width=2)
            pos = (model.t_start_ms, model.f_min_khz)
            size = (max(1, model.t_end_ms - model.t_start_ms), max(1, model.f_max_khz - model.f_min_khz))
            self.active_roi = pg.RectROI(pos, size, pen=pen, hoverPen=pg.mkPen('w', width=3))
            self.active_roi.addScaleHandle([1, 1], [0, 0])
            self.active_roi.addScaleHandle([0, 0], [1, 1])
            self.active_roi.addTranslateHandle([0.5, 0.5])
            
        # 2. FmaxE (Точка)
        elif typ == "fmaxe":
            cx = model.t_fmaxe_ms if model.t_fmaxe_ms else model.t_start_ms + (model.t_end_ms - model.t_start_ms)/2
            cy = model.fmaxe_khz if model.fmaxe_khz else model.f_min_khz + (model.f_max_khz - model.f_min_khz)/2
            self.active_roi = PointROI([cx, cy], pg.mkPen('y', width=2), pg.mkBrush(255, 255, 0, 150))

        # 3. Curve (Линия с узлами)
        elif typ == "curve":
            pts = model.signal_curves.get("main", []) if model.signal_curves else []
            if not pts:
                pts = [[model.t_start_ms, model.f_min_khz + (model.f_max_khz - model.f_min_khz)/2],
                       [model.t_end_ms, model.f_min_khz + (model.f_max_khz - model.f_min_khz)/2]]
            self.active_roi = SmoothPolyLineROI(pts, pg.mkPen((255, 100, 255), width=3))

        if self.active_roi:
            # Запоминаем изначальные параметры для вычисления дельты при драге
            self._prev_roi_pos = self.active_roi.pos()
            self._prev_roi_size = self.active_roi.size()
            
            self.active_roi.setZValue(100)
            self.active_roi.sigRegionChanged.connect(self.on_roi_changed)
            self.view.addItem(self.active_roi)
            
            # Убрано условие (if typ not in ...). Теперь autoRange срабатывает для всего!
            self.view.autoRange(items=[self.active_roi], padding=0.2)
                
        self._updating_from_code = False

    def on_roi_changed(self):
        if self._updating_from_code or not self.active_model: return
        
        if self.active_type in ["seq", "call"]:
            pos, size = self.active_roi.pos(), self.active_roi.size()
            
            # Вычисляем дельту перемещения
            dx = pos.x() - self._prev_roi_pos.x()
            dy = pos.y() - self._prev_roi_pos.y()
            
            # Если размер остался прежним, значит это чистое перетаскивание (translate)
            is_translating = (size.x() == self._prev_roi_size.x() and size.y() == self._prev_roi_size.y())
            
            # Обновляем координаты самого элемента
            self.active_model.t_start_ms = pos.x()
            self.active_model.f_min_khz = pos.y()
            self.active_model.t_end_ms = pos.x() + size.x()
            self.active_model.f_max_khz = pos.y() + size.y()
            
            # Если это перетаскивание - двигаем и всех детей
            if is_translating and (dx != 0 or dy != 0):
                if self.active_type == "seq":
                    for call in self.active_model.calls:
                        self._shift_call(call, dx, dy, shift_bounds=True)
                elif self.active_type == "call":
                    # Для звонка двигаем только его виртуальные узлы (сам звонок мы уже сдвинули выше)
                    self._shift_call(self.active_model, dx, dy, shift_bounds=False)
                    
            self._prev_roi_pos = pos
            self._prev_roi_size = size
            
        elif self.active_type == "fmaxe":
            pos = self.active_roi.pos()
            self.active_model.t_fmaxe_ms = pos.x()
            self.active_model.fmaxe_khz = pos.y()
            
        elif self.active_type == "curve":
            pts = self.active_roi.get_raw_points()
            if not self.active_model.signal_curves:
                self.active_model.signal_curves = {}
            new_curves = dict(self.active_model.signal_curves)
            new_curves["main"] = pts
            self.active_model.signal_curves = new_curves

        # Принудительно обновляем FastLayer, так как дети могли сместиться без вызова глобальных сигналов
        self.fast_layer.update()

    def _shift_call(self, call, dx, dy, shift_bounds=True):
        """Служебный метод для смещения координат писка и его виртуальных узлов"""
        if shift_bounds:
            call.t_start_ms += dx
            call.t_end_ms += dx
            call.f_min_khz += dy
            call.f_max_khz += dy
            
        if call.t_fmaxe_ms is not None:
            call.t_fmaxe_ms += dx
        if call.fmaxe_khz is not None:
            call.fmaxe_khz += dy
            
        if call.signal_curves and "main" in call.signal_curves:
            new_curves = dict(call.signal_curves)
            new_pts = []
            for pt in new_curves["main"]:
                new_pts.append([pt[0] + dx, pt[1] + dy])
            new_curves["main"] = new_pts
            call.signal_curves = new_curves

    def get_hit_threshold(self):
        px, py = self.view.viewPixelSize()
        return max(px, py) * 8

    def on_mouse_click(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton: return
        
        for item in self.scene().items(ev.scenePos()):
            if isinstance(item, pg.ROI) or (hasattr(item, 'parentItem') and isinstance(item.parentItem(), pg.ROI)):
                return

        pos = self.view.mapSceneToView(ev.scenePos())
        px, py, thresh2 = pos.x(), pos.y(), self.get_hit_threshold()**2

        # 1. Проверяем Точки (fmaxe)
        for seq in self.recording.sequences:
            for call in seq.calls:
                if call.fmaxe_khz is not None and call.t_fmaxe_ms is not None:
                    if (px - call.t_fmaxe_ms)**2 + (py - call.fmaxe_khz)**2 < thresh2:
                        return self.itemClicked.emit("fmaxe", call)

        # 2. Проверяем Кривые
        for seq in self.recording.sequences:
            for call in seq.calls:
                if call.signal_curves and "main" in call.signal_curves:
                    pts = call.signal_curves["main"]
                    for i in range(len(pts)-1):
                        d2 = point_line_distance(px, py, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
                        if d2 < thresh2:
                            return self.itemClicked.emit("curve", call)

        # 3. Проверяем Писки (Calls)
        for seq in self.recording.sequences:
            for call in seq.calls:
                if (call.t_start_ms <= px <= call.t_end_ms) and (call.f_min_khz <= py <= call.f_max_khz):
                    return self.itemClicked.emit("call", call)

        # 4. Проверяем Секвенции (Sequences)
        for seq in self.recording.sequences:
            if (seq.t_start_ms <= px <= seq.t_end_ms) and (seq.f_min_khz <= py <= seq.f_max_khz):
                return self.itemClicked.emit("seq", seq)

        self.itemClicked.emit("", None)
