from datetime import datetime
import os
import traceback

class VirtualKernel:
    def __init__(self):
        self.processes = []
        self.dmesg_file = "dmesg"
        self.filesystem_monitoring_enabled = False                                         self.last_error = None

    def create_process(self, program):
        new_process = VirtualProcess(program)
        self.processes.append(new_process)

    def schedule_processes(self):
        for process in self.processes:                                                         try:                                                                                   process.execute()
            except Exception as e:
                self.handle_error(e)
                                                                                                   # Recover from error by removing the last process and retrying
                self.recover_from_error()

    def log_command(self, command):                                                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.dmesg_file, "a") as f:
            f.write(f"[{timestamp}] {command}\n")
                                                                                       def boot_verbose(self):
        verbose_message = "VirtualOS boot-up completed."
        self.log_command(verbose_message)                                          
    def print_dmesg(self):                                                                 try:
            with open(self.dmesg_file, "r") as f:
                print(f.read())
        except FileNotFoundError:
            print("dmesg file not found.")

    def delete_dmesg(self):
        try:
            os.remove(self.dmesg_file)
            print("dmesg file deleted.")                                                   except FileNotFoundError:
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
        else:                                                                                  print("No processes left to recover from error.")

class VirtualProcess:
    def __init__(self, program):
        self.program = program

    def execute(self):
        pass