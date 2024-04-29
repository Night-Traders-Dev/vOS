import os
import hashlib
import base64
from datetime import datetime
import traceback
import uuid
import getpass

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
    def logout(self):
       os.system('cls' if os.name == 'nt' else 'clear')
       self.active_user = None
       self.login_prompt()

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
        self.password_file.login_prompt()

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
