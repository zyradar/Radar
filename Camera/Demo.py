#!/usr/bin/env python
# coding: utf-8
'''
Created on 2017-10-25

@author: 
'''
import gc
import cv2
import numpy
from Camera.ImageConvert import *
from Camera.MVSDK import *
import struct
import time
import datetime
from configfile import *

g_cameraStatusUserInfo = b"statusInfo"


# 取流回调函数
# grabbing callback function
def onGetFrame(frame):
    nRet = frame.contents.valid(frame)
    if (nRet != 0):
        print("frame is invalid!")
        # 释放驱动图像缓存资源
        # release frame resource before return
        frame.contents.release(frame)
        return

        # print("BlockId = %d"  %(frame.contents.getBlockId(frame)))
    # 此处客户应用程序应将图像拷贝出使用
    # Here you can copy image data out from frame for your own use
    '''
    '''
    # 释放驱动图像缓存资源
    # release frame resource at the end of use
    frame.contents.release(frame)


# 取流回调函数Ex
# grabbing callback function with userInfo parameter
def onGetFrameEx(frame, userInfo):
    nRet = frame.contents.valid(frame)
    if (nRet != 0):
        print("frame is invalid!")
        # 释放驱动图像缓存资源
        # release frame resource before return
        frame.contents.release(frame)
        return

        # print("BlockId = %d userInfo = %s"  %(frame.contents.getBlockId(frame), c_char_p(userInfo).value))
    # 此处客户应用程序应将图像拷贝出使用
    # Here you should copy image data out from frame for your own use
    '''
    '''
    # 释放驱动图像缓存资源
    # release frame resource at the end of use
    # cv2.imshow("frane", frame)
    frame.contents.release(frame)


# 相机连接状态回调函数
# camera connection status change callback
def deviceLinkNotify(connectArg, linkInfo):
    if (EVType.offLine == connectArg.contents.m_event):
        print("camera has off line, userInfo [%s]" % (c_char_p(linkInfo).value))
    elif (EVType.onLine == connectArg.contents.m_event):
        print("camera has on line, userInfo [%s]" % (c_char_p(linkInfo).value))


connectCallBackFuncEx = connectCallBackEx(deviceLinkNotify)
frameCallbackFunc = callbackFunc(onGetFrame)
frameCallbackFuncEx = callbackFuncEx(onGetFrameEx)


# 注册相机连接状态回调
# subscribe camera connection status change
def subscribeCameraStatus(camera):
    # 注册上下线通知
    # subscribe connection status notify
    eventSubscribe = pointer(GENICAM_EventSubscribe())
    eventSubscribeInfo = GENICAM_EventSubscribeInfo()
    eventSubscribeInfo.pCamera = pointer(camera)
    nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
    if (nRet != 0):
        print("create eventSubscribe fail!")
        return -1

    nRet = eventSubscribe.contents.subscribeConnectArgsEx(eventSubscribe, connectCallBackFuncEx, g_cameraStatusUserInfo)
    if (nRet != 0):
        print("subscribeConnectArgsEx fail!")
        # 释放相关资源
        # release subscribe resource before return
        eventSubscribe.contents.release(eventSubscribe)
        return -1

        # 不再使用时，需释放相关资源
    # release subscribe resource at the end of use
    eventSubscribe.contents.release(eventSubscribe)
    return 0


# 反注册相机连接状态回调
# unsubscribe camera connection status change
def unsubscribeCameraStatus(camera):
    # 反注册上下线通知
    # unsubscribe connection status notify
    eventSubscribe = pointer(GENICAM_EventSubscribe())
    eventSubscribeInfo = GENICAM_EventSubscribeInfo()
    eventSubscribeInfo.pCamera = pointer(camera)
    nRet = GENICAM_createEventSubscribe(byref(eventSubscribeInfo), byref(eventSubscribe))
    if (nRet != 0):
        print("create eventSubscribe fail!")
        return -1

    nRet = eventSubscribe.contents.unsubscribeConnectArgsEx(eventSubscribe, connectCallBackFuncEx,
                                                            g_cameraStatusUserInfo)
    if (nRet != 0):
        print("unsubscribeConnectArgsEx fail!")
        # 释放相关资源
        # release subscribe resource before return
        eventSubscribe.contents.release(eventSubscribe)
        return -1

    # 不再使用时，需释放相关资源
    # release subscribe resource at the end of use
    eventSubscribe.contents.release(eventSubscribe)
    return 0

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

    # 注册相机连接状态回调
    # subscribe camera connection status change
    nRet = subscribeCameraStatus(camera)
    if (nRet != 0):
        print("subscribeCameraStatus fail!")
        return -1

    return 0


