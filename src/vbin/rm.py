import os

class rm:
    def __init__(self):
        self.app_name = "rm"
        self.app_args = ["fs_instance", "current_directory", "path=None"]

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
                if fs.file_exists(path):
                    # Remove the file
                    fs.remove_file(path)
                    fs.save_file_system("file_system.json")
                    fs.kernel.log_command(f"Removed file: {path}")
                else:
                    print(f"Error: File '{path}' not found.")
            except FileNotFoundError:
                print(f"Error: File '{path}' not found.")
