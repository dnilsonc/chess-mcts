import copy
import math
import random
from classNode import Node

def uct(node: Node) -> float:
    # UCT formula: Q + C * sqrt(ln(N) / n)
    if node.visits == 0:
        return float('inf')
    C = 1.414  # Exploração constante, ajustável
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
        reward = 0
    return reward

def backpropagation(reward: int, node: Node) -> None:
    node.update(reward)

def best_child(root: Node, player: bool) -> Node:
    best_child = random.choice(root.children)
    best_visits = 0
       
    if root.board.turn == chess.WHITE:
        best_avaliation = -float('inf')        
        for child in root.children:
            avaliation = child.value / child.visits
            if avaliation > best_avaliation:
                best_avaliation = avaliation
                best_child = child
    else:
        best_avaliation = float('inf')        
        for child in root.children:
            avaliation = child.value / child.visits
            if avaliation < best_avaliation:
                best_avaliation = avaliation
                best_child = child

        # if child.visits > best_visits:
        #     best_visits = child.visits
        #     best_child = child
    return best_child

# def mcts(board: chess.Board, n_simulations: int, player: bool) -> Optional[chess.Move]:
#     root = Node(board)  # Inicialize a raiz da árvore fora do loop

    
#     for _ in range(n_simulations):
#         leaf = selection(root)  # Seleciona
#         node = expansion(leaf)  # Expande
#         reward = simulation(node)  # Simula
#         backpropagation(reward, node)  # Retropropaga

    
#     best = best_child(root, player)
#     move = best.from_move
#     return move

import threading
from typing import Optional
import chess  # Certifique-se de que a biblioteca python-chess está instalada

# Suponha que a estrutura Node e as funções selection, expansion, simulation e backpropagation já estejam definidas
# Vou usar um Lock global para sincronizar o acesso à árvore MCTS
lock = threading.Lock()

def mcts_worker(root, n_simulations, player):
    """Função que cada thread vai executar, responsável por realizar simulações."""
    for _ in range(n_simulations):
        # Seleção
        with lock:  # Protege o acesso à árvore para evitar concorrência no Node
            leaf = selection(root)  # Seleciona um nó folha a partir da raiz
            
        # Expansão
        node = expansion(leaf)  # Expande o nó selecionado

        # Simulação
        reward = simulation(node)  # Simula o resultado

        # Retropropagação
        with lock:  # Protege o acesso à árvore durante a retropropagação
            backpropagation(reward, node)  # Retropropaga o resultado

def mcts(board: chess.Board, n_simulations: int, player: bool, n_threads: int = 4) -> Optional[chess.Move]:
    root = Node(board)  # Inicializa a raiz da árvore

    # Define o número de simulações por thread
    simulations_per_thread = n_simulations // n_threads

    # Cria e inicia as threads
    threads = []
    for _ in range(n_threads):
        thread = threading.Thread(target=mcts_worker, args=(root, simulations_per_thread, player))
        thread.start()
        threads.append(thread)

    # Espera todas as threads terminarem
    for thread in threads:
        thread.join()

    # Seleciona o melhor movimento após todas as simulações
    best = best_child(root, player)
    move = best.from_move
    return move
