# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 10:42:25 2017

@author: Jesmond
"""

class Node:
    def __init__(self, val):
        self.l = None
        self.r = None
        self.v = val

class Tree:
    def __init__(self):
        self.root = None

    def getRoot(self):
        return self.root

# if tree has no root then new value will be the root
# else will add new value to the root left/right
    def add(self, new_value):
        if(self.root == None):
            self.root = Node(new_value)
        else:
            self._add(new_value, self.root)

# if current node left/right is empty, assign new value
# else create a new node object
    def _add(self, new_value, current_node):
        if(new_value < current_node.v):
            if(current_node.l != None):
                #self._add(val, node.l)
                current_node.l = new_value
            else:
                current_node.l = Node(new_value)
        else:
            if(current_node.r != None):
                #self._add(new_value, current_node.r)
                current_node.r = new_value
            else:
                current_node.r = Node(new_value)

    def find(self, val):
        if(self.root != None):
            return self._find(val, self.root)
        else:
            return None

    def _find(self, val, node):
        if(val == node.v):
            print (node.l + node.r)
            return node.v
        elif(val < node.v and node.l != None):
            self._find(val, node.l)
        elif(val > node.v and node.r != None):
            self._find(val, node.r)

    def find_inorder(self, node):
        if (self.root != None):
            return str(node.l)+str(node.v)+str(node.r)
        else:
            return None       
        
    def deleteTree(self):
        # garbage collector will do this for us. 
        self.root = None

    def printTree(self):
        if(self.root != None):
            self._printTree(self.root)

    def _printTree(self, node):
        if(node != None):
            self._printTree(node.l)
            print (str(node.v))
            self._printTree(node.r)


bt = Tree()
bt.add(10)
bt.add(22)
bt.add(5)
#binaryTree.add(4)
bt.printTree()