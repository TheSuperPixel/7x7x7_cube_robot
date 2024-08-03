obj-m += OLED_module.o #指定要编译的目标模块是OLED_module.o
#ccflags-y += -mfloat-abi=hard
LDLIBS += -lgcc_s #指定链接时要使用的库

all:
	make -C /usr/src/linux-headers-5.10.103-v7l+ M=$(PWD) modules
clean:
	make -C /usr/src/linux-headers-5.10.103-v7l+ M=$(PWD) clean
unload:
	rmmod OLED_module.ko
load:
	insmod OLED_module.ko
	sleep 0.5
	chmod 666 /dev/OLED_module0
