# -*- coding: utf-8 -*-
import cv2
import numpy as np
from functools import cmp_to_key
import sys
sys.path.append('../')  # 将父文件夹添加到Python模块搜索路径中
from qbr.src.video import webcam
from qbr.src.colordetection import color_detector
from qbr.src.config import config
import time
cap = None
def command_OLED(step):
    text = ""
    for x in step:
        text = text + "%s,%s"%(x[0],x[1])
    file_name  = '/dev/OLED_module0'#dev文件夹指的是外部设备
    # print("OLED_module_write:",text)
    with open(file_name, 'w') as f:
        f.write(text)
        f.flush()
def command_KEY():
    file = open('/dev/key_module0', 'r')
    key_value = file.read(1)
    # print("Key value:", key_value)
    file.close()
    return key_value
# 获取魔方图像
def init_camera():
    cap = cv2.VideoCapture(0) 

    # 设置曝光时间（以毫秒为单位）
    exposure_time = 0.0000001  # 例如，设置曝光时间为5毫秒
    # 设置曝光时间
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure_time)
    # cap.set(44,0)

    if cap.isOpened() != True:
        print("camera error")
        return None
    return cap
    
def cap_img(cap):
    for i in range(8):
        ret,preview = cap.read()
        # cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
        # preview = cv2.cvtColor(preview, cv2.COLOR_BGR2GRAY)  # 将图像转换为灰度图像，可以更容易地调整白平衡
        # preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)  # 将灰度图像转换回BGR格式
        cv2.imshow("preview", preview)
        k = cv2.waitKey(1)
    cap.grab()
    ret,img = cap.retrieve()
    #cv2.imwrite(file_name+"_1.png", img1)
    return img

def wait_and_prevew_camera(cap):
    k2c='n'
    cv2.namedWindow('preview')
    cv2.setMouseCallback('preview',mouse)
    while True:
        ret,preview = cap.read()

        #建立contours，把实时颜色识别的ROI存进去
        contours=[]
        my_w=30
        my_h=30
        for y in (60,125,180,230,280,330,390):
            for x in (158,228,278,328,378,430,500):
                contours.append((x,y,my_w,my_h))

        #实时图像部分的识别颜色和校准颜色
        if len(contours) == 49:
            webcam.draw_contours(contours,preview)#画出ROI区域
        
            if not webcam.calibrate_mode:#如果不是校准模式
                webcam.update_preview_state(contours,preview)#实时颜色识别函数
                pass
            elif (k == 32)or(k2c=='p') and webcam.done_calibrating is False:#空格键且还没校准完
                current_color = webcam.colors_to_calibrate[webcam.current_color_to_calibrate_index]
                (x, y, w, h) = contours[24]
                roi = preview[y+7:y+h-7, x+14:x+w-14]
                avg_bgr = color_detector.get_dominant_color(roi)
                webcam.calibrated_colors[current_color] = avg_bgr
                webcam.current_color_to_calibrate_index += 1
                webcam.done_calibrating = webcam.current_color_to_calibrate_index == len(webcam.colors_to_calibrate)
                if webcam.done_calibrating:
                    color_detector.set_cube_color_pallete(webcam.calibrated_colors)#生成校准后颜色信息
                    config.set_setting('cube_palette', color_detector.cube_color_palette)#把颜色信息写入文件
                pass
        if webcam.calibrate_mode:
            webcam.draw_current_color_to_calibrate()#画出上方的提示词
            # webcam.draw_calibrated_colors(preview)#画出左上方的颜色和文字
            pass
        else:
            webcam.draw_preview_stickers(preview)#画出左上方的贴纸
            pass
        cv2.imshow("preview", preview)
        k = cv2.waitKey(1)

        k2c=command_KEY()#按键抖动消除
        # if k2a!='n':
        #     time.sleep(0.1)
        #     k2b=command_KEY()
        #     if k2b!='n':  
        #         k2c=k2b

        if (k == ord('c'))or(k2c=='u'):
            webcam.reset_calibrate_mode()#重置校准模式
            webcam.calibrate_mode = not webcam.calibrate_mode
        if (k == 32 or command_KEY()=='r') and not webcam.calibrate_mode:#空格 或 右边按键
            print("space is prass")
            command_OLED([["Clear","0"]])
            command_OLED([["ShowString","40001Solve"]])
            command_OLED([["ShowString","00030the_kernel_is_start!"]]) 
            break
        if k == 27:#esc
            print("esc is prass")
            cv2.destroyAllWindows()
            break
    return k

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("mouse click",x,y)
def mouse2(event, x, y, flags, img):
    if event == cv2.EVENT_LBUTTONDOWN:
        # print(f"img.shape={img.shape}")#->h w
        print("mouse2 click",x,y)
        # cv2.imshow("before_resize", img)
        # img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img=cv2.resize(img,(1024,768)) #->w h
        # cv2.imshow("after_resize", img)
        half_size = 6
        color = [0,0,0]

        # color[0] = img[y,x,0]
        # color[1] = img[y,x,1]
        # color[2] = img[y,x,2]

        dot_count = 0
        for x2 in range(x-half_size, x+half_size,1):
            for y2 in range(y-half_size, y+half_size,1):
                color[0] += img[y2,x2,0]
                color[1] += img[y2,x2,1]
                color[2] += img[y2,x2,2]
                dot_count += 1
                point=(x2,y2) #往右边是x正方向，往下面是y正方向
                # cv2.circle(img, point, 1, (255, 0, 0), 1)
                # print(f"x={x2},y={y2}")
        # cv2.imshow("after", img)
        color[0] = int(color[0]/dot_count)
        color[1] = int(color[1]/dot_count)
        color[2] = int(color[2]/dot_count)

        h,s,v = rgb2hsv(color[2], color[1], color[0])
        print(f"r={color[2]},g={color[1]},b={color[0]};h={h:.1f},s={s:.3f}.v={v:.3f}")
    elif event == cv2.EVENT_RBUTTONDOWN:
        print("mouse3 click",x,y)
        color = [0,0,0]
        color[0] = img[y,x,0]
        color[1] = img[y,x,1]
        color[2] = img[y,x,2]
        h,s,v = rgb2hsv(color[2], color[1], color[0])
        print(f"r={color[2]},g={color[1]},b={color[0]};h={h:.1f},s={s:.3f}.v={v:.3f}")
