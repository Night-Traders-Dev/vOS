import platform

class TerminalInput:
    def __init__(self):
        self.input_data = None

    def get_input(self):
        if platform.system() == 'Windows':
            import msvcrt
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if ord(key) == 224:  # Arrow keys have an escape sequence of 224
                        arrow_key = msvcrt.getch()
                        if arrow_key == b'H':
                            self.input_data = "UP"
                            return
                        elif arrow_key == b'P':
                            self.input_data = "DOWN"
                            return
                else:
                    # Other regular key press, handle accordingly
                    pass
        else:  # Assume Unix-like system
            import sys
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    key = sys.stdin.read(1)
                    if key == '\x1b':  # Escape sequence for arrow keys
                        key = sys.stdin.read(2)  # Read two more characters for arrow keys
                        if key == '[A':
                            self.input_data = "UP"
                            return
                        elif key == '[B':
                            self.input_data = "DOWN"
                            return
                    else:
                        # Other regular key press, handle accordingly
                        pass
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

#    terminal_input = TerminalInput()
 #   terminal_input.get_input()
  #  print("You pressed:", terminal_input.input_data)
