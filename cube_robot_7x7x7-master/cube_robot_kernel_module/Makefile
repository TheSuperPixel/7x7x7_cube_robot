obj-m += step_moter.o #指定要编译的目标模块是step_moter.o
#ccflags-y += -mfloat-abi=hard
LDLIBS += -lgcc_s #指定链接时要使用的库

all:
	make -C /usr/src/linux-headers-5.10.103-v7l+ M=$(PWD) modules
clean:
	make -C /usr/src/linux-headers-5.10.103-v7l+ M=$(PWD) clean

table:
	python3 step_moter.py > step_tab.h

unload:
	rmmod step_moter.ko
load:
	insmod step_moter.ko
	sleep 0.5
	chmod 666 /dev/step_moter0
