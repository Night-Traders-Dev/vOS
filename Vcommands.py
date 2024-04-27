import os
import sys
import platform
from virtualfs import File

class VCommands:
    @staticmethod
    def mkdir(fs, path=None):
        if not path:
            print("Error: Please specify a directory path to create.")
            return

        # Check if the path starts with '/' indicating an absolute path
        if path.startswith('/'):
            directory_path = path
        else:
            # If not an absolute path, create the directory in the current directory
            directory_path = os.path.join(fs.current_directory.get_full_path(), path)

        fs.create_directory(directory_path)
        fs.kernel.log_command(f"Created directory: {directory_path}")

    @staticmethod
    def ls(fs, current_directory, path=None):
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
    def cd(fs, current_directory, path):
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
    def cat(fs, path=None):
        if not path:
            print("Error: Please specify a file path to read.")
            return

        try:
            file_content = fs.read_file(path)
            print(file_content)
        except FileNotFoundError:
            print(f"File '{path}' not found.")

    @staticmethod
    def rmdir(fs, path=None):
        if not path:
            print("Error: Please specify a directory path to remove.")
            return

        try:
            fs.remove_directory(path)
            fs.kernel.log_command(f"Removed directory: {path}")
        except FileNotFoundError:
            print(f"Directory '{path}' not found.")

    @staticmethod
    def nano(fs, current_directory, path=None):
        if not path:                                                                                                                                                     filename = input("Enter filename: ")
            if not filename.strip():
                print("Filename cannot be empty.")
                return
            path = os.path.join(current_directory.get_full_path(), filename)

        print("Nano-like text editor. Press :w to save and exit.")
        nano_file = ""
        while True:
            line = input()
            if line == ":w":
                fs.create_file(path, nano_file)
                break
            nano_file += line + "\n"

    @staticmethod
    def version():
        print("VOS Version: V0.0.1")
        print(f"Python Version: {sys.version}")
        print("VirtualFS Version: V0.0.1")
        print("VirtualMachine Version: V0.0.1")

    @staticmethod
    def clear_screen():
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    @staticmethod
    def pwd(current_directory):
        print(current_directory.get_full_path())

    @staticmethod
    def touch(fs, path=None):
        if not path:
            print("Error: Please specify a file path to create.")
            return

        # Check if the path starts with '/' indicating an absolute path
        if path.startswith('/'):
            file_path = path
        else:
            # If not an absolute path, create the file in the current directory
            file_path = os.path.join(fs.current_directory.get_full_path(), path)

        parent_directory_path, filename = os.path.split(file_path)
        parent_directory = fs.find_directory(fs.root, parent_directory_path)
        parent_directory.add_file(File(filename))
        fs.kernel.log_command(f"Created file: {file_path}")

    @staticmethod
    def rm(fs, path=None):
        if not path:
            print("Error: Please specify a file path to remove.")
            return

        try:
            fs.remove_file(path)
            fs.kernel.log_command(f"Removed file: {path}")
        except FileNotFoundError:
            print(f"File '{path}' not found.")

    @staticmethod
    def mv(fs, old_path, new_path):
        try:
            fs.rename_file(old_path, new_path)
            fs.kernel.log_command(f"Moved file '{old_path}' to '{new_path}'")
        except FileNotFoundError:
            print(f"File '{old_path}' not found.")
        except FileExistsError:
            print(f"File '{new_path}' already exists.")

    @staticmethod
    def cp(fs, src_path, dest_path):
        try:
            file_content = fs.read_file(src_path)
            fs.create_file(dest_path, file_content)
            fs.kernel.log_command(f"Copied file '{src_path}' to '{dest_path}'")
        except FileNotFoundError:
            print(f"File '{src_path}' not found.")

    @staticmethod
    def echo(*args):
        print(" ".join(args))