# 关闭相机
# close camera
def closeCamera(camera):
    # 反注册相机连接状态回调
    # unsubscribe camera connection status change
    nRet = unsubscribeCameraStatus(camera)
    if (nRet != 0):
        print("unsubscribeCameraStatus fail!")
        return -1

    # 断开相机
    # disconnect camera
    nRet = camera.disConnect(byref(camera))
    if (nRet != 0):
        print("disConnect camera fail!")
        return -1

    return 0


# 设置曝光
# set camera ExposureTime
def setExposureTime(camera, dVal):
    # 通用属性设置:设置曝光 --根据属性类型，直接构造属性节点。如曝光是 double类型，构造doubleNode节点
    # create corresponding property node according to the value type of property, here is doubleNode
    exposureTimeNode = pointer(GENICAM_DoubleNode())
    exposureTimeNodeInfo = GENICAM_DoubleNodeInfo()
    exposureTimeNodeInfo.pCamera = pointer(camera)
    exposureTimeNodeInfo.attrName = b"ExposureTime"
    nRet = GENICAM_createDoubleNode(byref(exposureTimeNodeInfo), byref(exposureTimeNode))
    if nRet != 0:
        print("create ExposureTime Node fail!")
        return -1

    # 设置曝光时间
    # set ExposureTime
    nRet = exposureTimeNode.contents.setValue(exposureTimeNode, c_double(dVal))
    if nRet != 0:
        print("set ExposureTime value [%f]us fail!" % (dVal))
        # 释放相关资源
        # release node resource before return
        exposureTimeNode.contents.release(exposureTimeNode)
        return -1
    else:
        print("set ExposureTime value [%f]us success." % (dVal))

    # 释放节点资源
    # release node resource at the end of use
    exposureTimeNode.contents.release(exposureTimeNode)
    return 0


# 设置伽马
def setGamma(camera, dVal):
    gammaDoubleNode = pointer(GENICAM_DoubleNode())
    gammaDoubleNodeInfo = GENICAM_DoubleNodeInfo()
    gammaDoubleNodeInfo.pCamera = pointer(camera)
    gammaDoubleNodeInfo.attrName = b"Gamma"
    nRet = GENICAM_createDoubleNode(byref(gammaDoubleNodeInfo), byref(gammaDoubleNode))
    if nRet != 0:
        print("create setGamma Node fail!")
        return -1
    nRet = gammaDoubleNode.contents.setValue(gammaDoubleNode, c_double(dVal))
    if nRet != 0:
        print("set setGamma value [%f]us fail!" % (dVal))
        gammaDoubleNode.contents.release(gammaDoubleNode)
        return -1
    else:
        print("set setGamma value [%f]us success." % (dVal))
    gammaDoubleNode.contents.release(gammaDoubleNode)
    return 0


# 设置增益
def setGainRaw(camera, dVal):
    gainRawDoubleNode = pointer(GENICAM_DoubleNode())
    gainRawDoubleNodeInfo = GENICAM_DoubleNodeInfo()
    gainRawDoubleNodeInfo.pCamera = pointer(camera)
    gainRawDoubleNodeInfo.attrName = b"GainRaw"
    nRet = GENICAM_createDoubleNode(byref(gainRawDoubleNodeInfo), byref(gainRawDoubleNode))
    if nRet != 0:
        print("create setGainRaw Node fail!")
        return -1
    nRet = gainRawDoubleNode.contents.setValue(gainRawDoubleNode, c_double(dVal))
    if nRet != 0:
        print("set setGainRaw value [%f]us fail!" % (dVal))
        gainRawDoubleNode.contents.release(gainRawDoubleNode)
        return -1
    else:
        print("set setGainRaw value [%f]us success." % (dVal))
    gainRawDoubleNode.contents.release(gainRawDoubleNode)
    return 0


