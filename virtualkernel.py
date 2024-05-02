import os
import hashlib
import base64
from datetime import datetime
import traceback
import uuid
import getpass
import json
import shutil
import urllib.request
import time
from zipfile import ZipFile, is_zipfile
from io import BytesIO


class QShellInterpreter:
    def __init__(self):
        self.ext = ".qs"
        self.variables = {}  # Dictionary to store variables

    def execute_script(self, script):
        if script.endswith(self.ext):
            # Split the script into individual lines
            lines = script.split('\n')
            for line in lines:
                # Execute each line of the script
                command = self.parse_line(line)
                if command:
                    yield command
        else:
            print(f"{script} must have {self.ext} extension")

    def parse_line(self, line):
        # Parse and return the individual command from the qShell script line
        if line.startswith("#"):
            return None  # Ignore comments
        elif "#" in line:
            command, _ = line.split("#", 1)  # Split at the first #
            return command.strip()  # Remove any trailing whitespace and return the command
        else:
            command_parts = line.split(" ")  # Split the line into parts
            command = command_parts[0]  # Extract the command

            if command == "if":
                condition = " ".join(command_parts[1:])  # Extract the condition
                return self.execute_if(condition)
            elif command == "for":
                variables = command_parts[1].split(",")  # Extract the variable(s)
                iterable = command_parts[3]  # Extract the iterable
                return self.execute_for(variables, iterable)
            elif command == "while":
                condition = " ".join(command_parts[1:])  # Extract the condition
                return self.execute_while(condition)
            else:
                return line.strip()  # Remove any leading/trailing whitespace and return the command

    def execute_if(self, condition):
        # Execute the if statement based on the condition
        if condition:
            return True
        else:
            return False

    def execute_for(self, variables, iterable):
        # Execute the for loop using the provided variables and iterable
        for variable in variables:
            self.variables[variable] = iterable
        return True

    def execute_while(self, condition):
        # Execute the while loop based on the condition
        while condition:
            return True
        return False

class UserAccount:
    def __init__(self, username, password, uid, gid, home_dir, shell):
        self.username = username
        self.password = self.encrypt_password(password)
        self.uid = uid
        self.gid = gid
        self.home_dir = home_dir
        self.shell = "/bin/qshell"


    def encrypt_password(self, password):
        # Use SHA-256 hashing algorithm for password encryption
        hashed_password = hashlib.sha256(password.encode()).digest()
        # Encode the hashed password using base64 for storage
        return base64.b64encode(hashed_password).decode()

    def check_password(self, password):
        # Encrypt the provided password and compare with the stored encrypted password
        return self.password == self.encrypt_password(password)

class PasswordFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.dmesg_file = "dmesg"
        self.active_user = None
    @staticmethod
    def generate_random_id():
        return uuid.uuid4().int & (1<<32)-1
    def online_user(self):
        return self.active_user

    def check_passwd_file(self, fs):
        """
        Check if the passwd file exists and if it's empty.
        If it doesn't exist or it's empty, prompt to create a new user.
        """
        if os.path.isfile(self.file_path):
            # Check if the file is empty
            if os.path.getsize(self.file_path) == 0:
                print("First Boot Account Setup")
                self.create_new_user(fs)
            else:
                self.login_prompt()
        else:
            print("First Boot Account Setup")
            self.create_new_user(fs)

    def create_new_user(self, fs):
        """
        Prompt to create a new user account.
        """
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        self.add_user(fs, username, password)
        os.system('cls' if os.name == 'nt' else 'clear')
        self.login_prompt()

    def add_user(self, fs, username, password):
        # Generate random uid and gid if not provided
        uid = self.generate_random_id()
        gid = self.generate_random_id()
        user_dir = "/home/" + username
        shell = "/bin/qshell"

        # Create a UserAccount instance
        user_account = UserAccount(username, password, uid, gid, user_dir, shell)

        # Write the user account information to the password file
        with open(self.file_path, 'a') as file:
            file.write(f"{user_account.username}:{user_account.password}:{user_account.uid}:"
                       f"{user_account.gid}:{user_account.home_dir}:{user_account.shell}\n")

    def remove_user(self, username):
        # Read all lines from the password file, excluding the user to be removed
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        with open(self.file_path, 'w') as file:
            for line in lines:
                if not line.startswith(f"{username}:"):
                    file.write(line)

    def update_user_password(self, username, new_password):
        # Read all lines from the password file, updating the password for the specified user
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        with open(self.file_path, 'w') as file:
            for line in lines:
                if line.startswith(f"{username}:"):
                    parts = line.strip().split(':')
                    parts[1] = UserAccount.encrypt_password(new_password)
                    file.write(':'.join(parts) + '\n')
                else:
                    file.write(line)

    def get_user(self, username):
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(':')
                if parts[0] == username:
                    return [parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]]
        return None

    def authenticate(self, username, password):
        user = self.get_user(username)
        user_account = UserAccount(username, password, user[2], user[3], user[4], user[5])
        VirtualKernel.log_command(self, f"auth: {user[1]} and {user_account.password}")
        if user[1] == user_account.password:
            return True
        else:
            return False

    def login_prompt(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        while True:
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            if self.authenticate(username, password):
                print("Login successful!")
                self.active_user = username
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                print("Invalid username or password. Please try again.")

    def su_prompt(self):
            while True:
                password = getpass.getpass("Password: ")
                username = self.active_user
                if self.authenticate(username, password):
                    return True
                    break
                else:
                    print("Invalid password. su cancelled")
                    return False
                    break


    def logout(self):
       os.system('cls' if os.name == 'nt' else 'clear')
       self.active_user = None
       self.login_prompt()

class VirtualKernel:
    def __init__(self):
        self.processes = []
        self.dmesg_file = "dmesg"
        self.create_process("dmesgd")
        self.filesystem_monitoring_enabled = True
        self.last_error = None
        self.password_file = PasswordFile("passwd")  # Initialize password file
        self.create_process("passwd")
        self.qshell_interpreter = QShellInterpreter()
        self.create_process("uptimed")
        self.start_time = time.time()  # Store the start time

    def get_uptime(self):
        """
        Get the uptime of the virtual operating system.
        """
        uptime_seconds = int(time.time() - self.start_time)
        return f"{uptime_seconds // 3600} hours, {(uptime_seconds % 3600) // 60} minutes, {uptime_seconds % 60} seconds"

    def get_checksum_file(self):
        checksums = {}
        try:
            # Define the paths to the OS components
            component_paths = [
                "virtualos.py",
                "virtualfs.py",
                "vcommands.py",
                "virtualkernel.py",
                "virtualmachine.py"
            ]

            # Calculate checksum for each component
            for component_path in component_paths:
                with open(component_path, "rb") as file:
                    checksum = hashlib.sha256(file.read()).hexdigest()
                    checksums[component_path] = checksum

            # Write the checksums to a checksum file
            with open("checksums.txt", "w") as checksum_file:
                for component_path, checksum in checksums.items():
                    checksum_file.write(f"{component_path}: {checksum}\n")

            print("Checksum file created successfully.")
        except Exception as e:
            print(f"Error creating checksum file: {e}")

    def compare_checksums(self):
        try:
            # Read the checksum file
            stored_checksums = {}
            with open("checksums.txt", "r") as checksum_file:
                for line in checksum_file:
                    component, checksum = line.strip().split(": ")
                    stored_checksums[component] = checksum

            # Initialize a flag to track if all checksums are matching
            all_checksums_match = True

            # Calculate checksum for each component and compare with stored checksums
            for component, stored_checksum in stored_checksums.items():
                with open(component, "rb") as file:
                    current_checksum = hashlib.sha256(file.read()).hexdigest()
                if current_checksum == stored_checksum:
                    self.log_command(f"{component}: OK")
                else:
                    self.log_command(f"{component}: Checksum mismatch!")
                    # Update flag if any checksum doesn't match
                    all_checksums_match = False

            # Print overall result based on the flag
            if all_checksums_match:
                self.log_command("All checksums passed successfully!")
            else:
                self.log_command("Some checksums failed. Checksum verification failed!")
                self.update_vos()

        except Exception as e:
            print(f"Error comparing checksums: {e}")

    def update_vos(self):
        # Specify the GitHub repository URL
        repo_url = "https://github.com/Night-Traders-Dev/vOS/archive/main.zip"
        self.log_command(f"vOS update started")

        try:
            # Download the repository zip file
            with urllib.request.urlopen(repo_url) as response:
                # Read the entire file into memory
                buffer = BytesIO(response.read())

            # Check if the downloaded file is empty
            if not buffer.getvalue():
                print("Error: Failed to fetch repository contents from GitHub. No data received.")
                self.log_command("Failed to fetch repository contents from GitHub. No data received.")
                return

            # Get the total size of the downloaded file
            total_size = len(buffer.getvalue())

            # Check if the downloaded file is a zip file
            if not is_zipfile(buffer):
                print("Error: Failed to fetch repository contents from GitHub. File is not a zip file.")
                print("Printing buffer contents:")
                print(buffer.getvalue())
                self.log_command("Failed to fetch repository contents from GitHub. File is not a zip file.")
                return

            # Extract to a temporary directory
            self.log_command(f"Extracting update")
            print("Extracting update")
            buffer.seek(0)
            with ZipFile(buffer, 'r') as zip_ref:
                temp_dir = os.path.join(os.getcwd(), "temp")
                zip_ref.extractall(temp_dir)

                # Move the contents of the temporary directory to vOS directory
                self.log_command(f"Copying update")
                print("Copying update")
                repo_dir = os.path.join(temp_dir, "vOS-main")
                self.move_files(repo_dir, os.getcwd())

                # Clean up: Remove the temporary directory
                shutil.rmtree(temp_dir)

            print("vOS updated successfully!")
            self.log_command("vOS updated successfully")

        except Exception as e:
            print("Failed to fetch repository contents from GitHub:", e)


    def print_progress(self, bytes_read, total_size):
        progress = bytes_read / total_size * 100
        status = f"{progress:.2f}%"
        print(f"Downloading vOS: {status}", end="\r")


    def move_files(self, src_dir, dest_dir):
        # Move files and directories from source directory to destination directory
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dest_item = os.path.join(dest_dir, item)
            if os.path.isdir(src_item):
                shutil.move(src_item1, dest_item)
            else:
                shutil.copy(src_item, dest_item)
                os.remove(src_item)

    def print_component_versions(self, verbose):
        try:
            with open("version.json", "r") as file:
                versions = json.load(file)
                for component, version in versions.items():
                    if verbose:
                        print(f"{component}: {version}")
                    else:
                        self.log_command(f"{component}: {version}")
        except FileNotFoundError:
            print("Version file not found.")

    def execute_qshell_script(self, script):
        # Execute a qShell script using the qShell interpreter
        self.qshell_interpreter.execute_script(script)


    def reboot_os(self):
        """Reboots the virtual operating system."""
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Reset kernel state or perform any necessary actions to reboot the OS
        print("Rebooting the virtual operating system...")
        self.log_command("[!!]Rebooting vOS...")
        self.processes = []  # Reset the list of processes
        print("Virtual operating system rebooted successfully.")
        self.password_file.login_prompt()

    def create_process(self, program):
        new_process = VirtualProcess(program)
        self.processes.append(new_process)
        self.log_command(f"[*]Starting {program}...")

    def schedule_processes(self):
        for process in self.processes:
            try:
                process.execute()
            except Exception as e:
                self.handle_error(e)
                # Recover from error by removing the last process and retrying
                self.recover_from_error()

    def log_command(self, command):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.dmesg_file, "a") as f:
            f.write(f"[{timestamp}] {command}\n")

    def boot_verbose(self):
        verbose_message = "VirtualOS boot-up completed."
        self.log_command(verbose_message)

    def print_dmesg(self):
        try:
            with open(self.dmesg_file, "r") as f:
                print(f.read())
        except FileNotFoundError:
            print("dmesg file not found.")

    def delete_dmesg(self):
        try:
            os.remove(self.dmesg_file)
            print("dmesg file deleted.")
        except FileNotFoundError:
            print("dmesg file not found.")

    def toggle_filesystem_monitoring(self):
        self.filesystem_monitoring_enabled = not self.filesystem_monitoring_enabled
        if self.filesystem_monitoring_enabled:
            print("Filesystem monitoring enabled.")
        else:
            print("Filesystem monitoring disabled.")

    def handle_error(self, error):
        self.last_error = error
        traceback.print_exc()  # Print the traceback
        self.log_command(f"Error occurred: {str(error)}")

    def recover_from_error(self):
        if self.processes:
            del self.processes[-1]  # Remove the last process that caused the error
            print("Recovered from error by removing the last process.")
        else:
            print("No processes left to recover from error.")
            self.reboot_os()

class VirtualProcess:
    def __init__(self, program):
        self.program = program
        self.start_time = time.time()  # Record the start time when the process is initialized

    def get_elapsed_time(self):
        """Get the elapsed time since the process started."""
        return time.time() - self.start_time
    def execute(self):
        pass
