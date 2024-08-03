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

#include "OLED_module.h"
#include "oledfont.h"
MODULE_LICENSE("GPL"); 
MODULE_VERSION("0.1"); 
/*
输入：   command,data

command			data
-------------------------------------------------------------------------			
ShowChar		格式：xxyyzw	x：x坐标 y：y坐标 z：字符 w：字体大小 0/1
ShowNum			格式：xxyyzzzw	x：x坐标 y：y坐标 zzz：三位数 w：字体大小 0/1
ShowString		格式：xxyywsss...		x：x坐标 y：y坐标 w：字体大小 0/1 s:字符串
ShowCHinese		不支持
DrawBMP			不支持
DisplayOff		0
DisplayOn		0
Clear			0
On				0
Init			0
*/
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

void OLED_SCLK_Set(void){
	gpio_set(OLED_SCL);
	udelay(1);
}
void OLED_SCLK_Clr(void){
	gpio_clr(OLED_SCL);
	udelay(1);
}
void OLED_SDIN_Clr(void){
	gpio_clr(OLED_SDA);
	udelay(1);
}
void OLED_SDIN_Set(void){
	gpio_set(OLED_SDA);
	udelay(1);
}
/***********************Delay****************************************/
void Delay_50ms(unsigned int Del_50ms)
{
	unsigned int m;
	for(m=0;m<50;m++){
		udelay(1000);
	}
}

void Delay_1ms(unsigned int Del_1ms)
{
	udelay(1000);
}


/**********************************************
//IIC Start
**********************************************/
void IIC_Start(void)
{
	OLED_SCLK_Set() ;
	OLED_SDIN_Set();
	OLED_SDIN_Clr();
	OLED_SCLK_Clr();
}

/**********************************************
//IIC Stop
**********************************************/
void IIC_Stop(void)
{
	OLED_SCLK_Set() ;
	OLED_SDIN_Clr();
	OLED_SDIN_Set();
}

void IIC_Wait_Ack(void)
{
	OLED_SCLK_Set() ;
	OLED_SCLK_Clr();
}
/**********************************************
// IIC Write byte
**********************************************/

void Write_IIC_Byte(unsigned char IIC_Byte)
{
	unsigned char i;
	unsigned char m,da;
	da=IIC_Byte;
	OLED_SCLK_Clr();
	for(i=0;i<8;i++)		
	{
			m=da;
		//	OLED_SCLK_Clr();
		m=m&0x80;
		if(m==0x80)
		{OLED_SDIN_Set();}
		else OLED_SDIN_Clr();
			da=da<<1;
		OLED_SCLK_Set();
		OLED_SCLK_Clr();
		}
}

/**********************************************
// IIC Write Command
**********************************************/
void Write_IIC_Command(unsigned char IIC_Command)
{
   IIC_Start();
   Write_IIC_Byte(0x78);            //Slave address,SA0=0
	IIC_Wait_Ack();	
   Write_IIC_Byte(0x00);			//write command
	IIC_Wait_Ack();	
   Write_IIC_Byte(IIC_Command); 
	IIC_Wait_Ack();	
   IIC_Stop();
}
/**********************************************
// IIC Write Data
**********************************************/
void Write_IIC_Data(unsigned char IIC_Data)
{
   IIC_Start();
   Write_IIC_Byte(0x78);			//D/C#=0; R/W#=0
	 IIC_Wait_Ack();	
   Write_IIC_Byte(0x40);			//write data
	 IIC_Wait_Ack();	
   Write_IIC_Byte(IIC_Data);
	 IIC_Wait_Ack();	
   IIC_Stop();
}
void OLED_WR_Byte(unsigned dat,unsigned cmd)
{
	if(cmd)
	{
		Write_IIC_Data(dat);
	}
	else 
	{	
		Write_IIC_Command(dat);
	}
}