# 设置亮度
def setBrightness(camera, dVal):
    BrightnessNode = pointer(GENICAM_IntNode())
    BrightnessNodeInfo = GENICAM_IntNodeInfo()
    BrightnessNodeInfo.pCamera = pointer(camera)
    BrightnessNodeInfo.attrName = b"brightness"
    nRet = GENICAM_createDoubleNode(byref(BrightnessNodeInfo), byref(BrightnessNode))
    if nRet != 0:
        print("create Brightness Node fail!")
        return -1
    nRet = BrightnessNode.contents.setValue(BrightnessNode, c_longlong(dVal))
    if nRet != 0:
        print("set Brightness value [%f]us fail!" % dVal)
        BrightnessNode.contents.release(BrightnessNode)
        return -1
    else:
        print("set Brightness value [%f]us success." % dVal)
    BrightnessNode.contents.release(BrightnessNode)
    return 0


def AutobalanceWhite(camera):
    AutobalanceWhiteNode = pointer(GENICAM_EnumNode())
    AutobalanceWhiteNodeInfo = GENICAM_EnumNodeInfo()
    AutobalanceWhiteNodeInfo.pCamera = pointer(camera)
    AutobalanceWhiteNodeInfo.attrName = b"BalanceWhiteAuto"
    nRet = GENICAM_createEnumNode(byref(AutobalanceWhiteNodeInfo), byref(AutobalanceWhiteNode))
    if nRet != 0:
        print("create AutobalanceWhite Node fail!")
        return -1
    nRet = AutobalanceWhiteNode.contents.setValueBySymbol(AutobalanceWhiteNode, b"Continuous")
    if nRet != 0:
        print("open AutobalanceWhite fail!")
        AutobalanceWhiteNode.contents.release(AutobalanceWhiteNode)
        return -1
    else:
        print("open AutobalanceWhite success.")
    AutobalanceWhiteNode.contents.release(AutobalanceWhiteNode)
    return 0


# 开启自动曝光
def Autoexposure(camera):
    AutoexposureNode = pointer(GENICAM_EnumNode())
    AutoAutoexposureNodeInfo = GENICAM_EnumNodeInfo()
    AutoAutoexposureNodeInfo.pCamera = pointer(camera)
    AutoAutoexposureNodeInfo.attrName = b"BalanceWhiteAuto"
    nRet = GENICAM_createEnumNode(byref(AutoAutoexposureNodeInfo), byref(AutoexposureNode))
    if nRet != 0:
        print("create AutobalanceWhite Node fail!")
        return -1
    nRet = AutoexposureNode.contents.setValueBySymbol(AutoexposureNode, b"Continuous")
    if nRet != 0:
        print("open AutobalanceWhite fail!")
        AutoexposureNode.contents.release(AutoexposureNode)
        return -1
    else:
        print("open AutobalanceWhite success.")
    AutoexposureNode.contents.release(AutoexposureNode)
    return 0


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


def grabOne(camera):
    # 创建流对象
    # create stream source object
    streamSourceInfo = GENICAM_StreamSourceInfo()
    streamSourceInfo.channelId = 0
    streamSourceInfo.pCamera = pointer(camera)

    streamSource = pointer(GENICAM_StreamSource())
    nRet = GENICAM_createStreamSource(pointer(streamSourceInfo), byref(streamSource))
    if (nRet != 0):
        print("create StreamSource fail!")
        return -1

    # 创建AcquisitionControl节点
    # create AcquisitionControl node
    acqCtrlInfo = GENICAM_AcquisitionControlInfo()
    acqCtrlInfo.pCamera = pointer(camera)
    acqCtrl = pointer(GENICAM_AcquisitionControl())
    nRet = GENICAM_createAcquisitionControl(pointer(acqCtrlInfo), byref(acqCtrl))
    if (nRet != 0):
        print("create AcquisitionControl fail!")
        # 释放相关资源
        # release stream source object before return
        streamSource.contents.release(streamSource)
        return -1

    # 执行一次软触发
    # execute software trigger once
    trigSoftwareCmdNode = acqCtrl.contents.triggerSoftware(acqCtrl)
    nRet = trigSoftwareCmdNode.execute(byref(trigSoftwareCmdNode))
    if (nRet != 0):
        print("Execute triggerSoftware fail!")
        # 释放相关资源
        # release node resource before return
        trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
        acqCtrl.contents.release(acqCtrl)
        streamSource.contents.release(streamSource)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    trigSoftwareCmdNode.release(byref(trigSoftwareCmdNode))
    acqCtrl.contents.release(acqCtrl)
    streamSource.contents.release(streamSource)

    return 0


