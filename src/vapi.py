# vapi.py

from virtualfs import File
from virtualfs import Directory
from virtualfs import VirtualFileSystem

from virtualkernel import VirtualKernel
from virtualkernel import QShellInterpreter
from virtualkernel import VirtualProcess
from virtualkernel import Animations
from virtualkernel import UserAccount
from virtualkernel import PasswordFile

from virtualmachine import VirtualMachine
from virtualmachine import Wallet
from virtualmachine import AddressTools
from virtualmachine import Block
from virtualmachine import Blockchain
from virtualmachine import Transaction

from virtualinput import TerminalInput

class UserConfig:
    user = None


def initialize_system():
    fs_instance = VirtualFileSystem()
    kernel_instance = VirtualKernel()
    animations_instance = Animations()
    vproc_instance = VirtualProcess("kernel", 0, "Kernel")
    passwordtools_instance = PasswordFile("passwd")
    qshell_instance = QShellInterpreter()

    return fs_instance, kernel_instance, animations_instance, vproc_instance, passwordtools_instance


def fs_instance_sys():
    fs_instance = VirtualFileSystem()
    return fs_instance

def kernel_instance_sys():
    kernel_instance = VirtualKernel()
    return kernel_instance

def animations_instance_sys():
    animations_instance = Animations()
    return animations_instance

def vproc_instance_sys():
    return vproc_instance

def passwordtools_instance_sys():
    passwordtools_instance = PasswordFile("passwd")
    return passwordtools_instance

def establish_directory(dir):
    return Directory(dir)

def qshell_instance_sys():
    return qshell_instance

def vm_addresstools_instance():
    return AddressTools

def get_active_user():
    fs_instance = VirtualFileSystem()
    passwordtools_instance = PasswordFile("passwd")
    active_user = passwordtools_instance.check_passwd_file(fs_instance)[0]
    return active_user
# Import the api to gain access to vOS components
#
#from vapi import initialize_system
