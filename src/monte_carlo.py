import math
import random
import multiprocessing
from typing import Optional, Tuple

import chess

from classNode import Node


C_PUCT = math.sqrt(2)

# Piece values for the rollout material evaluation (White's perspective).
_PIECE_VALUES = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.0,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0,
}

# Scale that maps a typical decisive material edge to a strong signal in [-1, 1].
# ~10 points (queen-ish advantage) saturates the heuristic, so a free knight (~3) reads as a clear plus.
_MATERIAL_SCALE = 10.0


def _terminal_reward(board: chess.Board) -> float:
    """Reward from White's perspective for a finished game."""
    result = board.result(claim_draw=True)
    if result == '1-0':
        return 1.0
    if result == '0-1':
        return -1.0
    return 0.0


def _material_eval(board: chess.Board) -> float:
    """Normalized material balance in [-1, 1] from White's perspective."""
    score = 0.0
    for piece_type, value in _PIECE_VALUES.items():
        score += value * len(board.pieces(piece_type, chess.WHITE))
        score -= value * len(board.pieces(piece_type, chess.BLACK))
    return max(-1.0, min(1.0, score / _MATERIAL_SCALE))


def uct(node: Node) -> float:
    if node.visits == 0:
        return float('inf')
    if node.parent is None:
        return node.value / node.visits
    # Q is negated: a child's stored value is from the opponent's perspective
    # relative to the parent that is choosing among its children.
    exploitation = -node.value / node.visits
    exploration = C_PUCT * math.sqrt(math.log(node.parent.visits) / node.visits)
    return exploitation + exploration


def selection(node: Node) -> Node:
    while not node.is_terminal() and node.is_fully_expanded():
        if not node.children:
            return node
        node = max(node.children, key=uct)
    return node


def expansion(node: Node) -> Node:
    if node.is_terminal():
        return node
    leaf = node.expand()
    return leaf if leaf is not None else node


def simulation(node: Node, max_depth: int = 40) -> float:
    """Random playout with depth cutoff and material fallback. Returns reward in [-1, 1] (White's POV)."""
    board = node.board.copy(stack=False)
    depth = 0
    while not board.is_game_over(claim_draw=True) and depth < max_depth:
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(random.choice(moves))
        depth += 1

    if board.is_game_over(claim_draw=True):
        return _terminal_reward(board)
    return _material_eval(board)


def backpropagation(reward: float, node: Node) -> None:
    node.update(reward)


def best_child(root: Node) -> Node:
    # Most-visited child is the standard, more robust choice than mean value.
    return max(root.children, key=lambda c: c.visits)


def _run_simulations(root: Node, n_simulations: int) -> None:
    for _ in range(n_simulations):
        leaf = selection(root)
        node = expansion(leaf)
        reward = simulation(node)
        backpropagation(reward, node)


def _mcts_worker(args):
    root, n_simulations, seed = args
    random.seed(seed)
    _run_simulations(root, n_simulations)
    return root


def _merge_trees(main: Node, other: Node) -> None:
    """Recursively merge `other` into `main`. Both must represent the same board state."""
    main.visits += other.visits
    main.value += other.value

    main_by_move = {c.from_move: c for c in main.children}
    for other_child in other.children:
        existing = main_by_move.get(other_child.from_move)
        if existing is not None:
            _merge_trees(existing, other_child)
        else:
            other_child.parent = main
            main.children.append(other_child)
            main_by_move[other_child.from_move] = other_child
            # If main had this move queued as untried, remove it.
            if main._untried_moves is not None:
                try:
                    main._untried_moves.remove(other_child.from_move)
                except ValueError:
                    pass


def monte_carlo_tree_search(
    root: Node,
    n_simulations: int,
    n_processes: int = 1,
) -> Tuple[Node, Optional[chess.Move]]:
    # Detach the root from any stale ancestor tree so backprop and deepcopies stay bounded.
    root.parent = None

    if n_processes <= 1:
        _run_simulations(root, n_simulations)
    else:
        simulations_per_process = max(1, n_simulations // n_processes)
        args = [(root, simulations_per_process, random.randint(0, 2**31 - 1)) for _ in range(n_processes)]
        with multiprocessing.Pool(processes=n_processes) as pool:
            results = pool.map(_mcts_worker, args)
        for temp_root in results:
            _merge_trees(root, temp_root)

    if not root.children:
        return root, None

    best = best_child(root)
    return best, best.from_move
