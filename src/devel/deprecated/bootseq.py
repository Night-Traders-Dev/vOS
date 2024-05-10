self.kernel.log_command("Kernel Loaded...")
        self.kernel.get_checksum_file()
        self.kernel.compare_checksums()
        self.kernel.log_command("Booting up VirtualOS...")
        self.kernel.log_command("Component Version Numbers:\n")
        self.kernel.print_component_versions(False)
        self.kernel.log_command(f"Python Version: {sys.version}")
        self.kernel.log_command("Initializing VirtualFileSystem...")
        self.kernel.create_process("filesystemd")
        self.kernel.log_command("VirtualFileSystem Loaded...")