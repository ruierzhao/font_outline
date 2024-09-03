from qgis.core import QgsGeometry
from fontTools.pens.basePen import BasePen

class ContourExtractor(BasePen):
    WKT = 1
    QG = 2
    def __init__(self):
        self.contours = []
        super().__init__()

    def addComponent(self, glyphName, transformation):
        pass

    def _moveTo(self, pt):
        self.current_contour = [pt]

    def _lineTo(self, pt):
        self.current_contour.append(pt)

    def _curveToOne(self, pt1, pt2, pt3):
        self.current_contour.extend([pt1, pt2, pt3])

    def _closePath(self):
        self.contours.append(self.current_contour)
    
    def coords(self):
        return self.contours
    
    def reboot(self):
        self.contours = []
    
    def bbox(self):
        minX =  maxX = self.contours[0][0][0]
        minY = maxY = self.contours[0][0][1]
        for contour in self.contours:
            for point in contour:
                if minX >= point[0]:minX = point[0] 
                if maxX <= point[0]: maxX = point[0]
                if minY >= point[1]: minY = point[1]
                if maxY <= point[1]: maxY = point[1]
        # for debug
        # return f"polygon(({minX} {minY}, {minX} {maxY}, {maxX} {maxY}, {maxX} {minY}, {minX} {minY}))"

        return (minX, minY, maxX, maxY)


    def parse(self, parsefunc=None):
        if len(self.contours) == 0:
            print("self.contours 为空。。")
            return
        
        if  parsefunc == ContourExtractor.WKT or parsefunc is None:
            parse_result = self._parse2wkt()
        elif parsefunc == ContourExtractor.QG:
            parse_result = self._parse2QgsGeometry()
        else:
            raise Exception("unexpected parse type error...")

        # contours 重设为空
        self.contours = []

        return parse_result
        

    def _parse2wkt(self):
        """
        debug:
        笔画解析为wkt格式。
        
        wkt_str:
          POLYGON ((1 2, 2 4, 4 4, 1 2), (3 3, 8 0, 5 5, 3 3))
        """
        i = 0
        wkt_str = "polygon("
        for contour in self.contours:
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
    


    def coordAffine(self, affine):
        """ 对字体坐标进行仿射变换 """
        # for contour in self.contours:
        #     for point in contour:
        #         affine.scale(point[0], point[1])


def contours2wkt(contours):
    """
    笔画解析为wkt格式。
    
    wkt_str:
        POLYGON ((1 2, 2 4, 4 4, 1 2), (3 3, 8 0, 5 5, 3 3))
    """
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