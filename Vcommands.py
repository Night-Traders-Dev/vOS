import os
import sys
import platform
from virtualfs import File                                                         
class VCommands:
    @staticmethod                                                                      def mkdir(fs, path):
        fs.create_directory(path)                                                          return fs

    @staticmethod
    def ls(fs, current_directory, path=None):
        if path:
            try:
                directory = fs.find_directory(current_directory, path)
                for name, item in directory.subdirectories.items():
                    print(f"{name}/")
                for name, item in directory.files.items():                                             print(name)
            except FileNotFoundError:
                print(f"Directory '{path}' not found.")
        else:
            for name, item in current_directory.subdirectories.items():
                print(f"{name}/")
            for name, item in current_directory.files.items():
                print(name)

    @staticmethod
    def cd(fs, current_directory, path):
        if path == "..":
            if current_directory == fs.root:
                print("Already at the top of the directory.")
            else:
                current_directory = current_directory.parent
        else:
            try:
                new_directory = fs.find_directory(current_directory, path)
                current_directory = new_directory                                              except FileNotFoundError:
                print(f"Directory '{path}' not found.")
        return current_directory

    @staticmethod
    def cat(fs, path):
        try:
            file_content = fs.read_file(path)
            print(file_content)
        except FileNotFoundError:                                                              print(f"File '{path}' not found.")
                                                                                       @staticmethod
    def rmdir(fs, path):
        try:
            fs.remove_directory(path)
        except FileNotFoundError:
            print(f"Directory '{path}' not found.")

    @staticmethod
    def nano(fs, current_directory, path=None):
        if path:
            try:
                nano_file = fs.read_file(path)
            except FileNotFoundError:
                nano_file = ""
        else:
            filename = input("Enter filename: ")
            if not filename.strip():                                                               print("Filename cannot be empty.")
                return
            path = os.path.join(current_directory.get_full_path(), filename)
            nano_file = ""                                                         
        print("Nano-like text editor. Press :w to save and exit.")                         while True:
            line = input()
            if line == ":w":
                fs.create_file(path, nano_file)
                break
            nano_file += line + "\n"
                                                                                       @staticmethod
    def version():                                                                         print("VOS Version: V0.0.1")
        print(f"Python Version: {sys.version}")
        print("VirtualFS Version: V0.0.1")                                                 print("VirtualMachine Version: V0.0.1")

    @staticmethod
    def clear_screen():
        if platform.system() == "Windows":
            os.system("cls")                                                               else:                                                                                  os.system("clear")

    @staticmethod                                                                      def pwd(current_directory):
        print(current_directory.get_full_path())

    @staticmethod
    def touch(fs, path=None):
        if not path:
            print("Error: Please specify a file path to create.")
            return

        # Check if the path starts with '/' indicating an absolute path
        if path.startswith('/'):
            directory_path, filename = os.path.split(path)
            parent_directory = fs.find_directory(fs.root, directory_path)
        else:
            # If not an absolute path, create the file in the current directory
            parent_directory = fs.current_directory
            filename = path
                                                                                           parent_directory.add_file(File(filename))
        fs.kernel.log_command(f"Created file: {os.path.join(parent_directory.get_full_path(), filename)}")
                                                                                       @staticmethod
    def rm(fs, path):
        try:                                                                                   fs.remove_file(path)
        except FileNotFoundError:
            print(f"File '{path}' not found.")

    @staticmethod
    def mv(fs, old_path, new_path):
        try:
            fs.rename_file(old_path, new_path)
        except FileNotFoundError:                                                              print(f"File '{old_path}' not found.")
        except FileExistsError:
            print(f"File '{new_path}' already exists.")

    @staticmethod
    def cp(fs, src_path, dest_path):
        try:
            file_content = fs.read_file(src_path)
            fs.create_file(dest_path, file_content)
        except FileNotFoundError:
            print(f"File '{src_path}' not found.")

    @staticmethod
    def echo(*args):
        print(" ".join(args))