# 设置感兴趣区域  --- 感兴趣区域的宽高 和 xy方向的偏移量  入参值应符合对应相机的递增规则
# set ROI
def setROI(camera, OffsetX, OffsetY, nWidth, nHeight):
    # 获取原始的宽度
    # get the max width of image
    widthMaxNode = pointer(GENICAM_IntNode())
    widthMaxNodeInfo = GENICAM_IntNodeInfo()
    widthMaxNodeInfo.pCamera = pointer(camera)
    widthMaxNodeInfo.attrName = b"WidthMax"
    nRet = GENICAM_createIntNode(byref(widthMaxNodeInfo), byref(widthMaxNode))
    if (nRet != 0):
        print("create WidthMax Node fail!")
        return -1

    oriWidth = c_longlong()
    nRet = widthMaxNode.contents.getValue(widthMaxNode, byref(oriWidth))
    if (nRet != 0):
        print("widthMaxNode getValue fail!")
        # 释放相关资源
        # release node resource before return
        widthMaxNode.contents.release(widthMaxNode)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    widthMaxNode.contents.release(widthMaxNode)

    # 获取原始的高度
    # get the max height of image
    heightMaxNode = pointer(GENICAM_IntNode())
    heightMaxNodeInfo = GENICAM_IntNodeInfo()
    heightMaxNodeInfo.pCamera = pointer(camera)
    heightMaxNodeInfo.attrName = b"HeightMax"
    nRet = GENICAM_createIntNode(byref(heightMaxNodeInfo), byref(heightMaxNode))
    if (nRet != 0):
        print("create HeightMax Node fail!")
        return -1

    oriHeight = c_longlong()
    nRet = heightMaxNode.contents.getValue(heightMaxNode, byref(oriHeight))
    if (nRet != 0):
        print("heightMaxNode getValue fail!")
        # 释放相关资源
        # release node resource before return
        heightMaxNode.contents.release(heightMaxNode)
        return -1

    # 释放相关资源
    # release node resource at the end of use
    heightMaxNode.contents.release(heightMaxNode)

    # 检验参数
    # check parameter valid
    if ((oriWidth.value < (OffsetX + nWidth)) or (oriHeight.value < (OffsetY + nHeight))):
        print("please check input param!")
        return -1

    # 设置宽度
    # set image width
    widthNode = pointer(GENICAM_IntNode())
    widthNodeInfo = GENICAM_IntNodeInfo()
    widthNodeInfo.pCamera = pointer(camera)
    widthNodeInfo.attrName = b"Width"
    nRet = GENICAM_createIntNode(byref(widthNodeInfo), byref(widthNode))
    if (nRet != 0):
        print("create Width Node fail!")
        return -1

    nRet = widthNode.contents.setValue(widthNode, c_longlong(nWidth))
    if (nRet != 0):
        print("widthNode setValue [%d] fail!" % (nWidth))
        # 释放相关资源
        # release node resource before return
        widthNode.contents.release(widthNode)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    widthNode.contents.release(widthNode)

    # 设置高度
    # set image height
    heightNode = pointer(GENICAM_IntNode())
    heightNodeInfo = GENICAM_IntNodeInfo()
    heightNodeInfo.pCamera = pointer(camera)
    heightNodeInfo.attrName = b"Height"
    nRet = GENICAM_createIntNode(byref(heightNodeInfo), byref(heightNode))
    if (nRet != 0):
        print("create Height Node fail!")
        return -1

    nRet = heightNode.contents.setValue(heightNode, c_longlong(nHeight))
    if (nRet != 0):
        print("heightNode setValue [%d] fail!" % (nHeight))
        # 释放相关资源
        # release node resource before return
        heightNode.contents.release(heightNode)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    heightNode.contents.release(heightNode)

    # 设置OffsetX
    # set OffsetX
    OffsetXNode = pointer(GENICAM_IntNode())
    OffsetXNodeInfo = GENICAM_IntNodeInfo()
    OffsetXNodeInfo.pCamera = pointer(camera)
    OffsetXNodeInfo.attrName = b"OffsetX"
    nRet = GENICAM_createIntNode(byref(OffsetXNodeInfo), byref(OffsetXNode))
    if (nRet != 0):
        print("create OffsetX Node fail!")
        return -1

    nRet = OffsetXNode.contents.setValue(OffsetXNode, c_longlong(OffsetX))
    if (nRet != 0):
        print("OffsetX setValue [%d] fail!" % (OffsetX))
        # 释放相关资源
        # release node resource before return
        OffsetXNode.contents.release(OffsetXNode)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    OffsetXNode.contents.release(OffsetXNode)

    # 设置OffsetY
    # set OffsetY
    OffsetYNode = pointer(GENICAM_IntNode())
    OffsetYNodeInfo = GENICAM_IntNodeInfo()
    OffsetYNodeInfo.pCamera = pointer(camera)
    OffsetYNodeInfo.attrName = b"OffsetY"
    nRet = GENICAM_createIntNode(byref(OffsetYNodeInfo), byref(OffsetYNode))
    if (nRet != 0):
        print("create OffsetY Node fail!")
        return -1

    nRet = OffsetYNode.contents.setValue(OffsetYNode, c_longlong(OffsetY))
    if (nRet != 0):
        print("OffsetY setValue [%d] fail!" % (OffsetY))
        # 释放相关资源
        # release node resource before return
        OffsetYNode.contents.release(OffsetYNode)
        return -1

        # 释放相关资源
    # release node resource at the end of use
    OffsetYNode.contents.release(OffsetYNode)
    return 0


