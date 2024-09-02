from fontTools.pens.basePen import BasePen

class ContourExtractor(BasePen):
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
    
    def parse2wkt(self):
        """
        笔画解析为wkt格式。
        
        wkt_str:
          POLYGON ((1 2, 2 4, 4 4, 1 2), (3 3, 8 0, 5 5, 3 3))
        """
        if len(self.contours) == 0:
            print("self.contours 为空。。")
            return
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
        # contours 重设为空
        self.contours = []

        return wkt_str

