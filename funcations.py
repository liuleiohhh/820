from PIL import Image
import shutil
import os
import glob
import numpy as np
import cv2
from tqdm import tqdm
from funs.funcation import *
import time
from YOLOV4.yolo import YOLO
from DeepLab.deeplab import DeeplabV3
from collections import Counter
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

try:
    from osgeo import gdal, gdalconst, osr, ogr
except:
    import gdal
    import osr
    import gdalconst
    import ogr
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题
plt.rcParams['axes.unicode_minus'] = False


def assign_spatial_reference_byfile(src_path, dst_path):
    """
    :param src_path: 有地理坐标系影像路径
    :param dst_path: 无地理坐标系影像路径
    :return: 粘贴坐标
    """
    src_ds = gdal.Open(src_path, gdal.GA_ReadOnly)
    sr = osr.SpatialReference()
    sr.ImportFromWkt(src_ds.GetProjectionRef())
    geoTransform = src_ds.GetGeoTransform()
    dst_ds = gdal.Open(dst_path, gdal.GA_Update)
    dst_ds.SetProjection(sr.ExportToWkt())
    dst_ds.SetGeoTransform(geoTransform)
    dst_ds = None
    src_ds = None


def raster2poly(raster, outshp):
    """
    :param raster:
    :param outshp:
    :return: #### 输出矢量出现锯齿毛刺
    """
    inraster = gdal.Open(raster)  # 读取路径中的栅格数据
    inband = inraster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1
    prj = osr.SpatialReference()
    prj.ImportFromWkt(inraster.GetProjection())  # 读取栅格数据的投影信息，用来为后面生成的矢量做准备

    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outshp):  # 若文件已经存在，则删除它继续重新做一遍
        drv.DeleteDataSource(outshp)
    Polygon = drv.CreateDataSource(outshp)  # 创建一个目标文件
    Poly_layer = Polygon.CreateLayer(raster[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
    newField = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
    Poly_layer.CreateField(newField)

    gdal.FPolygonize(inband, None, Poly_layer, 0)  # 核心函数，执行的就是栅格转矢量操作
    Polygon.SyncToDisk()
    simplify(outshp, outshp.replace('.', '_simplify.'))
    Polygon = None
    os.remove(outshp)
    os.remove(outshp.replace('shp', 'dbf'))
    os.remove(outshp.replace('shp', 'prj'))
    os.remove(outshp.replace('shp', 'shx'))


def PolyToRaster(input_file, output_file, templete_file):
    """
    矢量数据转为栅格数据
    :param input_file: 输入矢量图路径
    :param output_file: 输出栅格数据路径文件名
    :param templete_file: 对应参考影像（提供空间参考信息）
    :return: 栅格数据
    """
    # 参数说明： 输出的栅格数据，注意该数据必须以update模式打开、指定要更新的波段个数(更新123波段)、指定的图层、几何图形坐标转换图像行列号函数、几何图形坐标转换图像行列号参数、以及图层中属性字段属性值
    data = gdal.Open(templete_file, gdalconst.GA_ReadOnly)
    x_res = data.RasterXSize
    y_res = data.RasterYSize
    vector = ogr.Open(input_file)
    layer = vector.GetLayer()
    targetDataSet = gdal.GetDriverByName('GTiff').Create(output_file, x_res, y_res, 3, gdal.GDT_Byte)
    # targetDataSet=gdal.GetDriverByName('GTiff').CreateCopy(templetefile,data)
    targetDataSet.SetGeoTransform(data.GetGeoTransform())
    targetDataSet.SetProjection(data.GetProjection())
    band = targetDataSet.GetRasterBand(1)
    NoData_value = -999
    band.SetNoDataValue(NoData_value)
    # 缓存写入磁盘
    band.FlushCache()
    gdal.RasterizeLayer(targetDataSet, [1, 2, 3], layer, options=["ATTRIBUTE=VALUE"])  # 删除options?
    return targetDataSet


# 地理处理-分割栅格
class CutImgFun:
    def __init__(self, input_path, output_dir):
        image = cv2.imread(input_path)
        basename = os.path.basename(input_path)
        input_dir = os.path.splitext(input_path)[0]  # 输入文件路径（无后缀）
        self.input_path = input_path
        self.input_dir = input_dir
        self.output_dir = output_dir  # 输出文件夹名
        self.image = image
        self.h = image.shape[0]  # rows
        self.w = image.shape[1]  # cols
        self.basename = basename
        print('影像大小为:{}X{}'.format(self.h, self.w))

    def main(self, w, h):
        s_time = time.time()

        # clip detect at same time
        num_of_rows = int(self.h / h)
        num_of_cols = int(self.w / w)

        for i in tqdm(range(num_of_cols)):
            for j in range(num_of_rows):
                clip_image = self.image[j * 512:(j + 1) * 512, i * 512:(i + 1) * 512, :]
                cv2.imwrite(self.output_dir + '/' + str(j) + '_' + str(i) + '.png',
                            clip_image)


# 深度学习-目标检测
class DetectionFun:
    def __init__(self, input_path, output_dir):
        image = cv2.imread(input_path)
        basename = os.path.basename(input_path)
        input_dir = os.path.splitext(input_path)[0]  # 输入文件路径（无后缀）
        self.input_path = input_path
        self.input_dir = input_dir
        self.output_dir = output_dir  # 输出文件夹名
        self.image = image
        self.h = image.shape[0]  # rows
        self.w = image.shape[1]  # cols
        self.basename = basename
        print('影像大小为:{}X{}'.format(self.h, self.w))

    def main(self, log_path):
        s_time = time.time()
        yolo = YOLO(log_path)
        dir1 = self.input_dir + '-detect'
        dir2 = self.output_dir + '/pre_TIF'
        dir3 = self.output_dir + '/pre_SHP'
        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            os.makedirs(dir3)
        # clip detect at same time
        num_of_rows = int(self.h / 1024)
        num_of_cols = int(self.w / 1024)

        for i in tqdm(range(num_of_cols)):
            for j in range(num_of_rows):
                temp_image = cv2.cvtColor(self.image[j * 1024:(j + 1) * 1024, i * 1024:(i + 1) * 1024, :],
                                          cv2.COLOR_BGR2RGB)
                temp_image = Image.fromarray(temp_image)
                det_image = yolo.detect_image(temp_image)
                cv2.imwrite(dir1 + '/' + '_' + str(j) + '_' + str(i) + '.png',
                            det_image)
        # merge
        file_list = glob.glob(os.path.join(dir1, '*.png'))
        dst = np.zeros_like(self.image)
        for i in range(len(file_list)):
            img = cv2.imread(file_list[i], -1)

            rows_th = int(file_list[i].split('_')[-2])
            cols_th = int(file_list[i].split('_')[-1].split('.')[0])
            dst[rows_th * 1024:(rows_th + 1) * 1024, cols_th * 1024:(cols_th + 1) * 1024, :] = img
        # save predict image
        dst_path = os.path.join(dir2, self.basename)
        shp_path = os.path.join(dir3, self.basename.split('.')[0] + '.shp')
        cv2.imwrite(dst_path, dst)
        # delete clip dir  (-detect)
        os.system('rd/s/q {}'.format(dir1.replace('/', '\\')))

        assign_spatial_reference_byfile(self.input_path, dst_path)
        raster2poly(dst_path, shp_path)
        e_time = time.time()
        print('完成...目标检测用时{}分钟'.format(int((e_time - s_time) / 60)))


# 地物分类
class Segmentation:
    def __init__(self, input_path, output_dir):
        image = cv2.imread(input_path)
        basename = os.path.basename(input_path)
        input_dir = os.path.splitext(input_path)[0]  # 输入文件路径（无后缀）
        self.input_path = input_path
        self.input_dir = input_dir
        self.output_dir = output_dir  # 输出文件夹名
        self.image = image
        self.h = image.shape[0]  # rows
        self.w = image.shape[1]  # cols
        self.basename = basename
        print('影像大小为:{}X{}'.format(self.h, self.w))

    def main(self):
        s_time = time.time()
        deeplab = DeeplabV3()
        dir1 = self.input_dir + '-detect'
        dir2 = self.output_dir + '/pre_TIF'
        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)
        # clip detect at same time
        num_of_rows = int(self.h / 1024)
        num_of_cols = int(self.w / 1024)

        for i in tqdm(range(num_of_cols)):
            for j in range(num_of_rows):
                temp_image = cv2.cvtColor(self.image[j * 1024:(j + 1) * 1024, i * 1024:(i + 1) * 1024, :],
                                          cv2.COLOR_BGR2RGB)
                temp_image = Image.fromarray(temp_image)
                det_image = deeplab.detect_image(temp_image)
                cv2.imwrite(dir1 + '/' + '_' + str(j) + '_' + str(i) + '.png',
                            det_image)
        # merge
        file_list = glob.glob(os.path.join(dir1, '*.png'))
        dst = np.zeros_like(self.image)
        for i in range(len(file_list)):
            img = cv2.imread(file_list[i], -1)

            rows_th = int(file_list[i].split('_')[-2])
            cols_th = int(file_list[i].split('_')[-1].split('.')[0])
            dst[rows_th * 1024:(rows_th + 1) * 1024, cols_th * 1024:(cols_th + 1) * 1024, :] = img
        # save predict image
        dst_path = os.path.join(dir2, self.basename)
        cv2.imwrite(dst_path, dst)
        # delete clip dir  (-detect)
        os.system('rd/s/q {}'.format(dir1.replace('/', '\\')))
        assign_spatial_reference_byfile(self.input_path, dst_path)

        # 统计类别
        color = [[0, 0, 0], [255, 255, 0], [61, 89, 171], [0, 255, 0], [227, 207, 87], [0, 0, 255], [255, 255, 255],
                 [112, 128, 105], [160, 32, 240], [255, 0, 255], [255, 0, 0]]
        color = np.array(color)
        count_list = np.zeros([11, 1])
        img = cv2.imread(dst_path)
        for i in range(len(color)):
            location = np.all((img == color[i]), axis=2)
            count = Counter(location.flatten())
            count_list[i] = count[True]

        filly = count_list / np.sum(count_list)
        label = ['Nodata', '汽车', '停车场', '植被', '裸地', '水体', '道路', '广场', '操场', '彩钢瓦建筑', '建筑']
        plt.axes(aspect=1)
        plt.pie(x=filly[:, 0], labels=label, autopct='%3.1f%%')
        plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1))
        plt.title('地物类别分布图', fontsize=20)
        pie_save_path = os.path.join(dir2, 'pie.png')
        plt.savefig(pie_save_path)
        return dst_path, pie_save_path

        e_time = time.time()
        print('完成...分类用时{}分钟'.format(int((e_time - s_time) / 60)))


