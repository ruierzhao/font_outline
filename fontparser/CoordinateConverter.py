from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsPointXY, QgsWkbTypes, QgsGeometry

from .ContourExtractor import ContourExtractor

class CoordinateConverter:
    def __init__(self):
        # 定义 EPSG:4326 和 EPSG:3857 的坐标参考系
        self.crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS 84
        self.crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")  # Web Mercator

        # 创建转换器
        self.transform_to_3857 = QgsCoordinateTransform(self.crs_4326, self.crs_3857, QgsProject.instance())
        self.transform_to_4326 = QgsCoordinateTransform(self.crs_3857, self.crs_4326, QgsProject.instance())

    def to_3857(self, lon, lat):
        """将经纬度坐标 (EPSG:4326) 转换为 EPSG:3857"""
        point = QgsPointXY(lon, lat)
        transformed_point = self.transform_to_3857.transform(point)
        return transformed_point

    def to_4326(self, x, y):
        """将 EPSG:3857 坐标转换为经纬度坐标 (EPSG:4326)"""
        point = QgsPointXY(x, y)
        transformed_point = self.transform_to_4326.transform(point)
        return transformed_point



class ContourAffine:
    def __init__(self, base_position, width, gap):
        """
        初始化 WktScaler。
        :param base_position: 图形的新基准位置 (x, y)
        :param width: 新图形的宽度
        """
        self.base_x, self.base_y = base_position
        self.new_width = width
        self.gap = gap

    def transform(self, contourExtractor:ContourExtractor, i):
        """
        变换contour坐标：
        """
        minX, minY, maxX, maxY = contourExtractor.bbox()
        width = maxX - minX
        height = maxY - minY
        # 计算缩放因子
        scale_x = self.new_width / width
        scale_y = scale_x * (height / width)  # 保持宽高比

        contours = contourExtractor.coords()
        
        # 平应之后的坐标
        pin_base_x = self.base_x + (self.new_width + self.gap) * i
        pin_base_y = self.base_y

        for i, contour in enumerate(contours):
            for j, point in enumerate(contour):
                contours[i][j] = (pin_base_x + minX + (point[0] - minX) * scale_x, pin_base_y + minY + (point[1] - minY) * scale_y)

        return contours


    def scale_and_translate_wkt(self, wkt):
        """
        对 WKT 字符串应用缩放和平移变换。
        :param wkt: 输入的 WKT 字符串
        :return: 变换后的 WKT 字符串
        """
        geometry = QgsGeometry.fromWkt(wkt)
        if geometry.isNull():
            raise ValueError("无效的 WKT 输入")

        # 计算原图形的边界框
        bbox = geometry.boundingBox()
        original_width = bbox.width()
        original_height = bbox.height()

        # 计算缩放因子
        scale_x = self.new_width / original_width
        scale_y = scale_x * (original_height / original_width)  # 保持宽高比

        # 计算变换后的顶点
        transformed_vertices = []
        for vertex in geometry.vertices():
            # 缩放
            x = vertex.x() * scale_x
            y = vertex.y() * scale_y

            # 平移到新位置
            x += self.base_x - (bbox.xMinimum() * scale_x)
            y += self.base_y - (bbox.yMinimum() * scale_y)

            transformed_vertices.append(QgsPointXY(x, y))

        # 构造新的几何对象
        if geometry.type() == QgsWkbTypes.PointGeometry:
            return QgsGeometry.fromPointXY(transformed_vertices[0])
        elif geometry.type() == QgsWkbTypes.LineGeometry:
            return QgsGeometry.fromPolylineXY(transformed_vertices)
        elif geometry.type() == QgsWkbTypes.PolygonGeometry:
            return QgsGeometry.fromPolygonXY([transformed_vertices])

        return geometry

# 示例用法
if __name__ == "__main__":
    # 示例 WKT 数据
    wkt = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0), (1.7 6.6, 5.6 7.7, 7 5.5, 7.025 5.4, 7.7 3, 1.6 1.5, 1.5 4.3, 1.7 6.6))"
    
    # 初始化 WktScaler：基准位置 (50, 50)，新宽度 20
    scaler = ContourAffine(base_position=(50, 50), width=20)
    
    # 应用缩放和平移变换
    transformed_wkt = scaler.scale_and_translate_wkt(wkt)
    print("转换后的 WKT：", transformed_wkt)

