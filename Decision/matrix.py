import numpy as np
import cv2

"""p_mouse是在摄像头拍到的部分中选了[432:1200, 0:1920], 然后在x,y除2下的点

    p_map是小地图的下x, y都除于2下的点
"""
# 定义比例因子
x_factor = 1920 / 3840
y_factor = 768 / 1200
select_x = 1
select_y = 1
map_w = 679 // 2
map_h = 1229 // 2
sorce_img_w = 1920 // 2
sorce_img_h = 768 // 2

"warining!!"
warning_area_my = [[14, 71], [13, 276], [32, 272], [32, 214], [70, 212], [71, 177], [101, 156], [101, 111], [71, 111], [67, 71]]
warning_area_enemy = [[327, 338], [305, 337], [306, 402], [274, 404], [274, 404], [274, 438], [235, 463], [235, 509], [328, 509]]

"""小地图上的预警区域"""
fly_list = [155, 291]  # 飞坡预警金和区域预警 都是小地图上的
region_list = []
warning_area_a = [[127, 378], [123, 416], [187, 416], [182, 377]]

"""原图中感兴趣区域"""
sentry_poly = [[340, 226], [335, 326], [703, 300], [643, 210]]
old_area_a = [[44, 393], [45, 419], [62, 396], [126, 429], [192, 401], [188, 370], [135, 395], [72, 370]]
old_area_b = [[262, 44], [274, 102], [302, 142], [310, 349], [327, 342], [328, 44]]     # 敌方吊射点

p_map = [[12, 36], [12, 509], [328, 509], [328, 36]]  # M
p_mouse = [[236, 83], [16, 295], [807, 264], [518, 75]]
M = cv2.getPerspectiveTransform(np.float32(p_mouse), np.float32(p_map))

"""old_regin是透视变换图像中的区域块"""
# # 上边环形高地
right_old_region = [[138, 108], [106, 204], [112, 254], [141, 149], [184, 174], [274, 232], [290, 313], [302, 292],
                    [293, 189], [228, 133]]      # 敌方环高
lower_old_region = [[40, 306], [46, 354], [79, 345], [129, 391], [206, 397], [233, 422],
                    [237, 376], [191, 364], [140, 354], [76, 294]]      # 我方环高
fly_old_poly = [[14, 131], [12, 242], [28, 243], [27, 138]]
diaofly_old_poly = [[15, 273], [14, 391], [37, 392], [35, 275]]
buff_old_poly = [[23, 44], [26, 107], [54, 106], [52, 41]]
mybuff_old_poly = [[309, 385], [308, 455], [291, 491], [310, 488], [328, 444], [328, 389]]
Rhigh_old_poly = [[60, 59], [60, 135], [96, 124], [96, 51]]
myRhigh_old_poly = [[293, 439], [268, 462], [269, 518], [327, 508], [327, 484], [289, 492]]
base_old_poly = [[97, 44], [109, 192], [116, 177], [138, 108], [148, 105], [149, 39]]
outpost_old_poly = [[102, 143], [39, 157], [40, 295], [48, 301], [76, 294], [99, 310], [111, 285]]
myoutpost_old_poly = [[287, 335], [237, 376], [233, 422], [281, 437], [299, 433], [299, 345]]
sentry_old_poly = [[116, 476], [121, 563], [249, 547], [246, 489]]
center_old_poly = [[99, 310], [140, 343], [198, 357], [282, 340], [221, 246], [159, 252]]
# righthuan_old_poly = [[255, 121], [250, 153], [294, 241], [301, 218]]
our_old_region = [[38, 355], [37, 392], [116, 476], [246, 489], [281, 439], [233, 422], [191, 456], [126, 448]]
mydiao_old_poly = [[14, 391], [13, 510], [104, 524], [104, 463], [37, 392]]
all_region = [lower_old_region, right_old_region, fly_old_poly, diaofly_old_poly, buff_old_poly, mybuff_old_poly,
              Rhigh_old_poly, myRhigh_old_poly, base_old_poly, outpost_old_poly, myoutpost_old_poly, sentry_old_poly,
              center_old_poly, our_old_region, old_area_b, mydiao_old_poly]
