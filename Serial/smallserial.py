import platform
from threading import Thread, Lock
import struct
import time
import cv2
import serial as pyserial
from Serial.crc import *
# import random
import crcmod.predefined


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
    def __init__(self, port="", equeue=None, bps=115200, timeout=1):
        Thread.__init__(self, name="Serial")
        self.serial = pyserial.Serial()
        self.loop = 0
        self.time = 988
        self.mycolor = 444
        self.isRunning = True
        self.data_queue = equeue

    def run(self):
        # print("[INFO]::Thread-Serial running")
        self.process()
        self.serial.close()

    def getenemycolor(self):
        return self.mycolor

    def gettime(self):
        return self.time

    def process(self):
        self.getenemyColor()
        while self.isRunning:
            self.getcontestTime()
            self.data_queue.put(self.time)
            # print("serial:")

    def stop(self):
        print("[INFO]::Thread-Serial stopped")
        self.isRunning = False

    def getenemyColor(self):
        while True:
            # print("[INFO]::成功获取敌方颜色信息")
            if self.loop == 0:
                self.mycolor = 'R'
                break

    def getcontestTime(self):
        # print("进入getcontestTime",  self.time)
        time.sleep(1)
        self.time -= 1


if __name__ == "__main__":
    x = Serial()
    x.start()
    # while True:
    time.sleep(1)
    # x.stop()
    x.join()
