# 7x7x7_cube_robot

#### 介绍
使用树莓派控制的魔方机器人，可以在平均20分钟的时间内完成7阶魔方的还原。
这个工程的主要部分复刻了B站“爱跑步的小何”的七阶魔方机器人开源工程，但是在这个工程的基础上，使用了网上开源的CIEDE2000颜色算法识别魔方颜色，提升的颜色识别准确度，另外参照网上开源的OLED程序，额外移植并编写了Linux的OLED、LED和按键的设备驱动，编写了用户菜单界面，使得机器人通电后无需联网、键盘和鼠标，使用按钮进入菜单即可让装置单机还原魔方。
使用C + Python开发，含有结构设计、软件部分，演示视频。推荐使用树莓派4B 4GB，已经通过测试
工程代码添加了部分注释，有些是当时在阅读项目原作者代码时留下来的笔记，因为本人只是电子类大二的学生，Python，Linux，Opencv，Pcb等全部都是提前自学的，项目难免会有缺陷和问题，如果项目出现运行错误，可以参考项目原作者和参考开源项目的readme文件，期待大佬们的宝贵建议~
#### 项目主要参考开源资料：
1.七阶魔方机器人源程序：https://gitee.com/hemn1990/cube_robot_7x7x7
2.qbr颜色识别：https://github.com/kkoomen/qbr
3.高阶魔方求解算法：https://github.com/dwalton76/rubiks-cube-NxNxN-solver
4.三阶魔方求解算法：https://github.com/dwalton76/kociemba
5.OLED程序：https://gitee.com/oldzhai/stc89c51/tree/master/oled_i2c

#### 系统架构
```
12V电源--12V转5V电源模块--树莓派--+--步进电机驱动器(TB6560)--升降控制电机(42步进电机)
                                +--升降零点微动开关
                                |
                                +--步进电机驱动器(TB6560)--翻转控制电机(42步进电机)
                                +--翻转零点光电开关
                                |
                                +--步进电机驱动器(TB6560)--旋转控制电机(42步进电机)	
                                +--旋转零点光电开关
                                |
                                +--OLED显示屏，五向摇杆开关(用于脱机运行，OLED显示菜单，摇杆开关用于切换功能)
                                |
                                +--USB摄像头（120度视角）
                                +--键盘、鼠标、显示器
```                         

#### 演示视频：
【树莓派自制支持离线单机复原七阶魔方机器人】 https://www.bilibili.com/video/BV1At42157M8/?share_source=copy_web&vd_source=acff76156ca723d40e9f59889c9b9b52

#### 配置与运行步骤：
1、克隆项目到/home/pi/Desktop/,这个项目里面的文件编译链接，Makefile编写是使用绝对路径的，因此项目运行的路径是被固定的

2、安装python3-opencv
``` 
sudo apt-get install python3-opencv
```
3、安装ckociemba
``` 
cd cube_project\kociemba-develop\kociemba\ckociemba
make clean
make
sudo make install
``` 
3、安装rubiks-cube-NxNxN-solver（该版本相对于原始版本有修改，通过文件流把求解结果传送到cube_robot_motion.py进行运行）
``` 
cd \cube_project\rubiks-cube-NxNxN-solver-master
make clean
make init
./rubiks-cube-solver.py --state DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR
``` 
第二个步骤很慢，需要联网下载大量查找表，解压后需要占用数G空间。

4、编译并且加载内核模块，在此之前请安装好linux内核头文件，安装位置可参照Makefile
``` 
cd cube_project\cube_robot_7x7x7-master\cube_robot_kernel_module
make clean
make
sudo make load
cd ..
``` 
如需调整电机旋转速度，修改step_moter.py，make table后重新编译内核模块

6、运行主程序
``` 
cd cube_project
sudo run.sh
``` 
1.由于lunch.py使用了subprocess来获取IP信息并且打印在OLED屏幕上，因此如果设备未联网，可能会造成程序卡死或报错，如果无网络，可以将获取IP信息的代码注释，即可正常运行
2.运行后，OLED屏幕会显示菜单，使用五向开关来移动光标和选择选项。在主菜单中，选择“Solve!”进入还原模式，等待出现预览画面后，放入魔方，向右推动摇杆或按下空格键开始还原魔方，向上推动摇杆或按下键盘的'c'键开始进行魔方颜色校准，在校准模式下，向下推动摇杆或按下键盘的空格键校准下一个面的颜色。
3.魔方在转动过程中可能会出现卡顿现象，魔方可能会掉出，需要用手推回去，推测可能是因为3D打印结构缺陷引起
4.魔方颜色识别阈值信息被存储在/home/pi/.config/qbr/settings.json内，如果报错“找不到此文件”，可以尝试在同目录下创建一个同名空文件