# 图像处理部分
def four_point_transform(image, rect):
    # 获取坐标点，并将它们分离开来
    # 图像尺寸
    maxWidth = 256
    maxHeight = 256
    # 构建新图片的4个坐标点
    edge = 0
    dst = np.array([
        [edge, edge],
        [maxWidth - 1 - edge, edge],
        [maxWidth - 1 - edge, maxHeight - 1 - edge],
        [edge, maxHeight - 1 - edge]], dtype = "float32")
    # 获取仿射变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行仿射变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # 返回变换后的结果
    return warped

def mark_cube_one_point(img, x_center, y_center):
    half_size = 10
    roi=img[y_center-half_size:y_center+half_size,x_center-half_size:x_center+half_size]
    avg_bgr = color_detector.get_dominant_color(roi)
    closest_color_name = color_detector.get_closest_color(avg_bgr)['color_name']
    # print(closest_color_name)
    cv2.rectangle(img, (x_center-half_size, y_center-half_size),
                  (x_center+half_size, y_center+half_size), (0,0,0))
    cv2.rectangle(img, (x_center-half_size+1, y_center-half_size+1),
                  (x_center+half_size-1, y_center+half_size-1), (255,255,255))
    point=(x_center,y_center)
    cv2.circle(img, point, 1, (0, 0, 0), 1)
    #cv2.rectangle(img, (x_center-6, y_center-6),
    #              (x_center+6, y_center+6), color,-1)
    return closest_color_name

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    m = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        if g >= b:
            h = ((g-b)/m)*60
        else:
            h = ((g-b)/m)*60 + 360
    elif mx == g:
        h = ((b-r)/m)*60 + 120
    elif mx == b:
        h = ((r-g)/m)*60 + 240
    if mx == 0:
        s = 0
    else:
        s = m/mx
    v = mx
    # h,s,v,值的范围分别是0-360, 0-1, 0-1
    return h, s, v

def mark_cube(img,face):
    color_line = (0,0,0)
    colors = [0]*49
    i = 0
    closest_color_name_list=['']*49
    for y in (32,64,96,128,160,192,224):
        for x in (32,64,96,128,160,192,224):
            closest_color_name_list[i] = mark_cube_one_point(img,x,y)#标记并识别某一个色块
            i += 1
            
    # cv2.putText(img,str(face), (128-20,128-20), cv2.FONT_HERSHEY_DUPLEX,1,color_line)
    
    return closest_color_name_list

def class_color(hsv_49x5):
    min_std_shift = 0;
    min_std = 1000; # 0 - 360
    hsv_49x5_only_h = []
    for x in hsv_49x5:
        hsv_49x5_only_h.append(x[0])
    
    for shift in range(0,49):
        hsv_49x5_shift = list(hsv_49x5_only_h)
        for i in range(0, shift):
            hsv_49x5_shift[i] += 360
        hsv_49x5_shift = hsv_49x5_shift[shift:49*5] + hsv_49x5_shift[0:shift]
        
        std = [0] * 5
        for i in range(0,5):
            std[i] = np.std(hsv_49x5_shift[i * 49 : i * 49 + 49])
        std_mean = np.mean(std)
        
        if std_mean < min_std:
            min_std_shift = shift
            min_std = std_mean
            
    # print("min_std_shift =",min_std_shift,"min_std =",min_std)
    return hsv_49x5[min_std_shift:49*5] + hsv_49x5[0:min_std_shift] 

