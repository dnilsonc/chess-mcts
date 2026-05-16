import random
import chess
from typing import Optional, List


class Node:
    def __init__(self, board: chess.Board, parent: Optional['Node'] = None, from_move: Optional[chess.Move] = None):
        self.board = board
        self.parent = parent
        self.from_move = from_move
        self.children: List['Node'] = []
        self.visits = 0
        self.value = 0.0
        self._untried_moves: Optional[List[chess.Move]] = None

    def _ensure_untried(self) -> List[chess.Move]:
        if self._untried_moves is None:
            self._untried_moves = list(self.board.legal_moves)
            random.shuffle(self._untried_moves)
        return self._untried_moves

    def is_fully_expanded(self) -> bool:
        return not self._ensure_untried()

    def is_terminal(self) -> bool:
        return self.board.is_game_over()

    @property
    def rating(self) -> float:
        return self.value / self.visits if self.visits else 0.0

    def update(self, reward: float) -> None:
        # reward is from White's perspective: +1 White wins, -1 Black wins, 0 draw.
        # Each node stores value from the perspective of the side to move at the node.
        self.visits += 1
        self.value += reward if self.board.turn == chess.WHITE else -reward
        if self.parent is not None:
            self.parent.update(reward)

    def expand(self) -> Optional['Node']:
        untried = self._ensure_untried()
        if not untried:
            return None
        move = untried.pop()
        new_board = self.board.copy(stack=False)
        new_board.push(move)
        leaf = Node(new_board, parent=self, from_move=move)
        self.children.append(leaf)
        return leaf
