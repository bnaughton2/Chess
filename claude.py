"""
chess_gui.py
=================================================================
A pure DISPLAY + INPUT layer for a chess application, built with
pygame-ce so that SVG piece art can be loaded natively.

--------------------------------------------------------------
IMPORTANT DESIGN CONSTRAINT
--------------------------------------------------------------
This module contains ZERO chess knowledge. It does not:
    - generate moves
    - validate legality
    - know how pieces move
    - detect captures, check, or checkmate
    - mutate the board on its own

All of that lives in a separate "engine" (not included here,
or represented by a placeholder demo engine in the __main__
block purely so this file can be run standalone).

The GUI's job is limited to:
    1. Rendering whatever board it is given (set_board).
    2. Waiting for the user to click a square that holds a piece
       (get_selected_piece) and reporting that square back.
    3. Rendering whatever list of destination squares the engine
       decides are legal (set_legal_moves).
    4. Waiting for the user to click one of those squares
       (get_destination) and reporting the (from, to) move back --
       or reporting None if the user deselected the piece instead
       (by clicking it again or right-clicking).

The engine is the single source of truth for game state. The GUI
only ever reflects what the engine tells it via set_board() /
set_legal_moves(), and only ever reports raw mailbox coordinates
back via get_selected_piece() / get_destination().

--------------------------------------------------------------
BOARD REPRESENTATION (supplied by the engine)
--------------------------------------------------------------
12x12 mailbox board. Playable squares are rows 2-9, cols 2-9.

    99   = border / off-board
    0    = empty square
    1..6 = white pawn, knight, bishop, rook, queen, king
   -1..-6= black pawn, knight, bishop, rook, queen, king
"""

import os
import sys
import pygame
from Main import Board

# -----------------------------------------------------------------
# Constants (purely visual/layout -- not chess rules)
# -----------------------------------------------------------------
SQUARE_SIZE = 80
BOARD_SQUARES = 8
MARGIN = 40  # space around the board for rank/file labels
BOARD_PIXELS = SQUARE_SIZE * BOARD_SQUARES
WINDOW_WIDTH = BOARD_PIXELS + 2 * MARGIN
WINDOW_HEIGHT = BOARD_PIXELS + 2 * MARGIN
FPS = 60

# Mailbox bounds for the playable area
MAILBOX_MIN = 2
MAILBOX_MAX = 9  # inclusive

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BACKGROUND = (30, 30, 30)
SELECTED_BORDER = (255, 215, 0)      # yellow
LEGAL_MOVE_DOT = (0, 170, 0)         # green
LEGAL_CAPTURE_DOT = (200, 30, 30)    # red
LABEL_COLOR = (220, 220, 220)

# Piece value -> filename fragment
PIECE_FILENAMES = {
    1: "pawn-w.svg", 2: "knight-w.svg", 3: "bishop-w.svg",
    4: "rook-w.svg", 5: "queen-w.svg", 6: "king-w.svg",
    -1: "pawn-b.svg", -2: "knight-b.svg", -3: "bishop-b.svg",
    -4: "rook-b.svg", -5: "queen-b.svg", -6: "king-b.svg",
}

PIECES_DIR = "pieces-basic-svg"