/********************************************
// fill_Picture
********************************************/
void fill_picture(unsigned char fill_Data)
{
	unsigned char m,n;
	for(m=0;m<8;m++)
	{
		OLED_WR_Byte(0xb0+m,0);		//page0-page1
		OLED_WR_Byte(0x00,0);		//low column start address
		OLED_WR_Byte(0x10,0);		//high column start address
		for(n=0;n<128;n++)
			{
				OLED_WR_Byte(fill_Data,1);
			}
	}
}


//��������
void OLED_Set_Pos(unsigned char x, unsigned char y) 
{ 	OLED_WR_Byte(0xb0+y,OLED_CMD);
	OLED_WR_Byte(((x&0xf0)>>4)|0x10,OLED_CMD);
	OLED_WR_Byte((x&0x0f),OLED_CMD); 
} 

//����OLED��ʾ    
void OLED_Display_On(void)
{
	OLED_WR_Byte(0X8D,OLED_CMD);  //SET DCDC����
	OLED_WR_Byte(0X14,OLED_CMD);  //DCDC ON
	OLED_WR_Byte(0XAF,OLED_CMD);  //DISPLAY ON
}

//�ر�OLED��ʾ     
void OLED_Display_Off(void)
{
	OLED_WR_Byte(0X8D,OLED_CMD);  //SET DCDC����
	OLED_WR_Byte(0X10,OLED_CMD);  //DCDC OFF
	OLED_WR_Byte(0XAE,OLED_CMD);  //DISPLAY OFF
}

//��������,������,������Ļ�Ǻ�ɫ��!��û����һ��!!!	  
void OLED_Clear(void)  
{  
	u8 i,n;		    
	for(i=0;i<8;i++)  
	{  
		OLED_WR_Byte (0xb0+i,OLED_CMD);    //����ҳ��ַ��0~7��
		OLED_WR_Byte (0x00,OLED_CMD);      //������ʾλ�á��е͵�ַ
		OLED_WR_Byte (0x10,OLED_CMD);      //������ʾλ�á��иߵ�ַ   
		for(n=0;n<128;n++)OLED_WR_Byte(0,OLED_DATA); 
	} //������ʾ
}

void OLED_On(void)  
{  
	u8 i,n;		    
	for(i=0;i<8;i++)  
	{  
		OLED_WR_Byte (0xb0+i,OLED_CMD);    //����ҳ��ַ��0~7��
		OLED_WR_Byte (0x00,OLED_CMD);      //������ʾλ�á��е͵�ַ
		OLED_WR_Byte (0x10,OLED_CMD);      //������ʾλ�á��иߵ�ַ   
		for(n=0;n<128;n++)OLED_WR_Byte(1,OLED_DATA); 
	} //������ʾ
}

//��ָ��λ����ʾһ���ַ�,���������ַ�
//x:0~127
//y:0~63
//mode:0,������ʾ;1,������ʾ				 
//size:ѡ������ 16/12 
void OLED_ShowChar(u8 x,u8 y,u8 chr,u8 Char_Size)
{      	
	unsigned char c=0,i=0;	
		c=chr-' ';//�õ�ƫ�ƺ��ֵ			
		if(x>Max_Column-1){x=0;y=y+2;}
		if(Char_Size ==16)
			{
			OLED_Set_Pos(x,y);	
			for(i=0;i<8;i++)
			OLED_WR_Byte(F8X16[c*16+i],OLED_DATA);
			OLED_Set_Pos(x,y+1);
			for(i=0;i<8;i++)
			OLED_WR_Byte(F8X16[c*16+i+8],OLED_DATA);
			}
			else {	
				OLED_Set_Pos(x,y);
				for(i=0;i<6;i++)
				OLED_WR_Byte(F6x8[c][i],OLED_DATA);
				
			}
}

//m^n����
u32 oled_pow(u8 m,u8 n)
{
	u32 result=1;	 
	while(n--)result*=m;    
	return result;
}			

