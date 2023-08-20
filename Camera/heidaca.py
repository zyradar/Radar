'''import sys, os

__presentDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.insert(0, __presentDir)
import cv2
import time
import yaml

from threading import Thread
from cameraAPI import *
from Record.record import *


class Camera(Thread):
    def __init__(self):
        Thread.__init__(self, name="Camera")

        self.__frame = None
        self.__isLoop = False
        self.__streamSource = None
        # self.__printFps=True
        self.__printFps = True
        self.__exposureTime = 16000.0
        self.__gainRaw = 1.4
        self.__gamma = 0.6

        self.__openCamera()
        self.__recorder = Recorder()

    def run(self):
        print("[INFO]::Thread-Camera running")
        self.__process()

    # --------------------------------------------------------
    # 主体
    def __process(self):
        countFps = 0
        streamSource = self.__streamSource
        frame = pointer(GENICAM_Frame())

        while self.__isLoop:
            # 主动取图
            # get one frame
            if countFps == 0:
                fpsStart = time.time()
            countFps += 1

            nRet = streamSource.contents.getFrame(streamSource, byref(frame), c_uint(1000))
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
                self.__recorder.saveOne(self.__frame)
                self.__frame = numpy.array(colorByteArray).reshape(imageParams.height, imageParams.width, 3)
                # print(self.__frame.dtype)
            # --- end if ---

            # cv2.imshow('myWindow', self.__frame)
            # cv2.waitKey(1)
            gc.collect()
            time.sleep(0.01)

            if self.__printFps and countFps == 100:
                fpsEnd = time.time()
                print("ID:{:} FPS:{:<4.2f}".format(id(self.__frame), countFps / (fpsEnd - fpsStart)))
                countFps = 0

        # --- end while ---

    # --------------------------------------------------------
    # 外部API
    def getFrame(self):
        return self.__frame

    def stop(self):
        self.__recorder.release()
        self.__isLoop = False
        print("[INFO]::Thread-Camera stopped")

    def increaseExposure(self):
        self.__exposureTime += 1000
        setExposureTime(self.__camera, self.__exposureTime)
        print('[INFO]::ExposureTime:', self.__exposureTime)

    def decreaseExposure(self):
        if self.__exposureTime - 1000 < 1:
            return
        self.__exposureTime -= 1000
        setExposureTime(self.__camera, self.__exposureTime)
        print('[INFO]::ExposureTime:', self.__exposureTime)

    def increaseGainRaw(self):
        self.__gainRaw += .1
        setGainRaw(self.__camera, self.__streamSource, self.__gainRaw)
        print('[INFO]::GainRaw:', self.__gainRaw)

    def decreaseGainRaw(self):
        if self.__gainRaw - .1 < 1:
            return
        self.__gainRaw -= .1
        setGainRaw(self.__camera, self.__streamSource, self.__gainRaw)
        print('[INFO]::GainRaw:', self.__gainRaw)

    def increaseGamma(self):
        self.__gamma += .1
        setGamma(self.__camera, self.__streamSource, self.__gamma)
        print('[INFO]::Gamma:', self.__gamma)

    def decreaseGamma(self):
        if self.__gamma - .1 < 0:
            return
        self.__gamma -= .1
        setGamma(self.__camera, self.__streamSource, self.__gamma)
        print('[INFO]::Gamma:', self.__gamma)

    def saveParas(self):
        pass

    # --------------------------------------------------------
    # 内部API
    def __openCamera(self):
        # 发现相机
        # enumerate camera
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return -1

        # 显示相机信息
        # print camera info
        for index in range(0, cameraCnt):
            camera = cameraList[index]
            print("\nCamera Id = " + str(index))
            print("Key           = " + str(camera.getKey(camera)))
            print("vendor name   = " + str(camera.getVendorName(camera)))
            print("Model  name   = " + str(camera.getModelName(camera)))
            print("Serial number = " + str(camera.getSerialNumber(camera)))

        camera = cameraList[0]

        # 打开相机
        # open camera
        nRet = openCamera(camera)
        if (nRet != 0):
            print("openCamera fail.")
            return -1

        # 创建流对象
        # create stream source object
        streamSourceInfo = GENICAM_StreamSourceInfo()
        streamSourceInfo.channelId = 0
        streamSourceInfo.pCamera = pointer(camera)

        streamSource = pointer(GENICAM_StreamSource())
        self.__streamSource = streamSource
        self.__camera = camera
        nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
        if (nRet != 0):
            print("create StreamSource fail!")
            return -1
        # 自定义设置
        # --------1920-1920
        setROI(camera, 0, 1200 - 768, 1920, 768)
        # setTriggetModeOff(camera,streamSource)
        setExposureTime(camera, self.__exposureTime)
        autoBalanceWhite(camera, streamSource)
        # autoExposure(camera,streamSource)
        setGainRaw(camera, streamSource, self.__gainRaw)
        # setGamma(camera,streamSource,0.7)

        # 开始拉流
        # start grabbing
        nRet = streamSource.contents.startGrabbing(streamSource, c_ulonglong(0),
                                                   c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
        if (nRet != 0):
            print("startGrabbing fail!")
            # 释放相关资源
            # release stream source object before return
            streamSource.contents.release(streamSource)
            return -1
        self.__isLoop = True


if __name__ == "__main__":
    x = Camera()
    x.start()
    time.sleep(1000)
    x.stop()
    x.join()1'''