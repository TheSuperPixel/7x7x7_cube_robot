# -*- coding: utf-8 -*-
#!/usr/bin/python3
import subprocess
import time
import datetime
import os

def command(step):
    text = ""
    for x in step:
        text = text + "%d,%d;"%(x[0],x[1])
    file_name  = '/dev/step_moter0'#dev文件夹指的是外部设备
    print("moter_write:",text)
    with open(file_name, 'w') as f:
        f.write(text)
        f.flush()

if __name__=='__main__':
    print("starting init!")

    # 机械位置回零
    command([[1,40]])
    command([[0,0]])

    #初始化相机
    import cube_robot_image
    print("load cube_robot_image.py done")
    cap = cube_robot_image.init_camera()
    cube_robot_image.wait_and_prevew_camera(cap)

    file_name = "log/"+datetime.datetime.now().isoformat()+".log"
    print("log file is",file_name)
    
    img = [None]*6

    command([[2,810],[1,80],[1,785-162],[1,-785+162]])
    time.sleep(2)
    img[0] = cube_robot_image.cap_img(cap)#拍照
    time.sleep(1)
    command([[1,785-162],[3,820],[3,-20],[1,-785+162],[3,30],[3,-60],[3,30]])
    time.sleep(2)
    img[1] = cube_robot_image.cap_img(cap)
    time.sleep(1)
    command([[1,785-162],[3,820],[3,-20],[1,-785+162],[3,30],[3,-60],[3,30]])
    time.sleep(2)
    img[2] = cube_robot_image.cap_img(cap)
    time.sleep(1)
    command([[1,785-162],[3,820],[3,-20],[1,-785+162],[3,30],[3,-60],[3,30]])
    time.sleep(2)
    img[3] = cube_robot_image.cap_img(cap)
    time.sleep(1)
    command([[1,-80],[2,-810]])
    command([[1,80],[1,785-162],[2,810],[1,-785+162]])
    time.sleep(2)
    img[4] = cube_robot_image.cap_img(cap)
    time.sleep(1)
    command([[1,785-162],[3,1600],[1,-785+162],[3,30],[3,-60],[3,30]])
    time.sleep(2)
    img[5] = cube_robot_image.cap_img(cap)
    time.sleep(1)
    command([[1,-100],[2,-810]])

    command([[1,50]])
    command([[0,0]])
    cube_str = cube_robot_image.get_cube_string(img)#魔方图片转魔方状态字符串

    print("cube_str"),print(cube_str)
    with open('/home/pi/Desktop/cube_project/cube_robot_7x7x7-master/my_solution/my_solution.txt', 'w') as f:
        f.write(str(''))
    os.chdir("/home/pi/Desktop/cube_project/rubiks-cube-NxNxN-solver-master/")
    # print("current path:"),os.system("pwd")
    os.system("python3 rubiks-cube-solver.py --state %s " % (cube_str))
    os.chdir("/home/pi/Desktop/cube_project/cube_robot_7x7x7-master")
    os.system("python3 cube_robot_motion.py")
        
