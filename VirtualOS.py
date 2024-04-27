import sys
import time
from virtualfs import VirtualFileSystem
from vcommands import VCommands
from virtualmachine import VirtualMachine
from virtualkernel import VirtualKernel

class VirtualOS:
    def __init__(self):                                                                                                                                              self.kernel = VirtualKernel()
        self.kernel.log_command("Booting up VirtualOS")
        self.kernel.log_command("Initializing filesystem...")
        self.fs = VirtualFileSystem()  # Initialize the filesystem
        self.kernel.log_command("Loading file system from file_system.json...")
        self.load_with_loading_circle()  # Call method to load with loading circle                                                                                                                                                                                                                                                # Check if 'home' directory exists
        if "home" in self.fs.root.subdirectories:
            # Check if 'user' directory exists                                                                                                                           if "user" in self.fs.root.subdirectories["home"].subdirectories:                                                                                                 # Set default starting directory to /home/user
                self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]
            else:
                self.kernel.log_command("User directory not found. Creating...")
                self.fs.create_directory("/home/user")                                                                                                                       self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]                                                                  else:                                                                                                                                                            self.kernel.log_command("Home directory not found. Creating...")
            self.fs.create_directory("/home")                                                                                                                            self.fs.create_directory("/home/user")                                                                                                                       self.current_directory = self.fs.root.subdirectories["home"].subdirectories["user"]

        self.kernel.log_command("Initializing VirtualMachine...")
        self.vm = VirtualMachine(self.kernel, self.fs)  # Create a VirtualMachine instance
        self.kernel.log_command("Logging component version numbers...")
        self.kernel.log_command("Component Version Numbers:")
        self.kernel.log_command("VOS Version: V0.0.1")
        self.kernel.log_command(f"Python Version: {sys.version}")
        self.kernel.log_command("VirtualFS Version: V0.0.1")
        self.kernel.log_command("VirtualMachine Version: V0.0.1")
        self.kernel.log_command("Booting up kernel...")

        try:
            self.kernel.boot_verbose()
            self.kernel.log_command("VirtualOS boot-up completed.")
        except Exception as e:
            self.kernel.log_command(f"Error during kernel boot: {str(e)}")

    def load_with_loading_circle(self):
        self.kernel.log_command("Loading with loading circle...")
        loading_animation = ['|', '/', '-', '\\']  # ASCII characters for the loading animation
        for _ in range(10):  # Repeat the animation 10 times
            for char in loading_animation:
                sys.stdout.write('\r' + f"Loading... {char}")  # Overwrite the same line with the loading animation
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
                elif command.startswith("mkdir"):
                    _, path = command.split(" ", 1)
                    VCommands.mkdir(self.fs, path)
                    self.fs.save_file_system("file_system.json")  # Save filesystem
 #               elif command.startswith("ls"):
 #                   _, path = command.split(" ", 1)
 #                   VCommands.ls(self.fs, self.current_directory, path)


                elif command.startswith("ls"):
                    parts = command.split(" ")
                    if len(parts) > 1:
                        _, path = parts
                    else:
                        path = None
                    VCommands.ls(self.fs, self.current_directory, path)

                elif command.startswith("cd"):
                    _, path = command.split(" ", 1)
                    self.current_directory = VCommands.cd(self.fs, self.current_directory, path)
                elif command.startswith("cat"):
                    _, path = command.split(" ", 1)
                    VCommands.cat(self.fs, path)
                elif command.startswith("rmdir"):
                    _, path = command.split(" ", 1)
                    VCommands.rmdir(self.fs, path)
                    self.fs.save_file_system("file_system.json")  # Save filesystem
                elif command.startswith("nano"):
                    _, path = command.split(" ", 1)
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
#                elif command.startswith("touch"):
#                    _, path = command.split(" ", 1)
#                    VCommands.touch(self.fs, path)
                elif command.startswith("touch"):
                    try:
                        _, path = command.split(" ", 1)
                    except ValueError:
                        # If no path is specified, use the current directory
                        path = None
                    VCommands.touch(self.fs, self.current_directory, path)

                elif command.startswith("rm"):
                    _, path = command.split(" ", 1)
                    VCommands.rm(self.fs, path)
                elif command.startswith("mv"):
                    _, old_path, new_path = command.split(" ", 2)
                    VCommands.mv(self.fs, old_path, new_path)
                elif command.startswith("cp"):
                    _, src_path, dest_path = command.split(" ", 2)
                    VCommands.cp(self.fs, src_path, dest_path)
                elif command.startswith("echo"):
                    _, *args = command.split(" ")
                    VCommands.echo(*args)
                else:
                    print("Command not found. Available commands: mkdir, ls, cd, cat, rmdir, nano, version, clear, run_vm, dmesg, toggle_fs_monitoring, monitor_fs, exit")
                    self.kernel.log_command(f"[!] Command '{command}' not found.")
            except Exception as e:
                self.kernel.handle_error(e)

if __name__ == "__main__":
    virtual_os = VirtualOS()
    virtual_os.run_shell()
