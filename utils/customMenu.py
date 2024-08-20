# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2020/10/19 11:38
from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.core import QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType,QgsProject
from qgis.gui import QgsLayerTreeViewMenuProvider, QgsLayerTreeView, QgsLayerTreeViewDefaultActions, QgsMapCanvas

from widgets.attributeDialog import AttributeDialog
from widgets.Render import Ui_Dialog_RenderPolygonDialog


class CustomMenuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self, layerTreeView: QgsLayerTreeView, mapCanvas: QgsMapCanvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layerTreeView = layerTreeView
        self.mapCanvas = mapCanvas

    def createContextMenu(self):
        menu = QMenu()
        actions: QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()
        if not self.layerTreeView.currentIndex().isValid():
            # 不在图层上右键
            self.actionAddGroup = actions.actionAddGroup(menu)
            menu.addAction(self.actionAddGroup)
            menu.addAction('Expand All', self.layerTreeView.expandAll)
            menu.addAction('Collapse All', self.layerTreeView.collapseAll)
            return menu

        node: QgsLayerTreeNode = self.layerTreeView.currentNode()

        if QgsLayerTree.isGroup(node):
            # 图组操作
            self.actionRemoveGroup = actions.actionRemoveGroupOrLayer(self.mapCanvas)
            self.actionRemoveGroup.setText('移除组')
            menu.addAction(self.actionRemoveGroup)
            pass
            print('group')
            pass
        elif QgsLayerTree.isLayer(node):
            print('layer')
            self.actionZoomToLayer = actions.actionZoomToLayer(self.mapCanvas, menu)
            menu.addAction(self.actionZoomToLayer)

            self.actionRemoveLayer = actions.actionRemoveGroupOrLayer(self.mapCanvas)
            self.actionRemoveLayer.setText('移除')
            menu.addAction(self.actionRemoveLayer)
            # 图层操作
            layer = self.layerTreeView.currentLayer()
            if layer.type() == QgsMapLayerType.VectorLayer:
                # 矢量图层
                actionOpenAttributeDialog = QAction('打开属性表', menu)
                actionOpenAttributeDialog.triggered.connect(lambda: self.openAttributeDialog(layer))
                menu.addAction(actionOpenAttributeDialog)

                current_symbol_props = layer.renderer().symbol().symbolLayer(0).properties()
                if 'border_width_map_unit_scale' in current_symbol_props.keys():  # 面矢量
                    actionChangeDialog = QAction('符号渲染', menu)
                    actionChangeDialog.triggered.connect(lambda: self.changeRenderDialog(layer))
                    menu.addAction(actionChangeDialog)
                else:pass
            else:
                # 栅格图层
                pass
        else:
            print('node type is none')

        return menu

    def changeRenderDialog(self, layer):
        dialog = Ui_Dialog_RenderPolygonDialog(self.mapCanvas, layer, parent=self.mapCanvas.parent())
        dialog.exec_()
        pass


    def openAttributeDialog(self, layer):
        self.attributeDialog = AttributeDialog(self.mapCanvas, parent=self.mapCanvas.parent())
        self.attributeDialog.openAttributeDialog(layer)
        self.attributeDialog.show()

    def removeLayer(self):
        layer = self.layerTreeView.currentLayer()
        root = QgsProject.instance().layerTreeRoot()
        root.removeLayer(layer)


