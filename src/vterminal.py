from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events
import sys
import time
import datetime
import asyncio
from vcommands import VCommands
from virtualmachine import VirtualMachine
from virtualmachine import Wallet
from vapi import initialize_system
from vapi import establish_directory
from vapi import qshell_instance_sys
from vapi import vm_addresstools_instance


class QShell(Widget):


    BINDINGS = [
        Binding(key="ctrl+c", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        text_area = TextArea(id="output")
        text_area.read_only = True
        text_area.cursor_blink = False
        self.title = "qShell"
        text_area.theme = "vscode_dark"
        yield text_area
        yield Input(placeholder="$ ", id="input")

    @on(Input.Submitted)
    def execute_command(self):
        fs_instance, kernel_instance, animations_instance, vproc_instance, passwordtools_instance = initialize_system()
        self.kernel = kernel_instance
        self.animations = animations_instance
        self.addrtools = vm_addresstools_instance()
        self.qshell = qshell_instance_sys
        self.fs = fs_instance
        self.passwordtools_instance = passwordtools_instance
        self.vproc_instance = vproc_instance

        command = self.query_one("#input", Input)
        if command.value.strip():
            self.append_output(f"$ {command.value.strip()}\n")
#            command = input(f"{self.current_directory.get_full_path()} $ ").strip()
 #           self.history.append(command)
            command = command.value.strip()
            self.kernel.log_command(command)  # Log the command
            if command == "exit" or command == "shutdown":
                self.append_output("Shutting Down VirtualOS...\n")
                self.mount(Label("Shutting Down VirtualOS...\n"))
                self.vproc_instance.shutdown_vproc(self)
                self.fs.save_file_system("file_system.json")  # Save filesystem
                self.kernel.delete_dmesg()  # Delete dmesg file on exit
                self.display = False
                self.notify("VirtualOS Shutdown Completed!")
#                self.animations.shutdown_animation()
            elif command.startswith("su"):
                auth = self.passwordtools_instance.su_prompt()
                if auth:
                        parts = command.split(" ", 1)
                        permissions = parts[1] if len(parts) > 1 else "rwxrwxrwx"
                        VCommands.su(self, self.fs, self.current_directory, permissions)


            elif command.startswith("history"):
                if not self.history:
                    print("Command history is empty.")
                    return

                print("Command history:")
                for i, command in enumerate(reversed(self.history), start=1):
                    print(f"{i}: {command}")

            elif command.startswith("reboot"):
                confirmation = input("Are you sure you want to reboot? (yes/no): ").strip().lower()
                if confirmation == "yes":
                    self.kernel.reboot_os()  # Call the reboot function from the kernel
                else:
                    print("Reboot cancelled.")
                    self.kernel.log_command(f"[!]Reboot cancelled")

            elif command.startswith("perms"):
                _, path = command.split(" ", 1)
                VCommands.perms(self.fs, path)

            elif command.startswith("mkdir"):
                _, path = command.split(" ", 1)
                VCommands.mkdir(self.fs, self.current_directory, path)
                self.fs.save_file_system("file_system.json")  # Save filesystem

            elif command.startswith("sysmon"):
                self.vproc_instance.monitor_processes(self)

            elif command.startswith("diff"):
                _, path1, path2 = command.split(" ", 2)
                VCommands.diff(self, self.fs, self.current_directory, path1, path2)

            elif command.startswith("cmp"):
                _, path1, path2 = command.split(" ", 2)
                VCommands.CMP(self.fs, self.current_directory, path1, path2)


            elif command.startswith("qshell"):
                _, path = command.split(" ", 1)
                filepath = self.current_directory.get_full_path() + "/" + path
                self.kernel.log_command(f"qshell: {filepath}")
                if self.fs.file_exists(filepath):
                    qshell_commands = self.qshell.execute_script(path)
                    for qshell_command in qshell_commands:
                        if qshell_command:
                            # Execute the parsed qShell command using the appropriate method from vcommands
                            self.execute_vcommand(qshell_command)
                else:
                    print(f"{path} not found")
            elif command.startswith("ls"):
                parts = command.split(" ")
                if len(parts) > 1:
                    _, path = parts
                else:
                    path = None
                self.kernel.log_command(f"ls debug: {self.current_directory} and {path}")
                VCommands.ls(self.fs, self.current_directory, path)

            elif command.startswith("cd"):
                _, path = command.split(" ", 1)
                self.current_directory = VCommands.cd(self, self.fs, self.current_directory, path)

            elif command.startswith("cat"):
                try:
                    _, path = command.split(" ", 1)
                except ValueError:
                    # If no path is specified, use the current directory
                    path = None
                VCommands.cat(self.fs, self.current_directory, path)

            elif command.startswith("rmdir"):
                _, path = command.split(" ", 1)
                VCommands.rmdir(self.fs, self.current_directory, path)

            elif command.startswith("nano"):
                try:
                    _, path = command.split(" ", 1)
                except ValueError:
                    # If no path is specified, use the current directory
                    path = None
                VCommands.nano(self, self.fs, self.current_directory, path)

            elif command.startswith("version"):
                VCommands.version(self)

            elif command == "clear":
                VCommands.clear_screen()

            elif command == "run_vm":  # Command to run the virtual machine
                self.vm.run()

            elif command == "dmesg":  # Command to print virtual dmesg
                if self.su_check(command):
                    self.kernel.print_dmesg()

            elif command == "uptime":
                uptime = self.kernel.get_uptime()
                print(f"vOS uptime: {uptime}")


            elif command == "update":
                if self.su_check(command):
                    self.kernel.update_vos()

            elif command == "reset_fs":
                if self.su_check(command):
                    self.fs.reset_fs()

            elif command == "toggle_fs_monitoring":  # Command to toggle filesystem monitoring
                self.kernel.toggle_filesystem_monitoring()

            elif command == "monitor_fs":  # Command to monitor filesystem
                self.kernel.monitor_filesystem("file_system.json")

            elif command == "pwd":  # Corrected call to pwd method
                VCommands.pwd(self.current_directory)  # Pass the current directory

            elif command.startswith("snapshot"):
                VCommands.snapshot(self, self.fs)

            elif command.startswith("touch"):
                try:
                    _, path = command.split(" ", 1)
                except ValueError:
                    # If no path is specified, use the current directory
                    path = None
                VCommands.touch(self.fs, self.current_directory, path)

            elif command.startswith("rm"):
                _, path = command.split(" ", 1)
                VCommands.rm(self.fs, self.current_directory, path)

            elif command.startswith("mv"):
                _, old_path, new_path = command.split(" ", 2)
                VCommands.mv(self.fs, self.current_directory, old_path, new_path)

            elif command.startswith("cp"):
                _, src_path, dest_path = command.split(" ", 2)
                VCommands.cp(self.fs, self.current_directory, src_path, dest_path)

            elif command.startswith("echo"):
                parts = command.split(" ")
                args = parts[1:-1]  # Extract arguments
                file = parts[-1]  # Extract filename
                self.kernel.log_command(f"Parts: {parts} Args: {args} File: {file}")
                if ">>" not in command and ">" not in command:
                    file = None
                    args = parts[1:]
                VCommands.echo(self.fs, self.current_directory, *args, file=file)

            elif command.startswith("logout"):
                self.passwordtools_instance.logout()

            elif command.startswith("adduser"):
                if self.su_check(command):
                     _, username, password = command.split(" ", 2)
                     passwordtools_instance.add_user(self.fs, username, password)
                     path = "/home/" + username
                     VCommands.mkdir(self.fs, path)

            elif command.startswith("deluser"):
                if self.su_check(command):
                     _, username = command.split(" ", 1)
                     passwordtools_instance.delete_user(self.fs, username)

            elif command.startswith("updateuser"):
                if self.su_check(command):
                    _, username, new_password = command.split(" ", 2)
                    passwdtools_instance.update_user(self.fs, username, new_password)

            elif command.startswith("readuser"):
                _, username = command.split(" ", 1)
                passwdtools_instance.read_user(self.fs, username)

            elif command.startswith("wallet"):
                if self.fs.file_exists("/usr/addr"):
                    self.wallet.view_wallet(self.fs, self.addrtools)
                else:
                    self.wordlist = self.addrtools.grab_wordlist(self)
                    self.seed = self.addrtools.generate_seed_phrase(self, self.wordlist)
                    self.addr = self.addrtools.generate_crypto_address(self, self.fs, self.addrtools, self.seed, False)
                    self.wallet = Wallet(self.addr, "0")
                    print(f"P3:Address {self.addr}\n Seed Phrase: {self.seed}\n\nRun wallet again to login")

            elif command.startswith("help"):
                parts = command.split(" ")
                if len(parts) > 1:
                    _, command_name = parts
                    if hasattr(VCommands, command_name):
                        # Display command specific help
                        print(getattr(VCommands, command_name).__doc__)
                    else:
                        print(f"Command '{command_name}' not found.")
                else:
                    # Display overall help
                    print("Available commands:")
                    for method_name in dir(VCommands):
                        method = getattr(VCommands, method_name)
                        if callable(method) and not method_name.startswith("__"):
                            print(method.__doc__)
            else:
                print("Command not found. Type 'help' to see available commands.")
                self.kernel.log_command(f"[!] Command '{command}' not found.")

#            command.value = ""
#            except Exception as e:
#                self.kernel.handle_error(e)


    def append_output(self, text):
        output = self.query_one("#output", TextArea)
        output.replace(text, start=(0, 0), end=(0, 0))
