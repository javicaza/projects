#!/usr/bin/env python3
# coding : utf-8

from flask import Flask, Response, request, render_template, url_for
import chess, chess.pgn
import chess.engine
import traceback
import time
import collections
import json
from gevent.pywsgi import WSGIServer
import copy
import json
import sys
import os


options = {"Stockfish": r"C:\Users\Usuario\Desktop\TFG\CHESS\flask-chess-platform\CHESS-ENGINES\stockfish_14.1_win_x64_popcnt.exe",
# 3538
"Komodo" :r"C:\Users\Usuario\Desktop\TFG\CHESS\flask-chess-platform\CHESS-ENGINES\komodo-13.02-64bit.exe",
# 3408
"Alichess": r"C:\Users\Usuario\Desktop\TFG\CHESS\flask-chess-platform\CHESS-ENGINES\AliUCI425.exe",
# 2283
"Movei" : r"C:\Users\Usuario\Desktop\TFG\CHESS\flask-chess-platform\CHESS-ENGINES\Movei v0.08.438.exe"
# 2666
}


class Player(object):
    def __init__(self, board, game_time=300):
        self.__current_board = board

    def make_move(self, move):
        raise NotImplementedError()

class Player1(Player):
    def __init__(self, board, game_time=300):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None

    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == True:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's Blacks Turn (Player2)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == True

    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None

class Player2(Player):
    def __init__(self, board, game_time=300):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None
        self.chosen_engine = False
        
    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == False:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's White's Turn (Player1)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == False

    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None

    def init_stockfish(self,choice):
        self.__is_engine = True
        try:
            self.__engine = chess.engine.SimpleEngine.popen_uci(choice)
            return True
        except Exception:
            return False

    def is_engine(self):
        return self.__engine

    def engine_move(self):
        result = self.__engine.play(self.__current_board, chess.engine.Limit(time=0.100))
        move = result.move
        try:
            self.__current_board.push(move)
        except Exception:
            print("Cant push move")
        return self.__current_board

def board_to_game(board):
    game = chess.pgn.Game()

    # undo all moves
    switchyard = collections.deque()
    while board.move_stack:
        switchyard.append(board.pop())

    game.setup(board)
    node = game

    # Replay all moves
    while switchyard:
        move = switchyard.pop()
        node = node.add_variation(move)
        board.push(move)

    game.headers["Result"] = board.result()
    return game

def console_demo():
    global board
    board = chess.Board()
    p1 = Player1(board)
    p2 = Player2(board)
    print(board)
    print("------------------------------------------")

    while True:
        move_san = input('White move: ').strip()
        board = p1.make_move(move_san)
        print(board)
        print('-'*50)
        move_san = input('Black to move: ').strip()
        board = p2.make_move(move_san)
        print(board)
        print("-"*50)


