import os
import gzip
import json
from textual.app import App, ComposeResult
from textual.widgets import Tree
from textual.widget import Widget

class VirtualFSTree(Widget):
    filepath = "file_system.json"

    def load_virtual_fs_as_tree():
        if os.path.exists(file_path):
            try:
                with gzip.open(self.file_path, 'rb') as file:
                    data = json.loads(file.read().decode('utf-8'))
            except gzip.BadGzipFile:
                with open(file_path, 'r') as file:
                    data = json.load(file)
        else:
            print("File system JSON file not found.")
            return None

        root_node = Tree(data["name"])
        _build_tree(root_node, data)
        return root_node

    def _build_tree(tree_node, data):
        for directory_name, directory_data in data["subdirectories"].items():
            directory_node = tree_node.root.add(directory_name, expand=True)
            _build_subtree(directory_node, directory_data)

    def _build_subtree(parent_node, data):
        for directory_name, directory_data in data["subdirectories"].items():
            directory_node = parent_node.add(directory_name, expand=True)
            _build_subtree(directory_node, directory_data)
        for file_name in data["files"]:
            parent_node.add_leaf(file_name)

    def compose(self) -> ComposeResult:
        virtual_fs_tree = load_virtual_fs_as_tree()
        virtual_fs_tree.root.expand()
        yield virtual_fs_tree
