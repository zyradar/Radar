from shapely.geometry import LineString
from pasta import augment
from Location.models.common import DetectMultiBackend
from Location.utils.general import *
from Location.utils.general import (check_img_size, non_max_suppression)
from Location.utils.torch_utils import select_device
from Decision.matrix import *
from configfile import *

weights = CONFIG_colormodel_path
weightsmath = CONFIG_mathmodel_path

# 模型配置
imgsz = CONFIG_imgsz  # 输入图片的大小 默认640(pixels)
conf_thres = CONFIG_conf_thres  # object置信度阈值 默认0.25  用在nms中
iou_thres = CONFIG_iou_thres  # 做nms的iou阈值 默认0.45   用在nms中
max_det = CONFIG_max_det  # 每张图片最多的目标数量  用在nms中
device = CONFIG_device  # 设置代码执行的设备 cuda device, i.e. 0 or 0,1,2,3 or cpu
classes = CONFIG_classes  # 在nms中是否是只保留某些特定的类 默认是None 就是所有类只要满足条件都可以保留 --class 0, or --class 0 2 3
agnostic_nms = CONFIG_agnostic_nms  # 进行nms是否也除去不同类别之间的框 默认False
augment = CONFIG_augment  # 预测是否也要采用数据增强 TTA 默认False
visualize = CONFIG_visualize  # 特征图可视化 默认FALSE
half = CONFIG_half  # 是否使用半精度 Float16 推理 可以缩短推理时间 但是默认是False
dnn = CONFIG_dnn  # 使用OpenCV DNN进行ONNX推理

# 载入模型
device = select_device(device)  # 获取设备
model_color = DetectMultiBackend(weights, device=device, dnn=dnn, fp16=half)
model_math = DetectMultiBackend(weightsmath, device=device, dnn=dnn, fp16=half)
stride = model_color.stride
imgsz = check_img_size(imgsz)  # 检查图片尺寸

names = CONFIG_names
enemycolor = CONFIG_enemycolor
points_count = [0, 0, 0, 0, 0, 0]
prev_all_point = []


def get_distance(nowpoint, lastpoint):                      # 计算两点距离
    return int((nowpoint[0] ** 2 + nowpoint[1] ** 2) + (lastpoint[0] ** 2 + lastpoint[1] ** 2))


def distance_matching(all_point, prev_all_point):           # 前后帧距离匹配
    new_all_point = []  #
    new_prev_all_point = []  #
    now_handled = []
    prev_handled = []
    FtoL = False
    i = 0
    nearest_index = None
    if len(all_point) < len(prev_all_point):
        bigpoints = prev_all_point
        smallpoints = all_point
    elif len(all_point) >= len(prev_all_point):
        bigpoints = all_point
        smallpoints = prev_all_point
        FtoL = True
    while i < len(smallpoints):     # 根据距离判断是否为同一目标
        if smallpoints[i]:
            x1, y1, color1, math1, conf1 = smallpoints[i]
            min_distance = float('inf')
            nearest_index = None    # 上下两帧相邻的点，疑似同一目标
            j = 0  # 初始化索引
            while j < len(bigpoints):
                if bigpoints[j]:
                    x2, y2, color2, math2, conf2 = bigpoints[j]
                    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5     # 计算两点之间的距离
                    if 0 < distance <= 35:      # 如果距离小于最小距离，则更新最小距离和最近点的索引
                        if distance < min_distance:
                            min_distance = distance
                            nearest_index = j
                j += 1
        if FtoL:    # 对前后帧进行索引
            now_index = nearest_index
            prev_index = i
        else:
            now_index = i
            prev_index = nearest_index
        if nearest_index:
            new_all_point.append(all_point[now_index])  # 单纯传输当前帧已匹配的数据
            now_handled.append(now_index)   # 当前帧中已匹配好的点下标
            new_prev_all_point.append(prev_all_point[prev_index])    # 单纯传输上一帧已匹配的数据
            prev_handled.append(prev_index)     # 上一帧中已匹配好的点下标
        i += 1
    return new_all_point, now_handled, new_prev_all_point, prev_handled