# 数据增强-百分比截断拉伸
class TruncatedStretchFun:
    def __init__(self, raster_path, save_dir, save_name):
        print('正在获取数据....')
        dataset = gdal.Open(raster_path)
        if dataset is None:
            print(raster_path + '文件无法打开')
        # 获取影像宽高/波段数
        self.width = dataset.RasterXSize
        self.height = dataset.RasterYSize
        self.bands = dataset.RasterCount
        # 获取数据
        self.data = dataset.ReadAsArray(0, 0, self.width, self.height)
        self.geotrans = dataset.GetGeoTransform()
        self.proj = dataset.GetProjection()
        self.save_path = os.path.join(save_dir, save_name)
        print(self.save_path)

    def stretch(self):
        print('拉伸计算...')

        def gray_process(gray):
            # 获取百分比分位数
            truncated_up = np.percentile(gray, 98)
            truncated_down = np.percentile(gray, 2)
            # 拉伸
            gray = (gray - truncated_down) / (truncated_up - truncated_down) * 255
            # 截断
            gray[gray > 255] = 255
            gray[gray < 0] = 0
            gray = np.uint8(gray)
            return gray

        # 处理多波段
        if self.data.shape[0] == 3:
            image_stretch = []
            for i in range(self.data.shape[0]):
                gray = gray_process(self.data[i])
                image_stretch.append(gray)
            image_stretch = np.array(image_stretch)
        else:
            image_stretch = gray_process(self.data)
        return image_stretch

    def writeTiff(self):
        image_stretch = self.stretch()
        if 'int8' in image_stretch.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in image_stretch.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32
        # 保存影像
        driver = gdal.GetDriverByName('GTiff')
        targetDataset = driver.Create(self.save_path, self.width, self.height, self.bands, datatype)

        targetDataset.SetGeoTransform(self.geotrans)
        targetDataset.SetProjection(self.proj)
        for i in range(image_stretch.shape[0]):
            targetDataset.GetRasterBand(i + 1).WriteArray(image_stretch[i])
        del targetDataset


