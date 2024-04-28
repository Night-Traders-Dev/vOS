import json
import os
import gzip
from virtualkernel import VirtualKernel

class File:
    def __init__(self, name, content="", permissions=""):
        self.name = name
        self.content = content
        self.permissions = permissions if permissions else "rw-r--r--"  # Default permissions: rw-r--r--

    def read(self):
        return self.content

    def write(self, content):
        self.content = content

class Directory:
    def __init__(self, name, parent=None, permissions=""):
        self.name = name
        self.subdirectories = {}
        self.files = {}
        self.parent = parent
        self.permissions = permissions if permissions else "rwxr-xr-x"  # Default permissions: rwxr-xr-x


    def startswith(self, prefix):
        return self.name.startswith(prefix)

    def add_directory(self, directory, permissions=""):
        self.subdirectories[directory.name] = directory
        directory.parent = self
        directory.permissions = permissions if permissions else "rwxr-xr-x"  # Default permissions: rwxr-xr-x

    def remove_directory(self, name):
        del self.subdirectories[name]

    def add_file(self, file, permissions=""):
        self.files[file.name] = file
        file.parent = self
        file.permissions = permissions if permissions else "rw-r--r--"  # Default permissions: rw-r--r--

    def remove_file(self, name):
        del self.files[name]

    def get_full_path(self):
        path = self.name
        parent = self.parent
        while parent:
            if isinstance(parent.name, str):  # Check if parent directory name is a string
                path = os.path.join(parent.name, path)
            parent = parent.parent
        return '/' + path if path else '/'



class VirtualFileSystem:
    def __init__(self, permissions=""):
        self.permissions = permissions if permissions else "rwxr-xr-x"
        self.kernel = VirtualKernel()
        self.kernel.log_command("Kernel Module for VirtualFileSystem loaded")
        self.root = Directory("")
        self.filesystem_data = self.load_file_system("file_system.json")
        self.current_directory = self.root
        self.kernel.log_command(f"Setting Default Directory: {self.current_directory.get_full_path()}")
        self.kernel.log_command("Loading OS and Placing OS files...")
        self.add_os_filesystem(self.filesystem_data)
        self.users = {}

    def get_current_directory_path(self):
        """
        Get the full path of the current directory.
        """
        return self.current_directory.get_full_path()


    def allowed_perms(self, user_perms, object_perms):
        """
        Compare user's permissions with object's permissions.

        Parameters:
            user_perms (str): Permissions of the user (e.g., 'rwx').
            object_perms (str): Permissions of the file or directory being accessed.

        Returns:
            bool: True if the user's permissions are sufficient, False otherwise.
        """
        # Define operation mapping
        operation_map = {
            "read": 0,
            "write": 1,
            "execute": 2
        }

        # Check if the user's permissions supersede the object's permissions for each operation
        for operation, index in operation_map.items():
            if user_perms[index] < object_perms[index]:
                return False  # User's permissions are insufficient for this operation

        return True  # User's permissions are sufficient for all operations


    def find_item(self, path):
        """
        Find an item (file or directory) in the filesystem given its path.
        """
        # Split the path into directory components
        components = path.strip("/").split("/")

        # Start from the root directory
        current_directory = self.root

        # Traverse through each component of the path
        for component in components:
            if component == "":
                continue
            if component not in current_directory.subdirectories and component not in current_directory.files:
                raise FileNotFoundError(f"Item '{path}' not found.")
            if component in current_directory.subdirectories:
                current_directory = current_directory.subdirectories[component]
            elif component in current_directory.files:
                return current_directory.files[component]

        # Return the final item
        return current_directory


    def directory_exists(self, path):
        try:
            self.find_directory(self.root, path)
            return True
        except FileNotFoundError:
            return False

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

    def create_file(self, path, content="", permissions=""):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        new_file = File(filename, content, permissions)
        parent_directory.add_file(new_file)
        self.kernel.log_command(f"Created file: {os.path.join(parent_directory.get_full_path(), filename)}")

    def read_file(self, path):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        if filename in parent_directory.files:
            # Check permissions before allowing file access
            if self.check_permissions(parent_directory.files[filename].permissions, "read"):
                return parent_directory.files[filename].read()
            else:
                raise PermissionError("Permission denied: read access not allowed for file")
        else:
            raise FileNotFoundError("File not found")

    def remove_file(self, path):
        directory_path, filename = os.path.split(path)
        parent_directory = self.find_directory(self.root, directory_path)
        if filename in parent_directory.files:
            # Check permissions before allowing file deletion
            if self.check_permissions(parent_directory.files[filename].permissions, "execute"):
                parent_directory.remove_file(filename)
                self.kernel.log_command(f"Removed file: {path}")
            else:
                raise PermissionError("Permission denied: delete access not allowed for file")
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

    # Method to check file permissions
    def check_permissions(self, file_permissions, operation, elevated_permissions=None):
        # If elevated permissions are not provided, use the default permissions
        if elevated_permissions is None:
            elevated_permissions = self.permissions

        # Parse permission string
        owner_perms = file_permissions[0:3]
        group_perms = file_permissions[3:6]
        other_perms = file_permissions[6:]

        # Define operation mapping
        operation_map = {
            "read": 0,
            "write": 1,
            "execute": 2
        }

        # Determine which permissions to check based on the operation
        if operation == "read":
            perms_to_check = owner_perms[operation_map[operation]] + group_perms[operation_map[operation]]
        elif operation == "write":
            perms_to_check = owner_perms[operation_map[operation]] + group_perms[operation_map[operation]]
        elif operation == "execute":
            perms_to_check = owner_perms[operation_map[operation]] + group_perms[operation_map[operation]]
        else:
            raise ValueError("Invalid operation")

        # Check if the operation is permitted based on elevated permissions
        if elevated_permissions[0] == "r":
            owner_perm = "r"
        else:
            owner_perm = "-"
        if elevated_permissions[1] == "w":
            group_perm = "w"
        else:
            group_perm = "-"
        if elevated_permissions[2] == "x":
            other_perm = "x"
        else:
            other_perm = "-"

        elevated_perms_to_check = owner_perm + group_perm + other_perm

        return perms_to_check == elevated_perms_to_check

    def get_permissions(self, path):
        # Find the directory or file based on the provided path
        item = self.find_item(path)

        # Check if the item exists
        if item:
            # Check permissions for the item
            permissions = item.permissions

            # Return the permissions
            return permissions
        else:
            # Item not found
            return "Item not found"


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