//��ʾ2������
//x,y :�������	 
//len :���ֵ�λ��
//size:�����С
//mode:ģʽ	0,���ģʽ;1,����ģʽ
//num:��ֵ(0~4294967295);	 		  
void OLED_ShowNum(u8 x,u8 y,u32 num,u8 len,u8 size2)
{         	
	u8 t,temp;
	u8 enshow=0;						   
	for(t=0;t<len;t++)
	{
		temp=(num/oled_pow(10,len-t-1))%10;
		if(enshow==0&&t<(len-1))
		{
			if(temp==0)
			{
				OLED_ShowChar(x+(size2/2)*t,y,' ',size2);
				continue;
			}else enshow=1; 
		 	 
		}
	 	OLED_ShowChar(x+(size2/2)*t,y,temp+'0',size2); 
	}
} 

//��ʾһ���ַ��Ŵ�
void OLED_ShowString(u8 x,u8 y,u8 *chr,u8 Char_Size)
{
	unsigned char j=0;
	while (chr[j]!='\0')
	{		OLED_ShowChar(x,y,chr[j],Char_Size);
			x+=8;
		if(x>120){x=0;y+=2;}
			j++;
	}
}

//��ʾ����
void OLED_ShowCHinese(u8 x,u8 y,u8 no)
{      			    
	u8 t,adder=0;
	OLED_Set_Pos(x,y);	
    for(t=0;t<16;t++)
		{
				OLED_WR_Byte(Hzk[2*no][t],OLED_DATA);
				adder+=1;
     }	
		OLED_Set_Pos(x,y+1);	
    for(t=0;t<16;t++)
			{	
				OLED_WR_Byte(Hzk[2*no+1][t],OLED_DATA);
				adder+=1;
      }					
}

/***********������������ʾ��ʾBMPͼƬ128��64��ʼ������(x,y),x�ķ�Χ0��127��yΪҳ�ķ�Χ0��7*****************/
void OLED_DrawBMP(unsigned char x0, unsigned char y0,unsigned char x1, unsigned char y1,unsigned char BMP[])
{ 	
 unsigned int j=0;
 unsigned char x,y;
  
  if(y1%8==0) y=y1/8;      
  else y=y1/8+1;
	for(y=y0;y<y1;y++)
	{
		OLED_Set_Pos(x0,y);
    for(x=x0;x<x1;x++)
	    {      
	    	OLED_WR_Byte(BMP[j++],OLED_DATA);	    	
	    }
	}
} 

