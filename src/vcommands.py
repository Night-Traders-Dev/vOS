import os
import sys
import platform
from virtualfs import File
from virtualfs import Directory
from virtualfs import VirtualFileSystem
from virtualkernel import VirtualKernel
from virtualkernel import QShellInterpreter
from virtualkernel import VirtualProcess
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print
from vbin import *



class FancyTextEditor:
    def __init__(self, fs, current_directory, theme="blue"):
        self.console = Console()
        self.fs = fs
        self.current_directory = current_directory
        self.theme = theme

    def _create_editor_layout(self):
        layout = Layout()
        layout.split_row(Layout(name="header"), Layout(), Layout(size=3, name="editor"))
        layout["header"].update(Panel(Text("🚀 Fancy Text Editor 🚀", style=f"bold {self.theme}")))
        layout["editor"].update(Panel(""))
        return layout

    def _load_file_content(self, path):
        if self.fs.file_exists(path):
            try:
                return self.fs.read_file(path)
            except FileNotFoundError:
                self.console.print(f"[bold red]File '{path}' not found.[/]")
        return ""

    def edit(self, path=None):
        layout = self._create_editor_layout()
        self.console.print(layout)

        if not path:
            filename = Prompt.ask("Enter filename: ")
            if not filename.strip():
                self.console.print("[bold red]Filename cannot be empty.[/]")
                return
            path = os.path.join(self.current_directory.get_full_path(), filename)
        else:
            # Check if the path is relative or absolute
            if not path.startswith('/'):
                # If relative, make it relative to the current directory
                path = os.path.join(self.current_directory.get_full_path(), path)

        editor_content = self._load_file_content(path)

        while True:
            line = Prompt.ask(">> ")
            if line == ":w":
                self.fs.create_file(path, layout["editor"].renderable.content)
                break
            editor_content += line + "\n"
            layout["editor"].update(Panel(editor_content))

        self.console.print(layout)


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
    def text_edit(self, fs, current_directory, path = None):
        editor = FancyTextEditor(fs, current_directory)
        editor.edit()

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
    def diff(self, fs, current_directory, path1, path2):
        """
        diff: Compare two files or directories\nUsage: diff [file_or_directory_path_1] [file_or_directory_path_2]
        """
        if not path1 or not path2:
            print("Error: Please specify two file or directory paths to compare.")
            return

        # Concatenate current directory path with the specified paths if necessary
        if not path1.startswith('/'):
            path1 = os.path.join(current_directory.get_full_path(), path1)
        if not path2.startswith('/'):
            path2 = os.path.join(current_directory.get_full_path(), path2)
        dir1, filename1 = os.path.split(path1)
        dir2, filename2 = os.path.split(path2)
        # Check if both paths exist
        if not fs.directory_exists(dir1) or not fs.directory_exists(dir2):
            print("Error: One or both paths do not exist.")
            return

        # Check if both paths are files or directories
        is_path1_file = fs.file_exists(path1)
        is_path2_file = fs.file_exists(path2)
        is_path1_dir = fs.directory_exists(dir1)
        is_path2_dir = fs.directory_exists(dir2)

        if is_path1_file != is_path2_file:
            print("Error: Cannot compare a file with a directory.")
            return

        # Perform file or directory comparison
        if is_path1_file:
            file1_content = fs.read_file(path1)
            file2_content = fs.read_file(path2)
            if file1_content == file2_content:
                print("Files are identical.")
            else:
                print("Files are different.")
        else:
            directory_diff = fs.compare_directories(path1, path2)
            if not directory_diff:
                print("Directories are identical.")
            else:
                print("Directories are different.")

    @staticmethod
    def CMP(fs, current_directory, path1, path2):
        """
        CMP: Compare two files\nUsage: CMP [file_path_1] [file_path_2]
        """
        if not path1 or not path2:
            print("Error: Please specify two file paths to compare.")
            return

        # Concatenate current directory path with the specified paths if necessary
        if not path1.startswith('/'):
            path1 = os.path.join(current_directory.get_full_path(), path1)
        if not path2.startswith('/'):
            path2 = os.path.join(current_directory.get_full_path(), path2)

        # Check if both paths exist
        if not os.path.exists(path1) or not os.path.exists(path2):
            print("Error: One or both paths do not exist.")
            return

        # Check if both paths are files
        if not os.path.isfile(path1) or not os.path.isfile(path2):
            print("Error: Both paths must be files.")
            return

        # Perform file comparison
        file1_content = fs.read_file(path1)
        file2_content = fs.read_file(path2)
        if file1_content == file2_content:
            print("Files are identical.")
        else:
            print("Files are different.")


    @staticmethod
    def mkdir(fs, current_directory, path=None):
        """
        mkdir: Create a directory\nUsage: mkdir [directory_path]
        If no directory path is provided, creates a directory in the current directory.
        """
        if not path:
            print("Error: Please specify a directory path to create.")
            return
        # Concatenate current directory and path
        directory_path = os.path.join(current_directory.get_full_path(), path) if not path.startswith('/') else path
        fs.create_directory(directory_path)
        fs.save_file_system("file_system.json")
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
    def rmdir(fs, current_directory, path=None):
        """
        rmdir: Remove a directory\nUsage: rmdir [directory_path]
        """
        if not path:
            print("Error: Please specify a directory path to remove.")
            return
        try:
            if not path.startswith('/'):
                path = os.path.join(current_directory.get_full_path(), path)
            fs.remove_directory(path)
            fs.save_file_system("file_system.json")
            fs.kernel.log_command(f"Removed directory: {path}")
        except FileNotFoundError:
            print(f"Directory '{path}' not found.")


    @staticmethod
    def nano(self, fs, current_directory, path=None):
        console = Console()

        if not path:
            filename = Prompt.ask("Enter filename: ")
            if not filename.strip():
                console.print("[bold red]Filename cannot be empty.[/]")
                return
            path = os.path.join(current_directory.get_full_path(), filename)
        else:
            # Check if the path is relative or absolute
            if not path.startswith('/'):
                # If relative, make it relative to the current directory
                path = os.path.join(current_directory.get_full_path(), path)

        layout = Layout()
        layout.split_row(Layout(name="header"), Layout(), Layout(size=3, name="editor"))
        layout["header"].update(Panel("[bold green]Nano-like text editor. Press :w to save and exit.[/]"))
        layout["editor"].update(Panel(""))

        console.print(layout)

        # Load file content if the file exists
        if fs.file_exists(path):
            try:
                nano_file = fs.read_file(path)
                layout["editor"].update(Panel(nano_file))  # Update editor panel with existing content
            except FileNotFoundError:
                console.print(f"[bold red]File '{path}' not found.[/]")
                nano_file = ""
        else:
            nano_file = ""

        while True:
            line = Prompt.ask(">> ")
            if line == ":w":
                fs.create_file(path, layout["editor"].renderable.content)
                fs.save_file_system("file_system.json")
                break
            nano_file += line + "\n"
            layout["editor"].update(Panel(nano_file))

        console.print(layout)



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
        fs.save_file_system("file_system.json")
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
                fs.save_file_system("file_system.json")
                fs.kernel.log_command(f"Removed file: {path}")
            else:
                print(f"Error: File '{path}' not found.")
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")

    @staticmethod
    def mv(fs, current_directory, old_path, new_path):
        """
        mv: Move a file or directory\nUsage: mv [old_path] [new_path]
        """
        if not old_path or not new_path:
            print("Error: Please specify both old and new paths.")
            return

        # Concatenate current directory path with the specified paths
        if not old_path.startswith('/'):
           old_path = os.path.join(current_directory.get_full_path(), old_path)
        if not new_path.startswith('/'):
            new_path = os.path.join(current_directory.get_full_path(), new_path)

        try:
            file_content = fs.read_file(old_path)
            fs.create_file(new_path, file_content)
            fs.remove_file(old_path)
            fs.save_file_system("file_system.json")
            fs.kernel.log_command(f"Moved file '{old_path}' to '{new_path}'")
        except FileNotFoundError:
            print(f"File '{old_path}' not found.")
        except FileExistsError:
            print(f"File '{new_path}' already exists.")

    @staticmethod
    def cp(fs, current_directory, src_path, dest_path):
        """
        cp: Copy a file or directory\nUsage: cp [source_path] [destination_path]
        """
        if not src_path or not dest_path:
            print("Error: Please specify both source and destination paths.")
            return

        # Concatenate current directory path with the specified paths
        if not src_path.startswith('/'):
            src_path = os.path.join(current_directory.get_full_path(), src_path)
        if not dest_path.startswith('/'):
            dest_path = os.path.join(current_directory.get_full_path(), dest_path)

        try:
            file_content = fs.read_file(src_path)
            fs.create_file(dest_path, file_content)
            fs.save_file_system("file_system.json")
            fs.kernel.log_command(f"Copied file '{src_path}' to '{dest_path}'")
        except FileNotFoundError:
            print(f"File '{src_path}' not found.")



    @staticmethod
    def echo(fs, current_directory, *args, file=None):
        fs.kernel.log_command(f"{args} {file}")
        text = " ".join(args)
        if file:
            if ">>" in text:
                parts = text.split(">>")
                content = ">>".join(parts[:-1]).strip()
                try:
                    existing_content = fs.read_file(os.path.join(current_directory.get_full_path(), file))
                except FileNotFoundError:
                    existing_content = ""
                content = existing_content + "\n" + content
                fs.write_file(os.path.join(current_directory.get_full_path(), file), content)
                fs.save_file_system("file_system.json")
                fs.kernel.log_command(f"Appended content to file: {file}")
            elif ">" in text:
                parts = text.split(">")
                content = ">".join(parts[:-1]).strip()
                fs.create_file(os.path.join(current_directory.get_full_path(), file), content=content)
                fs.save_file_system("file_system.json")
                fs.kernel.log_command(f"Created/overwritten file: {file}")
            else:
                print(text)
        else:
            print(text)
