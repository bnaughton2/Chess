import pygame
import sys

pygame.init()

# =====================================================
# Configuration
# =====================================================
SQUARE_SIZE = 80
BOARD_SIZE = 8
OFFSET = 2

WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess GUI")

# =====================================================
# Piece Images
# =====================================================
piece_files = {
     1: "pieces-basic-svg/pawn-w.svg",
     2: "pieces-basic-svg/knight-w.svg",
     3: "pieces-basic-svg/bishop-w.svg",
     4: "pieces-basic-svg/rook-w.svg",
     5: "pieces-basic-svg/queen-w.svg",
     6: "pieces-basic-svg/king-w.svg",

    -1: "pieces-basic-svg/pawn-b.svg",
    -2: "pieces-basic-svg/knight-b.svg",
    -3: "pieces-basic-svg/bishop-b.svg",
    -4: "pieces-basic-svg/rook-b.svg",
    -5: "pieces-basic-svg/queen-b.svg",
    -6: "pieces-basic-svg/king-b.svg",
}

piece_images = {}

for piece, filename in piece_files.items():
    img = pygame.image.load(filename)
    img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
    piece_images[piece] = img


# =====================================================
# GUI Class
# =====================================================
class ChessGUI:

    def __init__(self):

        self.board = None
        self.selected = None

        self.clock = pygame.time.Clock()

    # ----------------------------------------------
    # Engine sends a new board here
    # ----------------------------------------------
    def set_board(self, board):
        self.board = board

    # ----------------------------------------------
    # Draw everything
    # ----------------------------------------------
    def draw(self):

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):

                color = LIGHT if (r + c) % 2 == 0 else DARK

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        c * SQUARE_SIZE,
                        r * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    ),
                )

        if self.selected:

            r, c = self.selected

            pygame.draw.rect(
                screen,
                HIGHLIGHT,
                (
                    (c - OFFSET) * SQUARE_SIZE,
                    (r - OFFSET) * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
                4,
            )

        if self.board is None:
            return

        for r in range(2, 10):
            for c in range(2, 10):

                piece = self.board[r][c]

                if piece == 0:
                    continue

                screen.blit(
                    piece_images[piece],
                    (
                        (c - OFFSET) * SQUARE_SIZE,
                        (r - OFFSET) * SQUARE_SIZE,
                    ),
                )

    # ----------------------------------------------
    # Convert mouse to mailbox coordinate
    # ----------------------------------------------
    def mouse_to_mailbox(self, pos):

        x, y = pos

        col = x // SQUARE_SIZE + OFFSET
        row = y // SQUARE_SIZE + OFFSET

        if row < 2 or row > 9:
            return None

        if col < 2 or col > 9:
            return None

        return (row, col)

    # ----------------------------------------------
    # Wait until player chooses a move
    #
    # Returns:
    #
    # ((src_row,src_col),(dst_row,dst_col))
    #
    # ----------------------------------------------
    def get_move(self):

        self.selected = None

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    square = self.mouse_to_mailbox(event.pos)

                    if square is None:
                        continue

                    # First click
                    if self.selected is None:

                        if self.board[square[0]][square[1]] != 0:
                            self.selected = square

                    # Second click
                    else:

                        move = (self.selected, square)
                        self.selected = None
                        return move

            self.draw()

            pygame.display.flip()

            self.clock.tick(60)


# =====================================================
# Example Usage
# =====================================================

board = [
[99,99,99,99,99,99,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99,99,99,99,99],
[99,99,-4,-2,-3,-5,-6,-3,-2,-4,99,99],
[99,99,-1,-1,-1,-1,-1,-1,-1,-1,99,99],
[99,99,0,0,0,0,0,0,0,0,99,99],
[99,99,0,0,0,0,0,0,0,0,99,99],
[99,99,0,0,0,0,0,0,0,0,99,99],
[99,99,0,0,0,-2,0,-2,0,0,99,99],
[99,99,1,1,1,1,1,1,1,1,99,99],
[99,99,4,2,3,5,6,3,2,4,99,99],
[99,99,99,99,99,99,99,99,99,99,99,99],
[99,99,99,99,99,99,99,99,99,99,99,99],
]

gui = ChessGUI()

while True:

    # Engine gives GUI the current board
    gui.set_board(board)

    # GUI waits for the player's move
    move = gui.get_move()

    print("Player chose:", move)

    # --------------------------------------
    # Example only:
    # Move the piece directly.
    #
    # Replace this section with:
    #
    # board = engine.make_move(board, move)
    #
    # --------------------------------------
    (sr, sc), (dr, dc) = move

    board[dr][dc] = board[sr][sc]
    board[sr][sc] = 0