def divideID(conf, result_points, point, conf_one):     # 对未识别出ID的点随机分配ID
    i = 3
    while i < 6:
        if result_points[str(i)]:
            i += 1
            continue
        else:
            point[3] = str(i)
            point[4] = conf_one
            conf[point[3]] = conf_one
            result_points[point[3]] = point
            i += 1
            break
    return conf, result_points


def ControlID(result, prev_all_point):                  # ID归类
    result_ture = []
    # 完全信任的匹配点
    for i in range(0, 6):
        if result[i] and prev_all_point[i]:
            distance = get_distance(result[i], prev_all_point[i])
            if 0 <= distance <= 40:
                result_ture.append(i)
    # 管理未完全信任点
    result_doubt = [i for i in range(0, 6) if i not in result_ture]
    for i in result_doubt:
        for j in result_doubt:
            if result[i] and prev_all_point[j]:
                distance = get_distance(result[i], prev_all_point[j])
                if distance > 60:
                    if int(prev_all_point[j][4] - result[i][4]) > 0.3:  # conf相差大
                        if prev_all_point[j][4] > result[i][4]:
                            result[i] = prev_all_point[j]
                    elif result[i][4] > 0.5:  # 处理识别点，随机点信任当前帧不做处理
                        for k in result_doubt:
                            if result[k]:
                                distance_kj = get_distance(result[k], prev_all_point[j])
                                if 0 <= distance_kj <= 40:  # 处理有匹配点，对无匹配点信任当前帧不处理
                                    if prev_all_point[k]:
                                        if result[k][4] > 0.5 and prev_all_point[k][4] > 0.5:  # 都是识别点时处理
                                            distance_jk = get_distance(result[j], prev_all_point[k])
                                            if 0 <= distance_jk <= 40:  # 匹配成功，ID互换
                                                result[j][3] = prev_all_point[k][3]
                                                result[k][3] = prev_all_point[j][3]
                                            else:  # 匹配失败，信任上一帧
                                                result[j] = prev_all_point[j]
                                                result[k] = prev_all_point[k]
                                        elif result[k][4] <= 0.5 and prev_all_point[k][4] > 0.5:  # 上一帧为识别点，当前帧为随机点时
                                            result[j] = prev_all_point[j]
                                            result[k] = prev_all_point[k]
                                    elif result[k][4] <= 0.5:
                                        result[j] = prev_all_point[j]
    return result, prev_all_point


def calc_speed(track_now, track_last):      # 根据前后帧计算目标移动速度，推算出下一帧的位置
    # x1, y1, color1, math1, conf1 = track_now
    pos2 = np.array(track_now[0:2])  # 当前帧的位置
    if track_last is not None:
        pos1 = np.array(track_last[0:2])  # 上一帧的位置
        d = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
        direction = pos2 - pos1     # 获得np坐标[   12,     2]
        if d == 0:
            normalized_direction = 0
            new_length = 0
        elif 0 < d < 5:
            normalized_direction = direction / d
            new_length = d
        else:
            normalized_direction = direction / d
            new_length = 5
        pos2 = pos1 + (normalized_direction * new_length)
    next_point = [pos2[0], pos2[1], track_now[2], track_now[3], track_now[4]]
    return next_point