def setTriggetModeOff(camera, streamSource):
    # 通用属性设置:设置触发模式为off --根据属性类型，直接构造属性节点。如触发模式是 enumNode，构造enumNode节点
    # create corresponding property node according to the value type of property, here is enumNode
    # 自由拉流：TriggerMode 需为 off
    # set trigger mode to Off for continuously grabbing
    trigModeEnumNode = pointer(GENICAM_EnumNode())
    trigModeEnumNodeInfo = GENICAM_EnumNodeInfo()
    trigModeEnumNodeInfo.pCamera = pointer(camera)
    trigModeEnumNodeInfo.attrName = b"TriggerMode"
    nRet = GENICAM_createEnumNode(byref(trigModeEnumNodeInfo), byref(trigModeEnumNode))
    if nRet != 0:
        print("create TriggerMode Node fail!")
        # 释放相关资源
        # release node resource before return
        streamSource.contents.release(streamSource)
        return -1

    nRet = trigModeEnumNode.contents.setValueBySymbol(trigModeEnumNode, b"Off")
    if nRet != 0:
        print("set TriggerMode value [Off] fail!")
        # 释放相关资源
        # release node resource before return
        trigModeEnumNode.contents.release(trigModeEnumNode)
        streamSource.contents.release(streamSource)
        return -1

    # 需要释放Node资源
    # release node resource at the end of use
    trigModeEnumNode.contents.release(trigModeEnumNode)


