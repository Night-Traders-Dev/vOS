import os

class VCommands:
    def __init__(self):

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
