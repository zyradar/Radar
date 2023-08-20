# 检验导入路径
import sys, os
# import platform

import cv2

__presentDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.insert(0, __presentDir)

import threading
from myserial import *
import serial as pyserial

class Camera(threading.Thread):
    def __init__(self, name, equeue=None, serial=None):
        Thread.__init__(self, name=name)
        # print("是在Camera里面报错的")
        self.cserial = serial
        self.cout = 0
        self.isRunning = True
        self.data_queue = equeue
        # print("!!!!!!!!!!!!!!!!![INFO]::sajhala!!!!!!!!", self.cserial.serial)
        # print("!!!!!!!!!!!!!!!!![INFO]::sajhala!!!!!!!!", Serial)
        # self.cserial.serial.close()
        # self.tosendLocation = Serial.sendLocation()
        self.enemycolor = 101

    def run(self):
        # print("[INFO]::Thread-Camera running")
        self.process()

    def stop(self):
        if isinstance(self.cserial, Serial):
            self.cserial.stop()
        # print("[INFO]::Thread-Locator stopped")

    def process(self):
        self.setEnemyColor()
        self.setFrame()

    def setEnemyColor(self):
        default = "R"
        if isinstance(self.cserial, Serial):
            # print("self.serial.getenemycolor()", self.serial.getenemycolor(), type(self.serial.getenemycolor()))
            if isinstance(self.cserial.getenemycolor(), str):
                self.enemycolor = self.cserial.getenemycolor()
                print("进入serial", self.enemycolor)
            else:
                self.enemycolor = default
                print("进入serial---setEnemyColor", self.enemycolor)
        else:
            self.enemycolor = default
            print("进入noserial---setEnemyColor", self.enemycolor)

    def setFlags(self):
        a = 3

    def setFrame(self):
        # self.cserial.serial = pyserial.Serial(self.cserial.port, self.cserial.bps, timeout=self.cserial.timeout)
        while self.isRunning:
            self.cserial.getcontestTime()
            print("访问一次Camera\n")
            # if self.data_queue.empty():
            #     continue
            etime = self.data_queue.get()
            self.setFlags()
            # time.sleep(1)
            print("[INFO]::成功获取比赛时间:", etime)
            # if time <= 980:
            print("[INFO]::发送位置:")
            # self.cserial.getcontestTime()
            self.cserial.sendLocation()
            self.cout += 1
            # k = cv2.waitKey(1)
            # if k == 27:
            #     break




if __name__ == "__main__":
    x = Camera()
    x.start()

    x.join()