# 数据集增强
def DatasetAug(input_path, save_path, a, b, c):
    num = 0
    img_path = os.path.join(input_path, '*.jpg')
    img_list = glob.glob(img_path)
    for img in tqdm(img_list):
        image = cv2.imread(img)
        cv2.imwrite(os.path.join(save_path, str(num) + '.png'), image)
        width, height, bands = image.shape
        if a:
            num += 1
            image1 = cv2.flip(image, flipCode=1)
            cv2.imwrite(os.path.join(save_path, str(num) + '.png'), image1)
        if b:
            num += 1
            image2 = cv2.flip(image, flipCode=0)
            cv2.imwrite(os.path.join(save_path, str(num) + '.png'), image2)
        if c:
            num += 1
            # 旋转
            matrotate = cv2.getRotationMatrix2D((width / 2, height / 2), 45, 0.7)
            image3 = cv2.warpAffine(image, matrotate, (width, height))
            cv2.imwrite(os.path.join(save_path, str(num) + '.png'), image3)

        num += 1


# YOLO数据格式转换
def TansFun(input_Dir, output_Dir):
    sets = [('2007', 'train'), ('2007', 'val'), ('2007', 'test')]

    classes = ['playground']

    image_root = os.path.join(input_Dir, 'Annotations/%s.xml')

    def convert_annotation(image_id, list_file):
        in_file = open(image_root % image_id, encoding='utf-8')
        tree = ET.parse(in_file)
        root = tree.getroot()

        for obj in root.iter('object'):
            difficult = 0
            if obj.find('difficult') != None:
                difficult = obj.find('difficult').text

            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (int(xmlbox.find('xmin').text), int(xmlbox.find('ymin').text), int(xmlbox.find('xmax').text),
                 int(xmlbox.find('ymax').text))
            list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))

    save_root = os.path.join(output_Dir, '%s_%s.txt')
    write_root = os.path.join(input_Dir, 'JPEGImages/%s.png')
    main_root = os.path.join(input_Dir, 'ImageSets/Main/%s.txt')
    for year, image_set in sets:
        image_ids = open(main_root % image_set).read().strip().split()
        list_file = open(save_root % (year, image_set), 'w')
        for image_id in image_ids:
            list_file.write(write_root % image_id)
            convert_annotation(image_id, list_file)
            list_file.write('\n')
        list_file.close()