def map_new(enemy_points, areas, xxyys, m):
    # enemy_points[color, math, centerx, centery, conf]
    get_point = []
    all_point = []
    def _distance(next_point):
        return (int(next_point[2]) ** 2 + int(next_point[3]) ** 2) ** 0.5
    global prev_all_point
    enemy_points = sorted(enemy_points, key=_distance)  # 对 enemy_points 中的每个点按照距离原点的距离进行排序
    len_enemy = len(enemy_points)
    for i in range(len_enemy):
        get_point.append(enemy_points[i][2:4])
    get_point = cv2.perspectiveTransform(np.array(get_point, dtype=np.float32).reshape(-1, 1, 2), m)
    get_point = get_point.reshape(get_point.shape[0], 2)

    for i in range(len_enemy):
        for index, xxyy in enumerate(xxyys):    # 判断该点是否在某块区域内
            if xxyy[0] <= get_point[i][0] <= xxyy[1] and xxyy[2] <= get_point[i][1] <= xxyy[3]:  # 纠正
                if pwpoly(get_point[i], areas[index]):  # areas框出的所有指定区域
                    get_point[i] = cv2.perspectiveTransform(np.array(get_point[i], dtype=np.float32).reshape(-1, 1, 2),
                                                            all_m[index])[0][0]
                    break
        all_point.append([])    # all_point[centerx, centery, color, math, conf]
        all_point[i].append(get_point[i][0])
        all_point[i].append(get_point[i][1])
        all_point[i].append(enemy_points[i][0])
        all_point[i].append(enemy_points[i][1])
        all_point[i].append(enemy_points[i][4])

    disappeared_points = []  # 储存上一帧消失的点
    # 将已匹配好且前后帧类相同的数据归类处理
    new_all_point, now_handled, new_prev_all_point, prev_handled = distance_matching(all_point, prev_all_point)


    # 将已匹配好的点做归类处理
    conf = {'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    result_points = {'0': None, '1': None, '2': None, '3': None, '4': None, '5': None}
    if new_all_point and new_prev_all_point:
        for now_point, prev_point in zip(new_all_point, new_prev_all_point):
            if now_point[3] == prev_point[3] and now_point[4] > conf[now_point[3]] and now_point[3] != 6:
                conf[now_point[3]] = now_point[4]
                result_points[now_point[3]] = now_point
            elif now_point[3] != 6 or prev_point[3] != 6:
                now_point[3] = now_point[3] if now_point[3] != 6 else prev_point[3]
                if now_point[4] > conf[now_point[3]]:
                    conf[now_point[3]] = now_point[4]
                    result_points[now_point[3]] = now_point
            else:
                conf, result_points = divideID(conf, result_points, now_point, 0.5)

    for index, point in enumerate(all_point):   # 处理未匹配的当前帧all_point
        if index not in now_handled:
            if point[3] != 6 and point[4] > conf[point[3]]:
                if result_points[point[3]]:
                    continue
                else:
                    conf[point[3]] = point[4]
                    result_points[point[3]] = point
            else:
                conf, result_points = divideID(conf, result_points, point, 0.3)

    for index, point in enumerate(prev_all_point):   # 处理未匹配的上一帧prev_all_point
        if index not in prev_handled:  # 储存消失点
            disappeared_points.append(point)

    result = list(result_points.values())
    if prev_all_point:
        result, prev_all_point = ControlID(result, prev_all_point)
        print("prev_all_point", prev_all_point)

        # # 消失点中补齐缺失点（视野残留）有问题，待修改
        # for index, point in enumerate(disappeared_points):
        #     if index == 1:
        #         continue
        #     result[index] = result[index] if result[index] else disappeared_points[index]

        # 视野残留消失
        if all(result):
            for i in range(0, 6):
                try:
                    if result[i] == prev_all_point[i]:
                        points_count[i] += 1
                except:
                    continue
        for i in range(0, 6):
            if points_count[i] == 5:
                result[i] = None
                prev_all_point[i] = None

        # A点插眼
        result[1] = result[1] if result[1] else [random.randint(287, 300), random.randint(235, 241), enemycolor, '1', 0.5]
    prev_all_point = result
    return result


def iscrosses(line1, line2):
    # 判断共线
    if LineString(line1).crosses(LineString(line2)):
        return 1
    return 0


def pwpoly(point, area):
    # 区域块
    maxy = 2000
    edge = len(area)
    up_cross = 0
    low_cross = 0
    upline = [[point[0], 0], point]
    lowline = [point, [point[0], maxy]]
    for i in range(edge):
        if (area[i - 1][0] <= point[0] <= area[i][0]) or (area[i][0] <= point[0] <= area[i - 1][0]):
            if up_cross == 0:
                up_cross += iscrosses(upline, [area[i - 1], area[i]])
            if low_cross == 0:
                low_cross += iscrosses(lowline, [area[i - 1], area[i]])
            if up_cross != 0 and low_cross != 0:
                return 1
    return 0


def poly_maxmin_xy(areas):
    # 获取区域块中的左上、右下角点
    xxyy = []
    for area in areas:
        xmin = np.min(area, axis=0)[0]
        ymin = np.min(area, axis=0)[1]
        xmax = np.max(area, axis=0)[0]
        ymax = np.max(area, axis=0)[1]
        xxyy.append([xmin, xmax, ymin, ymax])
    return xxyy


def detect(detimg):
    enemy = {'B': (255, 0, 0),
             'R': (0, 0, 255)}
    im0 = detimg
    im = detimg.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    im = np.ascontiguousarray(im)
    im = torch.from_numpy(im).to(device)
    im = im.half() if half else im.float()  # uint8 to fp16/32
    im /= 255  # 0 - 255 to 0.0 - 1.0
    if len(im.shape) == 3:
        im = im[None]  # expand for batch dim
    pred_color = model_color(im, augment=augment)[0]
    pred_math = model_math(im, augment=augment)[0]
    pred_color = non_max_suppression(pred_color, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    pred_math = non_max_suppression(pred_math, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    detections = []
    mathpoints = []
    colorpoints = []
    robot_point = []
    # enemycolor = 'R'
    for i, (det, det1) in enumerate(zip(pred_color, pred_math)):  # per image 每张图片
        if len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
            det1[:, :4] = scale_boxes(im.shape[2:], det1[:, :4], im0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                xyxy = (torch.tensor(xyxy).view(1, 4)).view(-1).tolist()
                cls = names[int(cls)]
                conf = float(conf)
                detections.append({'class': cls, 'conf': conf, 'position': xyxy})
                minx = min(int(xyxy[0]), int(xyxy[2]))
                maxx = max(int(xyxy[0]), int(xyxy[2]))
                miny = min(int(xyxy[1]), int(xyxy[3]))
                maxy = max(int(xyxy[1]), int(xyxy[3]))
                if cls == enemycolor and conf > 0.6:
                    cv2.rectangle(detimg, (minx, miny), (maxx, maxy), enemy[cls], 3)
                    colorpoints.append([minx, miny, maxx, maxy, cls, conf])
                    cv2.putText(detimg, str(cls), (minx, miny), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            for *xyxys, confs, clss in reversed(det1):
                clss = names[int(clss)]
                confs = float(confs)
                xywh = (xyxy2xywh(torch.tensor(xyxys).view(1, 4))).view(-1).tolist()
                xywh = [round(x) for x in xywh]
                xywh = [xywh[0] - xywh[2] // 2, xywh[1] - xywh[3] // 2, xywh[2], xywh[3], clss,
                        confs]  # 检测到目标位置，格式：（left，top，w，h）
                mathpoints.append(xywh)
            for m, mathpoint in enumerate(mathpoints):
                centerx = mathpoint[0] + mathpoint[2] * 0.5
                centery = mathpoint[1] + mathpoint[3] * 3
                for n, colorpoint in enumerate(colorpoints):
                    if colorpoint[0] < centerx < colorpoint[2] and colorpoint[1] < centery < colorpoint[3] and \
                            mathpoint[5] > 0.4:
                        cv2.circle(detimg, (int(centerx), int(centery)), 2, (0, 0, 255), 1)
                        cv2.rectangle(detimg, (mathpoint[0], mathpoint[1]),
                                      (mathpoint[0] + mathpoint[2], mathpoint[1] + mathpoint[3]), (255, 255, 255), 1)
                        cv2.putText(detimg, str(colorpoint[4] + mathpoint[4]), (int(centerx) - 30, int(centery - 10)),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                        robot = [colorpoint[4], mathpoint[4], centerx, centery, mathpoint[5]]
                        colorpoints.remove(colorpoints[n])
                        robot_point.append(robot)
    for i, ture_colorpoint in enumerate(colorpoints):
        centerx = (ture_colorpoint[0] + ture_colorpoint[2]) / 2
        centery = (ture_colorpoint[1] + ture_colorpoint[3]) / 1.9
        cv2.circle(detimg, (int(centerx), int(centery)), 2, (0, 0, 255), 1)
        robot = [ture_colorpoint[4], 6, centerx, centery, ture_colorpoint[5]]
        robot_point.append(robot)
    return detimg, robot_point

