import os
import sys
import platform
from virtualfs import File
from virtualfs import Directory
from virtualfs import VirtualFileSystem
from virtualkernel import VirtualKernel
from virtualkernel import QShellInterpreter
from virtualkernel import VirtualProcess

class VCommands:
    def __init__(self):
        self.kernel = VirtualKernel()
        self.vfs = VirtualFileSystem()
        self.qshell = QShellInterpreter()
        self.vproc = VirtualProcess("vprocd", 1)

    @staticmethod
    def help(command=None):
        """
        help: Display help information\nUsage: help [command]
        If no command is provided, displays overall help information.
        If a command is provided, displays specific help information for that command.
        """
        if command:
            if hasattr(VCommands, command):
                method = getattr(VCommands, command)
                print(method.__doc__ or "No help available for this command.")
            else:
                print(f"Command '{command}' not found.")
        else:
            print("Available commands:")
            print("mkdir - Create a directory")
            print("ls - List files and directories")
            print("cd - Change directory")
            print("cat - Display file content")
            print("rmdir - Remove a directory")
            print("nano - Open a file in a nano-like text editor")
            print("version - Show version information")
            print("clear - Clear the screen")
            print("pwd - Print the current directory")
            print("touch - Create a new file")
            print("rm - Remove a file")
            print("mv - Move a file or directory")
            print("cp - Copy a file or directory")
            print("echo - Display arguments")


    @staticmethod
    def su(self, fs, current_directory, permissions="rwxrwxrwx"):
        """
        su: Temporarily elevate privileges for all commands\nUsage: su [permissions]
        """
        try:
            pid = fs.kernel.create_process("su")
            # Store the original permissions
            original_permissions = current_directory.permissions

            # Temporarily change permissions to the specified value
            current_directory.permissions = permissions
            fs.permissions = permissions


            # Run a subshell with elevated privileges
            while True:
                command = input(f"{current_directory.get_full_path()} # ").strip()
                if command == "exit":
                    break

                # Execute the command with elevated privileges
                try:
                    if command == "dmesg":
                        self.kernel.print_dmesg()
                    elif command == "uptime":
                        uptime = self.kernel.get_uptime()
                        print(f"vOS uptime: {uptime}")
                    elif command == "update":
                        self.kernel.update_vos()
                    elif command == "reset_fs":
                        self.fs.reset_filesystem()
                    elif command == "sysmon":
                        self.vproc.monitor_processes(self)
                    elif command.startswith("reboot"):
                        confirmation = input("Are you sure you want to reboot? (yes/no): ").strip().lower()
                        if confirmation == "yes":
                            self.kernel.reboot_os()  # Call the reboot function from the kernel
                            break
                        else:
                            print("Reboot cancelled.")
                            self.kernel.log_command(f"[!]Reboot cancelled")
                    else:
                        parts = command.split(" ")
                        cmd = parts[0]
                        args = " ".join(parts[1:])
                        method = getattr(VCommands, cmd)
                        method(fs, current_directory, args)
