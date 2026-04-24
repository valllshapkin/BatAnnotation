import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from App.Utils import chaikin_smooth

class PointROI(pg.ROI):
    """Интерактивная точка (используется для fmaxe)"""
    def __init__(self, pos, pen, brush):
        super().__init__(pos, [0, 0], movable=True, resizable=False, rotatable=False)
        self.pen = pen
        self.brush = brush

    def paint(self, p, opt, widget):
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        px, py = self.pixelSize()
        rx, ry = 6 * px, 6 * py
        p.drawEllipse(QtCore.QRectF(-rx, -ry, rx * 2, ry * 2))

    def boundingRect(self):
        px, py = self.pixelSize()
        rx, ry = 8 * px, 8 * py
        return QtCore.QRectF(-rx, -ry, rx * 2, ry * 2)


class SmoothPolyLineROI(pg.PolyLineROI):
    """Полилиния со сглаживанием между управляющими узлами"""
    def __init__(self, positions, pen):
        # ИСПРАВЛЕНИЕ: Убрали handleSize из аргументов, чтобы не было ошибки
        super().__init__(
            positions, 
            closed=False, 
            pen=pg.mkPen(None), 
            hoverPen=None, 
            handlePen=pg.mkPen('w', width=2)
        )
        
        # Задаем размер ручек напрямую атрибутом (pyqtgraph подхватит его при отрисовке)
        self.handleSize = 14 
        
        # Обновляем все уже созданные ручки, чтобы они перерисовались в новом размере
        for h in self.getHandles():
            h.update()
            
        self.smooth_path_item = QtWidgets.QGraphicsPathItem(self)
        self.smooth_path_item.setPen(pen)
        self.smooth_path_item.setBrush(QtCore.Qt.BrushStyle.NoBrush) 
        self.smooth_path_item.setZValue(-1)
        
        self.sigRegionChanged.connect(self.update_smooth_path)
        self.update_smooth_path()

    def update_smooth_path(self):
        handles = self.getHandles()
        if len(handles) < 2: 
            return
            
        pts = np.array([[h.pos().x(), h.pos().y()] for h in handles])
        smooth_pts = chaikin_smooth(pts, iterations=3)
        
        path = pg.arrayToQPath(smooth_pts[:, 0], smooth_pts[:, 1], connect='finite')
        self.smooth_path_item.setPath(path)

    def get_raw_points(self):
        pts = []
        for h in self.getHandles():
            p = self.mapToParent(h.pos())
            pts.append([float(p.x()), float(p.y())])
        return pts
