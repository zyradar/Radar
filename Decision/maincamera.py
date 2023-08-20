# 检验导入路径
import sys, os

from Camera.Demo import demo, shutdown
from Mouse import Keypoly
__presentDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.insert(0, __presentDir)
from Decision.cameradetect import *
from Serial.myserial import *
import threading


class Camera(threading.Thread):
    def __init__(self, name, serial=None):
        Thread.__init__(self, name=name)
        self.mycolor = CONFIG_mycolor
        self.isLoop = CONFIG_isLoop
        self.printFPS = CONFIG_printFPS
        self.cserial = serial
        self.frame = np.zeros(())
        self.dst = None
        self.img = None
        self.robot_point = None
        self.t1 = time.time()
        self.gettime = None

    def run(self):
        print("[INFO]::Thread-Camera running")
        self.process()

    def stop(self):
        self.isLoop = False
        if isinstance(self.cserial, Serial):
            self.cserial.stop()
        print("[INFO]::Thread-Locator stopped")

    def process(self):
        self.setEnemyColor()
        self.isLoop = True
        if CONFIG_savevideo is True:
            self.getpickvi = cv2.VideoWriter(CONFIG_pickvi_path,cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),
                                             CONFIG_fps, CONFIG_picksize)
            self.getyuanvi = cv2.VideoWriter(CONFIG_yuanvi_path, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),
                                             CONFIG_fps, CONFIG_yuansize)
        if CONFIG_VID is True:
            self.openVideo()
        else:
            self.setFrame()

    def setEnemyColor(self):
        time.sleep(0.1)     # 目的是等待通信线程正常执行
        if isinstance(self.cserial, Serial):
            if isinstance(self.cserial.getmycolor(), str):
                self.mycolor = self.cserial.getmycolor()
                print("[INFO]::Locator成功获取我方颜色信息 {:s}".format(self.mycolor))
            else:
                print("[INFO]::Locator使用默认我方颜色信息 {:s}".format(self.mycolor))
        else:
            print("[INFO]::Locator使用默认我方颜色信息 {:s}".format(self.mycolor))

    def setFrame(self):
        CNT = 0
        mouse_position = []
        xxyys = poly_maxmin_xy(all_region)
        keymouse = Keypoly(mouse_position)
        while self.isLoop:
            self.t1 = time.time()
            if CNT == 0:
                cvImage, nRet, streamSource, camera, CNT = demo(None, None, None, None, CNT)
                print(len(cvImage))
            else:
                cvImage, nRet, streamSource, camera, CNT = demo(cvImage, nRet, streamSource, camera, CNT)
            self.dst = np.zeros((1200, 1920 * CNT, 3), dtype=np.uint8)
            for i in range(0, len(cvImage)):
                self.dst[0:1200, 1920 * i:1920 * (i + 1)] = cvImage[i]
            if CNT == 2:
                self.src = np.zeros((1200, (1920 - self.CONFIG_crop_width) * CNT, 3), dtype=np.uint8)
                if CONFIG_camera_swap:# 相机画面对换
                    self.src[0:1200, 1920 - CONFIG_crop_width:(1920 - CONFIG_crop_width) * 2] = self.dst[0:1200, 0:1920 - CONFIG_crop_width]
                    self.src[0:1200, 0:1920 - CONFIG_crop_width] = self.dst[0:1200, 1920 + CONFIG_crop_width:3840]
                else:
                    self.src[0:1200, 1920 - CONFIG_crop_width:(1920 - CONFIG_crop_width) * 2] = self.dst[0:1200, 1920 + CONFIG_crop_width:3840]
                    self.src[0:1200, 0:1920 - CONFIG_crop_width] = self.dst[0:1200, 0:1920 - CONFIG_crop_width]
                self.img = self.src
                self.img = cv2.resize(self.img, (1920, 768))
            if CNT == 1:
                self.img = self.dst[432:1200, 0:1920]
                # self.img = self.dst
            if self.savevideo is True:
                self.getpickvi.write(self.img)
                self.getyuanvi.write(self.dst)
            cvImage.clear()
            map_test = map.copy()
            h1, w1, c1 = self.img.shape[:]
            self.img = cv2.resize(self.img, (w1 // 2, h1 // 2))
            self.frame = self.img
            k = cv2.waitKey(1)
            if keymouse.isfinish:
                self.frame, self.robot_point = detect(self.frame)
                """通讯发送识别位置信息"""
                if self.robot_point:
                    new_enemy = map_new(self.robot_point, all_region, xxyys, keymouse.M)
                    if new_enemy:
                        if isinstance(self.cserial, Serial):
                            self.cserial.sendLocation(new_enemy)
                if CONFIG_ismatrix:
                    self.frame = darwyuan(self.frame, keymouse.position)
                self.frame = cv2.resize(self.frame, (1920, 768))
                cv2.namedWindow("cap", cv2.WINDOW_NORMAL)
                cv2.imshow("cap", self.frame)
            else:
                keymouse.keyboard(k, self.frame)
                keymouse.mouse()
                keymouse.viwe()
            if k == 109:
                cv2.imwrite(CONFIG_saveimg_path, self.img)
            if k == 27:
                nRet = shutdown(cvImage, nRet, streamSource, camera, CNT)
                if nRet != 0:
                    print("Some Error happend")
                print("--------- Demo end ---------")
                break

    def openVideo(self):
        mouse_position = []
        path = CONFIG_VID_path
        cap = cv2.VideoCapture(path)
        xxyys = poly_maxmin_xy(all_region)
        keymouse = Keypoly(mouse_position)
        while self.isLoop:
            self.t1 = time.time()
            ret, self.img = cap.read()
            k = cv2.waitKey(1)
            self.img = cv2.resize(self.img, (1920, 768))
            h1, w1, c1 = self.img.shape[:]
            self.img = cv2.resize(self.img, (w1 // 2, h1 // 2))
            self.frame = self.img
            if keymouse.isfinish:
                """通讯发送识别位置信息"""
                self.frame, self.robot_point = detect(self.frame)
                if self.robot_point:
                    new_enemy = map_new(self.robot_point, all_region, xxyys, keymouse.M)
                    if new_enemy:
                        if k == 97:
                            cv2.waitKey(0)
                        self.cserial.sendLocation(new_enemy)
                if CONFIG_ismatrix:
                    self.frame = darwyuan(self.frame, keymouse.position)
                self.frame = cv2.resize(self.frame, (1920, 768))
            else:
                keymouse.keyboard(k, self.frame)
                keymouse.mouse()
                keymouse.viwe()
            if k == 109:
                cv2.imwrite(CONFIG_saveimg_path, self.img)
            if k == 27:
                cap.release()
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":
    x = Camera()
    x.start()

    x.join()