#                except KeyboardInterrupt:
#                    break
                except Exception as e:
                    print(f"Error: {e}")

        finally:
            # Restore the original permissions
            current_directory.permissions = original_permissions
            fs.permissions = original_permissions
            self.vproc.kill_process(self, pid)




    @staticmethod
    def perms(fs, path=None):
        """
        perms: Check permissions for a file or directory\nUsage: perms [file_path]
        """
        if not path:
            print("Error: Please specify a file or directory path to check permissions.")
            return

        # Concatenate current directory path with the specified path
        if not path.startswith('/'):
            path = os.path.join(fs.current_directory.get_full_path(), path)

        try:
            # Check if the file or directory exists
            if fs.file_exists(path) or fs.directory_exists(path):
                permissions = fs.get_permissions(path)
                print(f"Permissions for '{path}': {permissions}")
            else:
                print(f"Error: File or directory '{path}' not found.")
        except FileNotFoundError:
            print(f"Error: File or directory '{path}' not found.")


    @staticmethod
    def mkdir(fs, path=None):
        """
        mkdir: Create a directory\nUsage: mkdir [directory_path]
        If no directory path is provided, creates a directory in the current directory.
        """
        if not path:
            print("Error: Please specify a directory path to create.")
            return
        # Concatenate current directory and path
        directory_path = os.path.join(fs.current_directory.get_full_path(), path) if not path.startswith('/') else path
        fs.create_directory(directory_path)
        fs.kernel.log_command(f"Created directory: {directory_path}")

    @staticmethod
    def ls(fs, current_directory, path=None):
        """
        ls: List files and directories\nUsage: ls [directory_path]
        If no directory path is provided, lists the contents of the current directory.
        """
        if not path:
            directory = current_directory
        else:
            try:
                directory = fs.find_directory(current_directory, path)
            except FileNotFoundError:
                print(f"Directory '{path}' not found.")
                return

        for name, item in directory.subdirectories.items():
            print(f"{name}/")
        for name, item in directory.files.items():
            print(name)

    @staticmethod
    def cd(self, fs, current_directory, path):
        """
        cd: Change directory\nUsage: cd [directory_path]
        """
        if not path or path == ".":
            return current_directory
        elif path == "..":
            if current_directory == fs.root:
                print("Already at the top of the directory.")
            else:
                return current_directory.parent
        else:
            try:
                new_directory = fs.find_directory(current_directory, path)
                return new_directory
            except FileNotFoundError:
                print(f"Directory '{path}' not found.")
                return current_directory




    @staticmethod
    def cat(fs, current_directory, path=None):
        # Get permissions of the current directory
        perms = current_directory.permissions

        if not path:
            print("Error: Please specify a file path to read.")
            return

        # Concatenate current directory path with the specified path if necessary
        if not path.startswith('/'):
            path = os.path.join(current_directory.get_full_path(), path)

        try:
            # Read the file content
            file_content = fs.read_file(path)
            # Print the file content
            print(file_content)
        except FileNotFoundError:
            print(f"File '{path}' not found.")


    @staticmethod
    def rmdir(fs, path=None):
        """
        rmdir: Remove a directory\nUsage: rmdir [directory_path]
        """
        if not path:
            print("Error: Please specify a directory path to remove.")
            return
        try:
            fs.remove_directory(path)
            fs.kernel.log_command(f"Removed directory: {path}")
        except FileNotFoundError:
            print(f"Directory '{path}' not found.")


    @staticmethod
    def nano(self, fs, current_directory, path=None):
        """
        nano: Open a file in a nano-like text editor\nUsage: nano [file_path]                         If no file path is provided, prompts the user to enter a file name and creates a new file in the current directory.
        """
        pid = fs.kernel.create_process("nano")
        if not path:
            filename = input("Enter filename: ")
            if not filename.strip():
                fs.kernel.log_command("[Nano] Filename cannot be empty.")
                print("Filename cannot be empty.")
                return
            path = os.path.join(current_directory.get_full_path(), filename)
        else:
            # Check if the path is relative or absolute
            if not path.startswith('/'):
                # If relative, make it relative to the current directory
                path = os.path.join(current_directory.get_full_path(), path)


        print("Nano-like text editor. Press :w to save and exit.")

        # Load file content if the file exists
        if fs.file_exists(path):
            try:
                nano_file = fs.read_file(path)
                print(nano_file)  # Print existing content
            except FileNotFoundError:
                fs.kernel.log_command(f"[Nano] File '{path}' not found.")
                nano_file = ""
        else:
            nano_file = ""

        while True:
            line = input()
            if line == ":w":
                fs.create_file(path, nano_file)
                self.vproc.kill_process(self, pid)
                break
            nano_file += line + "\n"



    @staticmethod
    def version(self):
        """
        version: Show version information
        """
        self.kernel.print_component_versions(True)
        print(f"Python Version: {sys.version}")

    @staticmethod
    def clear_screen():
        """
        clear: Clear the screen
        """
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    @staticmethod
    def pwd(current_directory):
        """
        pwd: Print the current directory
        """
        print(current_directory.get_full_path())

    @staticmethod
    def touch(fs, current_directory, path=None):
        """
        touch: Create a new file\nUsage: touch [file_path]
        If no file path is provided, creates a file in the curr>
        """
        if not path:
            print("Error: Please specify a file path to create.")
            return

        # Concatenate current directory path with the specified path
        file_path = os.path.join(current_directory.get_full_path(), path)

        parent_directory_path, filename = os.path.split(file_path)
        parent_directory = fs.find_directory(fs.root, parent_directory_path)
        parent_directory.add_file(File(filename))
        fs.kernel.log_command(f"Created file: {file_path}")



    @staticmethod
    def rm(fs, current_directory, path=None):
        """
        rm: Remove a file\nUsage: rm [file_path]
        """
        # Use the current directory if no path is specified
        if not path:
            print("Error: Please specify a file path to remove.")
            return

        # Check if the path is already a string
        if not isinstance(path, str):
            print("Error: Invalid file path.")
            return

        # Concatenate current directory path with the specified path
        if not path.startswith('/'):
            path = os.path.join(current_directory.get_full_path(), path)

        try:
            # Check if the file exists
            if fs.file_exists(path):
                # Remove the file
                fs.remove_file(path)
                fs.kernel.log_command(f"Removed file: {path}")
            else:
                print(f"Error: File '{path}' not found.")
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")

    @staticmethod
    def mv(fs, old_path, new_path):
        """
        mv: Move a file or directory\nUsage: mv [old_path] [new_path]
        """
        if not old_path or not new_path:
            print("Error: Please specify both old and new paths.")
            return

        # Concatenate current directory path with the specified paths
        if not old_path.startswith('/'):
           old_path = os.path.join(fs.current_directory.get_full_path(), old_path)
        if not new_path.startswith('/'):
            new_path = os.path.join(fs.current_directory.get_full_path(), new_path)

        try:
            fs.rename_file(old_path, new_path)
            fs.kernel.log_command(f"Moved file '{old_path}' to '{new_path}'")
        except FileNotFoundError:
            print(f"File '{old_path}' not found.")
        except FileExistsError:
            print(f"File '{new_path}' already exists.")

    @staticmethod
    def cp(fs, src_path, dest_path):
        """
        cp: Copy a file or directory\nUsage: cp [source_path] [destination_path]
        """
        if not src_path or not dest_path:
            print("Error: Please specify both source and destination paths.")
            return

        # Concatenate current directory path with the specified paths
        if not src_path.startswith('/'):
            src_path = os.path.join(fs.current_directory.get_full_path(), src_path)
        if not dest_path.startswith('/'):
            dest_path = os.path.join(fs.current_directory.get_full_path(), dest_path)

        try:
            file_content = fs.read_file(src_path)
            fs.create_file(dest_path, file_content)
            fs.kernel.log_command(f"Copied file '{src_path}' to '{dest_path}'")
        except FileNotFoundError:
            print(f"File '{src_path}' not found.")


    @staticmethod
    def echo(*args):
        """
        echo: Display arguments\nUsage: echo [arguments...]
        """
        print(" ".join(args))
