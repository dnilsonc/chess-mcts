import random
import chess
import copy
from typing import Optional, List

class Node:
    def __init__(self, board: chess.Board, parent: Optional['Node'] = None, from_move: Optional[chess.Move] = None):
        self.board = board
        self.parent = parent
        self.from_move = from_move
        self.children: List['Node'] = []
        self.visits = 0
        self.value = 0
        self.used_moves = set()  # Rastreamento dos movimentos já usados

    def is_fully_expanded(self) -> bool:
        return len(self.children) == len(list(self.board.legal_moves))

    def update(self, reward: int):
        self.visits += 1
        if self.board.turn == chess.WHITE and reward == 1:
            self.value += 1
        elif self.board.turn == chess.BLACK and reward == -1:
            self.value += 1
        elif reward == 0.5:
            self.value += reward
        if self.parent:
            self.parent.update(reward)

    def expand(self) -> Optional['Node']:
        legal_moves = list(self.board.legal_moves)
        available_moves = [move for move in legal_moves if move not in self.used_moves]
        if available_moves:
            move = random.choice(available_moves)
            self.used_moves.add(move)  # Marcar o movimento como usado
            available_moves.remove(move)
            new_board = copy.deepcopy(self.board)
            new_board.push(move)
            leaf = Node(new_board, parent=self, from_move=move)
            self.children.append(leaf)
        else:
            pass