def run_game():
    global board
    global undo_moves_stack
    undo_moves_stack = []
    board = chess.Board()
    Human  = Player1(board)
    Human2 = Player2(board)

    app = Flask(__name__, static_url_path='')
    @app.route('/', methods=['GET'])
    def index():
        global board
        return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))
    

    questions = []
    answer = []
    @app.route('/', methods=['GET', 'POST'])
    def basic():
        if request.method == 'POST':
            if request.form:
                questions.append(list(request.form.listvalues())[0][0])
                print("The selected option is ",questions)
                Human2.init_stockfish(options[questions[len(questions)-1]])
        return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))

    @app.route('/restart', methods=['GET', 'POST'])
    def restart():
        global board
        while board.move_stack:
            print("current move_stack",board.move_stack)
            board.pop()
            print("after board.pop",board.move_stack)
        
        print("Is this ", str(board_to_game(board).mainline_moves()))
        return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))


    @app.route('/form', methods=['GET', 'POST'])
    def basic2():
        if request.method == 'POST':
            if request.form:
                answer.append(list(request.form.listvalues())[0][0])
                last_answer = answer[len(answer)-1]
                print("The selected option is ",last_answer)
                if last_answer == "Engine":
                    Human2.init_stockfish(options["Stockfish"])
                    Human2.chosen_engine = True
                    return render_template('extend.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))
                else:
                    Human2.chosen_engine = False
                    return render_template('index.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()))


    @app.route('/move', methods=['GET'])
    def move():
        global board
        global undo_moves_stack
        if not board.is_game_over():
            move_san = request.args.get('move', default='')
            if move_san is not None and move_san != '':
                try:
                    if Human.is_turn():
                        print("White's turn to play:")
                    else:
                        print("Black's turn to play")
                    if Human.is_turn():
                
                        board = Human.make_move(str(move_san))
                        print("Is this 2", str(board_to_game(board).mainline_moves()))
                        undo_moves_stack = [] #make undo moves stack empty if any move is done.

                        squares = [] # Casillas libres (sin ataque por oponente)
                        squares2 = [] # Casillas con ataque del oponente
                        squares20 = [] # Piezas oponentes atacadas y número de atacantes
                        squares19 = [] # Piezas propias atacadas y número de atacantes
                        squares3 = [] # Casillas debiles del oponente (sin defensa de peon)
                        squares9 = [] # Piezas atacadas en doble movimiento de caballo propio
                        squares10 = [] # Movimiento de caballo propio sin defensa
                        squares12 = [] # Piezas oponente que no estan defendidas
                        squares17 = [] # Piezas oponente que no estan atacadas
                        squares5 = [] # Posible clavada en sig jugada de blanca (propia)
                        squares6 = [] # Posible jaque en siguiente jugada propia
                        squares16 = [] # Piezas propias que no estan atacadas
                        squares13 = [] # Piezas propias que no estan defendidas
                        squares11 = [] # Movimiento de caballo negro sin defensa
                        squares8 = [] # Piezas atacadas en doble movimiento de caballo oponente
                        squares7 = [] # Posible jaque en siguiente jugada del rival
                        squares4 = [] # Posible clavada en sig jugada de negra (oponente)
                        number_of_attackers = []
                        number_of_attackers2 = []

                    if Human2.is_turn():
                        if Human2.chosen_engine == False:
                            move_san = request.args.get('move', default='')
                            #####################################################################################################################                             
                            board = Human2.make_move(str(move_san))
                            #####################################################################################################################
                        if Human2.chosen_engine == True:
                             board = Human2.engine_move()
                        
                        board2 = copy.copy(board)
                        board2.turn = chess.BLACK

####################################################################################################################                            
                        print(" \n Movimiento de caballo negro sin defensa")
                        squares11 = []
                        knight_moves = []

                        board2 = copy.copy(board)
                        board2.turn = chess.BLACK

                        legal_moves = list(board2.legal_moves)
                        for i in legal_moves:
                            move = str(i)
                            original_square = move[0:2]
                            piece = str(board.piece_at(getattr(chess, original_square.upper())))
                            if piece == "n":
                                knight_moves.append(move)
                            
                        squares_reached = []
                        for i in knight_moves:
                            move = str(i)
                            final_square = move[2:4]
                            squares_reached.append(final_square)

                        for i in squares_reached:
                            if board.is_attacked_by(chess.WHITE,getattr(chess, i.upper())) == False:
                                squares11.append(i)
                        squares11 = list(set(squares11))
                        print(squares11)
#####################################################################################################################
                        print("\n Piezas atacadas en doble movimiento de caballo oponente")

                        squares8 = []
                        knight_moves = []
                        knight_moves2 = []
                        knight_moved_to = []

                        board2 = copy.copy(board)
                        board2.turn = chess.BLACK

                        legal_moves = list(board2.legal_moves)
                        for i in legal_moves:
                            move = str(i)
                            original_square = move[0:2]
                            piece = str(board2.piece_at(getattr(chess, original_square.upper())))
                            if piece == "n":
                                knight_moves.append(move)

                        for j in knight_moves:
                            board3 = copy.copy(board2)
                            move2 = chess.Move.from_uci(str(j))
                            board3.push(move2)

                            board3.turn = chess.BLACK

                            # squares where knights end up after being moved once 
                            move_made = str(j)
                            final_square = move_made[2:4]
                            knight_moved_to.append(final_square)

                            # once it is black's turn we can move black knights again
                            legal_moves2 = list(board3.legal_moves)

                            for i in legal_moves2:
                                move = str(i)
                                original_square = move[0:2]
                                if original_square in knight_moved_to:
                                    knight_moves2.append(move)

                            squares_reached = []
                            for i in knight_moves2:
                                move = str(i)
                                final_square = move[2:4]
                                squares_reached.append(final_square)

                        squares_reached = list(set(squares_reached))

                        # we now have to check whether there is a piece on the squares reached by the knights after
                        # two moves.
                            
                        for i in squares_reached:
                            piece = str(board.piece_at(getattr(chess, i.upper())))
                            if piece.isupper():
                                squares8.append(i)

                        print("Knights after 1 move: ",knight_moves)
                        print("Knights after 2 moves: ",knight_moves2)
                        print("Squares reached after 2 knight moves: ",squares_reached)
                        print("Squares reached with a white's piece: ",squares8)
#####################################################################################################################
                        print("\n Posible jaque en siguiente jugada del rival")

                        squares7 = []

                        board2 = copy.copy(board)
                        board2.turn = chess.BLACK

                        legal_moves = list(board2.legal_moves)
                        for i in legal_moves:
                            board3 = copy.copy(board2)
                            move = chess.Move.from_uci(str(i))
                            board3.push(move)
                            if board3.is_check():
                                move_made = str(i)
                                check = []
                                already_exists = False
                                index = 0

                                for h in range(len(squares7)):
                                    if move_made[0:2] == squares7[h][0]:
                                        already_exists = True
                                        index = h

                                if already_exists:
                                    squares7[index].append(move_made[2:4])
                                else:
                                    check.append(move_made[0:2])
                                    check.append(move_made[2:4])
                                    squares7.append(check)
                        if board.is_check():
                            squares7 = []
                            
                        print(squares7)

#####################################################################################################################
                            
                        print("\n Posible clavada en sig jugada de negra (oponente)")
                        print("Cada lista dentro de la lista principal corresponde a una posible clavada diferente")
                        print("El primer término es el cuadrado que quedaría clavado, el segundo la direccion de la clavada, el tecero el cuadrado inicial de la pieza movida por negras y el cuarto, el cuadrado final de la pieza movida por negras")
                        squares4 = []
                        already_pinned = []

                        for j in chess.SQUARES:
                                if board.is_pinned(chess.WHITE,j):
                                    already_pinned.append(j)

                        board2 = copy.copy(board)
                        board2.turn = chess.BLACK

                        legal_moves = list(board2.legal_moves)
                        for i in legal_moves:
                            board3 = copy.copy(board2)
                            move = chess.Move.from_uci(str(i))
                            board3.push(move)  # Make the move
                            for j in chess.SQUARES:
                                if board3.is_pinned(chess.WHITE,j):
                                    if j not in already_pinned:
                                        piece = str(board.piece_at(j))
                                        if piece != "None" and piece.isupper():
                                            pin = []
                                            move_made = str(i)

                                            already_exists = False
                                            index = 0
                                            for h in range(len(squares4)):
                                                if move_made[0:2] == squares4[h][0]:
                                                    already_exists = True
                                                    index = h
                                                
                                            if already_exists:
                                                squares4[index].append(chess.square_name(j))
                                                squares4[index].append(move_made[2:4])
                                            else:
                                                pin.append(move_made[0:2])
                                                pin.append(move_made[2:4])
                                                pin.append(chess.square_name(j))
                                                squares4.append(pin)
                        print(squares4)


####################################################################################################################
                            
                        print("\n Piezas propias que no estan atacadas")
                        squares16 = []

                        squares_with_white_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.isupper():
                                squares_with_white_pieces.append(chess.square_name(i))

                        squares_attacked_by_black = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == True:
                                squares_attacked_by_black.append(i)

                        for i in squares_with_white_pieces:
                            if i not in squares_attacked_by_black:
                                squares16.append(i)
                        print(squares16)
######################################################################################################################
                            
                        print("\n Piezas propias que no estan defendidas")
                        squares13 = []

                        squares_with_white_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.isupper():
                                squares_with_white_pieces.append(chess.square_name(i))

                        squares_attacked_by_white = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.WHITE,getattr(chess, i.upper())) == True:
                                squares_attacked_by_white.append(i)

                        for i in squares_with_white_pieces:
                            if i not in squares_attacked_by_white:
                                squares13.append(i)
                        print(squares13)
######################################################################################################################                            
                        print("\n Piezas oponentes atacadas y número de atacantes")
                            
                        squares20 = []
                        number_of_attackers = []

                        squares_with_black_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.islower():
                                squares_with_black_pieces.append(chess.square_name(i))

                        squares_attacked_by_white = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.WHITE,getattr(chess, i.upper())) == True:
                                squares_attacked_by_white.append(i)

                        for i in squares_with_black_pieces:
                            if i in squares_attacked_by_white:
                                squares20.append(i)

                        for i in squares20:
                            attackers = len(list(board.attackers(chess.WHITE,getattr(chess, i.upper()))))
                            number_of_attackers.append(attackers)
                        print(squares20)
                        print(number_of_attackers)
