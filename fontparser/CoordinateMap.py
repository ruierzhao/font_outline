"""
根据地图实际距离
把字体坐标映射到地图坐标
"""
from qgis.core import QgsGeometry, QgsPointXY

class CoordinateMap:
    """
    location_base_text = "24.52533,103.79736"
    """

    # 字体在3857地图上的实际宽度 (米)
    # 高度根据字体宽高比确定
    width = 5000
    # 字体之间间隙距离
    gap = 800

    def __init__(self, location_base_text="24.52533,103.79736") -> None:
        try :
            # self.point = (float(i) for i in location_base_text.split(","))
            coordList_str = location_base_text.split(",")
            self.point = (float(coordList_str[0]), float(coordList_str[1]))
        except:
            raise Exception("起始坐标解析错误。。。")

        self.affine = WktAffine()
    
    def font2map(self, wkt):
        pass

    # 计算第`input_char_index`个字符起始位置（左下角）
    def __boundingBox(self, font_wkt):
        """
        QgsRectangle:
            xMaximum
            xMinimum
            yMaximum
            yMinimum
        """
        geometry = QgsGeometry.fromWkt(font_wkt)
        boundingBox = geometry.boundingBox()
        return boundingBox

