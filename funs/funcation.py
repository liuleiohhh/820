try:
    from osgeo import gdal,gdalconst,osr,ogr
except:
    import gdal
    import osr
    import gdalconst
    import ogr
import os
from shapely import geometry as geos
from shapely import wkt


def getSRSPair(dataset):
    """
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    """
    gdal.AllRegister()
    dataset = gdal.Open(dataset)
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs


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
    os.remove(outshp.replace('shp','dbf'))
    os.remove(outshp.replace('shp','prj'))
    os.remove(outshp.replace('shp','shx'))


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




def CutRsImage():
    # 读取要切的原图
    in_ds = gdal.Open("data/2.tif")
    print("open tif file succeed")

    # 读取原图中的每个波段
    in_band1 = in_ds.GetRasterBand(1)
    in_band2 = in_ds.GetRasterBand(2)
    in_band3 = in_ds.GetRasterBand(3)

    # 定义切图的起始点坐标(相比原点的横坐标和纵坐标偏移量)
    offset_x = 0
    offset_y = 0

    # 定义切图的大小（矩形框）
    block_xsize = 512  # 行
    block_ysize = 512  # 列

    # 从每个波段中切需要的矩形框内的数据(注意读取的矩形框不能超过原图大小)
    out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
    out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

    # 获取Tif的驱动，为创建切出来的图文件做准备
    gtif_driver = gdal.GetDriverByName("GTiff")

    # 创建切出来的要存的文件（3代表3个波段，最后一个参数为数据类型，跟原文件一致）
    out_ds = gtif_driver.Create('clip.tif', block_xsize, block_ysize, 3, in_band1.DataType)
    print("create new tif file succeed")

    # 获取原图的原点坐标信息
    ori_transform = in_ds.GetGeoTransform()
    if ori_transform:
        print(ori_transform)
        print("Origin = ({}, {})".format(ori_transform[0], ori_transform[3]))  # 左上角位置
        print("Pixel Size = ({}, {})".format(ori_transform[1], ori_transform[5]))  # 像元宽度（东西方向分辨率）、像元高度（南北方向分辨率）

    # 读取原图仿射变换参数值
    top_left_x = ori_transform[0]  # 左上角x坐标
    w_e_pixel_resolution = ori_transform[1]  # 东西方向像素分辨率
    top_left_y = ori_transform[3]  # 左上角y坐标
    n_s_pixel_resolution = ori_transform[5]  # 南北方向像素分辨率

    # 根据反射变换参数计算新图的原点坐标
    top_left_x = top_left_x + offset_x * w_e_pixel_resolution
    top_left_y = top_left_y + offset_y * n_s_pixel_resolution

    # 将计算后的值组装为一个元组，以方便设置
    dst_transform = (top_left_x, ori_transform[1], ori_transform[2], top_left_y, ori_transform[4], ori_transform[5])

    # 设置裁剪出来图的原点坐标
    out_ds.SetGeoTransform(dst_transform)

    # 设置SRS属性（投影信息）
    out_ds.SetProjection(in_ds.GetProjection())

    # 写入目标文件
    out_ds.GetRasterBand(1).WriteArray(out_band1)
    out_ds.GetRasterBand(2).WriteArray(out_band2)
    out_ds.GetRasterBand(3).WriteArray(out_band3)

    # 将缓存写入磁盘
    out_ds.FlushCache()
    print("FlushCache succeed")

    # 计算统计值
    # for i in range(1, 3):
    #     out_ds.GetRasterBand(i).ComputeStatistics(False)
    # print("ComputeStatistics succeed")

    del out_ds

    print("End!")


def simplify(in_shp, out_shp):
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    # 支持中文编码
    gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    # 注册所有的驱动
    ogr.RegisterAll()

    # 读取shpfile、图层、要素个数
    in_ds = ogr.Open(in_shp)
    in_lyr = in_ds.GetLayer(0)
    feature_conut = in_lyr.GetFeatureCount()

    # 创建输出矢量文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(out_shp):
        driver.DeleteDataSource(out_shp)
    out_ds = driver.CreateDataSource(out_shp)
    out_lyr = out_ds.CreateLayer(out_shp,in_lyr.GetSpatialRef(), ogr.wkbPolygon)
    defn = out_lyr.GetLayerDefn()
    field_name = ogr.FieldDefn('building', ogr.OFTInteger)    # 创建字段、整形
    out_lyr.CreateField(field_name)

    # 面简化
    for i in range(feature_conut):
        feature = in_lyr.GetNextFeature()   # <class 'osgeo.ogr.Feature'>
        gemo = str(feature.GetGeometryRef())
        value = feature.GetField('value')

        if value == 0:
            continue
        # 获取简华面geometry
        polygon = wkt.loads(gemo)
        polygon = polygon.simplify(1e-5)    # <class 'shapely.geometry.polygon.Polygon'>
        geometry = ogr.CreateGeometryFromWkt(str(polygon))   # <class 'osgeo.ogr.Geometry'>

        # new shapefile
        out_feature = ogr.Feature(defn)
        out_feature.SetField('building',value)
        out_feature.SetGeometry(geometry)
        out_lyr.CreateFeature(out_feature)


    out_ds.FlushCache()

    del in_ds
    del out_ds
    # in_ds.Destroy()
    # out_ds.Destroy()


def read(data_path):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSoure = driver.Open(data_path,0) # drive.Open(<filename>,<updata>)updata为0只读，updata为1读写
    layer = dataSoure.GetLayer(0) # 默认为0，不填也为0
    n = layer.GetFeatureCount()
    print(n)



if __name__ == '__main__':
    a = 'change_output/add/tile_128_add_simplify.shp'
    read(data_path=a)