#####################################################################################################################
                        print("\n Piezas propias atacadas y número de atacantes")
                        
                        squares19 = []
                        number_of_attackers2 = []

                        squares_with_white_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.isupper():
                                squares_with_white_pieces.append(chess.square_name(i))

                        squares_attacked_by_black = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == True:
                                squares_attacked_by_black.append(i)

                        for i in squares_with_white_pieces:
                            if i in squares_attacked_by_black:
                                squares19.append(i)

                        for i in squares19:
                            attackers = len(list(board.attackers(chess.BLACK,getattr(chess, i.upper()))))
                            number_of_attackers2.append(attackers)
                        print(squares19)
                        print(number_of_attackers2)


######################################################################################################################
                        print("\n Casillas libres (sin ataque por oponente)")
                        squares = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == False:
                                squares.append(i)
                        print(squares)

######################################################################################################################                           
                        print("\n Casillas con ataque del oponente")
                        squares2 = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == True:
                                squares2.append(i)
                        print(squares2)

#######################################################################################################################                            
                        print("\n Casillas debiles del oponente (sin defensa de peon)")
                        squares3 = []
                        squares_with_opponents_pawns = []
                        
                        for i in chess.SQUARE_NAMES:
                            piece = str(board.piece_at(getattr(chess, i.upper())))
                            if piece == "p":
                                squares_with_opponents_pawns.append(i)
                        squares_defended_by_opponents_pawns = []
                        
                        for i in squares_with_opponents_pawns:
                            attacks = list(board.attacks(getattr(chess, i.upper())))
                            for j in attacks:
                                squares_defended_by_opponents_pawns.append(chess.square_name(j))
                
                        for i in chess.SQUARE_NAMES:
                            if i not in squares_defended_by_opponents_pawns:
                                squares3.append(i)
                        print(squares3)