class ChessGUI:
    """
    Display + input interface for a chess engine.

    The engine communicates with this class through exactly four
    methods:

        set_board(board)          -- push a new position to display
        get_selected_piece()      -- blocking call, returns (row, col)
        set_legal_moves(moves)    -- push list of legal destinations
        get_destination()         -- blocking call, returns
                                      ((from_row, from_col),
                                       (to_row, to_col))

    No other public surface is needed by an engine.
    """

    def __init__(self, pieces_dir=PIECES_DIR):
        pygame.init()
        pygame.display.set_caption("Chess GUI (display/input only)")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 16)

        # --- Engine-owned state, mirrored here purely for drawing ---
        self.board = self._empty_board()
        self.selected_square = None      # (row, col) or None
        self.legal_moves = []            # list of (row, col)

        # --- Load and pre-scale piece artwork ---
        self.piece_images = self._load_piece_images(pieces_dir)

        self._running = True

    # ---------------------------------------------------------------
    # Engine communication interface
    # ---------------------------------------------------------------
    def set_board(self, board):
        """
        Receive a fresh 12x12 mailbox board from the engine and
        redraw. This is the ONLY way the displayed position changes;
        the GUI never edits self.board except through this call.
        """
        self.board = board
        self.selected_square = None
        self.legal_moves = []
        self._render()

    def get_selected_piece(self):
        """
        Block until the player clicks a square that currently holds
        a piece (any non-empty, on-board square). Returns the
        mailbox (row, col) of that square.

        NOTE: This only filters "is there a piece here to pick up".
        It performs NO legality/ownership/turn checking -- that is
        entirely the engine's responsibility. The engine is free to
        reject the selection and ask again if it wants.
        """
        while True:
            button, square = self._wait_for_mouse_event()
            if button != 1 or square is None:
                continue  # only left-clicks on the board count here
            row, col = square
            piece = self.board[row][col]
            if piece != 0 and piece != 99:
                self.selected_square = square
                self._render()
                return square
            # Clicked an empty/border square -- ignore and keep waiting.

    def set_legal_moves(self, moves):
        """
        Receive the list of legal destination squares for the
        currently selected piece, as decided entirely by the engine.
        The GUI just highlights them.
        """
        self.legal_moves = list(moves)
        self._render()

    def get_destination(self):
        """
        Block until the player either:
          - left-clicks one of the squares supplied via
            set_legal_moves(), in which case the move is returned, or
          - deselects the current piece, in which case None is
            returned so the engine knows to go back and ask for a
            new selection instead of a move.

        Deselection happens on:
          - left-clicking the currently selected square again, or
          - right-clicking anywhere on the board.

        Clicks that are neither a legal destination nor a deselect
        action are simply ignored, and the GUI keeps waiting.

        Returns:
            ((from_row, from_col), (to_row, to_col))  -- on a move
            None                                       -- on deselect
        """
        while True:
            button, square = self._wait_for_mouse_event()

            if button == 3:  # right-click anywhere = deselect
                self._clear_selection()
                return None

            if square is None:
                continue  # click was off the board entirely

            if square == self.selected_square:
                # Clicking the selected piece again deselects it.
                self._clear_selection()
                return None

            if square in self.legal_moves:
                move = (self.selected_square, square)
                return move

            # Click was somewhere irrelevant (not a legal destination,
            # not the selected square) -- ignore and keep waiting.

    def _clear_selection(self):
        """Reset selection/highlight state and redraw."""
        self.selected_square = None
        self.legal_moves = []
        self._render()

    # ---------------------------------------------------------------
    # Input handling
    # ---------------------------------------------------------------
    def _wait_for_mouse_event(self):
        """
        Pump the event loop (keeping the window responsive and at
        FPS) until the player presses a mouse button. Returns:

            (button, mailbox_coord_or_None)

        where `button` is 1 for left-click, 3 for right-click, and
        `mailbox_coord_or_None` is the (row, col) clicked, or None
        if the click landed outside the playable 8x8 area (still
        returned so callers can react to e.g. a right-click anywhere
        as a "cancel" gesture).
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                    mailbox_coord = self._pixel_to_mailbox(event.pos)
                    return event.button, mailbox_coord

            self._render()
            self.clock.tick(FPS)

    def _pixel_to_mailbox(self, pos):
        """Convert a screen pixel position into a mailbox (row, col),
        or None if the click fell outside the 8x8 playable area."""
        x, y = pos
        x -= MARGIN
        y -= MARGIN
        if x < 0 or y < 0 or x >= BOARD_PIXELS or y >= BOARD_PIXELS:
            return None
        display_col = x // SQUARE_SIZE
        display_row = y // SQUARE_SIZE
        row = display_row + MAILBOX_MIN
        col = display_col + MAILBOX_MIN
        return (row, col)

    # ---------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------
    def _render(self):
        """Draw background, board squares, highlights, pieces, labels."""
        self.screen.fill(BACKGROUND)
        self._draw_squares()
        self._draw_selected_highlight()
        self._draw_legal_move_markers()
        self._draw_pieces()
        self._draw_labels()
        pygame.display.flip()

    def _draw_squares(self):
        for display_row in range(BOARD_SQUARES):
            for display_col in range(BOARD_SQUARES):
                color = LIGHT_SQUARE if (display_row + display_col) % 2 == 0 else DARK_SQUARE
                rect = self._square_rect(display_row, display_col)
                pygame.draw.rect(self.screen, color, rect)

    def _draw_selected_highlight(self):
        if self.selected_square is None:
            return
        row, col = self.selected_square
        display_row, display_col = row - MAILBOX_MIN, col - MAILBOX_MIN
        rect = self._square_rect(display_row, display_col)
        pygame.draw.rect(self.screen, SELECTED_BORDER, rect, width=4)

    def _draw_legal_move_markers(self):
        for (row, col) in self.legal_moves:
            display_row, display_col = row - MAILBOX_MIN, col - MAILBOX_MIN
            rect = self._square_rect(display_row, display_col)
            center = rect.center

            # A square is shown as a "legal capture" purely based on
            # whether it is currently occupied -- this is a visual
            # cue only, not a rules determination (the engine already
            # decided this square is a legal destination; the GUI is
            # just choosing a dot color).
            occupant = self.board[row][col]
            is_capture = occupant != 0 and occupant != 99
            color = LEGAL_CAPTURE_DOT if is_capture else LEGAL_MOVE_DOT

            if is_capture:
                pygame.draw.circle(self.screen, color, center, SQUARE_SIZE // 2 - 6, width=5)
            else:
                pygame.draw.circle(self.screen, color, center, SQUARE_SIZE // 6)

    def _draw_pieces(self):
        for row in range(MAILBOX_MIN, MAILBOX_MAX + 1):
            for col in range(MAILBOX_MIN, MAILBOX_MAX + 1):
                piece = self.board[row][col]
                if piece == 0 or piece == 99:
                    continue
                image = self.piece_images.get(piece)
                if image is None:
                    continue
                display_row, display_col = row - MAILBOX_MIN, col - MAILBOX_MIN
                rect = self._square_rect(display_row, display_col)
                image_rect = image.get_rect(center=rect.center)
                self.screen.blit(image, image_rect)

    def _draw_labels(self):
        files = "abcdefgh"
        for display_col in range(BOARD_SQUARES):
            label = self.font.render(files[display_col], True, LABEL_COLOR)
            x = MARGIN + display_col * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_width() // 2
            y = MARGIN + BOARD_PIXELS + 8
            self.screen.blit(label, (x, y))
        for display_row in range(BOARD_SQUARES):
            rank = str(8 - display_row)
            label = self.font.render(rank, True, LABEL_COLOR)
            x = MARGIN - label.get_width() - 8
            y = MARGIN + display_row * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_height() // 2
            self.screen.blit(label, (x, y))

    def _square_rect(self, display_row, display_col):
        return pygame.Rect(
            MARGIN + display_col * SQUARE_SIZE,
            MARGIN + display_row * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        )

    # ---------------------------------------------------------------
    # Asset loading
    # ---------------------------------------------------------------
    def _load_piece_images(self, pieces_dir):
        images = {}
        for value, filename in PIECE_FILENAMES.items():
            path = os.path.join(pieces_dir, filename)
            try:
                raw = pygame.image.load(path)  # pygame-ce: native SVG support
            except Exception as exc:
                print(f"Warning: could not load '{path}': {exc}")
                continue
            scaled = pygame.transform.smoothscale(
                raw, (SQUARE_SIZE - 10, SQUARE_SIZE - 10)
            )
            images[value] = scaled.convert_alpha() if scaled.get_bitsize() >= 24 else scaled
        return images

    @staticmethod
    def _empty_board():
        board = [[99] * 12 for _ in range(12)]
        for row in range(MAILBOX_MIN, MAILBOX_MAX + 1):
            for col in range(MAILBOX_MIN, MAILBOX_MAX + 1):
                board[row][col] = 0
        return board

    def _quit(self):
        pygame.quit()
        sys.exit(0)


# =====================================================================
# DEMONSTRATION / WIRING EXAMPLE
# =====================================================================
# Everything below this line is NOT part of the GUI. It is a minimal
# stand-in "engine" so this file can be run end-to-end on its own,
# following exactly the communication flow described in the spec:
#
#     gui.set_board(board)
#     selected = gui.get_selected_piece()
#     legal_moves = engine.get_legal_moves(board, selected)
#     gui.set_legal_moves(legal_moves)
#     move = gui.get_destination()
#     board = engine.make_move(board, move)
#
# Replace DemoEngine with a real chess engine to get a fully rules-
# compliant game. DemoEngine intentionally implements only crude,
# non-validated "moves anywhere on an empty or enemy square in a
# straight/diagonal line-ish way" logic (loosely piece-shaped, NOT
# rules-complete: no check detection, no turn enforcement, no
# special moves) purely so the highlight/click flow is visible.
# =====================================================================

class DemoEngine:
    """A placeholder engine, only for demoing the wiring above.
    This class -- not chess_gui.py -- is where real chess logic
    would live in a production setup."""

    START_BOARD = [
        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, -4, -2, -3, -5, -6, -3, -2, -4, 99, 99],
        [99, 99, -1, -1, -1, -1, -1, -1, -1, -1, 99, 99],
        [99, 99, 0, 0, 0, 0, 0, 0, 0, 0, 99, 99],
        [99, 99, 0, 0, 0, 0, 0, 0, 0, 0, 99, 99],
        [99, 99, 0, 0, 0, 0, 0, 0, 0, 0, 99, 99],
        [99, 99, 0, 0, 0, 0, 0, 0, 0, 0, 99, 99],
        [99, 99, 1, 1, 1, 1, 1, 1, 1, 1, 99, 99],
        [99, 99, 4, 2, 3, 5, 6, 3, 2, 4, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
    ]

    def get_legal_moves(self, board, selected):
        """Extremely crude placeholder: any empty/enemy square within
        one step in any of the 8 directions. NOT real chess rules."""
        row, col = selected
        piece = board[row][col]
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if MAILBOX_MIN <= r <= MAILBOX_MAX and MAILBOX_MIN <= c <= MAILBOX_MAX:
                    target = board[r][c]
                    if target == 0 or (piece > 0) != (target > 0):
                        moves.append((r, c))
        return moves

    def make_move(self, board, move):
        (from_row, from_col), (to_row, to_col) = move
        new_board = [row[:] for row in board]
        new_board[to_row][to_col] = new_board[from_row][from_col]
        new_board[from_row][from_col] = 0
        return new_board


def main():
    gui = ChessGUI()
    board = Board()
    board.storeAllMoves()

    game_running = True
    while game_running:
        # 1. Push current position to the GUI for display.
        gui.set_board(board.board)

        # 2. Ask the GUI (i.e. the player) to pick up a piece.
        selected = gui.get_selected_piece()
        print(selected)

        # 3. Ask the engine which destinations are legal for that piece.
        legal_moves = board.getLegalMoves(selected)
        

        # 4. Tell the GUI to highlight those destinations.
        gui.set_legal_moves(legal_moves)

        # 5. Ask the GUI (i.e. the player) to pick a destination.
        #    This can come back as None if the player deselected the
        #    piece instead (clicked it again, or right-clicked) --
        #    in that case, just loop back and let them pick again.
        move = gui.get_destination()
        if move is None:
            continue

        # 6. Ask the engine to apply the move and update state.
        board.makeMove(selected, move[1])


if __name__ == "__main__":
    main()