import chess
import chess.pgn
from mcts import mcts

def play_game():
    board = chess.Board()
    initial_fen =  "6k1/pp3p2/4p1p1/1PbpP2p/Pq3P2/6P1/2RN2Q1/K4B2 b - - 0 28"

    board.set_fen(initial_fen)

    print(board)
    move_history = []

    # Salvar o histórico dos movimentos em formato PGN
    game = chess.pgn.Game()
    game.headers["Event"] = "Test"
    game.headers["White"] = "MCTS"
    game.headers["Black"] = "MCTS"
    game.headers["SetUp"] = "1"
    game.headers["FEN"] = initial_fen

    # Jogo
    while not board.is_game_over():
        if board.turn == chess.WHITE:
            move = mcts(board, 1500, board.turn, 2)
            print(f"Player WHITE move: {board.san(move)}")
        else:
            move = mcts(board, 6000, board.turn, 10)
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

    # Salvar o histórico dos movimentos em formato PGN
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

play_game()