def get_cube_string(img):
    img[0],img[1],img[2],img[3],img[4],img[5] = img[0],img[3],img[5],img[2],img[1],img[4] 
    pts1 = np.array([[132,15],[547,11],[552,425],[137,425]], dtype = "float32")
    hsv_6_face = []
    angle_list = [180, 90, -90, 0, -90, 90]

    #cube_string = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB" 存储魔方色块颜色字符
    cube_string = ['?']*(49*6)
    cube_string_kociemba = ['?']*(49*6)
    for i in range(6):
        img[i] = four_point_transform(img[i], pts1)#进行仿射变换
        matRotate = cv2.getRotationMatrix2D((256*0.5, 256*0.5), angle_list[i], 1.0) #旋转图像
        img[i] = cv2.warpAffine(img[i], matRotate, (256, 256))#函数使用仿射变换来扭曲图像
        closest_color_name_list=mark_cube(img[i],i)#标记魔方，同时识别颜色
        cube_string[0+49*i:49+49*i]=closest_color_name_list[0:49]
        # print("closest_color_name_list"),print(type(closest_color_name_list)),print(closest_color_name_list)
    
    name_transform={'red': 'R', 'green': 'G', 'blue': 'B','orange': 'O', 'yellow': 'Y', 'white': 'W'}
    for i in range(49*6):
        cube_string[i]=name_transform[cube_string[i]]
    
    # 用于评估效果的图像
    null_img = np.zeros((256, 256, 3), np.uint8)
    row1 = np.hstack((null_img, img[0], null_img, null_img))#横向拼接图像
    row2 = np.hstack((img[4],   img[2], img[1],   img[5]))#横向拼接图像
    row3 = np.hstack((null_img, img[3], null_img, null_img))#横向拼接图像
    img_6in1 = np.vstack((row1, row2, row3))#垂直堆叠图像
    print(f"img_6in1={img_6in1.shape}")
    color_dict = {'R':(0,0,255), 'G':(0,255,0), 'B':(255,0,0),
                  'O':(0,192,255), 'Y':(0,255,255), 'W':(255,255,255)}
    offset = ((1,0),(2,1),(1,1),(1,2),(0,1),(3,1))
   
    for i in range(49*6):
        size = 6
        face = i // 49 #面
        index = i % 49 #单面中色块的序号
        x = (offset[face][0]*7 + index % 7 )* size + 620
        y = (offset[face][1]*7 + index // 7 )* size + 520
        cv2.rectangle(img_6in1,(x,y),(x+size-1,y+size-1),color_dict[cube_string[i]], -1) #画出识别结果的矩形色块
        #cv2.rectangle() 函数用于在图像上绘制矩形。
        #(x,y) 是矩形左上角的坐标。
        #(x+size-1,y+size-1) 是矩形右下角的坐标。
        #color_dict[cube_string[i]] 是矩形的颜色。
        #-1 是矩形的线宽。
        #该代码片段的作用是在图像 img_6in1 上绘制一个矩形，矩形的左上角坐标为 (x,y)，右下角坐标为 (x+size-1,y+size-1)，颜色为 color_dict[cube_string[i]]，线宽为 1。
    cv2.destroyAllWindows()
    cv2.imshow("cube", img_6in1)
    cv2.namedWindow('cube')
    k = cv2.waitKey(300)
    cv2.setMouseCallback('cube',mouse2,img_6in1)#测试颜色算法效果的鼠标回调函数
    # cv2.setMouseCallback('cube',mouse)

    # RGBWOY -> URFDLB
    u_color = cube_string[49*0+24]#提取出六个中心块颜色
    r_color = cube_string[49*1+24]
    f_color = cube_string[49*2+24]
    d_color = cube_string[49*3+24]
    l_color = cube_string[49*4+24]
    b_color = cube_string[49*5+24]
    
    #把魔方六个面颜色用URFDLB代替，遍历进行匹配
    for i in range(0,49*6):
        if cube_string[i] == u_color:
            cube_string_kociemba[i] = 'U'
        elif cube_string[i] == r_color:
            cube_string_kociemba[i] = 'R'
        elif cube_string[i] == f_color:
            cube_string_kociemba[i] = 'F'
        elif cube_string[i] == d_color:
            cube_string_kociemba[i] = 'D'
        elif cube_string[i] == l_color:
            cube_string_kociemba[i] = 'L'
        elif cube_string[i] == b_color:
            cube_string_kociemba[i] = 'B'
    cube_string_kociemba = ''.join(cube_string_kociemba)
    return cube_string_kociemba #适合cube_N*M*M_solver的输入格式
