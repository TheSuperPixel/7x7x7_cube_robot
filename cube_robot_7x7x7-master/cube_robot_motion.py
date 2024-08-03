#!/usr/bin/python3
#import subprocess
import time
import sys

# def command(text):
#     process = subprocess.Popen("./step",stdin=subprocess.PIPE)
#     pipe = process.stdin
#     pipe.write(bytes(text, encoding='ascii'))
#     pipe.close()
#     process.wait()# 运行过程避免IO操作（USB、TF等等），容易丢步

#test = "U' 3Bw R2 3Bw' 3Lw2 U' 3Fw' 3Lw' 3Dw' 3Rw2 3Fw Uw Bw'"
# 2021-01-17 更新，解决偶尔丢步问题，定时精度正负1us左右
def command(text):
    # i=0
    # 分段执行，每隔一段时间从内核态返回用户态，可以随时终止程序
    splited_text = text.split(';')
    file_name  = '/dev/step_moter0'
    error_flag=0
    with open(file_name, 'w') as f:
        #f.write(text)
        for x in splited_text:
            try:
                # print("x0:",x)
                x1 = x.strip()#去除从标准输入读取的内容中的前导空格和尾随换行符
                # print("x1:",x1)
                x2 = x1.split(',')#空格进行分割，返回一个包含分割后内容的列表
                # print("x2:",x2)
                if int(x2[0])==4 and int(x2[1])==1:
                    time.sleep(1)
                    continue
                if int(x2[0])==4 and int(x2[1])==2:
                    time.sleep(2)
                    continue
                if int(x2[0])==4 and int(x2[1])==5:
                    time.sleep(0.5)
                    continue
            except:
                print("the solve is end,exit.")
                error_flag=1
                break
            if error_flag==0:
                f.write(x)
                f.flush()
                print('.',end='')
                
            #原版代码：
            # # print("x0:",x)
            # x1 = x.strip()#去除从标准输入读取的内容中的前导空格和尾随换行符
            # # print("x1:",x1)
            # x2 = x1.split(',')#空格进行分割，返回一个包含分割后内容的列表
            # # print("x2:",x2)
            # if int(x2[0])==4 and int(x2[1])==1:
            #     time.sleep(1)
            #     continue
            # if int(x2[0])==4 and int(x2[1])==2:
            #     time.sleep(2)
            #     continue
            # if int(x2[0])==4 and int(x2[1])==5:
            #     time.sleep(0.5)
            #     continue
            # f.write(x)
            # f.flush()
            # print('.',end='')
            
            # i+=1
            # if i>200:
            #     f.write("1,40;")
            #     f.flush()
            #     f.write("0,0;")
            #     f.flush()

            # sys.stdout.flush()
            
            # time.sleep(0.5)
            # print("x2:",x2)
            # print("x2[0]=",x2[0],"x2[1]=",x2[1])
            # try:
            #     if int(x2[0])==3 and int(x2[1])<31 and int(x2[1])>-31:
            #         time.sleep(0.5)
            # except:
            #     pass
        
    
def decode_cube_str(x):
    direction = None # 1 顺时针 -1 逆时针 2 两圈
    face = None      # U R F D L B
    layer = None     # 1 2 3
    if x[-1] == "'":
        direction = -1
    elif x[-1] == "2":
        direction = 2
    else:
        direction = 1
        
    for item in ('U', 'R', 'F', 'D', 'L', 'B'):
        if item in x:
            face = item
    
    if 'w' in x:
        if x[0] == '2':
            layer = 2
        elif x[0] == '3':
            layer = 3
        else:
            layer = 2
    else:
        layer = 1
    
    return face,layer,direction
    
    
