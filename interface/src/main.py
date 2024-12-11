import pygame
import sys
import importlib.util

from const import *
from game import Game
from square import Square
from move import Move
import chess


# Charger dynamiquement la fonction predict_move depuis test.py
spec = importlib.util.spec_from_file_location(
    "test", "/Users/jasonperez/Desktop/Ing2/NLP2/chessLLM/test.py"
)
test_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_module)
predict_move = test_module.predict_move  # Importer la fonction predict_move

# Définir une nouvelle hauteur pour inclure le champ des mouvements
LOG_PANEL_HEIGHT = 50
WINDOW_HEIGHT = HEIGHT + LOG_PANEL_HEIGHT
SIDE_PANEL_WIDTH = 150
WINDOW_WIDTH = WIDTH + SIDE_PANEL_WIDTH


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.font = pygame.font.Font(None, 24)  # Police pour les boutons et le texte
        self.log = ""  # Texte unique pour les mouvements en notation PGN
        self.move_counter = 1  # Compteur de mouvements
        self.highlight_squares = []  # Stocke les cases à colorier en bleu

        # Boutons
        self.button_reset_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 - 20, 100, 40)  # Bouton RESET
        self.button_print_log_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 - 80, 100, 40)  # Bouton PRINT LOG
        self.button_ai_move_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 + 40, 100, 40)  # Bouton AI MOVE

        # Couleurs des boutons
        self.button_color = (200, 50, 50)  # Rouge
        self.button_hover_color = (255, 100, 100)  # Rouge clair

    def convert_to_standard_algebric(self,input_moves):
        """
        Convertit une séquence de coups en notation longue (e.g., d2d4 e7e5)
        en notation algébrique standard (e.g., d4 e5).

        Args:
            input_moves (str): Une séquence de coups en notation longue (ex: "d2d4 e7e5 d1d3 e5d4").

        Returns:
            str: La séquence de coups convertis en notation algébrique standard.
        """
        # Initialiser un échiquier
        board = chess.Board()

        # Séparer les coups
        moves = input_moves.split()
        standard_moves = []

        for move in moves:
            # Convertir le coup en format UCI
            uci_move = move
            chess_move = chess.Move.from_uci(uci_move)

            if chess_move in board.legal_moves:
                # Convertir en notation algébrique standard
                standard_moves.append(board.san(chess_move))
                # Appliquer le coup sur l'échiquier
                board.push(chess_move)
            else:
                raise ValueError(f"Coup illégal détecté : {uci_move}")

        # Joindre les coups convertis en une chaîne
        return " ".join(standard_moves)

    def draw_side_panel(self):
        """Dessine le panneau latéral et les boutons."""
        # Fond du panneau latéral
        side_panel_color = (40, 40, 40)  # Gris foncé
        pygame.draw.rect(self.screen, side_panel_color, (WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT))

        # Bouton PRINT LOG
        mouse_pos = pygame.mouse.get_pos()
        if self.button_print_log_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, self.button_hover_color, self.button_print_log_rect)
        else:
            pygame.draw.rect(self.screen, self.button_color, self.button_print_log_rect)

        button_print_log_text = self.font.render("PRINT LOG", True, (255, 255, 255))
        self.screen.blit(button_print_log_text, (self.button_print_log_rect.x + 5, self.button_print_log_rect.y + 10))

        # Bouton RESET
        if self.button_reset_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, self.button_hover_color, self.button_reset_rect)
        else:
            pygame.draw.rect(self.screen, self.button_color, self.button_reset_rect)

        button_reset_text = self.font.render("RESET", True, (255, 255, 255))
        self.screen.blit(button_reset_text, (self.button_reset_rect.x + 15, self.button_reset_rect.y + 10))

        # Bouton AI MOVE
        if self.button_ai_move_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, self.button_hover_color, self.button_ai_move_rect)
        else:
            pygame.draw.rect(self.screen, self.button_color, self.button_ai_move_rect)

        button_ai_move_text = self.font.render("AI MOVE", True, (255, 255, 255))
        self.screen.blit(button_ai_move_text, (self.button_ai_move_rect.x + 15, self.button_ai_move_rect.y + 10))

    def draw_log_panel(self):
        """Dessine le panneau des mouvements."""
        # Fond du panneau des mouvements
        log_panel_color = (30, 30, 30)  # Gris encore plus foncé
        pygame.draw.rect(self.screen, log_panel_color, (0, HEIGHT, WINDOW_WIDTH, LOG_PANEL_HEIGHT))

        # Affiche le texte des logs
        log_text = self.font.render(self.log, True, (255, 255, 255))
        self.screen.blit(log_text, (10, HEIGHT + 10))

    def highlight_ai_squares(self):
        """Colorie les cases retournées par l'IA en bleu."""
        for square in self.highlight_squares:
            if square:
                row, col = square
                rect = pygame.Rect(col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(self.screen, (0, 0, 255), rect)

    def update_log(self, move):
        """Met à jour le champ des mouvements avec le dernier mouvement en notation algébrique sans numéros."""
        # Conversion des coordonnées initiales et finales en notation algébrique
        initial = f"{chr(move.initial.col + 97)}{8 - move.initial.row}"  # Exemple: e2
        final = f"{chr(move.final.col + 97)}{8 - move.final.row}"  # Exemple: e4

        # Gestion des captures
        captured_piece = self.game.board.squares[move.final.row][move.final.col].piece
        if captured_piece:
            move_notation = f"{initial}{final}"  # Exemple: e2xe4 pour une capture
        else:
            move_notation = f"{final}"  # Exemple: e4

        # Ajout au log sans numéros de coups
        self.log += f"{move_notation} "

    def reset_log(self):
        """Réinitialise le champ des mouvements."""
        self.log = ""  # Efface les logs

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # Affichage des éléments du jeu
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            # Si un joueur déplace une pièce
            if dragger.dragging:
                dragger.update_blit(screen)

            # Dessin du panneau latéral et des boutons
            self.draw_side_panel()

            # Dessin du panneau des mouvements
            self.draw_log_panel()

            # Colorier les cases suggérées par l'IA
            if self.highlight_squares:
                self.highlight_ai_squares()

            for event in pygame.event.get():
                # Gestion des clics de souris
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    # Vérification si le bouton PRINT LOG est cliqué
                    if self.button_print_log_rect.collidepoint(event.pos):
                        # Convertir la chaîne de log en notation algébrique standard
                        standard_log =  self.log
                        res = self.convert_to_standard_algebric(standard_log)
                        print("ZZZZZZZZZ",res)  # Imprime les logs convertis dans la console

                    # Vérification si le bouton RESET est cliqué
                    elif self.button_reset_rect.collidepoint(event.pos):
                        game.reset()
                        board = game.board
                        dragger = game.dragger
                        self.reset_log()  # Réinitialise le champ des mouvements
                        self.highlight_squares = []  # Réinitialise la coloration des cases

                    # Vérification si le bouton AI MOVE est cliqué
                    elif self.button_ai_move_rect.collidepoint(event.pos):
                        if self.highlight_squares:  # Si des cases sont déjà colorées, on les réinitialise
                            self.highlight_squares = []
                        else:
                            ai_move = predict_move(self.log)  # Appelle la fonction predict_move
                            if len(ai_move) == 4:  # Vérifie si le mouvement est complet (exemple : "e2e4")
                                start_col = ord(ai_move[0]) - 97
                                start_row = 8 - int(ai_move[1])
                                end_col = ord(ai_move[2]) - 97
                                end_row = 8 - int(ai_move[3])
                                self.highlight_squares = [
                                    (start_row, start_col),
                                    (end_row, end_col),
                                ]  # Cases à colorier

                    # Déplacement d'une pièce
                    else:
                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                # Mise à jour de l'affichage
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                                self.highlight_squares = []  # Désactive la couleur des cases AI

                # Gestion du mouvement de la souris
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # Mise à jour de l'affichage
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                # Relâchement du clic de souris
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        if board.valid_move(dragger.piece, move):
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)
                            board.set_true_en_passant(dragger.piece)

                            game.play_sound(captured)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            self.update_log(move)  # Ajoute le mouvement au champ des mouvements
                            game.next_turn()
                            self.highlight_squares = []  # Désactive la couleur des cases AI

                    dragger.undrag_piece()

                # Gestion des touches clavier
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:  # Changer de thème
                        game.change_theme()
                    elif event.key == pygame.K_r:  # Réinitialiser
                        game.reset()
                        board = game.board
                        dragger = game.dragger
                        self.reset_log()  # Réinitialise le champ des mouvements
                        self.highlight_squares = []  # Réinitialise la coloration des cases

                # Quitter le jeu
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    main.mainloop()