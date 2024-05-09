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
