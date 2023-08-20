import platform, struct, os, sys, time, cv2
from threading import Thread
__presentDir=os.path.join(os.getcwd(),os.path.dirname(__file__))
#serial重名
sys.path.remove(sys.path[0])
import serial as pyserial
from crc import *
import crcmod.predefined
sys.path.insert(0,__presentDir)
import queue
sys.path.remove(__presentDir)


class Crc:
    __Crc8 = crcmod.mkCrcFun(poly=0x131, initCrc=0xff, xorOut=0x00, rev=True)
    __Crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xffff, xorOut=0x0000, rev=True)

    def caculateCrc8(dataPackage):
        return Crc.__Crc8(dataPackage)

    def caculateCrc16(dataPackage):
        return Crc.__Crc16(dataPackage)

    def verifyCrc8(dataPackage):
        return Crc.__Crc8(dataPackage[:-1]) == dataPackage[-1]

    def verifyCrc16(dataPackage):
        return Crc.__Crc16(dataPackage[:-2]) == int.from_bytes(dataPackage[-2:], "little")

commandDict = {
    "location":
    {
        "command": 0x0305,
    },
}

class Serial(Thread):
    def __init__(self, name="", equeue=None, port="", bps=115200, timeout=1):
        Thread.__init__(self, name=name)
        self.isRunning = True
        self.loop = 0
        self.mycolor = None
        self.time = -1
        self.seq = 0
        self.ddkv = 0.91140343
        self.serial = pyserial.Serial()
        self.data_queue = equeue
        try:
            # print("开始try")
            if platform.system() == "Windows":
                port = "COM4"
            # # !!!!!!未完成！！！！！！！
            elif platform.system() == "Linux":
                prot = "/dev/"  # 未定

            self.serial = pyserial.Serial(port, bps, timeout=timeout)
            print("串口是否打开：", self.serial.is_open)
            self.isLoop = True
        except Exception as e:
            print("[INFO]::{:s}".format(port + "can't found or error!Please inspect"))
            print(e)
            # raise

    def run(self):
        print("[INFO]::Thread-Serial running")
        self.process()
        self.serial.close()

    def process(self):
        print("已经访问完毕")
        self.getenemyColor()
        while self.isRunning:
            self.getcontestTime()
            self.data_queue.put(self.time)

    def stop(self):
        print("[INFO]::Thread-Serial stopped")
        self.isRunning = False

    def getenemycolor(self):
        return self.mycolor

    def gettime(self):
        return self.time

    def sendLocation(self):
        lastmap = cv2.imread(r"E:\mytest\Location\map.jpg")
        lastmap = cv2.resize(lastmap, (614, 339))
        cv2.circle(lastmap, (532, 117), 5, (255, 255, 255), -1)
        robotID = 102
        robotID = int.to_bytes(robotID, 2, "little")
        # initx, inity= struct.pack("f", initx * 28), struct.pack("f", inity * 15)
        initx, inity = struct.pack("f", self.ddkv * 28), struct.pack("f", (1 - 0.34866873) * 15)
        commandDict["location"]["data"] = robotID + initx + inity
        package = self.produceDataPackage("location")
        print("sendLocation")
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
                # print("headBytes", type(headBytes))
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
                                self.mycolor = "R9"
                            else:
                                self.mycolor = "B9"
                            print("[INFO]::成功获取我方颜色信息 {:s}".format(self.mycolor))
                            break

    def getcontestTime(self):
        # time.sleep(1)
        read = self.serial.read
        buff = read()
        print("[INFO]::time", self.time)
        if buff.hex() == "a5":
            dataLengthBytes = read(2)
            # 验证crc8
            headBytes = buff + dataLengthBytes + read(2)
            if Crc.verifyCrc8(headBytes):
                cmdIdBytes = read(2)
                if int.from_bytes(cmdIdBytes, "little") == 0x0001:
                    # 除 头帧 与 命令码 外的数据长度
                    print("[INFO]::into getcontestTime:", self.time)
                    elseLenth = int.from_bytes(dataLengthBytes, "little") + 2
                    # 验证Crc16
                    dataPackage = headBytes + cmdIdBytes + read(elseLenth)
                    if Crc.verifyCrc16(dataPackage):
                        # 判断比赛模式
                        print("dataPackage", type(dataPackage))
                        if dataPackage[7] == int("01000001", 2):  # 0001 0100逆置
                            self.time = int.from_bytes(dataPackage[8:10], "little")
                            # time.sleep(1)
                        else:
                            self.time = -1
                        self.sendLocation()
                        self.ddkv -= 0.003


if __name__ == "__main__":
    data_queue = queue.Queue()
    x = Serial("Serial", equeue=data_queue)
    x.start()
    # while True:
    #     print(x.getenemycolor())
    #     print(x.gettime())
    #     time.sleep(1)
    time.sleep(100)
    x.stop()
    x.join()
