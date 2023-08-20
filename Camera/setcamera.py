import gc
import cv2
import numpy
from Camera.ImageConvert import *
from Camera.MVSDK import *
import time


# 枚举相机
# enumerate camera
def enumCameras():
    # 获取系统单例
    # get system instance
    system = pointer(GENICAM_System())
    nRet = GENICAM_getSystemInstance(byref(system))
    if (nRet != 0):
        print("getSystemInstance fail!")
        return None, None
    # 发现相机
    # discover camera
    cameraList = pointer(GENICAM_Camera())
    cameraCnt = c_uint()
    nRet = system.contents.discovery(system, byref(cameraList), byref(cameraCnt), c_int(GENICAM_EProtocolType.typeAll));
    if (nRet != 0):
        print("discovery fail!")
        return None, None
    elif cameraCnt.value < 1:
        print("discovery no camera!")
        return None, None
    else:
        print("cameraCnt: " + str(cameraCnt.value))
        return cameraCnt.value, cameraList


# 打开相机
# open camera
def openCamera(camera):
    # 连接相机
    # connect camera
    nRet = camera.connect(camera, c_int(GENICAM_ECameraAccessPermission.accessPermissionControl))
    if (nRet != 0):
        print("camera connect fail!")
        return -1
    else:
        print("camera connect success.")
    return 0


def __process(self):
    cameraCnt, cameraList = enumCameras()
    if cameraCnt is None:
        return -1
    print(cameraCnt)
    camera = []
    # 显示相机信息
    # print camera info
    for index in range(0, cameraCnt):
        camera.append(cameraList[index])
        print("\nCamera Id = " + str(index))
        print("Key           = " + str(camera[index].getKey(camera[index])))
        print("vendor name   = " + str(camera[index].getVendorName(camera[index])))
        print("Model  name   = " + str(camera[index].getModelName(camera[index])))
        print("Serial number = " + str(camera[index].getSerialNumber(camera[index])))
    streamSource = []
    nRet = []
    countFps = 0
    for i in range(0, cameraCnt):
        # camera[i] = cameraList[i]

        # 打开相机
        # open camera
        nRet.append(openCamera(camera[i]))
        if nRet[i] != 0:
            print("openCamera fail.")
            return -1
        streamSource.append(pointer(GENICAM_StreamSource()))
        frame = pointer(GENICAM_Frame())
        nRet = streamSource.contents.getFrame(streamSource[i], byref(frame), c_uint(1000))
        if nRet != 0:
            print("getFrame fail! Timeout:[1000]ms")
            # 释放相关资源
            # release stream source object before return
            streamSource.contents.release(streamSource)
            return -1
        else:
            # print("getFrame success BlockId = [" + str(frame.contents.getBlockId(frame)) + "], get frame time: " + str(datetime.datetime.now()))
            pass

        nRet = frame.contents.valid(frame)
        if nRet != 0:
            print("frame is invalid!")
            # 释放驱动图像缓存资源
            # release frame resource before return
            frame.contents.release(frame)
            # 释放相关资源
            # release stream source object before return
            streamSource.contents.release(streamSource)
            return -1

            # 给转码所需的参数赋值
        # fill conversion parameter
        imageParams = IMGCNV_SOpenParam()
        imageParams.dataSize = frame.contents.getImageSize(frame)
        imageParams.height = frame.contents.getImageHeight(frame)
        imageParams.width = frame.contents.getImageWidth(frame)
        imageParams.paddingX = frame.contents.getImagePaddingX(frame)
        imageParams.paddingY = frame.contents.getImagePaddingY(frame)
        imageParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

        # 将裸数据图像拷出
        # copy image data out from frame
        imageBuff = frame.contents.getImage(frame)
        userBuff = c_buffer(b'\0', imageParams.dataSize)
        memmove(userBuff, c_char_p(imageBuff), imageParams.dataSize)

        # 释放驱动图像缓存
        # release frame resource at the end of use
        frame.contents.release(frame)

        # 如果图像格式是 Mono8 直接使用
        # no format conversion required for Mono8
        if imageParams.pixelForamt == EPixelType.gvspPixelMono8:
            grayByteArray = bytearray(userBuff)
            cvImage = numpy.array(grayByteArray).reshape(imageParams.height, imageParams.width)
        else:
            # 转码 => BGR24
            # convert to BGR24
            rgbSize = c_int()
            rgbBuff = c_buffer(b'\0', imageParams.height * imageParams.width * 3)

            nRet = IMGCNV_ConvertToBGR24(cast(userBuff, c_void_p), \
                                         byref(imageParams), \
                                         cast(rgbBuff, c_void_p), \
                                         byref(rgbSize))

            colorByteArray = bytearray(rgbBuff)
            frame = numpy.array(colorByteArray).reshape(imageParams.height, imageParams.width, 3)
            # print(self.__frame.dtype)
        # --- end if ---

        cv2.imshow('myWindow', frame)
        cv2.waitKey(1)
        gc.collect()
        time.sleep(0.01)


if __name__ == "__main__":
    __process()