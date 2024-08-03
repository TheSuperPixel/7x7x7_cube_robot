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


#include "step_moter.h"
#include "step_tab.h"

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
  gpio_fsel (M3_STEP, BCM2835_GPIO_FSEL_OUTP);//...
  gpio_fsel (M3_DIR,  BCM2835_GPIO_FSEL_OUTP);
  gpio_fsel (M2_STEP, BCM2835_GPIO_FSEL_OUTP);
  gpio_fsel (M2_DIR,  BCM2835_GPIO_FSEL_OUTP);
  gpio_fsel (M1_STEP, BCM2835_GPIO_FSEL_OUTP);
  gpio_fsel (M1_DIR,  BCM2835_GPIO_FSEL_OUTP);
  gpio_clr(M1_STEP);
  gpio_clr(M2_STEP);
  gpio_clr(M3_STEP);
  gpio_fsel(M3_SWITCH, BCM2835_GPIO_FSEL_INPT);
  gpio_fsel(M2_SWITCH, BCM2835_GPIO_FSEL_INPT);
  gpio_fsel(M1_SWITCH, BCM2835_GPIO_FSEL_INPT);
  gpio_set_pud(M1_SWITCH, BCM2835_GPIO_PUD_UP);
}


// 步进电机控制
// 加速算法参考http://hwml.com/LeibRamp.htm
static void move(int gpio_pin, int length, int *array, int step)
{
  int p, i;
  unsigned long flags;
  local_irq_save(flags);//关闭内核中断
  for (i=0; i<step; i++){
    if (i < length && i < step / 2)
       p = array[i];
    else if(step - 1 - i < length)
       p = array[step - 1 - i];
    else
       p = array[length - 1];
    // pull high
    gpio_set(gpio_pin);
    udelay(p);
    // pull low
    gpio_clr(gpio_pin);
    udelay(p);
  }
  local_irq_restore(flags);//恢复内核中断
}

// 回零点
static void m3_zero(void)
{
  int stat,stat_old,i;
  //让魔方笼先往一个方向转一个小角度
  gpio_set(M3_DIR);
  move(M3_STEP, m3_length, m3_array, 128);
  stat_old = gpio_read(M3_SWITCH);
  gpio_clr(M3_DIR);
  //让魔方笼往回转，直到传感器电平下降沿
  for(i=0;i<3200;i++){
    move(M3_STEP, m3_length, m3_array,1);
    stat = gpio_read(M3_SWITCH);
    if(stat == LOW && stat_old == HIGH){
      break;
    }
    stat_old = stat;
  }
  move(M3_STEP, m3_length, m3_array, 50);
}
static void m2_zero(void)
{
  int stat,stat_old,i;
  gpio_set(M2_DIR);
  //让翻转架先往一个方向转一个小角度
  move(M2_STEP, m2_length, m2_array, 128);
  stat_old = gpio_read(M2_SWITCH);
  gpio_clr(M2_DIR);
  //让翻转架往回转，直到传感器电平下降沿
  for(i=0;i<1600;i++){
    move(M2_STEP, m2_length, m2_array, 1);
    stat = gpio_read(M2_SWITCH);
    if(stat == LOW && stat_old == HIGH){
      break;
    }
    stat_old = stat;
  }
  move(M2_STEP, m2_length, m2_array, 36);
}
static void m1_zero(void)
{
  int stat,stat_old,i;
  //让升降杆先上升一下
  gpio_set(M1_DIR);
  move(M1_STEP, m1_length, m1_array,  48);
  stat_old = gpio_read(M1_SWITCH);
  gpio_clr(M1_DIR);
  //让升降杆慢慢下降，直到传感器电平下降沿
  for(i=0;i<1200;i++){
    move(M1_STEP, m1_length, m1_array,  1);
    stat = gpio_read(M1_SWITCH);
    if(stat == LOW && stat_old == HIGH){
      break;
    }
    stat_old = stat;
  }
  move(M1_STEP, m1_length, m1_array,  12);
}