# 数据集划分
def DatasetDivideFun(arg1, arg2, input_Dir, output_Dir):
    train_Annotations = os.path.join(output_Dir, 'train/Annotations')
    test_Annotations = os.path.join(output_Dir, 'test/Annotations')
    train_JPEG = os.path.join(output_Dir, 'train/JPEGImages')
    test_JPEG = os.path.join(output_Dir, 'test/JPEGImages')
    if not os.path.exists(train_Annotations):
        os.makedirs(train_Annotations)
        os.makedirs(train_JPEG)
        os.makedirs(test_Annotations)
        os.makedirs(test_JPEG)
    xml_list = glob.glob(os.path.join(input_Dir, 'Annotations/*.xml'))
    jpg_list = glob.glob(os.path.join(input_Dir, 'JPEGImages/*.png'))
    tatal = len(xml_list)
    train_num = int(tatal * arg1 / (arg1 + arg2))
    test_num = (tatal * arg2 / (arg1 + arg2))
    for i in range(tatal):
        xml_path = xml_list[i]
        jpg_path = jpg_list[i]
        if i < train_num:

            train_xml_path = os.path.join(train_Annotations, str(i) + '.xml')
            train_jpg_path = os.path.join(train_JPEG, str(i) + '.png')

            shutil.copy(xml_path, train_xml_path)
            shutil.copy(jpg_path, train_jpg_path)
        else:
            test_xml_path = os.path.join(test_Annotations, str(i) + '.xml')
            test_jpg_path = os.path.join(test_JPEG, str(i) + '.png')
            shutil.copy(xml_path, test_xml_path)
            shutil.copy(jpg_path, test_jpg_path)


if __name__ == '__main__':
    a = r'O:\pycharm_project\parking_detection\input_data\tile_128.TIF'
    b = r'O:\pycharm_project\parking_detection\input_data'
    c = 'tst.TIF '
    fun = TruncatedStretchFun(a, b, c)
    fun.writeTiff()
