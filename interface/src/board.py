from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os


class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        """Déplace une pièce sur l'échiquier."""
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # Mise à jour de l'échiquier
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # Gestion des pions (en passant et promotion)
        if isinstance(piece, Pawn):
            # Capture en passant
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()

            # Promotion
            self.check_promotion(piece, final)

        # Gestion du roque
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # Mise à jour des propriétés de la pièce
        piece.moved = True
        piece.clear_moves()

        # Enregistrement du dernier mouvement
        self.last_move = move

    def valid_move(self, piece, move):
        """Vérifie si un mouvement est valide."""
        return move in piece.moves

    def check_promotion(self, piece, final):
        """Gère la promotion des pions."""
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        """Vérifie si un mouvement est un roque."""
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        """Met à jour l'état de prise en passant pour tous les pions."""
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

    def in_check(self, color):
        """Vérifie si le roi de la couleur donnée est en échec."""
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_enemy_piece(color):
                    enemy_piece = self.squares[row][col].piece
                    self.calc_moves(enemy_piece, row, col, bool=False)
                    for move in enemy_piece.moves:
                        if isinstance(move.final.piece, King) and move.final.piece.color == color:
                            return True
        return False

    def calc_moves(self, piece, row, col, bool=True):
        """Calcule tous les mouvements possibles pour une pièce."""
        def simulate_move(piece, move):
            """Simule un mouvement pour vérifier s'il met le roi en échec."""
            temp_board = copy.deepcopy(self)
            temp_piece = copy.deepcopy(piece)
            temp_board.move(temp_piece, move, testing=True)
            return not temp_board.in_check(piece.color)

        def pawn_moves():
            # Déplacement de base
            steps = 1 if piece.moved else 2
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row) and self.squares[possible_move_row][col].isempty():
                    move = Move(Square(row, col), Square(possible_move_row, col))
                    if bool and simulate_move(piece, move):
                        piece.add_move(move)
                else:
                    break

            # Captures diagonales
            for delta_col in [-1, 1]:
                possible_move_col = col + delta_col
                possible_move_row = row + piece.dir
                if Square.in_range(possible_move_row, possible_move_col):
                    target_square = self.squares[possible_move_row][possible_move_col]
                    if target_square.has_enemy_piece(piece.color):
                        move = Move(Square(row, col), Square(possible_move_row, possible_move_col, target_square.piece))
                        if bool and simulate_move(piece, move):
                            piece.add_move(move)

            # Prise en passant
            if row == (3 if piece.color == 'white' else 4):
                for delta_col in [-1, 1]:
                    possible_move_col = col + delta_col
                    if Square.in_range(possible_move_col):
                        adjacent_square = self.squares[row][possible_move_col]
                        if adjacent_square.has_enemy_piece(piece.color):
                            adjacent_piece = adjacent_square.piece
                            if isinstance(adjacent_piece, Pawn) and adjacent_piece.en_passant:
                                move = Move(Square(row, col), Square(row + piece.dir, possible_move_col, adjacent_piece))
                                if bool and simulate_move(piece, move):
                                    piece.add_move(move)

        def knight_moves():
            # Tous les mouvements possibles du cavalier
            deltas = [
                (-2, 1), (-1, 2), (1, 2), (2, 1),
                (2, -1), (1, -2), (-1, -2), (-2, -1)
            ]
            for delta_row, delta_col in deltas:
                possible_row, possible_col = row + delta_row, col + delta_col
                if Square.in_range(possible_row, possible_col):
                    target_square = self.squares[possible_row][possible_col]
                    if target_square.isempty_or_enemy(piece.color):
                        move = Move(Square(row, col), Square(possible_row, possible_col, target_square.piece))
                        if bool and simulate_move(piece, move):
                            piece.add_move(move)

        def straightline_moves(directions):
            # Pour les tours, fous, et dame
            for delta_row, delta_col in directions:
                current_row, current_col = row + delta_row, col + delta_col
                while Square.in_range(current_row, current_col):
                    target_square = self.squares[current_row][current_col]
                    move = Move(Square(row, col), Square(current_row, current_col, target_square.piece))
                    if target_square.isempty():
                        if bool and simulate_move(piece, move):
                            piece.add_move(move)
                    elif target_square.has_enemy_piece(piece.color):
                        if bool and simulate_move(piece, move):
                            piece.add_move(move)
                        break
                    else:
                        break
                    current_row += delta_row
                    current_col += delta_col

        def king_moves():
            # Mouvements du roi
            deltas = [
                (-1, 0), (-1, 1), (0, 1), (1, 1),
                (1, 0), (1, -1), (0, -1), (-1, -1)
            ]
            for delta_row, delta_col in deltas:
                possible_row, possible_col = row + delta_row, col + delta_col
                if Square.in_range(possible_row, possible_col):
                    target_square = self.squares[possible_row][possible_col]
                    move = Move(Square(row, col), Square(possible_row, possible_col, target_square.piece))
                    if bool and simulate_move(piece, move):
                        piece.add_move(move)

            # Roque
            if not piece.moved:
                for rook, rook_col, castling_col in [(piece.left_rook, 0, 2), (piece.right_rook, 7, 6)]:
                    if rook and not rook.moved:
                        path_clear = all(self.squares[row][col].isempty() for col in range(min(col, rook_col) + 1, max(col, rook_col)))
                        if path_clear:
                            move = Move(Square(row, col), Square(row, castling_col))
                            if bool and simulate_move(piece, move):
                                piece.add_move(move)

        # Exécution des mouvements par type de pièce
        if isinstance(piece, Pawn):
            pawn_moves()
        elif isinstance(piece, Knight):
            knight_moves()
        elif isinstance(piece, Bishop):
            straightline_moves([(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif isinstance(piece, Rook):
            straightline_moves([(-1, 0), (0, 1), (1, 0), (0, -1)])
        elif isinstance(piece, Queen):
            straightline_moves([(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, 1), (1, 0), (0, -1)])
        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        """Crée les cases de l'échiquier."""
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        """Ajoute les pièces pour une couleur."""
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # Pions
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # Cavaliers
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Fous
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Tours
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Reine
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # Roi
        self.squares[row_other][4] = Square(row_other, 4, King(color))