# test = "U' 3Fw' L' 3Bw2 3Uw 3Bw 3Dw' R' 3Fw' 3Rw' 3Dw U Fw' Uw' 3Uw2 F 3Fw2 3Bw2 3Rw2 3Lw' D' 3Fw2 3Lw' 3Rw R2 Rw2 Dw' Lw Uw Lw Fw' Uw' L Fw 3Rw2 F' 3Lw' B' 3Rw' F' 3Bw2 U' 3Lw Lw2 F 3Dw2 3Lw2 Lw' U' 3Dw2 3Bw2 Lw' 3Dw2 U F Bw2 Lw' Rw' F' D' Lw2 U Rw 3Fw2 Uw2 3Bw2 L' Uw2 3Uw2 L 3Uw2 R U2 3Bw2 U2 Fw2 3Fw2 Lw2 3Lw2 Rw2 Fw2 U' Bw2 Uw2 Rw2 F Rw2 3Uw2 B' Uw2 F2 Rw2 Uw2 F 3Lw2 3Dw2 R B L 3Dw2 B' 3Dw2 R D' U2 F 3Uw2 3Rw2 U2 3Lw2 F' L2 3Rw2 D2 F U2 F' B 3Uw2 F2 D 3Lw2 3Rw2 3Fw2 B2 U' L2 U L2 U2 R2 3Fw2 3Rw2 U' 3Fw2 2Uw2 R F' 2Rw2 2Uw2 F2 D R U' U2 2Rw2 U2 B 2Rw2 U2 2Uw2 2Lw2 R2 F' 2Rw2 F B2 2Uw2 2Fw2 2Uw2 U' D' 2Bw2 2Lw2 D' R2 D 2Rw2 U' F2 U' F2 2Lw2 2Fw2 B2 2Bw2 2Lw2 U F B R' L F' B2 U B2 L' F U2 R2 U F2 B2 L2 B2 U B2 U2"
# test = test.split(' ')
# for x in test:
#     face,layer,direction = decode_cube_str(x)
#     print(x,face,layer,direction)

#face_top/front : (f0, f1, cw, ccw, cw2)
cube_dict = {
#A：原来魔方朝向某两个固定方向的两个中心块颜色
#B：翻转架顺时针转90度后魔方朝向原来两个固定方向的两个中心块颜色
#C：翻转架逆时针转90度后魔方朝向原来两个固定方向的两个中心块颜色
#D：魔方笼顺时针转90度后（从上面看）魔方朝向原来两个固定方向的两个中心块颜色
#E：魔方笼逆时针转90度后（从上面看）魔方朝向原来两个固定方向的两个中心块颜色
#G：魔方笼顺时针转180度后（从上面看）魔方朝向原来两个固定方向的两个中心块颜色
#    A      B      C    D     F     G
    'UR': ('RD', 'LU', 'UB', 'UF', 'UL'),
    'UB': ('BD', 'FU', 'UL', 'UR', 'UF'),
    'UL': ('LD', 'RU', 'UF', 'UB', 'UR'),
    'UF': ('FD', 'BU', 'UR', 'UL', 'UB'),
    'RB': ('BL', 'FR', 'RU', 'RD', 'RF'),
    'RD': ('DL', 'UR', 'RB', 'RF', 'RU'),
    'RF': ('FL', 'BR', 'RD', 'RU', 'RB'),
    'RU': ('UL', 'DR', 'RF', 'RB', 'RD'),
    'FR': ('RB', 'LF', 'FU', 'FD', 'FL'),
    'FD': ('DB', 'UF', 'FR', 'FL', 'FU'),
    'FL': ('LB', 'RF', 'FD', 'FU', 'FR'),
    'FU': ('UB', 'DF', 'FL', 'FR', 'FD'),
    'DR': ('RU', 'LD', 'DF', 'DB', 'DL'),
    'DB': ('BU', 'FD', 'DR', 'DL', 'DF'),
    'DL': ('LU', 'RD', 'DB', 'DF', 'DR'),
    'DF': ('FU', 'BD', 'DL', 'DR', 'DB'),
    'LD': ('DR', 'UL', 'LF', 'LB', 'LU'),
    'LB': ('BR', 'FL', 'LD', 'LU', 'LF'),
    'LU': ('UR', 'DL', 'LB', 'LF', 'LD'),
    'LF': ('FR', 'BL', 'LU', 'LD', 'LB'),
    'BR': ('RF', 'LB', 'BD', 'BU', 'BL'),
    'BD': ('DF', 'UB', 'BL', 'BR', 'BU'),
    'BL': ('LF', 'RB', 'BU', 'BD', 'BR'),
    'BU': ('UF', 'DB', 'BR', 'BL', 'BD')}

def can_route(now, need):
    if (need == 'U' or need == 'D') and (now[0] == 'U' or now[0] == 'D'):
        return True
    if (need == 'L' or need == 'R') and (now[0] == 'L' or now[0] == 'R'):
        return True
    if (need == 'F' or need == 'B') and (now[0] == 'F' or now[0] == 'B'):
        return True
    return False

#test = "U' 3Bw R2 3Bw' 3Lw2 U' 3Fw' 3Lw' 3Dw' 3Rw2 3Fw Uw Bw'"

z_now = 0
filp_now = 0
flip_type_now = 1
cube_now = "FL"
exit_flag = False
not_route_flag=0

