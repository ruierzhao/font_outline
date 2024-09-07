from qgis.core import QgsGeometry
from fontTools.pens.basePen import BasePen

class ContourExtractor(BasePen):
    WKT = 1
    QG = 2
    def __init__(self):
        self._contours = []
        self._char:str = None
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
        self._contours.append(self.current_contour)
    
    def coords(self):
        return self._contours
    
    def reboot(self):
        self._contours = []
        self._char = None
    
    def setChar(self, input_char):
        """
        :param input_char:当前字符
        :type input_char:str
        """
        self._char = input_char
    
    def bbox(self):
        if len(self._contours) == 0:
            return 
        minX =  maxX = self._contours[0][0][0]
        minY = maxY = self._contours[0][0][1]
        for contour in self._contours:
            for point in contour:
                if minX >= point[0]: minX = point[0]
                if maxX <= point[0]: maxX = point[0]
                if minY >= point[1]: minY = point[1]
                if maxY <= point[1]: maxY = point[1]
        # for debug
        # return f"polygon(({minX} {minY}, {minX} {maxY}, {maxX} {maxY}, {maxX} {minY}, {minX} {minY}))"
        print("==ori_width ", maxX - minX)
        print("==ori_height ", maxY - minY)
        return (minX, minY, maxX, maxY)

    def wh(self):
        """
        计算字符坐标：
        - 数字
        input_char:  1
        ori_width  897
        ori_height  1582
        - 小写字母
        input_char: x
        ori_width  986
        ori_height  1106
        ==input_char:  w
        w unicode编码为： 119
        ==ori_width  1567
        ==ori_height  1106
        - 大写字母
        input_char: X
        ori_width  1265
        ori_height  1549
        - 中文
        input_char: 赵
        ori_width  1994
        ori_height  1968

        :return wh:左下角坐标和宽高
        :type wh:(minx, miny, width, height)
        """
        if self.is_lowercase(): return (1265, 1106)
        if self._char.isdigit(): return (897, 1582)
        if self.is_uppercase(): return (1265, 1549)
        # if self.is_chinese(): return (2000, 1968)
        return (1265, 1549)

    def is_chinese(self):
        # 中文字符 Unicode 范围
        print("chinese char")
        return '\u4e00' <= self._char <= '\u9fff'

    def is_uppercase(self):
        # 判断是否是大写英文字母
        print("english uppercase char")
        return 'A' <= self._char <= 'Z'

    def is_lowercase(self):
        # 判断是否是小写英文字母
        print("english lowercase char")
        return 'a' <= self._char <= 'z'


    def parse(self, parsefunc=None):
        if len(self._contours) == 0:
            print("self.contours 为空。。")
            return
        
        if  parsefunc == ContourExtractor.WKT or parsefunc is None:
            parse_result = self._parse2wkt()
        elif parsefunc == ContourExtractor.QG:
            parse_result = self._parse2QgsGeometry()
        else:
            raise Exception("unexpected parse type error...")

        # contours 重设为空
        self._contours = []
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
        for contour in self._contours:
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