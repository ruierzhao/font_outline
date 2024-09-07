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
        
        width, height = contourExtractor.wh()

        # 计算缩放因子
        scale_x = self.new_width / height
        scale_y = scale_x   # 保持宽高比

        contours = contourExtractor.coords()
        
        # 平移之后的坐标
        pin_base_x = self.base_x + (self.new_width + self.gap) * i
        if contourExtractor.is_chinese():
            pin_base_y = self.base_y  # 中文不处理
        else:
            pin_base_y = self.base_y + minY * scale_y # 处理基线，类似g,j之类的字母
        pin_base_y = self.base_y + minY * scale_y # 处理基线，类似g,j之类的字母


        for i, contour in enumerate(contours):
            for j, point in enumerate(contour):
                contours[i][j] = (pin_base_x + minX + (point[0] - minX) * scale_x, pin_base_y + minY + (point[1] - minY) * scale_y)

        return contours
