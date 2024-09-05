## QGIS Plugin FontOutline

将任意文本字符串转为`geojson`矢量数据的 qgis 插件。

## usage

Your plugin FontOutline was created in:
D:/workspace/map\font_outline

Your QGIS plugin directory is located at:
~/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins

# dev

## 编译 ui 文件

```sh
# 设置 qgis 套件环境
o4w_env
# 编译 qrc 文件
pyrcc5 resources.qrc -o resources.py
# 编译 ui 文件
pyuic5 ui/main_ui.ui -o ui/main_ui.py
```
