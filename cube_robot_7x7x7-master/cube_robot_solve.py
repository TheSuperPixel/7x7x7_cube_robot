#!/usr/bin/python3
import time
import sys
import subprocess
#python3 rubiks-cube-solver.py --state XXX  2>/dev/null | python3 cube_robot_solve.py 


def solve_cube():
    process = subprocess.Popen(['taskset', '-c', '3', 'python3', '/home/pi/Desktop/cube_project/cube_robot_7x7x7-master/cube_robot_motion.py'], stdin=subprocess.PIPE)
    pipe = process.stdin
    
    steps_555_LR_centers_staged = 0
    steps_555_FB_centers_staged = 0
    steps_555_edges_EOed = 0
    steps_555_first_four_edges_staged = 0
    steps_555_first_four_edges_paired = 0
    steps_555_last_eight_edges_paired = 0
    all_steps = []

#     def w_to_3w(x):
#         for i in range(len(x)):
#             if 'w' in x[i]:
#                 x[i] = '3' + x[i]
#     def w_to_2w(x):
#         for i in range(len(x)):
#             if 'w' in x[i]:
#                 x[i] = '2' + x[i]
    len_old = 0;
    while True:
        print("solve start!")  # 打印提示信息，表示解决方案开始
        line = sys.stdin.readline()  # 从标准输入读取一行数据
        print('input:',line)  # 打印读取的输入行
        if not line:  # 如果输入行为空，则跳出循环
            break
        if "Solution" in line:  # 如果输入行包含"Solution"
            steps = line.split(":")[-1].strip().split(' ')  # 从line中提取出最后一个冒号后面的部分，并按空格进行分割，得到一个包含分割后的部分的列表
            print("steps:",type(steps),steps)  # 打印steps变量的类型和内容
            solution_id = line.split(":")[0]  # 从line中提取出最后一个冒号前面的部分
            print("solution_id:",type(solution_id),solution_id)  # 打印solution_id变量的类型和内容
            totel_comment = 0  # 初始化总评论数为0
            index_last = 0  # 初始化最后索引为0
            index_CENTERS_SOLVED = 0  # 初始化CENTERS_SOLVED索引为0
            # 截取最新的部分
            #totel_comment:步骤中“COMMENT”的个数
            #index_last:最后一个元素的索引
            #index_CENTERS_SOLVED：步骤中“CENTERS_SOLVED”的索引+1
            for i in range(len(steps)): 
                if 'COMMENT' in steps[i]: 
                    totel_comment += 1 
                    if i != len(steps) - 1:  # 如果不是最后一个步骤
                        index_last = i + 1 
                if 'CENTERS_SOLVED' in steps[i]:  
                    index_CENTERS_SOLVED = i + 1  

            if totel_comment == 0:  # 如果步骤中没有“COMMENT”
                print("!!! Find solution:", ' '.join(steps)) 
                if steps != all_steps: 
                    print("solution should be:", ' '.join(all_steps))  
                    raise Exception("read rubiks-cube-NxNxN-solver steps error.")  
                
            else:  # 如果步骤中有“COMMENT”
                if solution_id != 'Solution': 
                    if len_old != len(steps): 
                        len_old = len(steps) 
                        comment = steps[-1] 
                        steps = steps[index_last:-1]  # 截取步骤
                        all_steps += steps
                        to_write = ' '.join(steps)  # 将步骤连接为字符串
                        pipe.write(bytes( to_write + '\n' , encoding='ascii'))  # 写入管道
                        pipe.flush()  # 刷新管道
                        print("!!! %s: %s"%(solution_id, to_write))  # 打印解决方案

                else:  # 如果solution_id是'Solution'
                    steps = steps[index_CENTERS_SOLVED:-1]  # 截取步骤
                    steps_temp = []  # 初始化临时步骤列表
                    for step in steps:  # 遍历步骤
                        if 'COMMENT' not in step and 'EDGES_GROUPED' not in step:  # 如果步骤不包含'COMMENT'和'EDGES_GROUPED'
                            steps_temp.append(step)  # 添加到临时步骤列表
                    all_steps += steps_temp  # 添加到所有步骤中
                    to_write = ' '.join(steps_temp)  # 将步骤连接为字符串
                    pipe.write(bytes( to_write + '\n' , encoding='ascii'))  # 写入管道
                    pipe.flush()  # 刷新管道
                    print("!!! %s: %s"%(solution_id, to_write))  # 打印解决方案
                    pass  # 结束当前循环

    pipe.close()
    process.wait()
    
# read stdin
solve_cube()




