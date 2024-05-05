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
            command = Prompt.ask("[bold green]qShell[/bold green] > ")
            if command.lower() == "exit":
                self.console.print("[bold cyan]Exiting qShell...[/bold cyan]")
                break
            elif is_command_in_vbin(command):
                # Execute command from vbin directory
                self.execute_command(command)
            else:
                self.console.print(f"[bold red]Error:[/bold red] Command '{command}' not found.")

    def execute_command(self, command):
        try:
            module = importlib.import_module(f"vbin.{command}")
            function = getattr(module, command)
            function()
        except Exception as e:
            self.console.print(f"[bold red]Error executing command '{command}': {e}[/bold red]")


    def is_command_in_vbin(command_name):
        """
        Check if a command exists in the vbin directory.

        Parameters:
            command_name (str): The name of the command to check.

        Returns:
            bool: True if the command exists in vbin, False otherwise.
        """
        vbin_path = os.path.join(os.path.dirname(__file__), 'vbin')
        command_file = f"{command_name}.py"
        command_path = os.path.join(vbin_path, command_file)
        return os.path.isfile(command_path)

# Main function
if __name__ == "__main__":
    qshell = QShell()
    qshell.run()

