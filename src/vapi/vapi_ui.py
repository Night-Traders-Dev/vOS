#from multiprocessing import Process,Queue,Pipe
import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual import on, events
from textual.widgets import (Button,
                             Footer,
                             Header,
                             Static,
                             Input,
                             Label,
                             TextArea,
                             DataTable)


## component imports
from vui.vterminal import QShell
from vui.vlogin import VLogin
from vbin.fstree import VirtualFSTree



def QShell_widget():
    return QShell()

def VLogin_widget():
    return VLogin()


def FSTree_widget():
    return VirtualFSTree()

