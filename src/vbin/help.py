import os
import importlib

class help:
    def __init__(self):
        self.app_name = "help"

    @staticmethod
    def help(command=None):
        """
        help: Display help information\nUsage: help [command]\nIf no command is provided, displays overall help information.\nIf a command is provided, displays specific help information for that command.
        """

        # Get the path to the vbin directory
        current_directory = os.path.dirname(__file__)

        if command:
            module_name = command + ".py"
            if module_name in current_directory:
                module_path = os.path.join(current_directory, module_name)
                module = importlib.import_module(command)
                print(module.__doc__ or f"No help available for command '{command}'.")
            else:
                print(f"Command '{command}' not found.")
        else:
            print("Help Docs not found.")
