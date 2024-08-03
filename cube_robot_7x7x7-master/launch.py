import time
import subprocess
import os
import cv2
def command_LED(step):
    text = ""
    for x in step:
        text = text + "%d,%d;"%(x[0],x[1])
    file_name  = '/dev/led_module0'#dev文件夹指的是外部设备
    # file_name = '/dev/null'
    # print("LED_module0_write:",text)
    with open(file_name, 'w') as f:
        f.write(text)
        f.flush()
def command_OLED(step):
    text = ""
    for x in step:
        text = text + "%s,%s"%(x[0],x[1])
    file_name  = '/dev/OLED_module0'#dev文件夹指的是外部设备
    # file_name = '/dev/null'
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

if __name__=='__main__':
    print("kernel start already!")
    wait_cnt=60
    can_do_flag=0
    command_LED([[1,0]])
    command_LED([[2,0]])
    command_LED([[3,0]])
    command_LED([[1,1]])

    command_OLED([["Init","0"]])  
    command_OLED([["Clear","0"]]) 
    command_OLED([["ShowString","00001cube_robot"]])
    command_OLED([["ShowString","00030ip_address:"]])
    
    # 执行系统命令来获取IP地址信息
    result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
    # 从结果中提取IP地址
    ip_addresses = result.strip().split()
    # 输出IP地址
    print("IP地址:", ip_addresses[0])
    command_OLED([["ShowString","00040"+ip_addresses[0]]])
    command_OLED([["ShowString","00050by_super_pixel"]])
    # command_OLED([["ShowString","00040"+ip_addresses[1]]])

    while True:
        if command_KEY()=='p':
            can_do_flag=1
            command_LED([[1,0]])
            command_LED([[2,0]])
            command_LED([[3,0]])
            command_LED([[3,1]])
            break
        time.sleep(0.5)
        wait_cnt-=1
        if wait_cnt<10 and wait_cnt>0:
            command_OLED([["ShowNum","000700"+str(wait_cnt)+"0"]])
        elif wait_cnt>=10:
            command_OLED([["ShowNum","00070"+str(wait_cnt)+"0"]])
        else:
            command_OLED([["ShowString","00070exit"]])
        if wait_cnt<0:
            command_LED([[1,0]])
            command_LED([[2,0]])
            command_LED([[3,0]])
            break

    if can_do_flag==1:
        command_OLED([["Clear","0"]]) 

        page=0
        point=1
        point2=1
        while True:
            if page==0:
                command_OLED([["ShowString","40001Menu"]])
                command_OLED([["ShowString","100211.Solve!"]])
                command_OLED([["ShowString","100412.Motion"]])
                if point==1:
                    command_OLED([["ShowChar","0002*1"]])
                    command_OLED([["ShowChar","0004.1"]])
                if point==2:
                    command_OLED([["ShowChar","0002.1"]])
                    command_OLED([["ShowChar","0004*1"]])
            if page==1:
                command_OLED([["ShowString","40001Solve"]])
                command_OLED([["ShowString","00030r:start"]])
                command_OLED([["ShowString","00040u:color_adjust"]])
                command_OLED([["ShowString","00050d:adjust_next"]])

                command_LED([[1,0]])
                command_LED([[2,0]])
                command_LED([[3,0]])
                command_LED([[2,1]])

                os.chdir("/home/pi/Desktop/cube_project/cube_robot_7x7x7-master")
                os.system("/usr/bin/python3 cube_robot.py")
                page=0
                command_OLED([["Clear","0"]]) 
            if page==3:     
                command_LED([[1,0]])
                command_LED([[2,0]])
                command_LED([[3,0]])
                command_LED([[2,1]])
                command_LED([[3,1]])

                command_OLED([["ShowString","10000cw"]])
                command_OLED([["ShowString","10010cw'"]])
                command_OLED([["ShowString","10020cw2"]])
                
                command_OLED([["ShowString","10030f0"]])
                command_OLED([["ShowString","10040f1"]])

                command_OLED([["ShowString","10050zz"]])
                command_OLED([["ShowString","50000zf"]])
                command_OLED([["ShowString","50010z1"]])
                command_OLED([["ShowString","50020z2"]])
                command_OLED([["ShowString","50030z3"]])
                command_OLED([["ShowString","50040z4"]])
                command_OLED([["ShowString","50050z5"]])
                command_OLED([["ShowString","80000z6"]])
                command_OLED([["ShowString","80010z7"]])

                command_OLED([["ShowString","80020tz1"]])
                command_OLED([["ShowString","80030tz2"]])
                command_OLED([["ShowString","80040gui0"]])
                command_OLED([["ShowString","80050cw2'"]])
                if point2==1:
                    command_OLED([["ShowChar","0000*0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==2:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001*0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==3:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002*0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==4:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003*0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==5:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004*0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==6:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005*0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==7:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000*0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==8:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001*0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==9:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002*0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==10:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003*0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==11:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004*0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==12:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005*0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==13:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000*0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==14:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001*0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==15:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002*0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==16:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003*0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==17:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004*0"]])
                    command_OLED([["ShowChar","7005-0"]])
                elif point2==18:
                    command_OLED([["ShowChar","0000-0"]])
                    command_OLED([["ShowChar","0001-0'"]])
                    command_OLED([["ShowChar","0002-0"]])     
                    command_OLED([["ShowChar","0003-0"]])
                    command_OLED([["ShowChar","0004-0"]])
                    command_OLED([["ShowChar","0005-0"]])
                    command_OLED([["ShowChar","4000-0"]])
                    command_OLED([["ShowChar","4001-0"]])
                    command_OLED([["ShowChar","4002-0"]])
                    command_OLED([["ShowChar","4003-0"]])
                    command_OLED([["ShowChar","4004-0"]])
                    command_OLED([["ShowChar","4005-0"]])
                    command_OLED([["ShowChar","7000-0"]])
                    command_OLED([["ShowChar","7001-0"]])
                    command_OLED([["ShowChar","7002-0"]])
                    command_OLED([["ShowChar","7003-0"]])
                    command_OLED([["ShowChar","7004-0"]])
                    command_OLED([["ShowChar","7005*0"]])
            key=command_KEY()
            if key=='d':
                if page==0:
                    if point==1:
                        point=2
                if page==3 and point2<18:
                    point2+=1
                time.sleep(1)
            if key=='u':
                if page==0:
                    if point==2:
                        point=1
                if page==3 and point2>1:
                    point2-=1
                time.sleep(1)
            if key=='r':
                if page==0:
                    if point==1:
                        page=1 
                        command_OLED([["Clear","0"]])
                    if point==2:
                        page=3
                        command_OLED([["Clear","0"]])
                time.sleep(1)  
            if key=='p':
                if page==3:
                    os.chdir("/home/pi/Desktop/cube_project/cube_robot_7x7x7-master")
                    if point2==1:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py cw")#...
                    if point2==2:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py ccw")
                    if point2==3:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py cw2")
                    if point2==4:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py f0")
                    if point2==5:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py f1")
                    if point2==6:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py zz")
                    if point2==7:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py zf")
                    if point2==8:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z1")
                    if point2==9:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z2")
                    if point2==10:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z3")
                    if point2==11:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z4")
                    if point2==12:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z5")
                    if point2==13:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z6")
                    if point2==14:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py z7")
                    if point2==15:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py tz1")
                    if point2==16:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py tz2")
                    if point2==17:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py gui0")
                    if point2==18:
                        os.system("/usr/bin/python3 cube_robot_motion_single.py ccw2")
            if key=='l':
                if page==3:
                    page=0
                    command_OLED([["Clear","0"]])
            time.sleep(0.1)

# command1([[1,0]])
# command1([[2,0]])
# command1([[3,0]])
# command1([[1,1]])
        
# command2([["DisplayOff","!"]])
# time.sleep(2)
# command2([["DisplayOn","!"]])
# time.sleep(2)
# command2([["Clear","!"]])
# time.sleep(2)
# command2([["On","!"]])
# time.sleep(2)
# command2([["ShowChar","!"]])
# time.sleep(2)
# command2([["ShowNum","!"]])
# time.sleep(2)
# command2([["ShowString","!"]])
# time.sleep(2)
# command2([["ShowCHinese","!"]])
# time.sleep(2)
# command2([["DrawBMP","!"]])
# time.sleep(2)
        
# command2([["Init","0"]])  
# command2([["Clear","0"]])            
# command2([["ShowChar","0000c1"]])
# command2([["ShowNum","10021231"]])
# command2([["ShowString","20041apple"]])
# command2([["DisplayOff","0"]])
# time.sleep(2)
# command2([["DisplayOn","0"]])