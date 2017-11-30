# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 11:37:51 2017

@author: Jesmond
"""

class Node:
    def __init__(self,
                 key = None,
                 root = None, 
                 left = None, 
                 right = None, 
                 value = None):
        self.key = key
        self.root = root
        self.left = left
        self.right = right
        self.value = value
           
    def boisLeftChild(self):
        return self.root and self.root.left == self
    
    def boisRightChild(self):
        return self.root and self.root.right == self
    
    def boisRoot(self):
        return not self.root
    
    def boisLeaf(self):
        return not (self.left and self.right)
    
    def bohasAnyChildren(self):
        return self.left or self.right
    
    def bohasBothChildren(self):
        return self.left and self.right
    
    
class BinarySearchTree:
    def __init__(self):
        self.root = None
        self.size = 0
    
    def length(self):
        return self.size
    
    def __len__(self):
        return self.size
    
    def put(self, key, value):
        # place node under root
        if self.root:
            self._put(key, value, self.root)
        # create new root
        else:
            self.root = Node(key, value)
        self.size = self.size + 1
    
    def _put(self, key, value, currentNode):
        # key less than root place on left, otherwise right
        if key < currentNode.key:
            # place left value in left node
            if currentNode.left:
                self._put(key, value, currentNode.left) 
            # create new node to put left value
            else:
                currentNode.left = Node(key, value)
        else:
            
            if currentNode.right:
                self._put(key, value, currentNode.right)
            else:
                currentNode.right = Node(key, value)
    
    def get(self, key):
        if self.root:
            return self._get(key, self.root)
        else:
            return None
    
    def _get(self, key, currentNode):
        if not currentNode:
            return None
        elif currentNode.key == key:
            return currentNode
        elif key < currentNode.key:
            return self._get(key, currentNode.left)
        else:
            return self._get(key, currentNode.right)
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        self.put(key, value)
                
    def delete(self, key):
        if self.size > 1:
            removeNode = self._get(key, self.root)
            if removeNode:
                self.remove(removeNode)
                self.size = self.size - 1
            else:
                raise KeyError("error, key not in tree")
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = self.size - 1
        else:
            raise KeyError("error, key not in tree")
    
    def __delitem__(self, key):
        self.delete(key)
    
tree = BinarySearchTree()    
tree.put(5,"a")
tree.put(4,"e")
tree.put(6,"f")