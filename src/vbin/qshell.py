import os
from rich.console import Console
from rich.prompt import Prompt
import importlib

class QShell:
    def __init__(self):
        self.console = Console()

    def run(self):
        self.console.print("[bold cyan]Welcome to qShell![/bold cyan]")
        while True:
            command = Prompt.ask("[bold green]qShell[/bold green] $ ")
            if command.lower() == "exit":
                self.console.print("[bold cyan]Exiting qShell...[/bold cyan]")
                break
            elif self.is_command_in_vbin(command):
                # Execute command from vbin directory
                self.execute_command(command)
            else:
                self.console.print(f"[bold red]Error:[/bold red] Command '{command}' not found.")

    def execute_command(self, command):
        try:
            # Dynamically import the module from the vbin directory
            module = importlib.import_module(command)
            # Get the function from the module
            function = getattr(module, command)
            # Call the function
            function()
        except Exception as e:
            self.console.print(f"[bold red]Error executing command '{command}': {e}[/bold red]")

    def is_command_in_vbin(self, command_name):
        """
        Check if a command exists in the vbin directory.

        Parameters:
            command_name (str): The name of the command to check.

        Returns:
            bool: True if the command exists in vbin, False otherwise.
        """
        # Get the path to the vbin directory
        current_directory = os.path.dirname(__file__)
        # Construct the path to the command file
        command_file = f"{command_name}.py"
        command_path = os.path.join(current_directory, command_file)
        # Check if the file exists
        return os.path.isfile(command_path)

# Main function
if __name__ == "__main__":
    qshell = QShell()
    qshell.run()
