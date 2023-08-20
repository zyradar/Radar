import platform, struct, os, sys, time, cv2
from threading import Thread
import serial as pyserial
from Serial.crc import *
from configfile import *
__presentDir = os.path.join(os.getcwd(),os.path.dirname(__file__))
sys.path.remove(sys.path[0])
sys.path.insert(0, __presentDir)
sys.path.remove(__presentDir)

draw_color = CONFIG_draw_color
commandDict = CONFIG_commandDict


class Serial(Thread):
    def __init__(self, name="",  port="", bps=115200, timeout=1):
        Thread.__init__(self, name=name)
        self.isLoop = CONFIG_isLoop
        self.mycolor = CONFIG_mycolor           # 我方车辆颜色
        self.enemycolor = CONFIG_enemycolor     # 敌方颜色
        self.time = 1
        self.seq = 0
        self.serial = pyserial.Serial()

        try:
            if platform.system() == "Windows":
                port = "COM4"
            elif platform.system() == "Linux":
                prot = "/dev/ttyTHS0"  # ttyTHS0通信串口

            self.serial = pyserial.Serial(port, bps, timeout=timeout)
            print("串口是否打开：", self.serial.is_open)
            self.isLoop = True
        except Exception:
            print("[INFO]::{:s}".format(port + "can't found or error!Please inspect"))

    def run(self):
        print("[INFO]::Thread-Serial running")
        self.process()
        self.serial.close()

    def process(self):
        print("通信线程已经访问完毕")
        self.getenemyColor()
        while self.isLoop:
            self.getcontestTime()


    def stop(self):
        print("[INFO]::Thread-Serial stopped")
        self.isLoop = False

    def getmycolor(self):
        return self.mycolor

    def gettime(self):
        return self.time

    def test_point(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
                print(x, y)

    def sendLocation(self, initpoint):
        lastmap = cv2.imread(CONFIG_map_path)
        lastmap = cv2.resize(lastmap, (614, 339))
        isgetID = []
        print("initpoint", initpoint)
        for point in initpoint:
            if point:
                initx = point[0] / 339
                inity = point[1] / 614
                robotID = point[3]
                if self.mycolor == "B":
                    initx, inity = inity, initx
                    robotID = int(robotID)
                else:
                    initx, inity = 1 - inity, 1 - initx
                    robotID = int(robotID) + 100
                isgetID.append(robotID)
                cv2.circle(lastmap, (int(initx * 614), int((1 - inity) * 339)), 5, draw_color[self.enemycolor], -1)
                cv2.putText(lastmap, str(robotID), (int(initx * 614), int((1 - inity) * 339) + 3),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                robotID = int.to_bytes(robotID, 2, "little")
                initx, inity = struct.pack("f", initx * 28), struct.pack("f", inity * 15)
                commandDict["location"]["data"] = robotID + initx + inity
                package = self.produceDataPackage("location")
                self.serial.write(package)
                self.serial.inWaiting()
                time.sleep(0.1)
            else:
                continue
        print("isgetID", isgetID)
        cv2.namedWindow("lastmap", cv2.WINDOW_NORMAL)
        cv2.imshow("lastmap", lastmap)

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
                            if dataPackage[7] == 9:
                                self.mycolor = "R"
                                self.enemycolor = 'B'
                            else:
                                self.mycolor = "B"
                                self.enemycolor = 'R'
                            print("[INFO]::成功获取我方颜色信息 {:s}".format(self.mycolor))
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
                        else:
                            self.time = -1


if __name__ == "__main__":
    x = Serial()
    x.start()
    x.join()
