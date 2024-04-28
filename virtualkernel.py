import os
import hashlib
import base64
from datetime import datetime
import traceback
import uuid

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

    @staticmethod
    def generate_random_id():
        return uuid.uuid4().int & (1<<32)-1

    def add_user(self, fs, user, password):
        # Generate random uid and gid if not provided
        uid = self.generate_random_id()
        gid = self.generate_random_id()
        userdir = "/home/" + user
        shell = "/bin/qshell"

        # Write the user account information to the password file
        with open(self.file_path, 'a') as file:
            file.write(f"{user}:{password}:{uid}:{gid}:{userdir}:{shell}\n")


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
        # Read all lines from the password file, searching for the specified user
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(':')
                if parts[0] == username:
                    return UserAccount(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
        return None

class VirtualKernel:
    def __init__(self):
        self.processes = []
        self.dmesg_file = "dmesg"
        self.filesystem_monitoring_enabled = True
        self.last_error = None
        self.password_file = PasswordFile("passwd")  # Initialize password file

    def reboot_os(self):
        """Reboots the virtual operating system."""
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        # Reset kernel state or perform any necessary actions to reboot the OS
        print("Rebooting the virtual operating system...")
        self.log_command("[!!]Rebooting vOS...")
        self.processes = []  # Reset the list of processes
        print("Virtual operating system rebooted successfully.")
        self.print_dmesg()

    def create_process(self, program):
        new_process = VirtualProcess(program)
        self.processes.append(new_process)

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

    def execute(self):
        pass
