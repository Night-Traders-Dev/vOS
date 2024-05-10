from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Button, Footer, Header, Static, Input, Label, TextArea
from textual.widget import Widget
from textual import on, events
import sys
import time
import datetime
import asyncio
from vapi.vapi import  (establish_directory,
                        qshell_instance_sys,
                        vm_addresstools_instance,
                        get_active_user,
                        home_fs_init,
                        vcommands_instance,
                        vm_wallet_instance,
                        vm_instance,
                        fs_instance,
                        kernel_instance,
                        vproc_instance,
                        passwordtools_instance,
                        vm_wallet_instance,
                        vm_instance)




class QShell(Widget):

    BINDINGS = [
        Binding(key="ctrl+c", action="quit", description="Quit the app"),
    ]

    global passwordtools_instance
    global kernel_instance
    global fs_instance
    global vproc_instance
    global animations_instance
    global active_user_init
    global home_fs
    global home_init
    home_init = False
    kernel = kernel_instance()
    addrtools = vm_addresstools_instance()
    qshell = qshell_instance_sys
    fs = fs_instance()
    vproc_instance = vproc_instance()
    active_user_init = get_active_user()
    home_fs = home_fs_init(active_user_init)


    def compose(self) -> ComposeResult:
        global text_area
        text_area = TextArea(id="output")
        text_area.read_only = True
        text_area.cursor_blink = False
        text_area.theme = "vscode_dark"
        global fstree
#        fstree = VirtualFSTree()
        yield text_area
#        yield fstree
        yield Input(placeholder=f"{active_user_init} $ ", id="input")

    @on(Input.Submitted)
    def execute_command(self):
        self.history = []
        self.passwordtools_instance = passwordtools_instance
        self.active_user = active_user_init
        self.home_dir = "/home/" + self.active_user
        global home_init
        if home_init == False:
            self.current_directory = home_fs
            global cur_dir
            cur_dir = home_fs
            home_init = True
        else:
            self.current_directory = cur_dir


        VCommands = vcommands_instance()
        command = self.query_one("#input", Input)
        command_input = command
        if command.value.strip():
            self.append_output(f"$ {command.value.strip()}\n")
#            command = input(f"{self.current_directory.get_full_path()} $ ").strip()
            command = command.value.strip()
            self.history.append(command)
            self.kernel.log_command(command)  # Log the command
            if command.startswith("exit") or command.startswith("shutdown"):
                vproc_instance.shutdown_vproc(self)
                self.fs.save_file_system("file_system.json")  # Save filesystem
                parts = command.split(" ", 1)
                if len(parts) > 1 and parts[1] == "--debug":
                    pass
                else:
                    self.kernel.delete_dmesg()  # Delete dmesg file on exit
                self.display = False
                self.notify("VirtualOS Shutdown Completed!")
                exit()
            elif command.startswith("su"):
                auth = self.passwordtools_instance.su_prompt()
                if auth:
                        parts = command.split(" ", 1)
                        permissions = parts[1] if len(parts) > 1 else "rwxrwxrwx"
                        VCommands.su(self, self.fs, self.current_directory, permissions)

            elif command.startswith(f"whoami"):
                self.append_output(f"{self.active_user}\n")

            elif command.startswith("history"):
                if not self.history:
                    self.append_output("Command history is empty.")

                print("Command history:")
                for i, command in enumerate(reversed(self.history), start=1):
                    self.append_output(f"{i}: {command}")

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

            elif command.startswith("fstree"):
                self.visible = False
                fstree.visible = True

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
                    path = self.home_dir
                self.kernel.log_command(f"ls debug: {self.current_directory} and {path}")
                ls_list = VCommands.ls(self.fs, self.current_directory, path)
                for i in ls_list:
                    self.append_output(i + "\n")

            elif command.startswith("cd"):
                _, path = command.split(" ", 1)
                cur_dir = VCommands.cd(self, self.fs, self.current_directory, path)

            elif command.startswith("cat"):
                try:
                    _, path = command.split(" ", 1)
                except ValueError:
                    # If no path is specified, use the current directory
                    path = None
                text_area.language="python"
                self.append_output(VCommands.cat(self.fs, self.current_directory, path))
                text_area.language=None

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
                text_area.clear()

            elif command == "run_vm":  # Command to run the virtual machine
                self.vm.run()

            elif command == "dmesg":  # Command to print virtual dmesg
                #if self.su_check(command):
                dmesg_array = self.kernel.print_dmesg()
                for i in dmesg_array:
                    self.append_output(i + "\n")

            elif command == "uptime":
                uptime = self.kernel.get_uptime()
                self.append_output(f"vOS uptime: {uptime}")


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
                self.append_output(VCommands.pwd(self.current_directory) + "\n")  # Pass the current directory

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
                    self.append_output(VCommands.echo(self.fs, self.current_directory, *args, file=file) + "\n")
                else:
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
                self.append_output("Command not found. Type 'help' to see available commands.")
                self.kernel.log_command(f"[!] Command '{command}' not found.")

            command_input.value = ""
#            except Exception as e:
#                self.kernel.handle_error(e)


    def append_output(self, text):
        output = self.query_one("#output", TextArea)
        output.insert(text)


#    def on_key(self, event: events.Key) -> None:
#        keypress = self.query_one(event)
