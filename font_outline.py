# -*- coding: utf-8 -*-

import time
from .fontparser.FontParser import FontParser
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsPointXY, QgsVectorLayer,Qgis
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication 
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .font_outline_dialog import FontOutlineDialog
import os.path


class FontOutline:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        
        self.iface = iface
        
        self.plugin_dir = os.path.dirname(__file__)
        
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FontOutline_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Font Outline')

        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FontOutline', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/font_outline/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'font outline'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Font Outline'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = FontOutlineDialog()
        
        self.dlg.show() # show the dialog
        
        result = self.dlg.exec_() # Run the dialog event loop

        if result :
            input_str = self.dlg.lineEdit.text().strip()
            if input_str is "" or input_str is None:
                return self.iface.messageBar().pushMessage("warning", f"输入文本为空，生成失败。", level=Qgis.Warning, duration=5)
                # return self.iface.messageBar().pushWarning("warning", "输入文本为空，生成失败。")

            location_text = self.dlg.location_text.text()

            save_path = self.dlg.saveFileWidget.filePath()
            save_path = self._checkSavePath(save_path, input_str)
            
            self._save2file(input_str, location_text, save_path)

            self._result2project(save_path)


    def _save2file(self, input_str, location_text, save_path):
        fontparse = FontParser(os.path.join(self.plugin_dir,"assets", "msyahei.ttf"))
        fontparse.parse(input_str, location_text, save_path)
        

    def _result2project(self, geojson_path):
        # 加载GeoJSON文件作为QGIS矢量图层
        layer = QgsVectorLayer(geojson_path, "fontOutline", "ogr")

        # 检查图层是否有效
        if not layer.isValid():
            return self.iface.messageBar().pushMessage("error", f" geojson 文件：{geojson_path} 加载失败。。", level=Qgis.Error, duration=5)

        # 将图层添加到当前项目中
        QgsProject.instance().addMapLayer(layer)

        # 反馈信息
        self.iface.messageBar().pushMessage("success", f"成功加载 geojson 文件：{geojson_path}", level=Qgis.Info, duration=5)

    # 处理保存路径
    def _checkSavePath(self,save_path, input_str):
        if not os.path.isabs(save_path):
            default_path = os.path.join(os.environ['HOME'] if os.environ['HOME'] is not None else os.environ['USERPROFILE'], "Documents")
            if save_path is "" or save_path is None:
                save_path = os.path.join(default_path, input_str + "_" + str(int(time.time())))
            else:
                save_path = os.path.join(default_path, save_path)

        if not (save_path.endswith(".geojson") and save_path.endswith(".json")) :
            save_path += ".geojson"

        return save_path

            
              

