import time
from textual.widgets import DataTable
from textual.app import App, ComposeResult

class ProcessMonitor(App):
    def monitor_processes(self):
        running_processes["name": "kernel", "pid": "0",  "cache": "1", "start_time": "1715271209.6508136", "user": "Kernel"]
        highlighted_index = 0
        while True:
            terminal_width = self.width
            terminal_height = self.height

            table = DataTable(title="Process Monitor")
            table.add_column("Process Name", justify="center")
            table.add_column("PID", justify="center")
            table.add_column("Cache", justify="center")
            table.add_column("User", justify="center")
            table.add_column("Uptime", justify="center")

            def compose(self) -> ComposeResult:
                yield DataTable()

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
            self.clear()
            self.view(table)

            # Print control instructions
            self.view("Use arrow keys to navigate, and press Enter to select a process", justify="left")
            self.view("Press CTRL + C to exit", justify="left")
            # Wait for user input
            time.sleep(1)

if __name__ == "__main__":
    ProcessMonitor().run()
