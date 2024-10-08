#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <asm/delay.h>
#include <asm/io.h>
//#include <linux/slab.h> 
#include <linux/fs.h>
#include <asm/uaccess.h>    /* for put_user */
#include <linux/cdev.h>
#include <linux/errno.h>
#include <asm/current.h>
#include <linux/sched.h>
#include <linux/device.h>

#include "key_module.h"

MODULE_LICENSE("GPL"); 
MODULE_VERSION("0.1"); 

static uint32_t* gpio_base = 0;

/* Read input pin */
static uint8_t gpio_read(uint8_t pin)
{
    volatile uint32_t* paddr = gpio_base + BCM2835_GPLEV0/4 + pin/32;
    uint8_t shift = pin % 32;
    uint32_t value = ioread32(paddr);
    return (value & (1 << shift)) ? HIGH : LOW;
}

/* Set output pin */
static void gpio_set(uint8_t pin)
{
    volatile uint32_t* paddr = gpio_base + BCM2835_GPSET0/4 + pin/32;
    uint8_t shift = pin % 32;
    iowrite32(1 << shift, paddr);
}

/* Clear output pin */
static void gpio_clr(uint8_t pin)
{
    volatile uint32_t* paddr = gpio_base + BCM2835_GPCLR0/4 + pin/32;
    uint8_t shift = pin % 32;
    iowrite32(1 << shift, paddr);
}

/* Set the pullup/down resistor for a pin */
static void gpio_set_pud(uint8_t pin, uint8_t pud)
{
        int shiftbits = (pin & 0xf) << 1;
        uint32_t bits;
        uint32_t pull;
        volatile uint32_t* paddr;
        switch (pud)
        {
           case BCM2835_GPIO_PUD_OFF:  pull = 0; break;
           case BCM2835_GPIO_PUD_UP:   pull = 1; break;
           case BCM2835_GPIO_PUD_DOWN: pull = 2; break;
           default: return;
        }
        paddr = gpio_base + BCM2835_GPPUPPDN0/4 + (pin >> 4);
        
        bits = ioread32( paddr );
        bits &= ~(3 << shiftbits);
        bits |= (pull << shiftbits);
        iowrite32(bits, paddr);
}

/* set gpio input or output mode */
static void gpio_fsel(uint8_t pin, uint8_t mode)
{
    /* Function selects are 10 pins per 32 bit word, 3 bits per pin */
    volatile uint32_t* paddr = gpio_base + BCM2835_GPFSEL0/4 + (pin/10);
    uint8_t   shift = (pin % 10) * 3;
    uint32_t  mask = BCM2835_GPIO_FSEL_MASK << shift;
    uint32_t  value = mode << shift;
    
    uint32_t v = ioread32(paddr);
    v = (v & ~mask) | (value & mask);
    iowrite32(v, paddr);
}

static void gpio_init(void)
{
    gpio_fsel (KEY_UP, BCM2835_GPIO_FSEL_INPT);
    gpio_fsel (KEY_DOWN, BCM2835_GPIO_FSEL_INPT);
    gpio_fsel (KEY_LEFT, BCM2835_GPIO_FSEL_INPT);
    gpio_fsel (KEY_RIGHT, BCM2835_GPIO_FSEL_INPT);
    gpio_fsel (KEY_PUSH, BCM2835_GPIO_FSEL_INPT);

    gpio_set_pud (KEY_UP, BCM2835_GPIO_PUD_UP);
    gpio_set_pud (KEY_DOWN, BCM2835_GPIO_PUD_UP);
    gpio_set_pud (KEY_LEFT, BCM2835_GPIO_PUD_UP);
    gpio_set_pud (KEY_RIGHT, BCM2835_GPIO_PUD_UP);
    gpio_set_pud (KEY_PUSH, BCM2835_GPIO_PUD_UP);
}

static int Device_Open = 0; 
static char *msg_Ptr;
static char cmd_buffer[65536]={0};

static int device_open(struct inode *inode, struct file *file)
{
    if (Device_Open)
        return -EBUSY;
    Device_Open++;
    
    msg_Ptr = cmd_buffer;
    
    try_module_get(THIS_MODULE);
    return 0;
}

static int device_release(struct inode *inode, struct file *file)
{
    Device_Open--;
    module_put(THIS_MODULE);
    return 0;
}

