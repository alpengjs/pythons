#/router/bin/python-2.7.1
# Script to
#   build and modify the rootfs
#   build the bzImage with the roots
#
# Example:
#   Use default rootfs file:
#   ./build_kernel.py
#
#   Use custom rootfs file:
#   ./build_kernel.py -r /<path>/<to>/<victory-rootfs>/rootfs/utah
#
#   Build ovld rootfs before compiling kernel bzImage. this option uses
#   build_rootfs.config to determine which platform rootfs to build.
#   ./build_kernel.py -b /<path>/<to>/<victory-rootfs>/rootfs
#
############################################################

import sys
import stat
import os, getopt
import subprocess
import fileinput
import shutil
import re

# used for update path on CONFIG_INITRAMFS_SOURCE, .config file
import fileinput
import sys

kernel_name = 'linux-4.4.87'
rootfs_name = 'rootfs'
gitcmd = 'git clone '
gitsuffix='.git'
shared_path = '/home/shared/'
kernel_git = kernel_name + gitsuffix
rootfs_git = rootfs_name + gitsuffix
kernel_config = '.config'
config_cmd = 'CONFIG_CMDLINE_BOOL' 
enable_cmd = config_cmd + '=y\n'
setup_cmd = 'CONFIG_CMDLINE=\"rdinit=/sbin/init\"\n'
disable_cmd_over = '# CONFIG_CMDLINE_OVERRIDE is not set\n'
new_config_cmd = enable_cmd + setup_cmd + disable_cmd_over
config_init = 'CONFIG_INITRAMFS_SOURCE'
init_rootfs = config_init + '=\"../rootfs\"\n'
setup_root_uid = 'CONFIG_INITRAMFS_ROOT_UID=0\n'
setup_root_gid = 'CONFIG_INITRAMFS_ROOT_GID=0\n'
new_config_init = init_rootfs + setup_root_uid + setup_root_gid

CPIO_FILE = 'usr/initramfs_data.cpio.gz'


def replace_line(fname, keyword, rstring):
    for line in fileinput.input(fname, inplace = 1):
        if keyword in line:
            line = line.replace(line, rstring)

        sys.stdout.write(line) #necessary, write to file again 
    

def deal_with_rootfs(): 
    # if rootfs not exist, clone it!
    if not os.path.exists(rootfs_name):
        cmd = gitcmd + shared_path + rootfs_git 
        subprocess.call(cmd, shell= True)

        # change dir to rootfs and create /dev/console 
        # b/c char file 'console' is empty file
        # which cannot commit into git 
        os.chdir(rootfs_name)
        device = os.makedev(5, 1)
        os.mknod('dev/console', 0644|stat.S_IFCHR, device)
        os.chmod('dev/console', 0644|stat.S_IFCHR) 

        # change dir back to original
        os.chdir(owd)

    # already cloned, nothing to do.


def deal_with_kernel():
    # check kerenl available, clone it if not 
    if not os.path.exists(kernel_name):
        cmd = gitcmd + shared_path + kernel_git
        subprocess.call(cmd, shell= True)

        # change dir to kernel 
        os.chdir(kernel_name)

        # setup default .config file 
        cmd = 'make defconfig'
        subprocess.call(cmd, shell= True)

        # enable built-in cmd line and update the command
        replace_line(kernel_config, config_cmd, new_config_cmd)

        # update the path to CONFIG_INITRAMFS_SOURCE
        replace_line(kernel_config, config_init, new_config_init)

    # clean .cpio
    if os.path.exists(CPIO_FILE):
        os.remove(CPIO_FILE)

    print 'setup ready, start kernel build..'
    #default image is bzImage
    cmd = 'make -j6 bzImage ' 

    print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
    print cmd
    subprocess.call(cmd, shell= True)

    # change dir back to original
    os.chdir(owd)

     

# parse .config file 

# store current dir
owd = os.getcwd()

# rootfs and kernel 
deal_with_rootfs()
deal_with_kernel()


