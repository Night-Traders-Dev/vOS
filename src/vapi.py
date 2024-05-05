# vapi.py

#from virtualos import VirtualOS
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

from virtualinput import TerminalInput


def initialize_system():
 #   os_instance = VirtualOS()
    fs_instance = VirtualFileSystem()
    kernel_instance = VirtualKernel()
    animations_instance = Animations()
    vproc_instance = VirtualProcess("kernel", 0, "Kernel")
    passwordtools_instance = PasswordFile("passwd")

    return fs_instance, kernel_instance, animations_instance, vproc_instance, passwordtools_instance


# Import the api to gain access to vOS components
#
#from vapi import initialize_system
