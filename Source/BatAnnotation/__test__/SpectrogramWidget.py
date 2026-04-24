import numpy as np
import pyqtgraph as pg
import zlib
from pyqtgraph.Qt import QtCore, QtGui
from PySide6.QtCore import Qt

from BatAnnotation.QtModels import QtModelBase, QtRecording, QtSequence, QtBatCall

class PointROI(pg.ROI):
    def __init__(self, pos, pen, brush):
        super().__init__(pos, [0, 0], movable=True, resizable=False, rotatable=False)
        self.pen = pen
        self.brush = brush

    def paint(self, p, opt, widget):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        px, py = self.pixelSize()
        rx, ry = 5 * px, 5 * py
        p.drawEllipse(QtCore.QRectF(-rx, -ry, rx * 2, ry * 2))

    def boundingRect(self):
        px, py = self.pixelSize()
        rx, ry = 6 * px, 6 * py
        return QtCore.QRectF(-rx, -ry, rx * 2, ry * 2)

class FastAnnotationLayer(pg.GraphicsObject):
    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.active_model = None  
        self._color_cache = {}
        self.pen_pt = pg.mkPen((255, 255, 0), width=1)
        self.brush_pt = pg.mkBrush(255, 255, 0, 200)

        self.recording.changed.connect(self.update)

    def get_seq_colors(self, seq_id: str):
        if seq_id not in self._color_cache:
            h = zlib.adler32(seq_id.encode('utf-8')) % 360
            color = QtGui.QColor.fromHsv(h, 200, 255)
            seq_pen = pg.mkPen(color, width=1)
            color.setAlpha(30)
            seq_brush = pg.mkBrush(color)
            color.setAlpha(80)
            call_brush = pg.mkBrush(color)
            self._color_cache[seq_id] = (seq_pen, seq_brush, call_brush)
        return self._color_cache[seq_id]

    def set_active_model(self, model):
        self.active_model = model
        self.update()

    def paint(self, p, *args):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        px = self.pixelWidth() * 4 if self.pixelWidth() else 1
        py = self.pixelHeight() * 4 if self.pixelHeight() else 1

        for seq in self.recording.sequences:
            seq_id = seq.sequence_id if seq.sequence_id else "default"
            seq_pen, seq_brush, call_brush = self.get_seq_colors(seq_id)
            
            if seq != self.active_model:
                p.setPen(seq_pen)
                p.setBrush(seq_brush)
                w = seq.t_end_ms - seq.t_start_ms
                h = seq.f_max_khz - seq.f_min_khz
                p.drawRect(QtCore.QRectF(seq.t_start_ms, seq.f_min_khz, w, h))
                
            for call in seq.calls:
                if call != self.active_model:
                    p.setPen(seq_pen)
                    p.setBrush(call_brush)
                    cw = call.t_end_ms - call.t_start_ms
                    ch = call.f_max_khz - call.f_min_khz
                    p.drawRect(QtCore.QRectF(call.t_start_ms, call.f_min_khz, cw, ch))
                    
                    if call.fmaxe_khz is not None and call.t_fmaxe_ms is not None:
                        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
                        p.setPen(self.pen_pt)
                        p.setBrush(self.brush_pt)
                        cx, cy = call.t_fmaxe_ms, call.fmaxe_khz
                        p.drawEllipse(QtCore.QRectF(cx - px, cy - py, px * 2, py * 2))
                        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 999999, 200)

