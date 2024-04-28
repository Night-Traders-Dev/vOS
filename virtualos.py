import sys
import time
from virtualfs import VirtualFileSystem
from vcommands import VCommands
from virtualmachine import VirtualMachine
from virtualkernel import VirtualKernel

class VirtualOS:
    def __init__(self):
        self.kernel = VirtualKernel()
        VCommands.clear_screen()
        self.kernel.log_command("Logging component version numbers...")
        self.kernel.log_command("Component Version Numbers:\n")
        self.kernel.log_command("VirtualKernel Version: V0.0.1")
        self.kernel.log_command("VirtualOS Version: V0.0.1")
        self.kernel.log_command("VirtualFS Version: V0.0.1")
        self.kernel.log_command("VirtualMachine Version: V0.0.1")
        self.kernel.log_command(f"Python Version: {sys.version}")
        self.kernel.log_command("Initializing Kernel...")
        self.kernel.log_command("Booting up VirtualOS...")
        self.kernel.log_command("Initializing VirtualFileSystem...")
        self.fs = VirtualFileSystem()  # Initialize the filesystem
        self.kernel.log_command("Loading VirtualFileSystem...")
        self.load_with_loading_circle()  # Call method to load with loading circle
        self.user_perms = "rwxr-xr-x"
        self.kernel.log_command("Default user permissions set(rwxr-xr-x)...")

        # Check if 'home' directory exists
        if "home" in self.fs.root.subdirectories:
            # Check if 'user' directory exists
            if "user" in self.fs.root.subdirectories["home"].subdirectories:
                # Set default starting directory to /home/user
                self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]
            else:
                self.kernel.log_command("User directory not found. Creating...")
                self.fs.create_directory("/home/user")
                self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]
        else:
            self.kernel.log_command("Home directory not found. Creating...")
            self.fs.create_directory("/home")
            self.fs.create_directory("/home/user")
            self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]

        self.kernel.log_command("Initializing VirtualMachine...")
        self.vm = VirtualMachine(self.kernel, self.fs)  # Create a VirtualMachine instance
        self.kernel.log_command(f"Permissions: {self.current_directory.permissions}")

        try:
            self.kernel.boot_verbose()
            self.kernel.log_command(f"Current directory: {self.current_directory.get_full_path()}")
        except Exception as e:
            self.kernel.log_command(f"Error during kernel boot: {str(e)}")

    def load_with_loading_circle(self):
        self.kernel.log_command("Boot Animation Loaded...")
        loading_animation = ['|', '/', '-', '\\']  # ASCII characters for the loading animation
        for _ in range(10):  # Repeat the animation 10 times
            for char in loading_animation:
                sys.stdout.write('\r' + f"Booting vOS... {char}")  # Overwrite the same line with the loading animation
                sys.stdout.flush()
                time.sleep(0.1)  # Add a short delay to control the speed of the animation
        sys.stdout.write('\r')  # Clear the loading animation line
        sys.stdout.flush()
        self.kernel.log_command("File system loaded successfully.")

    def run_shell(self):
        while True:
            try:
                command = input(f"{self.current_directory.get_full_path()} $ ").strip()
                self.kernel.log_command(command)  # Log the command
                if command == "exit":
                    print("Exiting VirtualOS...")
                    self.fs.save_file_system("file_system.json")  # Save filesystem
                    self.kernel.delete_dmesg()  # Delete dmesg file on exit
                    break
                elif command.startswith("sudo "):  # Check if the command starts with 'sudo'
                    parts = command.split(" ")
                    sudo_command = parts[1]  # Extract the command after 'sudo'
                    # Extract permissions if provided
                    permissions = parts[2] if len(parts) > 2 else ""
                    # Capture the entire command including path and file
                    sudo_args = ' '.join(parts[1:])
                    VCommands.sudo(self, self.fs, self.current_directory, sudo_args)

                elif command.startswith("su"):
                    parts = command.split(" ", 1)
                    permissions = parts[1] if len(parts) > 1 else "rwxrwxrwx"
                    VCommands.su(self, self.fs, self.current_directory, permissions)



                elif command.startswith("reboot"):
                    confirmation = input("Are you sure you want to reboot? (yes/no): ").strip().lower()
                    if confirmation == "yes":
                        self.kernel.reboot_os()  # Call the reboot function from the kernel
                    else:
                        print("Reboot cancelled.")
                        self.kernel.log_command(f"[!]Reboot cancelled")

                elif command.startswith("perms"):
                    _, path = command.split(" ", 1)
                    VCommands.perms(self.fs, path)




                elif command.startswith("mkdir"):
                    _, path = command.split(" ", 1)
                    VCommands.mkdir(self.fs, path)
                    self.fs.save_file_system("file_system.json")  # Save filesystem


                elif command.startswith("ls"):
                    parts = command.split(" ")
                    if len(parts) > 1:
                        _, path = parts
                    else:
                        path = None
                    self.kernel.log_command(f"ls debug: {self.current_directory} and {path}")
                    VCommands.ls(self.fs, self.current_directory, path)

                elif command.startswith("cd"):
                    _, path = command.split(" ", 1)
                    self.current_directory = VCommands.cd(self, self.fs, self.current_directory, path)
                elif command.startswith("cat"):
                    try:
                        _, path = command.split(" ", 1)
                    except ValueError:
                  # If no path is specified, use the current directory
                        path = None
                    VCommands.cat(self.fs, self.current_directory, path)
                elif command.startswith("rmdir"):
                    _, path = command.split(" ", 1)
                    VCommands.rmdir(self.fs, path)
                    self.fs.save_file_system("file_system.json")  # Save filesystem
                elif command.startswith("nano"):
                    try:
                         _, path = command.split(" ", 1)
                    except ValueError:
                        # If no path is specified, use the current directory
                        path = None
                    VCommands.nano(self.fs, self.current_directory, path)
                elif command.startswith("version"):
                    VCommands.version()
                elif command == "clear":
                    VCommands.clear_screen()
                elif command == "run_vm":  # Command to run the virtual machine
                    self.vm.run()
                elif command == "dmesg":  # Command to print virtual dmesg
                    self.kernel.print_dmesg()
                elif command == "toggle_fs_monitoring":  # Command to toggle filesystem monitoring
                    self.kernel.toggle_filesystem_monitoring()
                elif command == "monitor_fs":  # Command to monitor filesystem
                    self.kernel.monitor_filesystem("file_system.json")
                elif command == "pwd":  # Corrected call to pwd method
                    VCommands.pwd(self.current_directory)  # Pass the current directory
                elif command.startswith("touch"):
                    try:
                        _, path = command.split(" ", 1)
                    except ValueError:
                        # If no path is specified, use the current directory
                        path = None
                    VCommands.touch(self.fs, self.current_directory, path)

                elif command.startswith("rm"):
                    _, path = command.split(" ", 1)
                    VCommands.rm(self.fs, self.current_directory, path)
                elif command.startswith("mv"):
                    _, old_path, new_path = command.split(" ", 2)
                    VCommands.mv(self.fs, old_path, new_path)
                elif command.startswith("cp"):
                    _, src_path, dest_path = command.split(" ", 2)
                    VCommands.cp(self.fs, src_path, dest_path)
                elif command.startswith("echo"):
                    _, *args = command.split(" ")
                    VCommands.echo(*args)

                elif command.startswith("help"):
                    parts = command.split(" ")
                    if len(parts) > 1:
                        _, command_name = parts
                        if hasattr(VCommands, command_name):
                            # Display command specific help
                            print(getattr(VCommands, command_name).__doc__)
                        else:
                            print(f"Command '{command_name}' not found.")
                    else:
                        # Display overall help
                        print("Available commands:")
                        for method_name in dir(VCommands):
                            method = getattr(VCommands, method_name)
                            if callable(method) and not method_name.startswith("__"):
                                print(method.__doc__)
                else:
                    print("Command not found. Type 'help' to see available commands.")
                    self.kernel.log_command(f"[!] Command '{command}' not found.")
            except Exception as e:
                self.kernel.handle_error(e)

if __name__ == "__main__":
    virtual_os = VirtualOS()
    virtual_os.run_shell()
