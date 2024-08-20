import sys

from qgis.core import (
    edit,
    QgsExpression,
    QgsExpressionContext,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsVectorLayer,
    QgsPointXY,
    QgsGeometry,
    QgsProject,
    QgsExpressionContextUtils
)
import os
import qgis.processing as processing
# os.environ['path']
# print(os.getenv('path'))
sys.path.append(r'D:\QGIS\apps\qgis\python\plugins')
# exp = QgsExpression('1+1')
# print(exp.evaluate())
