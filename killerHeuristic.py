from graphviz import Digraph

class Node:
    def __init__(self, name, depth, alpha, beta, is_pruned=False):
        self.name = name
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.is_pruned = is_pruned
        self.children = []
        self.is_killer_move = False

def build_tree(depth, max_depth, node_id_counter, killer_moves, parent=None):
    if depth > max_depth:
        return None, node_id_counter

    node_name = f'Node{node_id_counter}'
    node = Node(name=node_name, depth=depth, alpha=float('-inf'), beta=float('inf'))
    node_id_counter += 1

    # Determine if this move is a killer move
    if depth in killer_moves and killer_moves[depth] == node_name:
        node.is_killer_move = True

    # Simulate alpha-beta pruning
    if parent and parent.is_pruned:
        node.is_pruned = True
        return node, node_id_counter

    # Simulate beta cutoff
    if parent and parent.beta <= parent.alpha:
        node.is_pruned = True
        return node, node_id_counter

    # Generate child nodes
    num_children = 2  # For simplicity, each node has 2 children
    for _ in range(num_children):
        child, node_id_counter = build_tree(depth + 1, max_depth, node_id_counter, killer_moves, parent=node)
        if child:
            node.children.append(child)

    return node, node_id_counter

def visualize_tree(root):
    dot = Digraph(comment='Killer Heuristic Tree')

    def add_nodes_edges(node):
        # Set node label with alpha and beta values
        label = f'{node.name}\\nα={node.alpha}, β={node.beta}'
        if node.is_pruned:
            label += '\\nPruned'

        # Determine node color
        if node.is_pruned:
            color = 'gray'
            style = 'dashed'
        elif node.is_killer_move:
            color = 'red'
            style = 'bold'
        else:
            color = 'black'
            style = 'solid'

        dot.node(node.name, label=label, color=color, style=style)

        for child in node.children:
            add_nodes_edges(child)
            dot.edge(node.name, child.name, color=color, style=style)

    add_nodes_edges(root)
    dot.render('killer_heuristic_tree', view=True, format='png')

def main():
    max_depth = 3
    killer_moves = {
        1: 'Node1',
        2: 'Node3'
    }
    root, _ = build_tree(depth=0, max_depth=max_depth, node_id_counter=0, killer_moves=killer_moves)
    visualize_tree(root)

if __name__ == '__main__':
    main()
