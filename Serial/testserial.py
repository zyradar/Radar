import platform
import time
from threading import Thread
import struct
import serial as pyserial
from Serial.crc import *

commandDict = {
    "location":
    {
        "command": 0x0305,
    },
}


# class Serial(Thread):
#     def __init__(self, name, q, event1, event2, event3, serial_data, port='', bps=115200, timeout=1):
#         Thread.__init__(self, name=name)
#         self.isLoop = False
#         self.mycolor = None    # 我方车辆颜色
#         self.time = -1
#         self.seq = 0
#         self.serial = pyserial.Serial()
#         self.q = q
#         self.event1 = event1
#         self.event2 = event2
#         self.event3 = event3
#         self.serial_data = serial_data
#         try:
#             if platform.system() == "Windows":
#                 port = "COM20"
#             # !!!!!!未完成！！！！！！！
#             elif platform.system() == "Linux":
#                 prot = "/dev/"      # 未定
#
#             self.serial = pyserial.Serial(port, bps, timeout=timeout)
#             self.isLoop = True
#         except Exception:
#             print("[INFO]::{:s}".format(port+"can't found or error!Please inspect"))

class Serial(Thread):
    def __init__(self, port="", bps=115200, timeout=1):
        Thread.__init__(self, name="Serial")
        self.isLoop = True
        self.mycolor = None  # 我方车辆颜色
        self.time = -1
        self.seq = 0
        self.serial = pyserial.Serial()
        try:
            if platform.system() == "Windows":
                port = "COM7"
            # !!!!!!未完成！！！！！！！
            elif platform.system() == "Linux":
                prot = "/dev/"  # 未定

            self.serial = pyserial.Serial(port, bps, timeout=timeout)
            self.isLoop = True
        except Exception:
            print("[INFO]::{:s}".format(port + "can't found or error!Please inspect"))


    def run(self):
        print("[INFO]::Thread-Serial running")
        self.process()
        self.serial.close()


    def process(self):
        # print(self.mycolor)
        self.getenemyColor()
        while self.isLoop:
            self.getcontestTime()
            # print(x.getenemycolor())
            # print(x.gettime())
            print("OurColor:", self.mycolor)
            print("TimeRemaining:", self.time)


    def stop(self):
        self.isLoop = False
        print("[INFO]::Thread-Serial stopped")

    def getenemycolor(self):
        return self.mycolor

    def gettime(self):
        return self.time

    def sendLocation(self, robotID, x, y, angle=0):
        if self.mycolor == "B":
            x, y = 1 - y, 1-x
        else:
            x, y = y, x
        robotID = int.to_bytes(robotID, 2, "little")
        x, y, angle = struct.pack("f", x * 28), struct.pack("f", y * 15), struct.pack("f", angle)
        commandDict["location"]["data"] = robotID+x+y+angle
        package = self.produceDataPackage("location")
        self.serial.write(package)
        self.serial.inWaiting()

    def produceDataPackage(self, dictname):
        dic = commandDict[dictname]
        package = int.to_bytes(0xa5, 1, "little")
        package += int.to_bytes(len(dic["data"]), 2, "little")
        package += int.to_bytes(self.seq, 1, "little")
        package += int.to_bytes(Crc.caculateCrc8(package), 1, "little")
        package += int.to_bytes(dic["command"], 2, "little")
        package += dic["data"]
        package += int.to_bytes(Crc.caculateCrc16(package), 2, "little")
        return package


    def getenemyColor(self):
        read = self.serial.read
        while True:
            buff = read()
            # .hex()将字符串转换为十六进制表示形式,返回一个字符串
            if buff.hex() == "a5":
                dataLengthBytes = read(2)
                # 头帧
                headBytes = buff + dataLengthBytes + read(2)
                if Crc.verifyCrc8(headBytes):
                    # 命令行
                    cmdIdBytes = read(2)
                    # 机器人状态数据0x0201
                    if int.from_bytes(cmdIdBytes, "little") == 0x0201:
                        # 除头帧与命令码外的数据长度
                        elseLenth = int.from_bytes(dataLengthBytes, "little") + 2
                        dataPackage = headBytes + cmdIdBytes + read(elseLenth)
                        if Crc.verifyCrc16(dataPackage):
                            # print("dataPackage", dataPackage[1])
                            if dataPackage[7] == 9:
                                self.mycolor = "B"
                            else:
                                self.mycolor = "R"
                            print("[INFO]::成功获取敌方颜色信息 {:s}".format(self.mycolor))
                            break

    def getcontestTime(self):
        read = self.serial.read
        buff = read()
        if buff.hex() == "a5":
            dataLengthBytes = read(2)
            # 验证crc8
            headBytes = buff + dataLengthBytes + read(2)
            if Crc.verifyCrc8(headBytes):
                cmdIdBytes = read(2)
                if int.from_bytes(cmdIdBytes, "little") == 0x0001:
                    # 除 头帧 与 命令码 外的数据长度
                    elseLenth = int.from_bytes(dataLengthBytes, "little") + 2
                    # 验证Crc16
                    dataPackage = headBytes + cmdIdBytes + read(elseLenth)
                    if Crc.verifyCrc16(dataPackage):
                        # 判断比赛模式
                        if dataPackage[7] == int("01000001", 2):  # 0001 0100逆置
                            self.time = int.from_bytes(dataPackage[8:10], "little")
                            # time.sleep(1)
                        else:
                            self.time = -1


if __name__ == "__main__":
    x = Serial()
    x.start()
    # while True:
    time.sleep(1)
    # x.stop()
    x.join()
