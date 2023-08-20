# 项目模式选择
CONFIG_isserial = False     # 是否开启通信线程
CONFIG_VID = True           # 是否开启视频模式，False为相机模式
CONFIG_camera_swap = True   # 打开双相机时，画面是否需要调换位置

# 比赛必要设置
CONFIG_mycolor = 'B'
CONFIG_enemycolor = 'R'
CONFIG_crop_width = 0                       # 自定义相机裁剪宽度
CONFIG_ismatrix = True                      # 是否在原图界面显示矩阵
CONFIG_isLoop = True                        # 项目执行的标志位
CONFIG_printFPS = True                      # 是否输出帧率
CONFIG_draw_color = {'B': (255, 0, 0),      # 红蓝对应通道值
                     'R': (0, 0, 255)}

# 相机参数设置
CONFIG_exposureTime = 6000.0    # 曝光时间
CONFIG_gainRaw = 1.4            # 增益
CONFIG_gamma = 1                # 伽马
CONFIG_bright = 50              # 亮度

# 项目必要路径
CONFIG_colormodel_path = 'color.pt'                                 # 识别颜色的模型路径
CONFIG_mathmodel_path = 'math.pt'                                   # 识别ID的模型路径
CONFIG_VID_path = "E:/National/radar/yuan/National_yuanvi5.avi"     # 视频模型下的视频路径
CONFIG_map_path = "E:/MYproject/mytest/Location/map.jpg"            # 小地图路径
CONFIG_saveimg_path = "E:/mytest/Location/fenqu4.jpg"               # 原图帧的保存路径

# 内录配置
CONFIG_savevideo = False            # 是否保存视频
CONFIG_countsave = 7                # 保存视频的序列号
CONFIG_yuanvi_path = "E:/National/radar/pick/National_pick" + str(CONFIG_countsave) + ".avi"    # 原图保存路径
CONFIG_pickvi_path = "E:/National/radar/pick/National_pick" + str(CONFIG_countsave) + ".avi"    # 修剪图的保存路径
CONFIG_fps = 30                     # 保存的视频的帧率
CONFIG_yuansize = (3840, 1200)      # 保存原图视频的画质
CONFIG_picksize = (1920, 768)       # 保存修剪图视频的画质

# 模型配置
CONFIG_imgsz = 1184             # 输入图片的大小 默认640(pixels)
CONFIG_conf_thres = 0.25        # object置信度阈值 默认0.25  用在nms中
CONFIG_iou_thres = 0.45         # 做nms的iou阈值 默认0.45   用在nms中
CONFIG_max_det = 1000           # 每张图片最多的目标数量  用在nms中
CONFIG_device = '0'             # 设置代码执行的设备 cuda device, i.e. 0 or 0,1,2,3 or cpu
CONFIG_classes = None           # 在nms中是否是只保留某些特定的类 默认是None 就是所有类只要满足条件都可以保留 --class 0, or --class 0 2 3
CONFIG_agnostic_nms = False     # 进行nms是否也除去不同类别之间的框 默认False
CONFIG_augment = False          # 预测是否也要采用数据增强 TTA 默认False
CONFIG_visualize = False        # 特征图可视化 默认FALSE
CONFIG_half = False             # 是否使用半精度 Float16 推理 可以缩短推理时间 但是默认是False
CONFIG_dnn = False              # 使用OpenCV DNN进行ONNX推理
CONFIG_names = ['B', 'R', '0', '1', '2', '3', '4', '5', 'N']        # 单模型下的类，已弃用，当前为双模型结构

# 裁判系统协议
CONFIG_commandDict = {
                        "location":
                        {
                            "command": 0x0305,
                        },
                    }
