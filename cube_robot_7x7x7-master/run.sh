#!/bin/bash

echo "start_running!"
# # 命令所有者
# chown root:root /usr/bin/sudo
# # 赋权
# chmod 4755 /usr/bin/sudo

# # sudo文件库授权
# chown root:root  /usr/libexec/sudoers.so

cd /home/pi/Desktop/cube_project/cube_robot_7x7x7-master/cube_robot_kernel_module
make load
cd /home/pi/Desktop/cube_project/cube_robot_7x7x7-master/led_module
make load
cd /home/pi/Desktop/cube_project/cube_robot_7x7x7-master/OLED_module
make load
cd /home/pi/Desktop/cube_project/cube_robot_7x7x7-master/key_module
make load
cd ..
/usr/bin/python3 launch.py
# ./cube_robot.py
# su pi
# code .