"原图roi"
# old = [[199, 131], [199, 170], [254, 164], [324, 164], [454, 163], [523, 170], [494, 218],
#        [446, 164], [347, 161], [250, 167]]    # 我方环高
# old = [[337, 121], [311, 114], [314, 128], [352, 100], [399, 104], [479, 111], [514, 165], [519, 158], [522, 104], [441, 94]] #敌方环高
# old = [[497, 51], [497, 60], [518, 94], [669, 120], [697, 117], [558, 52]]    # 敌方吊射点
# old = [[213, 77], [184, 105], [204, 105], [225, 77]]  # 敌方飞坡点
# old = [[235, 61], [237, 95], [265, 94], [261, 60]]  # 敌方打符点
# old = [[177, 160], [204, 159], [116, 218], [154, 221]]   # 敌方R高
# old = [[312, 82], [315, 111], [324, 107], [349, 92], [359, 91], [359, 80]] # 敌方基地
old = [[242, 105], [231, 93], [219, 147], [210, 145], [261, 143], [291, 148], [311, 100]]   # 敌方前哨站
# old = [[289, 277], [281, 366], [659, 322], [591, 250]]      # 我方哨兵巡逻区
# old = [[351, 148], [279, 170], [348, 160], [414, 184], [518, 175], [416, 146]]    # 中心点
# old = [[518, 53], [518, 58], [598, 74], [600, 69]]      # 敌方右环形
# old = [[549, 128], [496, 151], [528, 173], [608, 185], [636, 181], [571, 132]]      # 我方前哨站
# old = [[182, 149], [163, 175], [291, 249], [581, 236], [610, 186], [528, 173], [439, 245], [312, 242]]    # 我方空地
# old = [[202, 104], [127, 166], [170, 163], [226, 106]]      # 敌方右环形
# old = [[168, 144], [114, 201], [152, 199], [194, 143]]   # 敌方飞坡落点
# old = [[115, 218], [16, 286], [253, 295], [269, 238], [155, 221]]   # 我方吊射点
# old = [[419, 111], [436, 117], [484, 93], [551, 179], [574, 175], [465, 109]]   # 敌方吊射点
# old = [[646, 205], [616, 224], [674, 280], [792, 247], [752, 221], [683, 233]]   # 我方R高
# old = [[613, 151], [677, 197], [688, 232], [724, 227], [701, 187], [645, 152]]   # 我方打符点


"""小地图上的区域块"""
right_new_region = [[152, 201], [107, 233], [117, 262], [163, 230], [204, 228],
                    [256, 267], [284, 291], [303, 265], [275, 243], [216, 201]]       # 对方全环高
lower_new_region = [[32, 321], [32, 349], [62, 372], [123, 411], [186, 413],
                    [233, 385], [219, 356], [180, 382], [134, 384], [51, 332]]      # 我方环高
fly_new_poly = [[12, 155], [12, 274], [32, 274], [32, 155]]
diaofly_new_poly = [[12, 291], [12, 416], [32, 416], [32, 291]]
buff_new_poly = [[38, 136], [38, 209], [64, 209], [64, 136]]
mybuff_new_poly = [[273, 401], [273, 436], [273, 477], [303, 477], [303, 439], [303, 401]]
Rhigh_new_poly = [[69, 108], [69, 177], [101, 155], [101, 108]]
myRhigh_new_poly = [[273, 434], [234, 460], [234, 509], [327, 509], [327, 477], [273, 477]]
base_new_poly = [[112, 36], [112, 162], [130, 214], [152, 199], [166, 199], [166, 36]]
outpost_new_poly = [[36, 212], [36, 315], [57, 323], [103, 287], [103, 168], [69, 185], [69, 212]]
myoutpost_new_poly = [[277, 290], [220, 360], [236, 387], [272, 401], [305, 401], [305, 305]]
sentry_new_poly = [[115, 457], [115, 509], [224, 509], [224, 457]]
center_new_poly = [[57, 323], [137, 373], [178, 373], [277, 289], [202, 238], [166, 238]]
our_new_region = [[32, 353], [32, 408], [115, 457], [231, 457], [272, 401], [236, 387], [187, 417], [124, 417]]
warning_area_b = [[236, 109], [236, 157], [306, 202], [306, 323], [328, 323], [328, 109]]
mydiao_new_poly = [[12, 416], [12, 509], [102, 509], [102, 459], [34, 416]]

