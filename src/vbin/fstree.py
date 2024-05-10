import os
import gzip
import json
from textual.app import App, ComposeResult
from textual.widgets import Tree, Header
from textual.screen import Screen
from textual.command import Hit, Hits, Provider

class FSTreeCommands(Provider):

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        icon: var[str] = var('🔎')


        command = "back_to_shell()"
        score = matcher.match(command)
        if score > 0:
            yield Hit(
                score,
                matcher.highlight(command),
                partial="back",
                text="Back",
                help="Exit fstree",
                command="back_to_shell()",
            )


class VirtualFSTree(Screen[bool]):

    COMMANDS = Screen.COMMANDS | {FSTreeCommands}

    def back_to_shell(self):
        self.switch_screen("qshell")

    def load_virtual_fs_as_tree(self):
       file_path = "vinit/file_system.json" 
       if os.path.exists(file_path):
            try:
                with gzip.open(file_path, 'rb') as file:
                    data = json.loads(file.read().decode('utf-8'))
            except gzip.BadGzipFile:
                with open(file_path, 'r') as file:
                    data = json.load(file)
       else:
           print("File system JSON file not found.")
           self.dismiss(False)

       root_node = Tree(data["name"])
       self._build_tree(root_node, data)
       return root_node

    def _build_tree(self, tree_node, data):
        for directory_name, directory_data in data["subdirectories"].items():
            directory_node = tree_node.root.add(directory_name, expand=True)
            self._build_subtree(directory_node, directory_data)

    def _build_subtree(self, parent_node, data):
        for directory_name, directory_data in data["subdirectories"].items():
            directory_node = parent_node.add(directory_name, expand=True)
            self._build_subtree(directory_node, directory_data)
        for file_name in data["files"]:
            parent_node.add_leaf(file_name)

    def compose(self) -> ComposeResult:
        yield Header()
        self.title = "vOS FStree"
        self.virtual_fs_tree = self.load_virtual_fs_as_tree()
        self.virtual_fs_tree.root.expand()
        yield self.virtual_fs_tree