#########################################################################################################################
                        print("\n Posible clavada en sig jugada de blanca (propia)")
                        print("Cada lista dentro de la lista principal corresponde a una posible clavada diferente")
                        print("El primer término es el cuadrado que quedaría clavado, el segundo la direccion de la clavada, el tecero el cuadrado inicial de la pieza movida por negras y el cuarto, el cuadrado final de la pieza movida por negras")
                        squares5 = []
                        already_pinned = []

                        for j in chess.SQUARES:
                            if board.is_pinned(chess.BLACK,j):
                                already_pinned.append(j)

                        legal_moves = list(board.legal_moves)
                        for i in legal_moves:
                            board2 = copy.copy(board)
                            move = chess.Move.from_uci(str(i))
                            board2.push(move)  # Make the move
                            for j in chess.SQUARES:
                                if board2.is_pinned(chess.BLACK,j):
                                    if j not in already_pinned:
                                        piece = str(board.piece_at(j))
                                        if piece != "None" and piece.islower():
                                            pin = []
                                            move_made = str(i)

                                            already_exists = False
                                            index = 0
                                            for h in range(len(squares5)):
                                                if move_made[0:2] == squares5[h][0]:
                                                    already_exists = True
                                                    index = h
                                                
                                            if already_exists:
                                                squares5[index].append(chess.square_name(j))
                                                squares5[index].append(move_made[2:4])
                                            else:
                                                pin.append(move_made[0:2])
                                                pin.append(move_made[2:4])
                                                pin.append(chess.square_name(j))
                                                squares5.append(pin)
                        print(squares5)
