#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0xcaec5711, "module_layout" },
	{ 0x78770421, "device_destroy" },
	{ 0xedc03953, "iounmap" },
	{ 0xae651774, "cdev_del" },
	{ 0x6091b333, "unregister_chrdev_region" },
	{ 0xf0462214, "class_destroy" },
	{ 0x5d3eb04, "device_create" },
	{ 0x84e8af7f, "__class_create" },
	{ 0xc2bcb805, "cdev_add" },
	{ 0xe3ec2f2b, "alloc_chrdev_region" },
	{ 0xaaad239e, "cdev_init" },
	{ 0x89827d65, "cdev_alloc" },
	{ 0x1d37eeed, "ioremap" },
	{ 0x86332725, "__stack_chk_fail" },
	{ 0x328a05f1, "strncpy" },
	{ 0x85df9b6c, "strsep" },
	{ 0xbcab6ee6, "sscanf" },
	{ 0x5f754e5a, "memset" },
	{ 0x28118cb6, "__get_user_1" },
	{ 0xc5850110, "printk" },
	{ 0x8f678b07, "__stack_chk_guard" },
	{ 0xe707d823, "__aeabi_uidiv" },
	{ 0x8e865d3c, "arm_delay_ops" },
	{ 0xbb72d4fe, "__put_user_1" },
	{ 0x836feaf2, "try_module_get" },
	{ 0xe9d59def, "module_put" },
	{ 0xb1ad28e0, "__gnu_mcount_nc" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "377FC4875E10A67555461D0");
