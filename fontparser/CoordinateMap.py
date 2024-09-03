"""
根据地图实际距离
把字体坐标映射到地图坐标
"""
from .CoordinateConverter import ContourAffine, CoordinateConverter
from qgis.core import QgsGeometry, QgsFeature, QgsFields, QgsField, QgsVectorLayer, QgsVectorFileWriter, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

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
        self.features = []

    
    def font2map(self, contourExtractor, i):
        """获取仿射变换后的坐标。"""
        # 缩放字体
        trans_contours = self.affine.transform(contourExtractor, i)
        # 构建feature
        _wkt = self.contours2wkt(trans_contours)
        geometry = QgsGeometry.fromWkt(_wkt)

        # fields = QgsFields()
        # fields.append(QgsField('id', QVariant.Int))
        feature = QgsFeature(i)
        feature.setGeometry(geometry)

        self.features.append(feature)


    def contours2wkt(self, contours):
        i = 0
        wkt_str = "polygon("
        for contour in contours:
            if i == 0:
                wkt_str += "("
            else:
                wkt_str += ",("

            point_1 = self.coordConverter.to_4326(contour[0][0], contour[0][1])

            for point in contour:
                _point = self.coordConverter.to_4326(point[0], point[1])
                wkt_str += str(_point.x()) + " " + str(_point.y()) + ", "
                
            wkt_str += str(point_1.x()) + " " + str(point_1.y()) + ")"
            i += 1
        wkt_str += ")"

        return wkt_str
    

    def toGeojson(self):
        layer = QgsVectorLayer('Polygon?crs=EPSG:4326', 'fontoutline_temporary_layer', 'memory')
        layer.addFeatures(self.features)

        writer = QgsVectorFileWriter('output5656.geojson', 'UTF-8', layer.fields(), QgsWkbTypes.Polygon, layer.crs(), 'GeoJSON')
        for feature in layer.getFeatures():
            writer.addFeature(feature)
        del writer
        

        

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