while True:
    step = []#存储全部转动微指令

    mode=1
    #模式1是步骤模式，输入U R这类的指令
    #模式2是微指令模式：
    #cw ccw cw2 ccw2 控制魔方笼转动
    #f0 f1 控制翻转架
    #zz zf z1 z2 z3 z4 z5 z6 z7 控制伸缩杆运动

    cnt=0#运行步数标志位，用于定期回零校准

    # #使用打开特定文件或从命令行输入来读取数据，调试时选择从命令行输入，运行时选择打开特定文件来读取数据
    with open('/home/pi/Desktop/cube_project/cube_robot_7x7x7-master/my_solution/my_solution.txt', 'r') as file:
        test = file.read()# 读取文件内容并存储到变量中
    # test = sys.stdin.readline()
    # print("input:",type(test),test)
        
    if not test:
        # 方便取出还原好的魔方
        # print('cube solved.')
        step.append('zz')
        step.append('f0')
        exit_flag = True
    else:
        if mode==1:
            print("step mode")
            test = test.strip()#去除从标准输入读取的内容中的前导空格和尾随换行符
            test = test.split()#空格进行分割，返回一个包含分割后内容的列表
            
            for item in test:
                # 1.解析魔方指令
                face,layer,direction = decode_cube_str(item)#解析魔方指令

                # 2.将期望的面翻转到上方或者下方
                if can_route(cube_now, face):
                    print(item,'need not route')
                    not_route_flag=1
                    pass
                elif can_route(cube_dict[cube_now][flip_type_now], face):
                    #flip_type_now为0时，会引起翻转架逆时针转90度（屏幕向自己）
                    #flip_type_now为1时，会引起翻转架顺时针转90度（屏幕向自己）
                    #print(item,'need route f0')
                    cube_now = cube_dict[cube_now][flip_type_now]
                    step.append('z1')#降下升降杆子，防止魔方砸在上面
                    step.append('zf')
                    step.append('tz1')#抖动魔方笼，让魔方掉下来
                    step.append('tz1')
                    step.append('d.5s')#延时0.5s
                    if cnt>5 and flip_type_now==1:
                        step.append('gui0')#回零校准
                        cnt=0
                    if flip_type_now == 0:
                        step.append('f0')
                        flip_type_now = 1
                    else:
                        step.append('f1')
                        flip_type_now = 0
                    #print(cube_now)
                else:
                    #print(item,'need route cw f0')
                    temp = cube_dict[cube_now][2]
                    step.append('z7')
                    step.append('cw')
                    cube_now = cube_dict[temp][flip_type_now]
                    step.append('z1')#降下升降杆子，防止魔方砸在上面
                    step.append('zf')
                    step.append('tz1')#抖动魔方笼，让魔方掉下来
                    step.append('tz1')
                    step.append('d2s')#延时2s
                    if cnt>5 and flip_type_now==1:
                        step.append('gui0')#回零校准
                        cnt=0
                    if flip_type_now == 0:
                        step.append('f0')
                        flip_type_now = 1
                    else:
                        step.append('f1')
                        flip_type_now = 0
                    #print(cube_now)
                        
                # 3.旋转指令中描述的层
                if cube_now[0] == face:#要旋转的面刚好面对魔方笼
                    step.append('zf')#降下升降杆子，防止魔方砸在上面
                    step.append('tz1')#抖动魔方笼，让魔方掉下来
                    step.append('tz1')
                    step.append('d.5s')
                    #来回翻动下翻转架，让魔方归位
                    if flip_type_now==1 and not_route_flag==1:
                        step.append('f1')
                        step.append('f0')
                        not_route_flag=0
                    elif flip_type_now==0 and not_route_flag==1:
                        step.append('f0')
                        step.append('f1')
                        not_route_flag=0
                    #然后把升降杆上升到指定的位置
                    if layer == 1:
                        step.append('z1')
                    elif layer == 2:
                        step.append('z2')
                    elif layer == 3:
                        step.append('z3')
                    if direction == 1:
                        step.append('cw')
                    elif direction == -1:
                        step.append('ccw')
                    elif direction == 2:
                        step.append('cw2')
                else:#要旋转的面背对魔方笼
                    step.append('zf')#降下升降杆子，防止魔方砸在上面
                    step.append('tz1')#抖动魔方笼，让魔方掉下来
                    step.append('tz1')
                    step.append('d.5s')
                    #来回翻动下翻转架，让魔方归位
                    if flip_type_now==1 and not_route_flag==1:
                        step.append('f1')
                        step.append('f0')
                        not_route_flag=0
                    elif flip_type_now==0 and not_route_flag==1:
                        step.append('f0')
                        step.append('f1')
                        not_route_flag=0
                    #然后把升降杆上升到指定的位置
                    if layer == 1:
                        step.append('z6')
                    elif layer == 2:
                        step.append('z5')
                    elif layer == 3:
                        step.append('z4')
                    if direction == 1:
                        step.append('cw')
                        cube_now = cube_dict[cube_now][2]#此时的转动会影响魔方中心块朝向
                    elif direction == -1:
                        step.append('ccw')
                        cube_now = cube_dict[cube_now][3]#此时的转动会影响魔方中心块朝向
                    elif direction == 2:
                        step.append('cw2')
                        cube_now = cube_dict[cube_now][4]#此时的转动会影响魔方中心块朝向
                cnt+=1
                # print("cnt=",cnt)
            step.append('zz')#全部完成后把机械结构归位
            step.append('f0')
            step.append('tz1')
            step.append('d.5s')
        else:
            print("motor mode")
            test = test.strip()#去除从标准输入读取的内容中的前导空格和尾随换行符
            test = test.split()#空格进行分割，返回一个包含分割后内容的列表
            for item in test:
                step.append(item)
    print("step:",type(step),step)
    # #大个的磁力魔方
    # #       z0  z1  z2  z3  z4  z5  z6  z7
    z_list = (164,250,320,385,450,515,580,685)
    z_list = tuple(x - 5 for x in list(z_list))
    #小个的魔方
    #         z0  z1  z2  z3  z4  z5  z6  z7
    # z_list = (162,282,349,410,475,540,605,700)
    # print(z_list)

    #把微指令转化为发给步进电机的指令
    text = ""#存储发给步进电机的指令
    for item in step:
        if item == 'zf': # for filp
            # if 10 - z_now != 0:
            #     text = text + "%d,%d;" % (1, 10 - z_now)
            # z_now = 10
            if z_now != 0:
                text = text + "%d,%d;" % (1, 0 - z_now)
            z_now = 0
        elif item == 'zz':
            if z_now != 0:
                text = text + "%d,%d;" % (1, 0 - z_now)
            z_now = 0
        elif item[0] == 'z': # up or down
            num = z_list[ int(item[1]) ]
            if num - z_now != 0:
                text = text + "%d,%d;" % (1, num - z_now)
            z_now = num
        elif item == 'cw':
            text = text + "3,810;"
            text = text + "3,-10;"
        elif item == 'ccw':
            text = text + "3,-810;"
            text = text + "3,10;"
        elif item == 'cw2':
            text = text + "3,1610;"
            text = text + "3,-10;"
        elif item == 'ccw2':# cw2 等价于 ccw2
            text = text + "3,-1610;"
            text = text + "3,10;"
        elif item == 'tz1':# 抖动步进电机算法1
            text = text + "3,30;"
            text = text + "3,-60;"
            text = text + "3,30;"
        elif item == 'tz2':# 抖动步进电机算法2
            text = text + "3,-30;"
            text = text + "3,30;"
        elif item == 'gui0':# 回0
            text = text + "1,40;"
            text = text + "0,0;"
        elif item == 'd1s':# 延时1s
            text = text + "4,1;"
        elif item == 'd2s':# 延时2s
            text = text + "4,2;"
        elif item == 'd.5s':# 延时0.5s
            text = text + "4,5;"
        
        elif item[0] == 'f': # 翻转flip
            if 50 < z_now < 415:
                print("filp not allowed when 50 < z_now < 415")
                pass
            else:
                if item[1] == '0':
                    if filp_now == 1:
                        text = text + "2,-810;"
                        filp_now = 0
                    else:
                        pass
                        #print("filp 0 not allowed")
                elif item[1] == '1':
                    if filp_now == 0:
                        text = text + "2,810;"
                        filp_now = 1
                    else:
                        pass
                        #print("filp 1 not allowed")
        elif item == '8':#升降杆往上微调一点
            text = text + "1,1"
        elif item == '2':#升降杆往下微调一点
            text = text + "1,-1"
        else:
            print("unknown command",item)


    t1=time.time()
    # print("text:",text)
    command(text)#把指令发给步进电机
    t2=time.time()
    print("time cost %.2fs"%(t2-t1))
    sys.stdout.flush()
    # if exit_flag:
    #     print('exit.')
    break