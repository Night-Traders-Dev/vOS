import os


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
