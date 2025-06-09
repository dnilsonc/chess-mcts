import copy
import math
import random
import multiprocessing
from classNode import Node

def uct(node: Node) -> float:
    # UCT formula: Q + C * sqrt(ln(N) / n)
    if node.visits == 0:
        return float('inf')
    C = math.sqrt(2) # Exploração constante, ajustável

    return node.value / node.visits + C * math.sqrt(math.log(node.parent.visits) / node.visits)

def selection(node: Node) -> Node:
    while node.is_fully_expanded():
        if not node.children:  # Verifica se a lista children está vazia
            return node
        node = max(node.children, key=uct)
    return node

def expansion(node: Node) -> Node:
    if not node.is_fully_expanded():
        node.expand()
        children = max(node.children, key=uct)
        return children
    else:
        if node.children:
            children = max(node.children, key=uct)
            return children
        else:
            return node    

def simulation(node: Node) -> int:
    board = copy.deepcopy(node.board)
    while not board.is_game_over():
        legal_moves = list(board.legal_moves)
        move = random.choice(legal_moves)
        board.push(move)
    result = board.result()
    if result == '1-0':
        reward = 1
    elif result == '0-1':
        reward = -1
    else:
        reward = 0.5
    return reward

def backpropagation(reward: int, node: Node) -> None:
    node.update(reward)

def best_child(root: Node) -> Node:
    # best_child = random.choice(root.children)
    # best_avaliation = -float('inf')
    # for child in root.children:
    #     avaliation = 1 - (child.value / child.visits)
    #     if avaliation > best_avaliation:
    #         best_avaliation = avaliation
    #         best_child = child
    best_child = max(root.children, key=lambda x: x.rating)
    return best_child

def mcts_worker(root, n_simulations):
    """
    Função que cada processo vai executar. Ela cria um novo nó raiz baseado no estado do tabuleiro
    e realiza simulações, retornando uma lista de atualizações de valor e visitas para retropropagação.
    """
    root = copy.deepcopy(root)  # Cria uma nova cópia do nó raiz para o processo

    for _ in range(n_simulations):
        leaf = selection(root) 
        node = expansion(leaf)  
        reward = simulation(node) 
        backpropagation(reward, node)

    return root

def merge_trees(main_root, temp_root):
    """
    Função para combinar os resultados das árvores de cada processo na árvore principal.
    """
    main_root.value += temp_root.value
    main_root.visits += temp_root.visits
    
    for child in temp_root.children:
        main_child = next((temp_child for temp_child in main_root.children if temp_child.from_move == child.from_move), None)
        if main_child:
            main_child.visits += child.visits
            main_child.value += child.value
        else:
            main_root.children.append(child)
            main_root.used_moves.add(child.from_move)

def monte_carlo_tree_search(root: Node, n_simulations: int, n_processes: int = 4):
    simulations_per_process = n_simulations
    with multiprocessing.Pool(processes=n_processes) as pool:
        results = pool.starmap(mcts_worker, [(root, simulations_per_process) for _ in range(n_processes)])

    # Combina os resultados das árvores de cada processo na árvore principal
    for temp_root in results:
        merge_trees(root, temp_root)

    # Seleciona o melhor movimento após todas as simulações
    best = best_child(root)
    move = best.from_move
    return best, move