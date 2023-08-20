# 检验导入路径
from Camera.Demo import demo, shutdown
from Decision.Mouse import Keypoly
from Decision.cameradetect import *
from Serial.myserial import *
import threading
__presentDir = os.path.join(os.getcwd(), os.path.dirname(__file__))
sys.path.insert(0, __presentDir)

draw_color = CONFIG_draw_color


class Camera(threading.Thread):
    def __init__(self, name):
        Thread.__init__(self, name=name)
        self.mycolor = CONFIG_mycolor
        self.enemycolor = CONFIG_enemycolor
        self.isLoop = CONFIG_isLoop
        self.printFPS = CONFIG_printFPS
        self.frame = np.zeros(())
        self.robot_point = None
        self.dst = None
        self.img = None
        self.gettime = None

    def run(self):
        print("[INFO]::Thread-Camera running")
        self.process()

    def stop(self):
        self.isLoop = False
        print("[INFO]::Thread-Locator stopped")

    def process(self):
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

    def capture_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN <= 3:
            print(x, y)

    def setFrame(self):
        CNT = 0
        mouse_position = []
        xxyys = poly_maxmin_xy(all_region)
        keymouse = Keypoly(mouse_position)
        while self.isLoop:
            self.t1 = time.time()
            if CNT == 0:
                map_test = map.copy()
                cvImage, nRet, streamSource, camera, CNT = demo(None, None, None, None, CNT)
                print(len(cvImage))
            else:
                cvImage, nRet, streamSource, camera, CNT = demo(cvImage, nRet, streamSource, camera, CNT)
            self.dst = np.zeros((1200, 1920 * CNT, 3), dtype=np.uint8)
            for i in range(0, len(cvImage)):
                self.dst[0:1200, 1920 * i:1920 * (i + 1)] = cvImage[i]
            if CNT == 2:
                self.src = np.zeros((1200, (1920 - self.crop_width) * CNT, 3), dtype=np.uint8)
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
            if self.savevideo is True:
                self.getpickvi.write(self.img)
                self.getyuanvi.write(self.dst)
            cvImage.clear()
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
                        self.sendLocation(new_enemy)
                if CONFIG_ismatrix:
                    self.frame = darwyuan(self.frame, keymouse.position)
                self.frame = cv2.resize(self.frame, (1920, 768))
                cv2.namedWindow("cap", cv2.WINDOW_NORMAL)
                cv2.imshow("cap", self.frame)
                cv2.setMouseCallback("cap", capture_event)
            else:
                keymouse.keyboard(k, self.frame)
                keymouse.mouse()
                keymouse.viwe()
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
                        self.sendLocation(new_enemy)
                if CONFIG_ismatrix:
                    self.frame = darwyuan(self.frame, keymouse.position)
                self.frame = cv2.resize(self.frame, (1920, 768))
                cv2.namedWindow("cap", cv2.WINDOW_NORMAL)
                cv2.imshow("cap", self.frame)
                cv2.setMouseCallback("cap", capture_event)
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
                time.sleep(0.1)
            else:
                continue
        print("isgetID", isgetID)
        cv2.namedWindow("lastmap", cv2.WINDOW_NORMAL)
        cv2.imshow("lastmap", lastmap)

if __name__ == "__main__":
    x = Camera()
    x.start()

    x.join()
