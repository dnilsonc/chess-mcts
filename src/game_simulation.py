import chess
import chess.pgn

from classNode import Node
from monte_carlo import monte_carlo_tree_search


def play_game(initial_fen: str = chess.STARTING_FEN, simulations: int = 3000, processes: int = 1) -> chess.pgn.Game:
    board = chess.Board(initial_fen)
    print(board)

    game = chess.pgn.Game()
    game.headers["Event"] = "Test"
    game.headers["White"] = "MCTS"
    game.headers["Black"] = "MCTS"
    if initial_fen != chess.STARTING_FEN:
        game.headers["SetUp"] = "1"
        game.headers["FEN"] = initial_fen

    move_history = []
    root = Node(board.copy(stack=False))

    while not board.is_game_over(claim_draw=True):
        root, move = monte_carlo_tree_search(root, simulations, processes)
        if move is None:
            break

        side = "WHITE" if board.turn == chess.WHITE else "BLACK"
        san = board.san(move)
        print(f"Player {side} move: {san}")
        move_history.append(san)
        board.push(move)

    if board.is_checkmate():
        winner = "WHITE" if board.turn == chess.BLACK else "BLACK"
        print(f'Player {winner} Wins!')
    else:
        print('Draw!')
    game.headers["Result"] = board.result(claim_draw=True)

    # Rebuild PGN main line from the recorded SAN history.
    node = game
    replay = chess.Board(initial_fen)
    for san in move_history:
        move = replay.parse_san(san)
        node = node.add_main_variation(move)
        replay.push(move)

    print("\nHistórico de movimentos:")
    print(game)
    return game


if __name__ == "__main__":
    play_game()
