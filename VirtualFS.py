import json
import os
import gzip
from virtualkernel import VirtualKernel

class File:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content

    def read(self):
        return self.content

    def write(self, content):
        self.content = content

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.subdirectories = {}
        self.files = {}
        self.parent = parent

    def add_directory(self, directory):
        self.subdirectories[directory.name] = directory

    def remove_directory(self, name):
        del self.subdirectories[name]

    def add_file(self, file):
        self.files[file.name] = file

    def remove_file(self, name):
        del self.files[name]

    def get_full_path(self):
        path = self.name
        parent = self.parent
        while parent:
            path = os.path.join(parent.name, path)
            parent = parent.parent
        return '/' + path if path else '/'

class VirtualFileSystem:
    def __init__(self):
        self.kernel = VirtualKernel()
        self.kernel.log_command("Kernel Module for VirtualFileSystem loaded")
        self.root = Directory("")
        self.filesystem_data = self.load_file_system("file_system.json")
        self.current_directory = self.root
        self.kernel.log_command("Loading OS and Placing OS files...")
        self.add_os_filesystem(self.filesystem_data)

    def add_default_filesystem(self):
        default_filesystem_data = {
            "name": "",
            "files": {},
            "subdirectories": {
                "bin": {"name": "bin", "files": {}, "subdirectories": {}},
                "boot": {"name": "boot", "files": {"kernel": "Dummy kernel file", "initrd": "Dummy initrd file", "config": "Dummy config file"}, "subdirectories": {}},
                "dev": {"name": "dev", "files": {}, "subdirectories": {}},
                "etc": {"name": "etc", "files": {}, "subdirectories": {}},
                "home": {"name": "home", "files": {}, "subdirectories": {"user": {"name": "user", "files": {}, "subdirectories": {}}}},
                "lib": {"name": "lib", "files": {}, "subdirectories": {}},
                "mnt": {"name": "mnt", "files": {}, "subdirectories": {}},
                "opt": {"name": "opt", "files": {}, "subdirectories": {}},
                "proc": {"name": "proc", "files": {}, "subdirectories": {}},
                "root": {"name": "root", "files": {}, "subdirectories": {}},
                "run": {"name": "run", "files": {}, "subdirectories": {}},
                "sbin": {"name": "sbin", "files": {"init": "Dummy init file", "mount": "Dummy mount file", "fsck": "Dummy fsck file"}, "subdirectories": {}},
                "srv": {"name": "srv", "files": {}, "subdirectories": {}},
                "sys": {"name": "sys", "files": {}, "subdirectories": {}},
                "tmp": {"name": "tmp", "files": {}, "subdirectories": {}},
                "usr": {"name": "usr", "files": {}, "subdirectories": {}},
                "var": {"name": "var", "files": {}, "subdirectories": {}}
            }
        }

        default_directory = self._decode_directory(default_filesystem_data)
        self.root = default_directory


    def add_os_filesystem(self, filesystem_data):
        # Add provided files to their relevant locations
        provided_files = {
            "vcommands.py": {"name": "bin/vcommands.py"},  # Place vcommands.py in /bin
            "virtualkernel.py": {"name": "boot/virtualkernel.py"},  # Place virtualkernel.py in /boot
            "virtualos.py": {"name": "boot/virtualos.py"},  # Place virtualos.py in /boot
            "virtualfs.py": {"name": "boot/virtualfs.py"},  # Place virtualfs.py in /boot
            "virtualmachine.py": {"name": "sbin/virtualmachine.py"}  # Place virtualmachine.py in /sbin
        }

        for file_name, file_data in provided_files.items():
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            with open(file_path, 'r') as file:
                content = file.read()

            # Get the parent directory name from the file data
            directory_name = os.path.dirname(file_data["name"])

            # Find the directory corresponding to the parent directory name in the filesystem data
            parent_directory = self.find_directory(self.root, directory_name)

            # Get the base file name from the file data
            base_file_name = os.path.basename(file_data["name"])

            # Add the file to the parent directory with the base file name
            parent_directory.add_file(File(base_file_name, content))


    def file_exists(self, path):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        if filename in parent_directory.files:
            return True
        else:
            return False

    def create_directory(self, path):
        current_directory = self.root
        for directory_name in path.split('/'):
            if directory_name:
                if directory_name not in current_directory.subdirectories:
                    current_directory.add_directory(Directory(directory_name, current_directory))
                current_directory = current_directory.subdirectories[directory_name]

    def remove_directory(self, path):
        current_directory = self.root
        parts = path.split('/')
        for directory_name in parts[:-1]:
            if directory_name:
                if directory_name in current_directory.subdirectories:
                    current_directory = current_directory.subdirectories[directory_name]
                else:
                    raise FileNotFoundError("Directory not found")
        directory_name = parts[-1]
        if directory_name in current_directory.subdirectories:
            del current_directory.subdirectories[directory_name]
        else:
            raise FileNotFoundError("Directory not found")

    def find_directory(self, current_directory, path):
        if not path:
            return self.root
        if path.startswith('/'):
            current_directory = self.root

        for directory_name in path.split('/'):
            if directory_name:
                if directory_name == '..':
                    current_directory = current_directory.parent
                elif directory_name in current_directory.subdirectories:
                    current_directory = current_directory.subdirectories[directory_name]
                else:
                    raise FileNotFoundError("Directory not found")

        return current_directory

    def create_file(self, path, content=""):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        parent_directory.add_file(File(filename, content))
        self.kernel.log_command(f"Created file: {os.path.join(parent_directory.get_full_path(), filename)}")

    def read_file(self, path):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        if filename in parent_directory.files:
            return parent_directory.files[filename].read()
        else:
            raise FileNotFoundError("File not found")

    def remove_file(self, path):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        if filename in parent_directory.files:
            parent_directory.remove_file(filename)
            self.kernel.log_command(f"Removed file: {path}")
        else:
            raise FileNotFoundError("File not found")

    def rename_file(self, old_path, new_path):
        old_directory_path, old_filename = os.path.split(old_path)
        new_directory_path, new_filename = os.path.split(new_path)
        old_parent_directory = self.find_directory(self.root, old_directory_path)
        new_parent_directory = self.find_directory(self.root, new_directory_path)
        if old_filename in old_parent_directory.files:
            if new_filename not in new_parent_directory.files:
                new_parent_directory.add_file(old_parent_directory.files.pop(old_filename))
                self.kernel.log_command(f"Renamed file: {old_path} to {new_path}")
            else:
                raise FileExistsError("File already exists")
        else:
            raise FileNotFoundError("File not found")

    def load_file_system(self, file_path):
        if os.path.exists(file_path):
            try:
                with gzip.open(file_path, 'rb') as file:
                    data = json.loads(file.read().decode('utf-8'))
                    self.root = self._decode_directory(data)
                    return data

                    if 'home' not in self.root.subdirectories:
                        self.root.add_directory(Directory('home', self.root))
            except gzip.BadGzipFile:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    self.root = self._decode_directory(data)
                    return data

                    if 'home' not in self.root.subdirectories:
                        self.root.add_directory(Directory('home', self.root))
        else:
            print("File system JSON file not found. Initializing with default root directory.")
            self.kernel.log_command("[!] File system JSON file not found. Initializing with default root directory.")
            self.add_default_filesystem()

    def save_file_system(self, file_path):
        with gzip.open(file_path, 'wb') as file:
            encoded_data = json.dumps(self._encode_directory(self.root)).encode('utf-8')
            file.write(encoded_data)

    def _encode_directory(self, directory):
        data = {
            'name': directory.name,
            'files': {name: file.content for name, file in directory.files.items()},
            'subdirectories': {name: self._encode_directory(subdirectory) for name, subdirectory in directory.subdirectories.items()}
        }
        return data

    def _decode_directory(self, data, parent=None):
        directory = Directory(data['name'], parent)
        for name, content in data['files'].items():
            directory.add_file(File(name, content))
        for name, subdirectory_data in data['subdirectories'].items():
            directory.add_directory(self._decode_directory(subdirectory_data, directory))
        return directory