"""二次投影矩阵"""
low_m, _ = cv2.findHomography(np.float32(lower_old_region), np.float32(lower_new_region))
rig_m, _ = cv2.findHomography(np.float32(right_old_region), np.float32(right_new_region))
fly_m, _ = cv2.findHomography(np.float32(fly_old_poly), np.float32(fly_new_poly))
diaofly_m, _ = cv2.findHomography(np.float32(diaofly_old_poly), np.float32(diaofly_new_poly))
buff_m, _ = cv2.findHomography(np.float32(buff_old_poly), np.float32(buff_new_poly))
mybuff_m, _ = cv2.findHomography(np.float32(mybuff_old_poly), np.float32(mybuff_new_poly))
Rhigh_m, _ = cv2.findHomography(np.float32(Rhigh_old_poly), np.float32(Rhigh_new_poly))
myRhigh_m, _ = cv2.findHomography(np.float32(myRhigh_old_poly), np.float32(myRhigh_new_poly))
base_m, _ = cv2.findHomography(np.float32(base_old_poly), np.float32(base_old_poly))
outpost_m, _ = cv2.findHomography(np.float32(outpost_old_poly), np.float32(outpost_new_poly))
myoutpost_m, _ = cv2.findHomography(np.float32(myoutpost_old_poly), np.float32(myoutpost_new_poly))
sentry_m, _ = cv2.findHomography(np.float32(sentry_old_poly), np.float32(sentry_new_poly))
center_m_1, _ = cv2.findHomography(np.float32(center_old_poly), np.float32(center_new_poly))
our_m, _ = cv2.findHomography(np.float32(our_old_region), np.float32(our_new_region))
Thigh_m, _ = cv2.findHomography(np.float32(old_area_b), np.float32(warning_area_b))
mydiao_m, _= cv2.findHomography(np.float32(mydiao_old_poly), np.float32(mydiao_new_poly))
all_m = [low_m, rig_m, fly_m, diaofly_m, buff_m, mybuff_m, Rhigh_m, myRhigh_m, base_m, outpost_m, myoutpost_m,
         sentry_m, center_m_1,  our_m, Thigh_m, mydiao_m]  # 矩阵(16个)

all_old_roi = [fly_old_poly, old_area_a, old_area_b, sentry_poly, buff_old_poly]
all_roi = []  # 经过mouse类后生成

points = []


def capture_event(event, x, y, flags, param):
    global points
    # 检测鼠标左键单击事件
    if event == cv2.EVENT_LBUTTONDOWN <= 3:
        # 将点击的坐标添加到列表中
        print([x, y])
        points.append([x, y])