class SpectrogramWidget(pg.PlotWidget):
    itemClicked = QtCore.Signal(str, object) 

    def __init__(self, recording: QtRecording):
        super().__init__()
        self.recording = recording
        self.view = self.getViewBox()

        self.setLabel('bottom', 'Time', units='ms')
        self.setLabel('left', 'Frequency', units='kHz')
        
        self.setup_dummy_background()
        self.fast_layer = FastAnnotationLayer(self.recording)
        self.view.addItem(self.fast_layer)
        
        self.active_roi = None
        self.active_fmaxe_roi = None
        self.active_model = None
        self.active_type = None
        self._updating_from_code = False 
        
        self.scene().sigMouseClicked.connect(self.on_mouse_click)

    def setup_dummy_background(self):
        img = pg.ImageItem()
        noise = np.random.normal(size=(10000, 200), loc=50, scale=20).astype(np.uint8)
        img.setImage(noise)
        img.setRect(QtCore.QRectF(0, 0, 10000, 200)) 
        colormap = pg.colormap.get('magma')
        img.setColorMap(colormap)
        self.view.addItem(img)

    def set_selection(self, typ: str, model: QtModelBase):
        self._updating_from_code = True
        
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

        if typ == "rec":
            max_time_ms = (self.active_model.duration_s * 1000) if hasattr(self.active_model, 'duration_s') and self.active_model.duration_s else 10000
            max_freq_khz = (self.active_model.sample_rate_hz / 2000) if hasattr(self.active_model, 'sample_rate_hz') and self.active_model.sample_rate_hz else 150
            self.view.setRange(xRange=[0, max_time_ms], yRange=[0, max_freq_khz], padding=0.0)
            self._updating_from_code = False
            return

        seq = model.parent() if typ == "call" else model
        seq_id = seq.sequence_id if seq and hasattr(seq, 'sequence_id') else "default"
        h = zlib.adler32(seq_id.encode('utf-8')) % 360
        
        color = QtGui.QColor.fromHsv(h, 255, 255)
        pen = pg.mkPen(color, width=2)
        
        pos = (model.t_start_ms, model.f_min_khz)
        size = (max(1, model.t_end_ms - model.t_start_ms), max(1, model.f_max_khz - model.f_min_khz))
        
        self.active_roi = pg.ROI(pos, size, pen=pen, hoverPen=pg.mkPen('w', width=3), rotatable=False, resizable=True, movable=True)
        for sx, sy in [(0,0), (1,1), (0,1), (1,0), (0.5,0), (0.5,1), (0,0.5), (1,0.5)]:
            self.active_roi.addScaleHandle([sx, sy], [1-sx, 1-sy])
            
        self.active_roi.sigRegionChanged.connect(self.on_roi_changed)
        self.active_roi.setZValue(100)
        self.view.addItem(self.active_roi)

        if typ == "call":
            cx = model.t_fmaxe_ms if model.t_fmaxe_ms else model.t_start_ms + size[0]/2
            cy = model.fmaxe_khz if model.fmaxe_khz else model.f_min_khz + size[1]/2
            
            pt_pen = pg.mkPen('y', width=2)
            pt_brush = pg.mkBrush(255, 255, 0, 150)
            self.active_fmaxe_roi = PointROI([cx, cy], pt_pen, pt_brush)
            self.active_fmaxe_roi.sigRegionChanged.connect(self.on_roi_changed)
            self.active_fmaxe_roi.setZValue(101)
            self.view.addItem(self.active_fmaxe_roi)

        self.view.autoRange(items=[self.active_roi], padding=0.2)
        self._updating_from_code = False

    def on_roi_changed(self):
        if self._updating_from_code or not self.active_model: return
        
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

    def on_mouse_click(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton: return
        
        for item in self.scene().items(ev.scenePos()):
            if isinstance(item, pg.ROI) or (hasattr(item, 'parentItem') and isinstance(item.parentItem(), pg.ROI)):
                return

        pos = self.view.mapSceneToView(ev.scenePos())
        px, py = pos.x(), pos.y()

        hit_typ, hit_model = None, None

        for seq in self.recording.sequences:
            for call in seq.calls:
                if (call.t_start_ms <= px <= call.t_end_ms) and (call.f_min_khz <= py <= call.f_max_khz):
                    hit_typ, hit_model = "call", call
                    break
            if hit_model: break

        if not hit_model:
            for seq in self.recording.sequences:
                if (seq.t_start_ms <= px <= seq.t_end_ms) and (seq.f_min_khz <= py <= seq.f_max_khz):
                    hit_typ, hit_model = "seq", seq
                    break

        self.itemClicked.emit(hit_typ or "rec", hit_model or self.recording)
