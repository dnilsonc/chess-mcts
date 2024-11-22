import chess
import chess.pgn
from classNode import Node
from monte_carlo import monte_carlo_tree_search

def play_game():

    board = chess.Board()
    initial_fen =  "k5n1/2Q5/8/1p3B2/4P3/4K1P1/PP5r/2R4q w - - 3 36"

    board.set_fen(initial_fen)

    print(board)
    move_history = []

    game = chess.pgn.Game()
    game.headers["Event"] = "Test"
    game.headers["White"] = "MCTS"
    game.headers["Black"] = "MCTS"
    game.headers["SetUp"] = "1"
    game.headers["FEN"] = initial_fen

    root = Node(board)
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            root, move = monte_carlo_tree_search(root, 3000, 10)
            print(f"Player WHITE move: {board.san(move)}")
        else:
            root, move = monte_carlo_tree_search(root, 3000, 10)
            print(f"Player BLACK move: {board.san(move)}")

        move_history.append(board.san(move))
        board.push(move)

        if board.is_checkmate():
            print(f'Player {"WHITE" if board.turn == chess.BLACK else "BLACK"} Wins!')
            game.headers["Result"] = board.result()
            break
        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            print('Draw!')
            game.headers["Result"] = board.result()
            break
    
    node = game
    board = chess.Board()  # Resetar o tabuleiro para a posição inicial
    board.set_fen(initial_fen)  # Redefinir a posição inicial

    for move in move_history:
        move = board.parse_san(move)  # Converter SAN para objeto Move
        node = node.add_main_variation(move)
        board.push(move)  # Atualizar o tabuleiro com o movimento

    # Imprimir o histórico de movimentos
    print("\nHistórico de movimentos:")
    print(game)

if __name__ == "__main__":
    play_game()