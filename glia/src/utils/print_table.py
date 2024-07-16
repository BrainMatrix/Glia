from rich.tree import Tree
from enum import Enum

def build_tree(data, tree=None):
    if tree is None:
        tree = Tree("root")

    if isinstance(data, dict):
        for key, value in data.items():
            branch = tree.add(f"[bold]{key}[/bold]")
            build_tree(value, branch)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            branch = tree.add(f"[bold][{index}][/bold]")
            build_tree(value, branch)
    elif isinstance(data, Enum):
        tree.add(f"{data.name}")
    elif hasattr(data, "__dict__"):
        branch = tree.add("Object")
        build_tree(data.__dict__, branch)
    else:
        tree.add(f"{data}")

    return tree
