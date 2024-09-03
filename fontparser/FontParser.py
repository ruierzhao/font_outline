from fontTools.ttLib import TTFont

from .ContourExtractor import ContourExtractor
from .CoordinateMap import CoordinateMap

class FontParser:

    def __init__(self, fontAssetPath="../assets/msyahei.ttf") -> None:
        self.font = TTFont(fontAssetPath)
        self._wkts = []
        self.contourExtractor = ContourExtractor()
        self.fcmap_table = self.font["cmap"] # 获取字体名称表
        self.glyf_table = self.font["glyf"] #  获取字体字形表

        self.bcmap = self.fcmap_table.getBestCmap()
    
    # 关闭TTFont
    def __del__(self):
        self.font.close()
        print("parse finished, close font...")

    # 获取字符的unicode编码
    def _getUniCode(self, char):
        charuni = ord(char)
        print(char, "unicode编码为：", charuni)

        return self.bcmap.get(charuni, None)

    # 获取字体坐标数组
    def _getContours(self, input_char):
        input_char_bcmap = self._getUniCode(input_char) # self.bcmap.get(ord(input_char),None)
        if input_char_bcmap is None:
            print("char: ", input_char, " bestmap is none")
            return
        self.glyf_table[input_char_bcmap].draw(self.contourExtractor, self.glyf_table)
        

    # 解析输入字符串为矢量数据
    def parse(self, input_str, location_text, savepath):
        coordMap = CoordinateMap(location_text)

        for i, input_char in enumerate(input_str):
            print("==input_char: ", input_char)
            self._getContours(input_char)
            coordMap.font2map(self.contourExtractor, i)
            
            self.contourExtractor.reboot() # TODO: debug写法，待优化

        coordMap.toGeojson(savepath)
        
        # return geonjson

        
        

