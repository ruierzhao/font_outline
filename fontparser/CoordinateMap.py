"""
根据地图实际距离
把字体坐标映射到地图坐标
"""
from .CoordinateConverter import ContourAffine, CoordinateConverter
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
        self.coordConverter = CoordinateConverter()
        try :
            # self.point = (float(i) for i in location_base_text.split(","))
            coordList_str = location_base_text.split(",")
            basePoint = self.coordConverter.to_3857(float(coordList_str[1]), float(coordList_str[0]))
            self.affine = ContourAffine(basePoint, CoordinateMap.width, CoordinateMap.gap)
        except:
            raise Exception("起始坐标解析错误。。。")

    
    def font2map(self, contourExtractor, i):
        """获取仿射变换后的坐标。"""
        # print("== cc:", contours2wkt(contourExtractor.contours))
        # 缩放字体
        vv = self.affine.transform(contourExtractor, i)
        # print("== cc:", contours2wkt(vv))

        

def contours2wkt(contours):
    i = 0
    wkt_str = "polygon("
    for contour in contours:
        if i == 0:
            wkt_str += "("
        else:
            wkt_str += ",("
        point_1 = contour[0]
        for point in contour:
            wkt_str += str(point[0]) + " " + str(point[1]) + ", "
            
        wkt_str += str(point_1[0]) + " " + str(point_1[1]) + ")"
        i += 1
    wkt_str += ")"

    return wkt_str
