import os

from qgis.PyQt.QtGui import QPixmap,QPalette
from qgis.PyQt.QtWidgets import QLabel, QMainWindow, QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox, QDialog
from qgis.core import QgsVectorLayer, QgsProject, QgsLayerTreeModel, QgsRasterLayer
from qgis.gui import QgsMapCanvas, QgsMapToolZoom, QgsMapToolPan, QgsLayerTreeView, \
    QgsLayerTreeMapCanvasBridge

from ui.main_ui import Ui_MainWindow
from utils.customMenu import CustomMenuProvider
from widgets.Dialog import CutDialog, DetectionDialog, StretchDialog, V2RDialog, ClassifyDialog, DataSetAugDialog, \
    ProjDefineDialog, R2VDialog,YoloTransDialog,DataSetDivideDialog

PROJECT = QgsProject.instance()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.first_flag = True
        self.setWindowTitle('卫星及无人机遥感影像智能解译软件')
        # 调整窗口大小
        self.resize(1000, 600)
        # 初始化图层树
        vl = QVBoxLayout(self.dockWidgetContents)
        self.layerTreeView = QgsLayerTreeView(self)
        vl.addWidget(self.layerTreeView)
        # 初始化地图画布
        self.mapCanvas = QgsMapCanvas(self)
        hl = QHBoxLayout(self.frame)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self.mapCanvas)

        # 建立桥梁
        self.model = QgsLayerTreeModel(PROJECT.layerTreeRoot(), self)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)
        self.model.setAutoCollapseLegendNodes(10)
        self.layerTreeView.setModel(self.model)
        self.layerTreeBridge = QgsLayerTreeMapCanvasBridge(PROJECT.layerTreeRoot(), self.mapCanvas, self)
        # 显示经纬度
        self.mapCanvas.xyCoordinates.connect(self.showLngLat)

        # 地图工具
        self.actionPanTriggered()
        self.actionPan.triggered.connect(self.actionPanTriggered)
        self.actionZoomin.triggered.connect(self.actionZoomInTriggered)
        self.actionZoomout.triggered.connect(self.actionZoomOutTriggered)

        # 图层
        self.actionShapefile.triggered.connect(self.actionShapefileTriggered)
        self.actionGeotiff.triggered.connect(self.actionGeotiffTriggered)
        self.actionPan.triggered.connect(self.actionPanTriggered)
        # self.actionIdentify.triggered.connect(self.actionIdentifyTriggered)

        # 功能
        self.actionClip.triggered.connect(self.actionCutImgTriggered)
        self.actionStretch.triggered.connect(self.actionStretchTtiggered)
        self.action_vector2raster.triggered.connect(self.action_vector2rasterTriggered)
        # self.actionDatasetDivide.triggered.connect(self.actiondemoTriggered)
        self.actionDataFlip.triggered.connect(self.actionDataFlipTriggered)
        self.actionprojection.triggered.connect(self.actionprojectionTriggered)
        self.action_raster2vector.triggered.connect(self.actionraster2vectorTriggered)
        self.actiondTrans.triggered.connect(self.actiondTransTriggered)
        self.actionDatasetDivide.triggered.connect(self.actionDatasetDivideTriggered)

        # 左侧菜单栏
        self.pushButton_1.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_2.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_3.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_7.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_5.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_6.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_13.clicked.connect(self.actionTargetDetTriggered)
        self.pushButton_feilei.clicked.connect(self.actionClassifyTriggered)

        # 帮忙
        self.actionPyQGISdevelop.triggered.connect(self.actionPyQGISTriggered)
        self.action_aboutsystem.triggered.connect(self.action_aboutsystemTtiggered)

        # 图层右键菜单
        self.customMenuProvider = CustomMenuProvider(self.layerTreeView, self.mapCanvas)
        self.layerTreeView.setMenuProvider(self.customMenuProvider)
        # self.layerTreeRegistryBridge = QgsLayerTreeRegistryBridge(PROJECT.layerTreeRoot(), PROJECT, self)

    def actionPanTriggered(self):
        self.mapTool = QgsMapToolPan(self.mapCanvas)
        self.mapCanvas.setMapTool(self.mapTool)

    def actionZoomInTriggered(self):
        self.mapTool = QgsMapToolZoom(self.mapCanvas, False)
        self.mapCanvas.setMapTool(self.mapTool)

    def actionZoomOutTriggered(self):
        self.mapTool = QgsMapToolZoom(self.mapCanvas, True)
        self.mapCanvas.setMapTool(self.mapTool)

    def showFeatures(self, feature):
        print(type(feature))

        QMessageBox.information(self, '信息', ''.join(feature.attributes()))

    def actionAddGroupTriggered(self):
        PROJECT.layerTreeRoot().addGroup('group1')

    def actionShapefileTriggered(self):
        """打开shp"""
        data_file, ext = QFileDialog.getOpenFileGDB(self, '打开', '', '*.gdb')
        if data_file:
            layer = QgsVectorLayer(data_file, os.path.splitext(os.path.basename(data_file))[0], "ogr")
            self.addLayer(layer)

    def actionGeotiffTriggered(self):
        """加载geotiff"""
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '', '*.tif')
        if data_file:
            layer = QgsRasterLayer(data_file, os.path.basename(data_file))
            self.addLayer(layer)

    # 触发窗口函数------地理处理menu
    def actionCutImgTriggered(self):
        """裁剪影像"""
        dialog = CutDialog(self)
        dialog.exec_()

    def actionTargetDetTriggered(self):
        """目标检测"""
        dialog = DetectionDialog(self)
        dialog.exec_()

    # 触发窗口函数---数据增强menu
    def actionStretchTtiggered(self):
        dialog = StretchDialog(self)
        dialog.exec_()

    # 数据转换----矢量转栅格
    def action_vector2rasterTriggered(self):
        dialog = V2RDialog(self)
        dialog.exec_()

    # 数据转换----栅格转矢量
    def actionraster2vectorTriggered(self):
        dialog = R2VDialog(self)
        dialog.exec_()

    # Tap菜单栏--地物分类
    def actionClassifyTriggered(self):
        dialog = ClassifyDialog(self)
        dialog.exec_()
        if dialog.close():
            layer = QgsRasterLayer(dialog.out_file_path,os.path.basename(dialog.out_file_path))
            self.addLayer(layer)
            pie_dialog = QDialog()
            pie_dialog.resize(640, 480)
            pie_dialog.setWindowTitle('地物类别统计')
            pic = QPixmap(dialog.pie_file_path)
            label_pic = QLabel('show', pie_dialog)
            label_pic.setPixmap(pic)
            label_pic.setGeometry(0, 0, 640, 480)
            pie_dialog.exec_()

    # 数据增强=--数据集增广
    def actionDataFlipTriggered(self):
        dialog = DataSetAugDialog(self)
        dialog.exec_()

    # 地理处理--定义投影
    def actionprojectionTriggered(self):
        dialog = ProjDefineDialog(self)
        dialog.exec_()
    # 深度学习-==格式转换
    def actiondTransTriggered(self):
        dialog = YoloTransDialog()
        dialog.exec_()

    # 深度学习--数据集划分
    def actionDatasetDivideTriggered(self):
        dialog = DataSetDivideDialog()
        dialog.exec_()


    # 帮忙menu
    def actionPyQGISTriggered(self):
        """
        :return:打开pyqgis开发者文档
        """
        os.system('"C:/Program Files/Internet Explorer/iexplore.exe" '
                  'https://docs.qgis.org/3.16/zh_Hans/docs/pyqgis_developer_cookbook/index.html')

    def action_aboutsystemTtiggered(self):
        AQMessageBox = QMessageBox()

        AQMessageBox.information(self, '关于本系统', '遥感影像目标检测系统 '
                                                '\n版本1.0', QMessageBox.Ok)

    def addLayer(self, layer):
        if layer.isValid():
            if self.first_flag:
                self.mapCanvas.setDestinationCrs(layer.crs())
                self.mapCanvas.setExtent(layer.extent())
                self.first_flag = False
            PROJECT.addMapLayer(layer)
            layers = [layer] + [PROJECT.mapLayer(i) for i in PROJECT.mapLayers()]
            self.mapCanvas.setLayers(layers)
            self.mapCanvas.refresh()
            print(type(layer))


        else:
            print('图层无效.')

    def showLngLat(self, point):
        x = point.x()
        y = point.y()
        self.statusbar.showMessage(f'经度:{x}, 纬度:{y}')
