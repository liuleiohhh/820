import os

from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox,QLabel
from qgis.PyQt.QtGui import QPixmap
from qgis.core import QgsRasterLayer,QgsProject
from qgis.gui import QgsMapCanvas
from ui.cut_ui import Ui_cut
from ui.detection_ui import Ui_TargetDet
from ui.stretch_ui import Ui_ImgStretch
from ui.v2r_ui import Ui_Vector2Raster
from ui.R2V_ui import Ui_Raster2Vector
from ui.DialogClassify import Ui_DialogClassify
from ui.datasetaug_ui import Ui_DataSetAug
from ui.proj_ui import Ui_ProjDef
from ui.yolotrans_ui import Ui_YOLOTRANS
from ui.datasetdivide import Ui_DatasstDvide
# 调用核心函数
from funcations import *


# 地理处理-分割栅格
class CutDialog(QDialog, Ui_cut):
    def __init__(self, parent=None):
        super(CutDialog, self).__init__(parent)
        self.setupUi(self)
        self.openButton.clicked.connect(self.chooseImg)
        self.saveButton.clicked.connect(self.saveImg)
        self.okButton.clicked.connect(self.main)
        self.cancelButton.clicked.connect(self.cancel)

    def actionGeotiffTriggered(self):
        """加载geotiff"""
        data_file, ext = QFileDialog.getOpenFileName(self, '打开', '', '*.tif')
        if data_file:
            layer = QgsRasterLayer(data_file, os.path.basename(data_file))
            self.addLayer(layer)

    def chooseImg(self):
        input_file = QFileDialog.getOpenFileName(self, '选择影像', '*.tif')
        self.lineEdit_openpath.setText(input_file[0])

    def saveImg(self):
        save_path = QFileDialog.getExistingDirectory(self, '选择保存路径', '所有(*.*)')
        self.lineEdit_savepath.setText(save_path)

    def main(self):
        w = int(self.lineEdit_w.text())
        h = int(self.lineEdit_h.text())
        path1 = self.lineEdit_openpath.text()
        path2 = self.lineEdit_savepath.text()
        print(w, h, path1, path2)
        fun = CutImgFun(path1, path2)
        fun.main(w, h)
        finishmessagebox = QMessageBox()
        finishmessagebox.information(self, '提示！', '裁剪完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 深度学习-目标检测
class DetectionDialog(QDialog, Ui_TargetDet):
    def __init__(self, parent=None):
        super(DetectionDialog, self).__init__(parent)
        self.setupUi(self)
        self.input_Button.clicked.connect(self.chooseImg)
        self.output_Button.clicked.connect(self.saveImg)
        self.pthButton.clicked.connect(self.choosePth)
        self.okButton.clicked.connect(self.main)
        self.cancelButton.clicked.connect(self.cancel)


    def chooseImg(self):
        self.input_file = QFileDialog.getOpenFileName(self, '选择文件', '*.tif')
        self.lineEdit_inputpath.setText(self.input_file[0])

    def choosePth(self):
        self.pthfile = QFileDialog.getOpenFileName(self, '选择权重文件', '*.pth')
        self.lineEdit_pthpath.setText(self.pthfile[0])

    def saveImg(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, '选择输出文件夹', '所有(*.*)')
        self.lineEdit_outputpath.setText(self.save_dir)

    def main(self):
        fun = DetectionFun(self.input_file[0], self.save_dir)
        fun.main(self.pthfile[0])
        messagebox = QMessageBox()
        messagebox.information(self, '提示', '预测完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 数据增强-拉伸
class StretchDialog(QDialog, Ui_ImgStretch):
    # 初始化设置-----
    def __init__(self, parent=None):
        super(StretchDialog, self).__init__(parent)
        self.setupUi(self)
        self.input_Button.clicked.connect(self.chooseImg)
        self.output_Button.clicked.connect(self.chooseDir)
        self.ensure_pushButton.clicked.connect(self.main)
        self.cancel_pushButton.clicked.connect(self.cancel)

    def chooseImg(self):
        self.input_file = QFileDialog.getOpenFileName(self, '选择文件', '*.tif')
        self.lineEdit_input.setText(self.input_file[0])

    def chooseDir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, '选择输出文件夹', '所有(*.*)')
        self.lineEdit_savedir.setText(self.output_dir)

    def main(self):
        # 调用拉伸函数
        fun = TruncatedStretchFun(self.input_file[0], self.output_dir, self.lineEdit_saveName.text())
        fun.writeTiff()
        messagebox = QMessageBox.information(self, '提示', '完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 地物分类
class ClassifyDialog(QDialog, Ui_DialogClassify):
    def __init__(self, parent=None):
        super(ClassifyDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_inputImg.clicked.connect(self.chooseFile)
        self.pushButton_outputDir.clicked.connect(self.chooseDir)
        self.pushButtonOK.clicked.connect(self.main)
        self.pushButtonCancel.clicked.connect(self.cancel)

    def chooseFile(self):
        self.input_file = QFileDialog.getOpenFileName(self, '打开文件', '*.tif')
        self.lineEdit_inputImg.setText(self.input_file[0])

    def chooseDir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, '选择文件夹', '所有(*.*)')
        self.lineEdit_outputDir.setText(self.output_dir)

    def main(self):
        seg = Segmentation(self.input_file[0],self.output_dir)
        dst_path,pie_path = seg.main()
        self.out_file_path = dst_path
        self.pie_file_path = pie_path

        QMessageBox.information(self, "提示", '完成', QMessageBox.Ok)
        self.close()
        # dialog = QDialog()
        # dialog.resize(640, 480)
        # dialog.setWindowTitle('地物类别统计')
        # pic = QPixmap(pie_path)
        # label_pic = QLabel('show', dialog)
        # label_pic.setPixmap(pic)
        # label_pic.setGeometry(0, 0, 640, 480)
        # dialog.exec_()

    def cancel(self):
        self.close()


# 数据转换-矢量转栅格
class V2RDialog(QDialog, Ui_Vector2Raster):
    def __init__(self, parent=None):
        super(V2RDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_vector.clicked.connect(self.chooseVet)
        self.pushButton_tempfile.clicked.connect(self.chooseTemp)
        self.pushButton_raster.clicked.connect(self.chooseDir)
        self.pushButton_ok.clicked.connect(self.main)
        self.pushButton_cancel.clicked.connect(self.cancel)

    def chooseVet(self):
        self.input_file = QFileDialog.getOpenFileName(self, '打开文件', '*.shp')
        self.lineEdit_vector.setText(self.input_file[0])

    def chooseTemp(self):
        self.tempFile = QFileDialog.getOpenFileName(self, '打开文件', '*.tif')
        self.lineEdit_tempfile.setText(self.tempFile[0])

    def chooseDir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, '选择文件夹', '所有(*.*)')
        self.lineEdit_outdir.setText(self.output_dir)

    def main(self):
        raster_path = os.path.join(self.output_dir, self.lineEdit_outname.text())
        PolyToRaster(self.input_file[0], raster_path, self.tempFile[0])
        QMessageBox.information(self, "提示", '完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 数据转换--栅格转矢量
class R2VDialog(QDialog,Ui_Raster2Vector):
    def __init__(self,parent=None):
        super(R2VDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_ok.clicked.connect(self.main)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_raster.clicked.connect(self.chooseFile)
        self.pushButton_outputDir.clicked.connect(self.chooseDir)

    def chooseFile(self):
        self.raster_path = QFileDialog.getOpenFileName(self,'选择文件','*.tif')
        self.lineEdit_raster.setText(self.raster_path[0])

    def chooseDir(self):
        self.outDir = QFileDialog.getExistingDirectory(self,"选择文件夹",'所有(*.*)')
        self.lineEdit_outputDir.setText(self.outDir)

    def main(self):
        out_shp = os.path.join(self.outDir,self.lineEdit_outputName.text())
        print(out_shp)
        raster2poly(self.raster_path[0],out_shp)
        QMessageBox.information(self, '提示', '完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 数据集增广
class DataSetAugDialog(QDialog, Ui_DataSetAug):
    def __init__(self, parent=None):
        super(DataSetAugDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButtonOK.clicked.connect(self.main)
        self.pushButtonInput.clicked.connect(self.choosedata)
        self.pushButton_outputDir.clicked.connect(self.chooseDir)
        self.pushButtonCancel.clicked.connect(self.cancel)

    def choosedata(self):
        self.input_dir = QFileDialog.getExistingDirectory(self, '选择文件夹', '所有(*.*)')
        self.lineEditinputDataset.setText(self.input_dir)

    def chooseDir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, '选择文件夹', '所有(*.*)')
        self.lineEditOutputDir.setText(self.output_dir)

    def main(self):
        a = self.checkBox.isChecked()
        b = self.checkBox_2.isChecked()
        c = self.checkBox_3.isChecked()
        DatasetAug(self.input_dir, self.output_dir, a, b, c)
        QMessageBox.information(self, '提示', '完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# 定义投影
class ProjDefineDialog(QDialog, Ui_ProjDef):
    def __init__(self, parent=None):
        super(ProjDefineDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_NOXY.clicked.connect(self.chooseN)
        self.pushButton_HaveXY.clicked.connect(self.chooseH)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(self.main)
    def chooseH(self):
        self.imgHave = QFileDialog.getOpenFileName(self, '选择文件', '*.tif')
        self.lineEdit_have.setText(self.imgHave[0])
    #
    def chooseN(self):
        self.imgNo = QFileDialog.getOpenFileName(self, '选择文件', '*.tif')
        self.lineEdit_no.setText(self.imgNo[0])
    #
    def main(self):
        assign_spatial_reference_byfile(self.imgHave[0], self.imgNo[0])
        QMessageBox.information(self, "提示", '完成', QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()


# YOLO数据格式转换
class YoloTransDialog(QDialog,Ui_YOLOTRANS):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButtoninput.clicked.connect(self.chooseinDir)
        self.pushButton_outDir.clicked.connect(self.chooseoutDir)
        self.pushButton_ok.clicked.connect(self.main)
        self.pushButton_cancel.clicked.connect(self.cancel)

    def chooseinDir(self):
        self.in_dir = QFileDialog.getExistingDirectory(self,'选择文件所在位置','所有(*.*)')
        self.lineEditinDIR.setText(self.in_dir)

    def chooseoutDir(self):
        self.out_dir = QFileDialog.getExistingDirectory(self,'选择文件保存位置','所有(*.*)')
        self.lineEdit_outDir.setText(self.out_dir)

    def main(self):
        TansFun(self.in_dir,self.out_dir)
        QMessageBox.information(self,'提示','完成',QMessageBox.Ok)
        self.close()
    def cancel(self):
        self.close()


# 数据集划分
class DataSetDivideDialog(QDialog,Ui_DatasstDvide):
    def __init__(self,parent=None):
        super(DataSetDivideDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_input.clicked.connect(self.chooseDir)
        self.pushButton_save.clicked.connect(self.chooseoutDir)
        self.pushButton_ok.clicked.connect(self.main)
        self.pushButton_cancel.clicked.connect(self.cancel)

    def chooseDir(self):
        self.in_dir = QFileDialog.getExistingDirectory(self, '选择文件所在位置', '所有(*.*)')
        self.lineEdit_inputDIR.setText(self.in_dir)

    def chooseoutDir(self):
        self.outDir = QFileDialog.getExistingDirectory(self,'选择文件所在位置', '所有(*.*)')
        self.lineEdit_save.setText(self.outDir)

    def main(self):

        DatasetDivideFun(int(self.lineEdit_train.text()),int(self.lineEdit_test.text()),self.in_dir,self.outDir)
        QMessageBox.information(self,'提示','完成',QMessageBox.Ok)
        self.close()

    def cancel(self):
        self.close()




    
        