//��ʼ��SSD1306					    
void OLED_Init(void)
{ 	
 
	OLED_WR_Byte(0xAE,OLED_CMD);//--display off
	OLED_WR_Byte(0x00,OLED_CMD);//---set low column address
	OLED_WR_Byte(0x10,OLED_CMD);//---set high column address
	OLED_WR_Byte(0x40,OLED_CMD);//--set start line address  
	OLED_WR_Byte(0xB0,OLED_CMD);//--set page address
	OLED_WR_Byte(0x81,OLED_CMD); // contract control
	OLED_WR_Byte(0xFF,OLED_CMD);//--128   
	//OLED_WR_Byte(0xA1,OLED_CMD);//set segment remap 
	OLED_WR_Byte(0xA6,OLED_CMD);//--normal / reverse
	OLED_WR_Byte(0xA8,OLED_CMD);//--set multiplex ratio(1 to 64)
	OLED_WR_Byte(0x3F,OLED_CMD);//--1/32 duty
	//OLED_WR_Byte(0xC8,OLED_CMD);//Com scan direction
	OLED_WR_Byte(0xD3,OLED_CMD);//-set display offset
	OLED_WR_Byte(0x00,OLED_CMD);//

	OLED_WR_Byte(0xA0,OLED_CMD);
	OLED_WR_Byte(0xC0,OLED_CMD);
	
	OLED_WR_Byte(0xD5,OLED_CMD);//set osc division
	OLED_WR_Byte(0x80,OLED_CMD);//
	
	OLED_WR_Byte(0xD8,OLED_CMD);//set area color mode off
	OLED_WR_Byte(0x05,OLED_CMD);//
	
	OLED_WR_Byte(0xD9,OLED_CMD);//Set Pre-Charge Period
	OLED_WR_Byte(0xF1,OLED_CMD);//
	
	OLED_WR_Byte(0xDA,OLED_CMD);//set com pin configuartion
	OLED_WR_Byte(0x12,OLED_CMD);//
	
	OLED_WR_Byte(0xDB,OLED_CMD);//set Vcomh
	OLED_WR_Byte(0x30,OLED_CMD);//
	
	OLED_WR_Byte(0x8D,OLED_CMD);//set charge pump enable
	OLED_WR_Byte(0x14,OLED_CMD);//
	
	OLED_WR_Byte(0xAF,OLED_CMD);//--turn on oled panel
}  
//*************************************************************************************************
static void gpio_init(void)
{
  gpio_fsel (OLED_SCL, BCM2835_GPIO_FSEL_OUTP);
  gpio_fsel (OLED_SDA, BCM2835_GPIO_FSEL_OUTP);
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
	printk("start");
	int a, b, ret, i;
	const char *p;
	for (i = 0; i < length && i < 65535; i++)
		get_user(cmd_buffer[i], buffer + i);
	cmd_buffer[i] = 0;
	p = cmd_buffer;
	char all_data[100]={0};//全部的数据
	char my_command[20]={0};//输入指令
	char my_data[80]={0};//数据数据
	int my_command_num;
	ret = sscanf(p, "%s", all_data);//读入用户的数据，ret表示成功解析的参数数量

	char *token, *str, *saveptr;
	str = all_data;
    token = strsep(&str, ",");
    if (token != NULL) {
        strncpy(my_command, token, sizeof(my_command));
        token = strsep(&str, ",");
        if (token != NULL) {
            strncpy(my_data, token, sizeof(my_data));
            printk(KERN_INFO "my_command: %s\n", my_command);
            printk(KERN_INFO "my_data: %s\n", my_data);
        } else {
            printk(KERN_ERR "Error: Unable to tokenize inputArray.\n");
        }
    } else {
        printk(KERN_ERR "Error: Unable to tokenize inputArray.\n");
    }
		// 测试指令和数据解析结果
		// OLED_ShowString(0,0,my_command,8); 
		// OLED_ShowString(0,1,my_data,8); 
		// OLED_ShowString(0,2,&(my_command[0]),8); 
		// OLED_ShowString(0,3,&(my_command[4]),8);

		if(my_command[0]=='S'&&my_command[4]=='C'&&my_command[5]=='h'){//ShowChar
			//格式：xxyyzw	x：x坐标 y：y坐标 z：字符 w：字体大小 0/1
			// OLED_ShowString(0,4,"ShowChar",8);
			// OLED_ShowNum(0,0,(int)my_data[0]-48,2,8);
			// OLED_ShowNum(0,1,(int)my_data[1]-48,2,8);
			// OLED_ShowNum(0,2,(int)my_data[2]-48,2,8);
			// OLED_ShowNum(0,3,(int)my_data[3]-48,2,8);
			int data1=(int)my_data[0]-48;//减去ascii码得到数字
			int data2=(int)my_data[1]-48;
			int data3=(int)my_data[2]-48;
			int data4=(int)my_data[3]-48;
			u8 x=10*data1+data2;
			u8 y=10*data3+data4;
			u8 chr=(int)my_data[4];
			u8 Char_Size=(int)my_data[5]-48;//字体大小转换
			if(Char_Size==1){
				Char_Size=16;
			}
			if(Char_Size==0){
				Char_Size=8;
			}
			// OLED_ShowNum(0,0,x,2,8);
			// OLED_ShowNum(0,1,y,2,8);
			// OLED_ShowChar(0,2,chr,8);
			// OLED_ShowNum(0,3,Char_Size,2,8);
			OLED_ShowChar(x,y,chr,Char_Size);
		}
		if(my_command[0]=='S'&&my_command[4]=='N'){//ShowNum
			//格式：xxyyzzzw	x：x坐标 y：y坐标 zzz：三位数 w：字体大小 0/1
			// OLED_ShowString(0,4,"ShowNum",8);
			int data1=(int)my_data[0]-48;//减去ascii码得到数字
			int data2=(int)my_data[1]-48;
			int data3=(int)my_data[2]-48;
			int data4=(int)my_data[3]-48;
			int data5=(int)my_data[4]-48;
			int data6=(int)my_data[5]-48;
			int data7=(int)my_data[6]-48;
			int data8=(int)my_data[7]-48;
			u8 x=10*data1+data2;
			u8 y=10*data3+data4;
			u8 num=100*data5+10*data6+data7;
			u8 Char_Size=data8;//字体大小转换
			if(Char_Size==1){
				Char_Size=16;
			}
			if(Char_Size==0){
				Char_Size=8;
			}
			OLED_ShowNum(x,y,num,3,Char_Size);
		}
		if(my_command[0]=='S'&&my_command[4]=='S'){//ShowString
			// OLED_ShowString(0,4,"ShowString",8);
			//格式：xxyywsss...		x：x坐标 y：y坐标 w：字体大小 0/1 s:字符串
			int data1=(int)my_data[0]-48;//减去ascii码得到数字
			int data2=(int)my_data[1]-48;
			int data3=(int)my_data[2]-48;
			int data4=(int)my_data[3]-48;
			u8 x=10*data1+data2;
			u8 y=10*data3+data4;
			u8 Char_Size=(int)my_data[4]-48;
			if(Char_Size==1){//字体大小转换
				Char_Size=16;
			}
			if(Char_Size==0){
				Char_Size=8;
			}
			char *src = my_data;
			OLED_ShowString(x,y,src+5,Char_Size);		
		}
		if(my_command[0]=='S'&&my_command[4]=='C'&&my_command[5]=='H'){//ShowCHinese
			OLED_ShowString(0,4,"No_Support_ShowCHinese",8);
			// OLED_ShowCHinese(u8 x,u8 y,u8 no)
		}
		if(my_command[0]=='D'&&my_command[4]=='B'){//DrawBMP
			OLED_ShowString(0,4,"No_Support_DrawBMP",8);
			// OLED_DrawBMP(unsigned char x0, unsigned char y0,unsigned char x1, unsigned char y1,unsigned char BMP[])
		}
		if(my_command[0]=='D'&&my_command[8]=='f'){//DisplayOff
			// OLED_ShowString(0,4,"DisplayOff",8);
			OLED_Display_Off();
		}
		if(my_command[0]=='D'&&my_command[7]=='O'){//DisplayOn
			// OLED_ShowString(0,4,"DisplayOn",8);
			OLED_Display_On();
		}
		if(my_command[0]=='C'&&my_command[4]=='r'){//Clear
			// OLED_ShowString(0,4,"Clear",8);
			OLED_Clear();
		}
		if(my_command[0]=='O'&&my_command[1]=='n'){//On
			// OLED_ShowString(0,4,"On",8);
			OLED_On();
		}
		if(my_command[0]=='I'&&my_command[1]=='n'){//Init
			OLED_Init();
		}
	printk("end");
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

#define DEVNAME "OLED_module" //设备号
static int major = 0; //主设备号
static int minor = 0;  //次设备号
const  int count = 1;
static struct cdev *demop = NULL;
static struct class *cls = NULL;

static int __init OLED_module_init(void) 
{ 
    dev_t devnum; //设备号
    int ret, i;
    struct device *devp = NULL;
    
    printk(KERN_INFO "OLED_module driver loaded.\n"); 
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

static void __exit OLED_module_exit(void) 
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
  
module_init(OLED_module_init); 
module_exit(OLED_module_exit); 