static void udelay_test(int x)
{
  unsigned long flags;
  unsigned int time_start, time_end;
  int i, diff;
  int avg_val = 0;
  int temp[16] = {0};
  
  local_irq_save(flags);
  for(i=0;i<100;i++){
    time_start = get_cycles();
    udelay(80);
    time_end = get_cycles();
    avg_val += time_end - time_start;
  }
  avg_val /= 100;
  for(i=0;i<x;i++){
    time_start = get_cycles();
    udelay(80);
    time_end = get_cycles();
    diff = time_end - time_start - avg_val;
    diff = (diff + 40) / 5;
    if(diff > 15)
      diff = 15;
    else if(diff < 0)
      diff = 0;
    temp[diff] += 1; 
  }
  local_irq_restore(flags);
  
  printk(KERN_INFO "avg delay cycles of udelay(80) is %d\n", avg_val);
  for(i=0;i<16;i++){
    printk(KERN_INFO "%d ~ %d error is %d\n", i*5-40,i*5+4-40,temp[i]);
  }
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
    int bytes_read = 0;

    if (*msg_Ptr == 0)
        return 0;

    while (length && *msg_Ptr) {
        put_user(*(msg_Ptr++), buffer++);
        length--;
        bytes_read++;
    }

    return bytes_read;
}

static ssize_t device_write(struct file *file, const char *buffer, size_t length, loff_t *offset)
{
    int a, b, ret, i;
    const char *p;
    for (i = 0; i < length && i < 65535; i++)
        get_user(cmd_buffer[i], buffer + i);//读入用户的数据
    cmd_buffer[i] = 0;
    p = cmd_buffer;
    while(1){
      ret = sscanf(p, "%d,%d", &a,&b);//读入用户的数据，ret表示成功解析的参数数量
      if(2 == ret){
        //printk(KERN_INFO "a=%d, b=%d\n", a, b);
        if(0 == a){//回0
          m3_zero();
          m2_zero();
          m1_zero();
        }else if(1 == a){
          if(b<0){
            b = -b;
            gpio_clr(M1_DIR);
          }else{
            gpio_set(M1_DIR);
          }
          b*=8;
          move(M1_STEP, m1_length, m1_array, b);
        }else if(2 == a){
          if(b<0){
            b = -b;
            gpio_clr(M2_DIR);
          }else{
            gpio_set(M2_DIR);
          }
          move(M2_STEP, m2_length, m2_array, b);
        }else if(3 == a){
          if(b<0){
            b = -b;
            gpio_set(M3_DIR);
          }else{
            gpio_clr(M3_DIR);
          }
          move(M3_STEP, m3_length, m3_array, b);
        }else if(4 == a){
          udelay_test(b);
        }
      }else{
        return length;
      }
      // 搜索下一指令
      while(1){
        if(*p == ';'){
          p++;
          break;
        }else if (*p == 0){
          return length;
        }else{
          p++;
        }
      }
    }
}

static struct file_operations fops = {
    //内核定义好的结构体 内核源码里有
    //就是驱动的结构体 要加载到内核驱动链表
    .read = device_read,//当用户空间程序调用 read 系统调用时，内核会调用这个函数来处理读取操作。
    .write = device_write,//当用户空间程序调用 write 系统调用时，内核会调用这个函数来处理写入操作。
    .open = device_open,//当用户空间程序调用 open 系统调用时，内核会调用这个函数来处理打开文件的操作
    .release = device_release//当所有文件描述符关闭或进程终止时，内核会调用这个函数来释放文件相关的资源。
};

#define DEVNAME "step_moter" //设备号
static int major = 0; //主设备号
static int minor = 0;  //次设备号
const  int count = 1;
static struct cdev *demop = NULL;
static struct class *cls = NULL;

static int __init step_moter_init(void) 
{ 
    dev_t devnum; //设备号
    int ret, i;
    struct device *devp = NULL;
    
    printk(KERN_INFO "step moter driver loaded.\n"); 
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

static void __exit step_moter_exit(void) 
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
  
module_init(step_moter_init); 
module_exit(step_moter_exit); 
