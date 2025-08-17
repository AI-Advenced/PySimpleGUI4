from ..core import Element
from ..constants import *




class TreeData:
    """
    Class that user fills in to represent their tree data. It's a very simple tree representation with a root "Node"
    with possibly one or more children "Nodes".  Each Node contains a key, text to display, list of values to display
    and an icon.  The entire tree is built using a single method, Insert.  Nothing else is required to make the tree.
    """

    class Node:
        """
        Contains information about the individual node in the tree
        """

        def __init__(self, parent, key, text, values, icon=None):
            """
            Represents a node within the TreeData class

            :param parent: The parent Node
            :type parent:  (TreeData.Node)
            :param key:    Used to uniquely identify this node
            :type key:     str | int | tuple | object
            :param text:   The text that is displayed at this node's location
            :type text:    (str)
            :param values: The list of values that are displayed at this node
            :type values:  List[Any]
            :param icon:   just a icon
            :type icon:    str | bytes
            """

            self.parent = parent  # type: TreeData.Node
            self.children = []  # type: List[TreeData.Node]
            self.key = key  # type: str
            self.text = text  # type: str
            self.values = values  # type: List[Any]
            self.icon = icon  # type: str | bytes

        def _Add(self, node):
            self.children.append(node)

    def __init__(self):
        """
        Instantiate the object, initializes the Tree Data, creates a root node for you
        """
        self.tree_dict = {}  # type: Dict[str, TreeData.Node]
        self.root_node = self.Node("", "", "root", [], None)  # The root node
        self.tree_dict[""] = self.root_node  # Start the tree out with the root node

    def _AddNode(self, key, node):
        """
        Adds a node to tree dictionary (not user callable)

        :param key:  Uniquely identifies this Node
        :type key:   (str)
        :param node: Node being added
        :type node:  (TreeData.Node)
        """
        self.tree_dict[key] = node

    def insert(self, parent, key, text, values, icon=None):
        """
        Inserts a node into the tree. This is how user builds their tree, by Inserting Nodes
        This is the ONLY user callable method in the TreeData class

        :param parent: the parent Node
        :type parent:  (Node)
        :param key:    Used to uniquely identify this node
        :type key:     str | int | tuple | object
        :param text:   The text that is displayed at this node's location
        :type text:    (str)
        :param values: The list of values that are displayed at this node
        :type values:  List[Any]
        :param icon:   icon
        :type icon:    str | bytes
        """

        node = self.Node(parent, key, text, values, icon)
        self.tree_dict[key] = node
        parent_node = self.tree_dict[parent]
        parent_node._Add(node)

    def __repr__(self):
        """
        Converts the TreeData into a printable version, nicely formatted

        :return: (str) A formatted, text version of the TreeData
        :rtype:
        """
        return self._NodeStr(self.root_node, 1)

    def _NodeStr(self, node, level):
        """
        Does the magic of converting the TreeData into a nicely formatted string version

        :param node:  The node to begin printing the tree
        :type node:   (TreeData.Node)
        :param level: The indentation level for string formatting
        :type level:  (int)
        """
        return "\n".join(
            [
                str(node.key)
                + " : "
                + str(node.text)
                + " [ "
                + ", ".join([str(v) for v in node.values])
                + " ]"
            ]
            + [
                " " * 4 * level + self._NodeStr(child, level + 1)
                for child in node.children
            ]
        )

    Insert = insert

