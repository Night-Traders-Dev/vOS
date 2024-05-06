
import signal
import sys
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
import threading
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel

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


    def change_password(self, current_password, new_password):
        """
        Change the user's password.
        
        Parameters:
            current_password (str): The current password of the user.
            new_password (str): The new password to set.
        
        Returns:
            bool: True if the password was successfully changed, False otherwise.
        """
        if self.check_password(current_password):
            self.password = self.encrypt_password(new_password)
            return True
        else:
            return False



class PasswordFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.dmesg_file = "dmesg"
        self.active_user = None
#        self.clock_thread = threading.Thread(target=self.update_clock, daemon=True)  # Create a daemon thread for the clock
#        self.clock_thread.start()  # Start the clock thread

    def update_clock(self):
        while True:
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clock_panel = Panel(Text(current_datetime, style="bold white"), width=20)
            self.console.print(Layout().update(self.console.options, {"upper-right": clock_panel}))
            time.sleep(1)  # Update the clock every second

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
                self.login_prompt_rich()
                # Create and run the login prompt
                #self.run()
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
        self.login_prompt_rich()

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
        try:
            user_account = UserAccount(username, password, user[2], user[3], user[4], user[5])
        except Exception as e:
            return False
        VirtualKernel.log_command(self, f"auth: {user[1]} and {user_account.password}")
        if user[1] == user_account.password:
            pid = VirtualKernel.create_process(self, "qShell", True, "qShell_Instance")
            self.active_user = user[0]
            return True
        else:
            return False

    def login_prompt_rich(self):
        console = Console()

        try:
            console.clear()

            # Get console width
            console_width = console.width

            # Display title bar
            console.print("[bold magenta]╔" + "═" * (console_width - 2) + "╗[/bold magenta]")
            console.print("[bold magenta]║" + " " * ((console_width - 10) // 2) + "[bold white]vOS Login[/bold white]" + " " * ((console_width - 10) // 2) + "[bold magenta]║[/bold magenta]")
            console.print("[bold magenta]╚" + "═" * (console_width - 2) + "╝[/bold magenta]")

            # Get username and password
            username = Prompt.ask("[bold cyan]Username:[/bold cyan]")
            password = Prompt.ask("[bold cyan]Password:[/bold cyan]", password=True)

            # Check authentication
            if self.authenticate(username, password):
                console.clear()
                console.print("[bold green]Login successful![/bold green]")
                time.sleep(1)  # Wait for 1 second before clearing the screen
            else:
                console.print("[bold red]Invalid username or password. Please try again.[/bold red]")
                time.sleep(2)  # Wait for 2 seconds before clearing the screen

        except KeyboardInterrupt:
            console.print("[bold red]Shutting Down VirtualOS...[/bold red]")
            VirtualKernel.delete_dmesg(self)  # Delete dmesg file on exit
            time.sleep(2)  # Wait for 2 seconds before exiting
            sys.exit(0)

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



class Animations:
    @classmethod
    def boot_animation_rich(cls):
        console = Console()

        with Progress(
            SpinnerColumn(spinner_name="dots"), "{task.description}", transient=True
        ) as progress:
            task = progress.add_task("Booting vOS...", total=10)
            for _ in range(10):
                progress.update(task, advance=1)
                time.sleep(0.1)

        console.print("Welcome to vOS")

    @classmethod
    def reboot_animation(cls):
        console = Console()

        with Progress() as progress:
            task = progress.add_task("[cyan]Rebooting vOS...", total=20)
            for i in range(20):
                progress.update(task, advance=1)
                time.sleep(0.1)

        console.print("[green]Reboot complete. Goodbye!")

    @classmethod
    def shutdown_animation(cls):
        console = Console()

        with Progress() as progress:
            task = progress.add_task("[cyan]Shutting down vOS...", total=20)
            for i in range(20):
                progress.update(task, advance=1)
                time.sleep(0.1)

        console.print("[green]Shutdown complete. Goodbye!")


class KernelMessage:
    dmesg_file = "dmesg"

    @classmethod
    def log_process(cls, program):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(cls.dmesg_file, "a") as f:
            f.write(f"[{timestamp}] {program}\n")


    @classmethod
    def format_uptime(cls, uptime):
        weeks, days = divmod(uptime, 60 * 60 * 24 * 7)
        days, hours = divmod(days, 60 * 60 * 24)
        hours, minutes = divmod(hours, 60 * 60)
        minutes, seconds = divmod(minutes, 60)

        if weeks > 0:
            return f"{weeks:,.0f} weeks, {days:,.0f} days"
        elif days > 0:
            return f"{days:,.0f} days, {hours:,.0f} hours"
        elif hours > 0:
            return f"{hours:,.0f} hours, {minutes:,.0f} minutes"
        elif minutes > 0:
            return f"{minutes:,.0f} minutes, {seconds:,.4f} seconds"
        else:
            return f"{seconds:,.4f} seconds"

class VirtualKernel:
    def __init__(self):
        self.processes = ProcessList.running_processes
        self.create_process("VirtualKernel")
        self.dmesg_file = "dmesg"
        self.create_process("dmesgd")
        self.filesystem_monitoring_enabled = True
        self.last_error = None
        self.password_file = PasswordFile("passwd")  # Initialize password file
        self.create_process("passwd")
        self.qshell_interpreter = QShellInterpreter()
        self.create_process("uptimed")
        self.start_time = time.time()  # Store the start time
        self.active_user = self.password_file.online_user()

    def get_uptime(self):
        """
        Get the uptime of the virtual operating system.
        """
        uptime = int(time.time() - self.start_time)
        formatted_uptime = KernelMessage.format_uptime(uptime)
        return formatted_uptime

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
        pid = self.create_process("update_vos", False, self.active_user)
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
                repo_dir = os.path.join(temp_dir, "vOS-main", "src")
                self.move_files(repo_dir, os.getcwd())

                # Clean up: Remove the temporary directory
                shutil.rmtree(temp_dir)

            print("vOS updated successfully!")
            self.log_command("vOS updated successfully")
            VirtualProcess.kill_process(self, pid)

        except Exception as e:
            print("Failed to fetch repository contents from GitHub:", e)
            VirtualProcess.kill_process(self, pid)



    def move_files(self, src_dir, dest_dir):
        # Move files and directories from source directory to destination directory
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dest_item = os.path.join(dest_dir, item)
            if os.path.isdir(src_item):
                shutil.move(src_item, dest_item)
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
        VirtualProcess.shutdown_vproc(self)
        self.processes = ProcessList.running_processes
        self.dmesg_file = "dmesg"
        self.create_process("dmesgd")
        self.filesystem_monitoring_enabled = True
        self.last_error = None
        self.password_file = PasswordFile("passwd")
        self.create_process("passwd")
        self.qshell_interpreter = QShellInterpreter()
        self.create_process("uptimed")
        self.start_time = time.time()
        Animations.reboot_animation()
        self.log_command("Virtual operating system rebooted successfully.")
        self.password_file.login_prompt_rich()


    def create_process(self, program, allow_multiple=False, user=None):
        KernelMessage.log_process(f"Initialize {program} Allow_Multiple: {allow_multiple} User: {user}")
        # Check if the process is already running
        for pid, process_info in ProcessList.running_processes.items():
            if process_info['name'] == program:
                if not allow_multiple:
                    return None

        # If not running or allowing multiple instances, create a new process instance
        pid = ProcessList.get_next_pid()
        if user == None:
            user = "Root"
        else:
            user = PasswordFile.online_user(self)
        new_process = VirtualProcess(program, pid, user)
        return pid

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
        traceback = traceback.print_exc()  # Print the traceback
        self.log_command(f"Error occurred: {str(error)}")
#        self.log_command("Stack Trace: {traceback}")

    def recover_from_error(self):
        if self.processes:
            del self.processes[-1]  # Remove the last process that caused the error
            print("Recovered from error by removing the last process.")
        else:
            print("No processes left to recover from error.")
            self.reboot_os()


class ProcessList:
    running_processes = {}

    @classmethod
    def add_process(cls, name, pid, cache, user):
        if not cls.running_processes:
            cls.next_pid = 0
        start_time = time.time()
        cls.running_processes[pid] = {'name': name, 'cache': cache, 'start_time': {start_time}, 'user': user}
        KernelMessage.log_process(f"name: {name}, pid: {pid},  cache: {cache}, start_time: {start_time}, user: {user}")

    @classmethod
    def remove_process(cls, pid):
        if pid in cls.running_processes:
            del cls.running_processes[pid]

    @classmethod
    def get_next_pid(cls):
        if not cls.running_processes:
            return 100
        else:
            last_pid = max(cls.running_processes.keys())
            return max(100, last_pid + 1)

    @classmethod
    def get_running_pids(cls):
        return list(cls.running_processes.keys())



class VirtualProcess:
    def __init__(self, program, pid, user):
        self.program = program
        self.pid = pid
        self.cache = 1
        KernelMessage.log_process(f"[*]{user} starting {program}...")
        ProcessList.add_process(self.program, self.pid, self.cache, user)


    def get_elapsed_time(self):
        """Get the elapsed time since the process started."""
        return time.time() - self.start_time

    def execute(self):
        pass



    @staticmethod
    def kill_process(self, pid, verbose=False):
        if pid in ProcessList.running_processes:
            process_info = ProcessList.running_processes[pid]
            process_name = process_info['name']
            del ProcessList.running_processes[pid]
            if verbose:
                print(f"Process '{process_name}' with PID {pid} has been killed.")
            KernelMessage.log_process(f"Process '{process_name}' with PID {pid} has been killed.")
        else:
            print(f"Process with PID {pid} not found.")

    @staticmethod
    def kill_process_by_name(self, process_name, verbose=False):
        pid_to_remove = None
        for pid, process_info in ProcessList.running_processes.items():
            if process_info['name'] == process_name:
                pid_to_remove = pid
                break

        if pid_to_remove is not None:
            VirtualProcess.kill_process(self, pid_to_remove, verbose)
        else:
            print(f"Process '{process_name}' not found.")


    @staticmethod
    def shutdown_vproc(self):
        # Create a copy of the dictionary to avoid modifying it during iteration
        running_processes_copy = ProcessList.running_processes.copy()
        for pid, process_info in running_processes_copy.items():
            process_name = process_info['name']
            VirtualProcess.kill_process(self, pid)




    @staticmethod
    def monitor_processes(self):
        sysmon_pid = VirtualKernel.create_process(self, "sysmon", True, self.active_user)

        console = Console()

        try:
            highlighted_index = 0

            while True:
                terminal_width = console.width
                terminal_height = console.height

                table = Table(title="Process Monitor")
                table.add_column("Process Name", justify="center")
                table.add_column("PID", justify="center")
                table.add_column("Cache", justify="center")
                table.add_column("User", justify="center")
                table.add_column("Uptime", justify="center")

                # Populate the table with process information
                for pid, process_info in ProcessList.running_processes.items():
                    process_name = process_info['name']
                    cache = process_info['cache']
                    start_time = float(next(iter(process_info['start_time'])))
                    elapsed_time = time.time() - start_time
                    formatted_uptime = KernelMessage.format_uptime(elapsed_time)
                    user = process_info['user']
                    table.add_row(process_name, str(pid), str(cache), user, formatted_uptime)

                # Highlight the current process
                table.highlighted = highlighted_index

                # Render the table
                console.clear()
                console.print(table)

                # Print control instructions
                console.print("Use arrow keys to navigate, and press Enter to select a process", justify="left")
                console.print("Press CTRL + C to exit", justify="left")
                # Wait for user input
                time.sleep(1)

                # Handle user input
 #               event = keyboard.read_event(suppress=True)
 #               if event.event_type == "down":
 #                   if event.name == "down":
 #                       highlighted_index = min(highlighted_index + 1, len(ProcessList.running_processes) - 1)
 #                   elif event.name == "up":
 #                       highlighted_index = max(highlighted_index - 1, 0)
 #                   elif event.name == "enter":
                        # Process selection logic goes here
#                        pass

        except KeyboardInterrupt:
            console.print("\nExiting process monitor.")
            VirtualProcess.kill_process(self, sysmon_pid)
        except Exception as e:
            console.print("\nError gaining keyboard perms")
