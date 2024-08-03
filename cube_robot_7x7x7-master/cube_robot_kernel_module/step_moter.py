#!/bin/python3
from math import sqrt

def plot(half_p_list, step):
    from matplotlib import pyplot as plt 
    length = len(half_p_list)
    #print("数组长度：%d steps" % length)
    v_list = []
    t_list = []
    time = 0
    for i in range(0, step):
        if i < length and i < step / 2:
            p = half_p_list[i]
        elif step - 1 - i < length:
            p = half_p_list[step - 1 - i ]
        else:
            p = half_p_list[length - 1]
        v = 1000000 / p / 2
        v_list.append(v)
        t_list.append(time)
        time = time + 1 / v
        
    
    plt.title("stepping motor control") 
    plt.xlabel("time (s)") 
    plt.ylabel("speed (steps/s)") 
    plt.plot(t_list, v_list) 
    plt.show()

def export_c_array(half_p_list, name):
    print("int %s = %d;" % (name + "_length", len(half_p_list)))
    print("int %s[%d] = {" % (name + "_array", len(half_p_list)))
    for i in range(0,len(half_p_list)):
        if i % 16 == 0:
            print("    ", end='')
        print("%3d" % half_p_list[i], end='')
        if i != len(half_p_list) - 1:
            print(", ", end='')
        else:
            print()
        if (i + 1) % 16 == 0:
            print()
    print("};")


def get_array(v0 = 1500, v = 7000, a = 60000):
    # 加速算法参考http://hwml.com/LeibRamp.htm
    F = 1000000; # F : timer frequency
    vi = v0;
    S = (v**2 - v0**2) / (2 * a)
    print("// 初始速度：%.2f steps/s" % v0)
    print("// 最大速度：%.2f steps/s" % v)
    print("// 加速度：%.2f steps/s2" % a)
    print("// 加速距离：%.2f steps" % S)

    half_p_list = []
    while(True):
        vi = sqrt(vi**2 + 2*a)
        if vi > v:
            break
        half_p_list.append(round(F / vi / 2))
    
    return half_p_list
    
# m3 = get_array(1000, 6000, 50000)
# export_c_array(m3, "m3")
# m2 = get_array(1000, 6000, 30000)
# export_c_array(m2, "m2")
# m1 = get_array(250, 4000, 10000)
# export_c_array(m1, "m1")
#plot(m3, 1000)

m3 = get_array(1000, 6000, 50000)
export_c_array(m3, "m3")
m2 = get_array(1000, 3000, 5000)
export_c_array(m2, "m2")
m1 = get_array(300, 4500, 12000)
export_c_array(m1, "m1")