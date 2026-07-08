import pygame
import sys

pygame.init()

# ==========================================================
# Constants
# ==========================================================
SQUARE_SIZE = 80
BOARD_SIZE = 8
BOARD_OFFSET = 2  # Mailbox board playable area starts at row/col 2

WIDTH = BOARD_SIZE * SQUARE_SIZE
HEIGHT = BOARD_SIZE * SQUARE_SIZE

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mailbox Chess")

# ==========================================================
# Example mailbox board (12x12)
# ==========================================================
board = [
    [99,99,99,99,99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99,99,99,99,99],
    [99,99,-4,-2,-3,-5,-6,-3,-2,-4,99,99],
    [99,99,-1,-1,-1,-1,-1,-1,-1,-1,99,99],
    [99,99, 0, 0, 0, 0, 0, 0, 0, 0,99,99],
    [99,99, 0, 0, 0, 0, 0, 0, 0, 0,99,99],
    [99,99, 0, 0, 0, 0, 0, 0, 0, 0,99,99],
    [99,99, 0, 0, 0,-2, 0,-2, 0, 0,99,99],
    [99,99, 1, 1, 1, 1, 1, 1, 1, 1,99,99],
    [99,99, 4, 2, 3, 5, 6, 3, 2, 4,99,99],
    [99,99,99,99,99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99,99,99,99,99],
]

# ==========================================================
# Piece image files
# ==========================================================
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

# ==========================================================
# Load images
# ==========================================================
piece_images = {}

for piece, filename in piece_files.items():
    image = pygame.image.load(filename)
    image = pygame.transform.smoothscale(
        image,
        (SQUARE_SIZE, SQUARE_SIZE)
    )
    piece_images[piece] = image


# ==========================================================
# Chess Board Class
# ==========================================================
class ChessBoard:

    def __init__(self, board):
        self.board = board

    def set_board(self, new_board):
        """Replace the current mailbox board."""
        self.board = new_board

    def draw(self, surface, selected=None):

        # Draw squares
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                color = LIGHT if (row + col) % 2 == 0 else DARK

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        col * SQUARE_SIZE,
                        row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE
                    )
                )

        # Highlight selected square
        if selected is not None:

            r, c = selected

            pygame.draw.rect(
                surface,
                HIGHLIGHT,
                (
                    (c - BOARD_OFFSET) * SQUARE_SIZE,
                    (r - BOARD_OFFSET) * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                ),
                4
            )

        # Draw pieces
        for row in range(BOARD_OFFSET, BOARD_OFFSET + BOARD_SIZE):
            for col in range(BOARD_OFFSET, BOARD_OFFSET + BOARD_SIZE):

                piece = self.board[row][col]

                if piece in (0, 99):
                    continue

                x = (col - BOARD_OFFSET) * SQUARE_SIZE
                y = (row - BOARD_OFFSET) * SQUARE_SIZE

                surface.blit(piece_images[piece], (x, y))


# ==========================================================
# Utility Functions
# ==========================================================
def screen_to_mailbox(pos):
    """Convert mouse position to mailbox coordinates."""

    x, y = pos

    col = x // SQUARE_SIZE + BOARD_OFFSET
    row = y // SQUARE_SIZE + BOARD_OFFSET

    if row < 2 or row > 9 or col < 2 or col > 9:
        return None

    return row, col


# ==========================================================
# Create board
# ==========================================================
chessboard = ChessBoard(board)

selected = None

clock = pygame.time.Clock()

# ==========================================================
# Main Loop
# ==========================================================
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            square = screen_to_mailbox(event.pos)

            if square is None:
                continue

            row, col = square

            # ----------------------------------------------
            # Nothing selected
            # ----------------------------------------------
            if selected is None:

                if chessboard.board[row][col] != 0:
                    selected = (row, col)

            # ----------------------------------------------
            # Piece already selected
            # ----------------------------------------------
            else:

                src_row, src_col = selected

                # Clicking selected piece deselects it
                if (row, col) == selected:
                    selected = None
                    continue

                # Move piece (no legality checking)
                chessboard.board[row][col] = chessboard.board[src_row][src_col]
                chessboard.board[src_row][src_col] = 0

                selected = None

    chessboard.draw(screen, selected)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()