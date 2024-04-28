# virtualmachine.py

class VirtualMachine:
    def __init__(self, virtual_os, filesystem):  # Pass VirtualOS instance as an argument
        self.virtual_os = virtual_os  # Store reference to VirtualOS instance
        self.filesystem = filesystem

    def run(self):
        print("Running Virtual Machine...")
        # Implement VM logic here