def darwyuan(img, p_mouse):
    _M = cv2.getPerspectiveTransform(np.float32(p_map), np.float32(p_mouse))
    m = cv2.getPerspectiveTransform(np.float32(p_mouse), np.float32(p_map))
    area_a = cv2.perspectiveTransform(np.array(lower_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    right_poly = cv2.perspectiveTransform(np.array(right_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    fly_poly = cv2.perspectiveTransform(np.array(fly_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    diaofly_poly = cv2.perspectiveTransform(np.array(diaofly_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    buff_poly = cv2.perspectiveTransform(np.array(buff_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    mybuff_poly = cv2.perspectiveTransform(np.array(mybuff_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    our_region = cv2.perspectiveTransform(np.array(our_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    outpost_poly = cv2.perspectiveTransform(np.array(outpost_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    myoutpost_poly = cv2.perspectiveTransform(np.array(myoutpost_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    Rhigh_poly = cv2.perspectiveTransform(np.array(Rhigh_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    myRhigh = cv2.perspectiveTransform(np.array(myRhigh_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    base_poly = cv2.perspectiveTransform(np.array(base_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    center_poly = cv2.perspectiveTransform(np.array(center_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    sentry_poly = cv2.perspectiveTransform(np.array(sentry_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    area_b = cv2.perspectiveTransform(np.array(old_area_b, dtype=np.float32).reshape(1, -1, 2), _M)
    mydiao = cv2.perspectiveTransform(np.array(mydiao_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    m_old = cv2.perspectiveTransform(np.array(old, dtype=np.float32).reshape(1, -1, 2), m)
    cv2.polylines(img, np.array([p_mouse], dtype=np.int32), 1, 255)
    cv2.polylines(img, np.array([myRhigh[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([mybuff_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([diaofly_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([our_region[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([myoutpost_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([right_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([center_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([sentry_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([outpost_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([base_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([Rhigh_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([buff_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([fly_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([area_a[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([area_b[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img, np.array([mydiao[0]], dtype=np.int32), 1, (0, 255, 0))
    return img


def darwallpoly(img1, img2, img_h):
    """green ROI"""
    # 原图

    cv2.polylines(img1, np.array([p_mouse], dtype=np.int32), 1, 255)
    cv2.polylines(img1, np.array([myRhigh[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([mybuff_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([diaofly_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([our_region[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([myoutpost_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([right_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([center_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([sentry_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([outpost_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([base_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([Rhigh_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([buff_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([fly_poly[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([area_a[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([area_b[0]], dtype=np.int32), 1, (0, 255, 0))
    cv2.polylines(img1, np.array([mydiao[0]], dtype=np.int32), 1, (0, 255, 0))

    """blue ROI"""
    # 透视变换
    cv2.polylines(img_h, np.array([lower_old_region], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([right_old_region], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([fly_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([diaofly_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([buff_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([mybuff_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([outpost_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([myoutpost_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([Rhigh_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([myRhigh_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([center_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([sentry_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([base_old_poly], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([our_old_region], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([old_area_b], dtype=np.int32), 1, 255)
    cv2.polylines(img_h, np.array([mydiao_old_poly], dtype=np.int32), 1, 255)

    """map red ROI"""
    cv2.polylines(img2, np.array([fly_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([buff_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([warning_area_b], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([myRhigh_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([mybuff_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([mydiao_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([base_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([lower_new_region], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([right_new_region], dtype=np.int32), 1, (0, 0, 255))
    cv2.polylines(img2, np.array([our_new_region], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([diaofly_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([center_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([myoutpost_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([outpost_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([sentry_new_poly], dtype=np.int32), 1, (0, 255, 255))
    cv2.polylines(img2, np.array([Rhigh_new_poly], dtype=np.int32), 3, (0, 255, 255))
    cv2.polylines(img2, np.array([p_map], dtype=np.int32), 3, (0, 0, 0))
    cv2.circle(img2, (293, 241), 1, (255, 255, 255), 1)    # 预警区
    cv2.circle(img2, (300, 241), 1, (255, 255, 255), 1)  # 预警区
    cv2.circle(img2, (287, 235), 1, (255, 255, 255), 1)  # 预警区
    return img1, img2, img_h


if __name__ == "__main__":
    img1 = cv2.imread("E:/mytest/Location/National3.jpg")
    img1 = cv2.resize(img1, (1920, 768))
    img2 = cv2.imread("E:/mytest/Location/allmap.jpg")
    h1, w1, c1 = img1.shape[:]
    h2, w2, c2 = img2.shape[:]
    img1 = cv2.resize(img1, (w1 // 2, h1 // 2))
    img2 = cv2.resize(img2, (w2 // 2, h2 // 2))
    _M = cv2.getPerspectiveTransform(np.float32(p_map), np.float32(p_mouse))
    m = cv2.getPerspectiveTransform(np.float32(p_mouse), np.float32(p_map))
    fly_poly = cv2.perspectiveTransform(np.array(fly_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)[0]
    xmin = np.min(fly_poly, axis=0)[0]
    ymin = np.min(fly_poly, axis=0)[1]
    xmax = np.max(fly_poly, axis=0)[0]
    ymax = np.max(fly_poly, axis=0)[1]
    img_h = cv2.warpPerspective(img1, M, (w2 // 2, h2 // 2))
    points = [187, 119]
    points1 = [99, 323]
    cv2.circle(img_h, tuple(map(int, points)), 5, (0, 0, 255), -1)

    cv2.circle(img_h, tuple(map(int, points1)), 5, (0, 0, 255), -1)
    get_point1 = cv2.perspectiveTransform(np.array(points1, dtype=np.float32).reshape(-1, 1, 2), low_m)
    get_point1 = get_point1.reshape(get_point1.shape[0], 2)
    get_point1 = get_point1.flatten()  # 展平数组
    cv2.circle(img2, tuple(map(int, get_point1)), 5, (0, 0, 255), -1)  # 在地图上绘制蓝色圆形

    area_a = cv2.perspectiveTransform(np.array(lower_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    right_poly = cv2.perspectiveTransform(np.array(right_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    fly_poly = cv2.perspectiveTransform(np.array(fly_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    diaofly_poly = cv2.perspectiveTransform(np.array(diaofly_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    buff_poly = cv2.perspectiveTransform(np.array(buff_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    mybuff_poly = cv2.perspectiveTransform(np.array(mybuff_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    our_region = cv2.perspectiveTransform(np.array(our_old_region, dtype=np.float32).reshape(1, -1, 2), _M)
    outpost_poly = cv2.perspectiveTransform(np.array(outpost_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    myoutpost_poly = cv2.perspectiveTransform(np.array(myoutpost_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    Rhigh_poly = cv2.perspectiveTransform(np.array(Rhigh_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    myRhigh = cv2.perspectiveTransform(np.array(myRhigh_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    base_poly = cv2.perspectiveTransform(np.array(base_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    center_poly = cv2.perspectiveTransform(np.array(center_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    sentry_poly = cv2.perspectiveTransform(np.array(sentry_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    area_b = cv2.perspectiveTransform(np.array(old_area_b, dtype=np.float32).reshape(1, -1, 2), _M)
    mydiao = cv2.perspectiveTransform(np.array(mydiao_old_poly, dtype=np.float32).reshape(1, -1, 2), _M)
    m_old = cv2.perspectiveTransform(np.array(old, dtype=np.float32).reshape(1, -1, 2), m)
    print(m_old)
    img1, img2, img_h = darwallpoly(img1, img2, img_h)
    cv2.namedWindow("Mini Map", cv2.WINDOW_NORMAL)
    cv2.namedWindow("source", cv2.WINDOW_NORMAL)
    cv2.imshow("Mini Map", img2)  # 小地图
    cv2.imshow("source", img1)  # 原图
    cv2.setMouseCallback("source", capture_event)
    cv2.setMouseCallback("Mini Map", capture_event)
    if cv2.waitKey(0) == 27:
        cv2.destroyAllWindows()