def demo(cvImage, nRet, streamSource, camera, cnt):
    if cnt == 0:
        # 发现相机
        # enumerate camera
        cameraCnt, cameraList = enumCameras()
        if cameraCnt is None:
            return -1

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
        streamSourceInfo = []
        streamSource = []
        nRet = []
        for i in range(0, cameraCnt):
            # camera[i] = cameraList[i]

            # 打开相机
            # open camera
            nRet.append(openCamera(camera[i]))
            if nRet[i] != 0:
                print("openCamera fail.")
                return -1

            # 创建流对象
            # create stream source object
            streamSourceInfo.append(GENICAM_StreamSourceInfo())
            streamSourceInfo[i].channelId = 0
            streamSourceInfo[i].pCamera = pointer(camera[i])

            streamSource.append(pointer(GENICAM_StreamSource()))
            nRet[i] = GENICAM_createStreamSource(pointer(streamSourceInfo[i]), byref(streamSource[i]))
            if nRet[i] != 0:
                print("create StreamSource fail!")
                return -1

            # 通用属性设置:设置触发模式为off --根据属性类型，直接构造属性节点。如触发模式是 enumNode，构造enumNode节点
            # create corresponding property node according to the value type of property, here is enumNode
            # 自由拉流：TriggerMode 需为 off
            # set trigger mode to Off for continuously grabbing
            trigModeEnumNode = pointer(GENICAM_EnumNode())
            trigModeEnumNodeInfo = GENICAM_EnumNodeInfo()
            trigModeEnumNodeInfo.pCamera = pointer(camera[i])
            trigModeEnumNodeInfo.attrName = b"TriggerMode"
            nRet[i] = GENICAM_createEnumNode(byref(trigModeEnumNodeInfo), byref(trigModeEnumNode))
            if nRet[i] != 0:
                print("create TriggerMode Node fail!")
                # 释放相关资源
                # release node resource before return
                streamSource[i].contents.release(streamSource[i])
                return -1

            nRet[i] = trigModeEnumNode.contents.setValueBySymbol(trigModeEnumNode, b"Off")
            if nRet[i] != 0:
                print("set TriggerMode value [Off] fail!")
                # 释放相关资源
                # release node resource before return
                trigModeEnumNode.contents.release(trigModeEnumNode)
                streamSource[i].contents.release(streamSource[i])
                return -1

            # 需要释放Node资源
            # release node resource at the end of use
            trigModeEnumNode.contents.release(trigModeEnumNode)

            # 设置相机参数
            nRet[i] = setExposureTime(camera[i], CONFIG_exposureTime)  # 曝光
            nRet[i] = setGamma(camera[i], CONFIG_gamma)  # 伽马
            nRet[i] = setGainRaw(camera[i], CONFIG_gainRaw)  # 增益
            nRet[i] = setBrightness(camera[i], CONFIG_bright)  # 亮度
            # nRet[i] = Autoexposure(camera[i])               # 自动曝光
            nRet[i] = AutobalanceWhite(camera[i])  # 自动白平衡
            if nRet[i] != 0:
                print("set Camera_parameters fail")
                # 释放相关资源
                # release stream source object before return
                streamSource[i].contents.release(streamSource[i])
                return -1

            # 注册拉流回调函数
            # subscribe grabbing callback
            userInfo = b"test"
            nRet[i] = streamSource[i].contents.attachGrabbingEx(streamSource[i], frameCallbackFuncEx, userInfo)
            if (nRet[i] != 0):
                print("attachGrabbingEx fail!")
                # 释放相关资源
                # release stream source object before return
                streamSource[i].contents.release(streamSource[i])
                return -1

            # 反注册回调函数
            # unsubscribe grabbing callback
            nRet[i] = streamSource[i].contents.detachGrabbingEx(streamSource[i], frameCallbackFuncEx, userInfo)
            if (nRet[i] != 0):
                print("detachGrabbingEx fail!")
                # 释放相关资源
                # release stream source object before return
                streamSource[i].contents.release(streamSource[i])
                return -1

            # 开始拉流
            # start grabbing
            nRet[i] = streamSource[i].contents.startGrabbing(streamSource[i], c_ulonglong(0), \
                                                             c_int(GENICAM_EGrabStrategy.grabStrartegySequential))
            if nRet[i] != 0:
                print("startGrabbing fail!")
                # 释放相关资源
                # release stream source object before return
                streamSource[i].contents.release(streamSource[i])
                return -1

        # 主动取图
        # get one frame
        cnt = cameraCnt
    cvImage = []
    for i in range(0, cnt):
        frame = pointer(GENICAM_Frame())
        # dst = numpy.array(frame).reshape(1080, 2160, 3)
        # cv2.imshow("frame", dst)\
        nRet[i] = streamSource[i].contents.getFrame(streamSource[i], byref(frame), c_uint(1000))
        if nRet[i] != 0:
            print("SoftTrigger getFrame fail! timeOut [1000]ms")
            # 释放相关资源
            # release stream source object before return
            streamSource[i].contents.release(streamSource[i])
            return -1
        # else:
        # print("SoftTrigger getFrame success BlockId = " + str(frame.contents.getBlockId(frame)))
        # print("get frame time: " + str(datetime.datetime.now()))

        nRet[i] = frame.contents.valid(frame)
        if nRet[i] != 0:
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
        convertParams = IMGCNV_SOpenParam()
        convertParams.dataSize = frame.contents.getImageSize(frame)
        convertParams.height = frame.contents.getImageHeight(frame)
        convertParams.width = frame.contents.getImageWidth(frame)
        convertParams.paddingX = frame.contents.getImagePaddingX(frame)
        convertParams.paddingY = frame.contents.getImagePaddingY(frame)
        convertParams.pixelForamt = frame.contents.getImagePixelFormat(frame)

        # 将裸数据图像拷出
        # copy image data out from frame
        buffAddr = frame.contents.getImage(frame)
        frameBuff = c_buffer(b'\0', convertParams.dataSize)
        memmove(frameBuff, c_char_p(buffAddr), convertParams.dataSize)

        # 释放驱动图像缓存
        # release frame resource at the end of use
        frame.contents.release(frame)

        # 如果图像格式是 Mono8 不需要转码
        # no format conversion required for Mono8
        if convertParams.pixelForamt == EPixelType.gvspPixelMono8:
            # 初始化调色板rgbQuad 实际应用中 rgbQuad 只需初始化一次
            grayByteArray = bytearray(frameBuff)
            cvImage.append(numpy.array(grayByteArray).reshape(convertParams.height, convertParams.width))
        else:
            # 转码 => BGR24
            # convert to BGR24
            rgbSize = c_int()
            rgbBuff = c_buffer(b'\0', convertParams.height * convertParams.width * 3)
            nRet[i] = IMGCNV_ConvertToBGR24(cast(frameBuff, c_void_p), byref(convertParams), \
                                            cast(rgbBuff, c_void_p), byref(rgbSize))

            colorByteArray = bytearray(rgbBuff)
            img = numpy.array(colorByteArray).reshape(convertParams.height, convertParams.width, 3)
            # img = cv2.resize(img, (960, 768))
            cvImage.append(img)
            # if ( nRet != 0 ):
            #     print("image convert fail! errorCode = " + str(nRet))
            #     # 释放相关资源
            #     # release stream source object before return
            #     streamSource.contents.release(streamSource)
            #     return -1

    # 显示相机拉流图像
    # for i in range(0, cnt):
    #     # print(type(cvImage[i]))
    #     cv2.imshow('myWindow'+str(i), cvImage[i])
    gc.collect()

    # if cv2.waitKey(1) == 27:
    #     break
    return cvImage, nRet, streamSource, camera, cnt


def shutdown(cvimage, nRet, streamSource, camera, cnt):
    for i in range(0, cnt):
        # 停止拉流
        # stop grabbing
        nRet[i] = streamSource[i].contents.stopGrabbing(streamSource[i])
        if nRet[i] != 0:
            print("stopGrabbing fail!")
            # 释放相关资源
            # release stream source object before return
            streamSource[i].contents.release(streamSource[i])
            return -1

        # 关闭相机
        # close camera
        nRet[i] = closeCamera(camera[i])
        if nRet[i] != 0:
            print("closeCamera fail")
            # 释放相关资源
            # release stream source object before return
            streamSource[i].contents.release(streamSource[i])
            return -1

        # 释放相关资源
        # release stream source object at the end of use
        streamSource[i].contents.release(streamSource[i])
    return 0


if __name__ == "__main__":

    cvImage, nRet, streamSource, camera = demo()
    nRet = shutdown(cvImage, nRet, streamSource, camera)
    if nRet != 0:
        print("Some Error happend")
    print("--------- Demo end ---------")
    # 3s exit
    time.sleep(0.5)
