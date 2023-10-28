class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class Visited():
    def __init__(self):
        self.visited = []

    def add(self, node):
        self.visited.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.visited)

    def empty(self):
        return len(self.visited) == 0
    
    def get_node_by_state(self, state):
        for node in self.visited:
            if node.state == state:
                return node
        return None

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
