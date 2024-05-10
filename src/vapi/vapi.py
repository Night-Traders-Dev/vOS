# vapi.py
import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))


from vsystem.virtualfs import File
from vsystem.virtualfs import Directory
from vsystem.virtualfs import VirtualFileSystem

from vsystem.virtualkernel import VirtualKernel
from vsystem.virtualkernel import QShellInterpreter
from vsystem.virtualkernel import VirtualProcess
from vsystem.virtualkernel import Animations
from vsystem.virtualkernel import UserAccount
from vsystem.virtualkernel import PasswordFile

from vsystem.virtualmachine import VirtualMachine
from vsystem.virtualmachine import Wallet
from vsystem.virtualmachine import AddressTools
from vsystem.virtualmachine import Block
from vsystem.virtualmachine import Blockchain
from vsystem.virtualmachine import Transaction

from vsystem.virtualinput import TerminalInput

from vsystem.vcommands import VCommands


## VirtualAPI Class Instamces

def fs_instance():
    fs_instance = VirtualFileSystem()
    return fs_instance

def kernel_instance():
    kernel_instance = VirtualKernel()
    return kernel_instance

def animations_instance():
    animations_instance = Animations()
    return animations_instance

def vproc_instance():
    vproc_instance = VirtualProcess("vprocd", 0, "Kernel")
    return vproc_instance

def passwordtools_instance():
    passwordtools_instance = PasswordFile("passwd")
    return passwordtools_instance

def establish_directory(dir):
    return Directory(dir)

def qshell_instance_sys():
    return qshell_instance

def vm_instance():
    return VirtualMachine()

def vm_addresstools_instance():
    return AddressTools()

def vm_wallet_instance():
    return Wallet()

def vcommands_instance():
    return VCommands()

## VirtualAPI Functions

def get_active_user():
    try:
        fs_instance = VirtualFileSystem()
        passwordtools_instance = PasswordFile("passwd")
        active_user = passwordtools_instance.check_passwd_file(fs_instance)[0]
        return active_user
    except:
        active_user = passwordtools_instance.check_passwd_file(fs_instance)[0]
        return active_user

def home_fs_init(active_user):
    user_dir = "/home/" + active_user
    kernel = VirtualKernel()
    fs = VirtualFileSystem()
    # Check if 'home' directory exists
    if "home" in fs.root.subdirectories:
        # Check if 'user' directory exists
        if active_user in fs.root.subdirectories["home"].subdirectories:                                                                       # Set default starting directory to /home/user
            current_directory = fs.root.subdirectories["home"].subdirectories[active_user]
        else:
            kernel.log_command("User directory not found. Creating...")
            fs.create_directory(user_dir)
            current_directory = fs.root.subdirectories["home"].subdirectories[active_user]
    else:
        kernel.log_command("Home directory not found. Creating...")
        fs.create_directory("/home")
        fs.create_directory(user_dir)
        current_directory = fs.root.subdirectories["home"].subdirectories[active_user]
#    self.kernel.log_command("Initializing VirtualMachine...")
#    vm = VirtualMachine(kernel, fs)  # Create a VirtualMachine instance
    kernel.log_command(f"Permissions: {current_directory.permissions}")

    try:
        kernel.boot_verbose()
        kernel.log_command(f"Current directory: {current_directory.get_full_path()}")
        return current_directory
    except Exception as e:
        kernel.log_command(f"Error during kernel boot: {str(e)}")

    def su_check(self, command):
            if not self.su:
                print(f"{command} requires su permission")
                self.kernel.log_command(f"[!!]su_check: {self.active_user} invalid permissions for {command}")
                return False
            else:
                return True


# Import the api to gain access to vOS components
#
#from vapi import initialize_system