static ssize_t device_read(struct file *file, char *buffer, size_t length, loff_t *offset)
{
    //返回值 u b l r p n
    int bytes_read = 0;
    int i;

    // if (*msg_Ptr == 0)
    //     return 0;

    // while (length && *msg_Ptr) {
    //     put_user(*(msg_Ptr++), buffer++);
    //     length--;
    //     bytes_read++;
    // }

    // if(gpio_read(KEY_UP)==0)    cmd_buffer[i] = 'u';
    // else if(gpio_read(KEY_DOWN)==0)    cmd_buffer[i] = 'd';
    // else if(gpio_read(KEY_LEFT)==0)    cmd_buffer[i] = 'l';
    // else if(gpio_read(KEY_RIGHT)==0)    cmd_buffer[i] = 'r';
    // else if(gpio_read(KEY_PUSH)==0)    cmd_buffer[i] = 'p';
    // else cmd_buffer[i] = '0';

    // cmd_buffer[0]='8';
    // cmd_buffer[1]=gpio_read(KEY_UP);
    // cmd_buffer[2]=gpio_read(KEY_DOWN);
    // cmd_buffer[3]=gpio_read(KEY_LEFT);
    // cmd_buffer[4]=gpio_read(KEY_RIGHT);
    // cmd_buffer[5]=gpio_read(KEY_PUSH);
    // cmd_buffer[6]='9';
    int k1=0,k2=0,k3=0,k4=0,k5=0;
    k1=gpio_read(KEY_UP);
    k2=gpio_read(KEY_DOWN);
    k3=gpio_read(KEY_LEFT);
    k4=gpio_read(KEY_RIGHT);
    k5=gpio_read(KEY_PUSH);
    if(k1==0){
        cmd_buffer[0] = 'u';
    }else if(k2==0){
        cmd_buffer[0] = 'd';
    }else if(k3==0){
        cmd_buffer[0] = 'l';
    }else if(k4==0){
        cmd_buffer[0] = 'r';
    }else if(k5==0){
        cmd_buffer[0] = 'p';
    }else{
        cmd_buffer[0] = 'n';
    }


    for (i = 0; i < length && i < 65535; i++)
        put_user(cmd_buffer[i], buffer + i);
        bytes_read++;
    return bytes_read;
}

static ssize_t device_write(struct file *file, const char *buffer, size_t length, loff_t *offset)
{
  int a, b, ret, i;
  const char *p;
  for (i = 0; i < length && i < 65535; i++)
      get_user(cmd_buffer[i], buffer + i);
  return length;
}

static struct file_operations fops = {
    //内核定义好的结构体 内核源码里有
    //就是驱动的结构体 要加载到内核驱动链表
    .read = device_read,//当用户空间程序调用 read 系统调用时，内核会调用这个函数来处理读取操作。
    .write = device_write,//当用户空间程序调用 write 系统调用时，内核会调用这个函数来处理写入操作。
    .open = device_open,//当用户空间程序调用 open 系统调用时，内核会调用这个函数来处理打开文件的操作
    .release = device_release//当所有文件描述符关闭或进程终止时，内核会调用这个函数来释放文件相关的资源。
};

#define DEVNAME "key_module" //设备号
static int major = 0; //主设备号
static int minor = 0;  //次设备号
const  int count = 1;
static struct cdev *demop = NULL;
static struct class *cls = NULL;

static int __init key_module_init(void) 
{ 
    dev_t devnum; //设备号
    int ret, i;
    struct device *devp = NULL;
    
    printk(KERN_INFO "key_module driver loaded.\n"); 
    gpio_base = (uint32_t *)ioremap(RPI4_GPIO_ADDR, RPI4_GPIO_SIZE);
    gpio_init();//初始化GPIO
    
    //1. alloc cdev obj
    demop = cdev_alloc();
    if(NULL == demop){
        return -ENOMEM;
    }
    //2. init cdev obj
    cdev_init(demop, &fops);

    ret = alloc_chrdev_region(&devnum, minor, count, DEVNAME);
    if(ret){
        goto ERR_STEP;
    }
    major = MAJOR(devnum);

    //3. register cdev obj
    ret = cdev_add(demop, devnum, count);
    if(ret){
        goto ERR_STEP1;
    }
    cls = class_create(THIS_MODULE, DEVNAME);
    if(IS_ERR(cls)){
        ret = PTR_ERR(cls);
        goto ERR_STEP1;
    }
    for(i = minor; i < (count+minor); i++){
        devp = device_create(cls, NULL, MKDEV(major, i), NULL, "%s%d", DEVNAME, i);
        if(IS_ERR(devp)){
            ret = PTR_ERR(devp);
            goto ERR_STEP2;
        }
    }
    return 0;
    ERR_STEP2:
        for(--i; i >= minor; i--){
            device_destroy(cls, MKDEV(major, i));
        }
        class_destroy(cls);
    ERR_STEP1:
        unregister_chrdev_region(devnum, count);
    ERR_STEP:
        cdev_del(demop);
        printk(KERN_INFO "alloc_chrdev_region - fail.\n");
        return ret;

} 

static void __exit key_module_exit(void) 
{ 
    int i;
    iounmap(gpio_base);
    gpio_base = 0;
    //get command and pid
    printk(KERN_INFO "step moter driver exit.\n");
    for(i=minor; i < (count+minor); i++){
        device_destroy(cls, MKDEV(major, i));
    }
    class_destroy(cls);
    unregister_chrdev_region(MKDEV(major, minor), count);
    cdev_del(demop);
} 
  
module_init(key_module_init); 
module_exit(key_module_exit); 
