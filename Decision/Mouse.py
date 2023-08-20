# from testcamera import *
from Decision.matrix import *

class Keypoly:
    def __init__(self, position: list):
        self.position = position
        # self.position = [[227, 102], [29, 271], [948, 271], [707, 81]]
        self.dst_point = (1920, 1184)  # 变换目标大小
        self.M = None
        self.isfinish = False
        self.getwin_name = "getwindow"
        self.getwindow = cv2.namedWindow(self.getwin_name, cv2.WINDOW_NORMAL)
        self.splicing_img = None
        self.temporary_xy = []
        self.EVENT_LBUTTONDOWN = cv2.EVENT_LBUTTONDOWN
        self.EVENT_MOUSEMOVE = 0
        self.key_new = None
        self.key_withdraw = None
        self.toushi_dst = None
        self.count = 0
        self.mini_size = (100, 100)
        self.radius = 5
        self.circle_color = (0, 255, 0)
        self.arrowedLine_color = (125, 0, 255)
        self.line_color = (0, 0, 255)
        self.circle_thickness = -1  # 画实心圆
        self.arrowedLine_thickness = 2

    def capture_event(self, event, x, y, flags, param):
            self.temporary_xy = [x, y]
            if event == self.EVENT_LBUTTONDOWN:
                print(x, y)
                self.position.append([x, y])

    def mouse(self):
        if self.key_new and len(self.position) < 5:
            cv2.imshow(self.getwin_name, self.splicing_img)
            cv2.setMouseCallback(self.getwin_name, self.capture_event)

    def keyboard(self, k, img):
        self.splicing_img = img
        self.key_withdraw = k if (k == ord('z' or 'Z') and 0 < len(self.position) < 4) else None
        self.key_new = k if (k == ord('n' or 'N') and 0 <= len(self.position) < 4) else None
        if self.key_withdraw:
            del self.position[-1]

    def make_roi(self, m):
        for poly in all_old_roi:
            # print("2")
            area = cv2.perspectiveTransform(np.array(poly, dtype=np.float32).reshape(1, -1, 2), m)[0]
            xmin = np.min(area, axis=0)[0] if np.min(area, axis=0)[0] >= 0 else 0
            ymin = np.min(area, axis=0)[1] if np.min(area, axis=0)[1] >= 0 else 0
            xmax = np.max(area, axis=0)[0] if np.max(area, axis=0)[0] <= sorce_img_w else sorce_img_w
            ymax = np.max(area, axis=0)[1] if np.max(area, axis=0)[1] <= sorce_img_h else sorce_img_h
            all_roi.append([ymin, ymax, xmin, xmax])

    def viwe(self):
        if self.temporary_xy and self.temporary_xy[0] >= 10 and self.temporary_xy[1] >= 10:
            mini_img = self.splicing_img[self.temporary_xy[1] - 10:self.temporary_xy[1] + 10,
                       self.temporary_xy[0] - 10:self.temporary_xy[0] + 10]
            mini_img = cv2.resize(mini_img, self.mini_size)
            cv2.line(mini_img, (mini_img.shape[1] // 2, mini_img.shape[0] // 2 - 2),
                     (mini_img.shape[1] // 2, mini_img.shape[0] // 2 + 2), (0, 255, 0))
            cv2.line(mini_img, (mini_img.shape[1] // 2 - 2, mini_img.shape[1] // 2),
                     (mini_img.shape[0] // 2 + 2, mini_img.shape[0] // 2), (0, 255, 0))
        if self.temporary_xy and 0 < len(self.position) < 4:
            position = self.position.copy()
            position.append(self.temporary_xy)
            for i, p in enumerate(position[0:-1]):
                cv2.circle(self.splicing_img, (p[0], p[1]), self.radius, self.circle_color, self.circle_thickness)
                cv2.arrowedLine(self.splicing_img, (p[0], p[1]), (position[i + 1][0], position[i + 1][1]),
                                self.arrowedLine_color, self.arrowedLine_thickness)

        if len(self.position) == 4:
            # self.position = [[227, 102], [29, 271], [948, 271], [707, 81]]
            self.M = cv2.getPerspectiveTransform(np.float32(self.position), np.float32(p_map))
            m = cv2.getPerspectiveTransform(np.float32(p_map), np.float32(self.position))
            self.make_roi(m)
            self.isfinish = True
            cv2.destroyWindow(self.getwin_name)