########################################################################################################################
                        print("\n Posible jaque en siguiente jugada propia")

                        squares6 = []
                        legal_moves = list(board.legal_moves)
                        for i in legal_moves:
                            board2 = copy.copy(board)
                            move = chess.Move.from_uci(str(i))
                            board2.push(move)
                            if board2.is_check():
                                move_made = str(i)
                                check = []
                                already_exists = False
                                index = 0
                                        
                                for h in range(len(squares6)):
                                    if move_made[0:2] == squares6[h][0]:
                                        already_exists = True
                                        index = h
                                                
                                if already_exists:
                                    squares6[index].append(move_made[2:4])
                                else:
                                    check.append(move_made[0:2])
                                    check.append(move_made[2:4])
                                    squares6.append(check)
                        if board.is_check():
                            squares6 = []
                        print(squares6)
#############################################################################################################################
                        print("\n Piezas atacadas en doble movimiento de caballo propio")

                        squares9 = []
                        knight_moves = []
                        knight_moves2 = []
                        knight_moved_to = []

                        legal_moves = list(board.legal_moves)
                        for i in legal_moves:
                            move = str(i)
                            original_square = move[0:2]
                            piece = str(board.piece_at(getattr(chess, original_square.upper())))
                            if piece == "N":
                                knight_moves.append(move)

                        for j in knight_moves:
                            board2 = copy.copy(board)
                            move2 = chess.Move.from_uci(str(j))
                            board2.push(move2)

                            black_legal_moves = list(board2.legal_moves)
                            # make a random move for black
                            # this is done to  be able to move a white knight again
                            random_black_move = chess.Move.from_uci(str(black_legal_moves[0]))
                            board2.push(random_black_move)

                            # squares where knights end up after being moved once 
                            move_made = str(j)
                            final_square = move_made[2:4]
                            knight_moved_to.append(final_square)

                            # once it is white's turn we can move white's knights again
                            legal_moves2 = list(board2.legal_moves)

                            for i in legal_moves2:
                                move = str(i)
                                original_square = move[0:2]
                                if original_square in knight_moved_to:
                                    knight_moves2.append(move)

                            squares_reached = []
                            for i in knight_moves2:
                                move = str(i)
                                final_square = move[2:4]
                                squares_reached.append(final_square)

                        squares_reached = list(set(squares_reached))

                        # we now have to check whether there is a piece on the squares reached by the knights after
                        # two moves.
                            
                        for i in squares_reached:
                            piece = str(board.piece_at(getattr(chess, i.upper())))
                            if piece.islower():
                                squares9.append(i)

                        print("Knights after 1 move: ",knight_moves)
                        print("Knights after 2 moves: ",knight_moves2)
                        print("Squares reached after 2 knight moves: ",squares_reached)
                        print("Squares reached with a black's piece: ",squares9)

#########################################################################################################################
                        print(" \n Movimiento de caballo propio sin defensa")
                        squares10 = []
                        knight_moves = []

                        legal_moves = list(board.legal_moves)
                        for i in legal_moves:
                            move = str(i)
                            original_square = move[0:2]
                            piece = str(board.piece_at(getattr(chess, original_square.upper())))
                            if piece == "N":
                                knight_moves.append(move)
                        
                        squares_reached = []
                        for i in knight_moves:
                            move = str(i)
                            final_square = move[2:4]
                            squares_reached.append(final_square)

                        for i in squares_reached:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == False:
                                squares10.append(i)
                        squares10 = list(set(squares10))
                        print(squares10)

#########################################################################################################################
                        print("\n Piezas oponente que no estan defendidas")
                        squares12 = []

                        squares_with_black_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.islower():
                                squares_with_black_pieces.append(chess.square_name(i))

                        squares_attacked_by_black = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.BLACK,getattr(chess, i.upper())) == True:
                                squares_attacked_by_black.append(i)

                        for i in squares_with_black_pieces:
                            if i not in squares_attacked_by_black:
                                squares12.append(i)
                        print(squares12)

#####################################################################################################################
                        print("\n Piezas oponente que no estan atacadas")
                        squares17 = []

                        squares_with_black_pieces = []
                        for i in chess.SQUARES:
                            piece = str(board.piece_at(i))
                            if piece.islower():
                                squares_with_black_pieces.append(chess.square_name(i))

                        squares_attacked_by_white = []
                        for i in chess.SQUARE_NAMES:
                            if board.is_attacked_by(chess.WHITE,getattr(chess, i.upper())) == True:
                                squares_attacked_by_white.append(i)

                        for i in squares_with_black_pieces:
                            if i not in squares_attacked_by_white:
                                squares17.append(i)
                        print(squares17)

#########################################################################################################################

                    print("This is the board")        
                    print(board)
                except Exception:
                    traceback.print_exc()
                game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
                print(game_moves_san)
                if board.is_game_over():
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true', 'squares': squares, 'squares2':squares2,'squares20':squares20, 'squares19':squares19,'squares3':squares3,'squares9':squares9,'squares10':squares10,'squares12':squares12,'squares17':squares17,'squares5':squares5,'squares6':squares6,'squares16':squares16,'squares13':squares13,'squares11':squares11,'squares8':squares8,'squares7':squares7,'squares4':squares4,'number_of_attackers':number_of_attackers,'number_of_attackers2':number_of_attackers2}
                else:
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'false', 'squares': squares, 'squares2': squares2,'squares20':squares20, 'squares19':squares19,'squares3':squares3,'squares9':squares9,'squares10':squares10,'squares12':squares12,'squares17':squares17,'squares5':squares5,'squares6':squares6,'squares16':squares16,'squares13':squares13,'squares11':squares11,'squares8':squares8,'squares7':squares7,'squares4':squares4,'number_of_attackers':number_of_attackers,'number_of_attackers2':number_of_attackers2}
                response = app.response_class(
                    response=json.dumps(resp),
                    status=200,
                    mimetype='application/json'
                )
                return response
        else:
            game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
            print(game_moves_san)
            resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true', 'squares': squares, 'squares2':squares2,'squares20':squares20,'squares19':squares19,'squares3':squares3,'squares9':squares9,'squares10':squares10,'squares12':squares12,'squares17':squares17,'squares5':squares5,'squares6':squares6,'squares16':squares16,'squares13':squares13,'squares11':squares11,'squares8':squares8,'squares7':squares7,'squares4':squares4,'number_of_attackers':number_of_attackers,'number_of_attackers2':number_of_attackers2}
            response = app.response_class(
                response=json.dumps(resp),
                status=200,
                mimetype='application/json'
            )
            return response
        return index()

    #http_server = WSGIServer(('0.0.0.0', 1337), app)
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
    #app.run(host='127.0.0.1', debug=True)

if __name__ == "__main__":
    #console_demo()
    run_game()