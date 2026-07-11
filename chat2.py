import pygame
import sys
from Main import Board

pygame.init()

# ==========================================================
# CONFIGURATION
# ==========================================================

SQUARE_SIZE = 80
BOARD_SIZE = 8
OFFSET = 2

WIDTH = BOARD_SIZE * SQUARE_SIZE
HEIGHT = BOARD_SIZE * SQUARE_SIZE

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)

SELECTED = (255, 255, 0)
MOVE_COLOR = (50, 180, 50)
CAPTURE_COLOR = (220, 50, 50)

FPS = 60

# ==========================================================
# PIECE IMAGES
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
# GUI
# ==========================================================

class ChessGUI:

    def __init__(self):

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")

        self.clock = pygame.time.Clock()

        self.images = {}

        self.load_images()

        self.board = None

        self.selected = None

        self.legal_moves = []

    # ------------------------------------------------------

    def load_images(self):

        for piece, filename in piece_files.items():

            img = pygame.image.load(filename)

            img = pygame.transform.smoothscale(
                img,
                (SQUARE_SIZE, SQUARE_SIZE)
            )

            self.images[piece] = img

    # ------------------------------------------------------

    def set_board(self, board):

        """
        Receive a new mailbox board from the engine.
        """

        self.board = board

    # ------------------------------------------------------

    def mailbox_to_screen(self, row, col):

        x = (col - OFFSET) * SQUARE_SIZE
        y = (row - OFFSET) * SQUARE_SIZE

        return x, y

    # ------------------------------------------------------

    def screen_to_mailbox(self, pos):

        x, y = pos

        col = x // SQUARE_SIZE + OFFSET
        row = y // SQUARE_SIZE + OFFSET

        if row < 2 or row > 9:
            return None

        if col < 2 or col > 9:
            return None

        return (row, col)

    # ------------------------------------------------------

    def draw_board(self):

        for r in range(BOARD_SIZE):

            for c in range(BOARD_SIZE):

                color = LIGHT if (r + c) % 2 == 0 else DARK

                pygame.draw.rect(

                    self.screen,

                    color,

                    (

                        c * SQUARE_SIZE,

                        r * SQUARE_SIZE,

                        SQUARE_SIZE,

                        SQUARE_SIZE

                    )

                )

    # ------------------------------------------------------

    def draw_selected(self):

        if self.selected is None:
            return

        row, col = self.selected

        x, y = self.mailbox_to_screen(row, col)

        pygame.draw.rect(

            self.screen,

            SELECTED,

            (

                x,

                y,

                SQUARE_SIZE,

                SQUARE_SIZE

            ),

            4

        )

    # ------------------------------------------------------
    # Draw legal move markers
    # ------------------------------------------------------

    def draw_moves(self):

        if self.board is None:
            return

        for row, col in self.legal_moves:

            x, y = self.mailbox_to_screen(row, col)

            piece = self.board[row][col]

            center = (
                x + SQUARE_SIZE // 2,
                y + SQUARE_SIZE // 2
            )

            # Empty square = green move marker
            if piece == 0:

                pygame.draw.circle(

                    self.screen,
                    MOVE_COLOR,
                    center,
                    12

                )

            # Capture = red outline
            else:

                pygame.draw.circle(

                    self.screen,
                    CAPTURE_COLOR,
                    center,
                    30,
                    4

                )


    # ------------------------------------------------------
    # Draw pieces
    # ------------------------------------------------------

    def draw_pieces(self):

        if self.board is None:
            return

        for row in range(2, 10):

            for col in range(2, 10):

                piece = self.board[row][col]

                if piece == 0:
                    continue

                x, y = self.mailbox_to_screen(row, col)

                self.screen.blit(

                    self.images[piece],

                    (
                        x,
                        y
                    )

                )


    # ------------------------------------------------------
    # Complete redraw
    # ------------------------------------------------------

    def draw(self):

        self.draw_board()

        self.draw_moves()

        self.draw_selected()

        self.draw_pieces()


        pygame.display.flip()


    # ------------------------------------------------------
    # Select a piece
    # ------------------------------------------------------

    def select_piece(self, square):

        row, col = square

        piece = self.board[row][col]

        if piece == 0:
            return False

        self.selected = square

        return True


    # ------------------------------------------------------
    # Clear selection
    # ------------------------------------------------------

    def clear_selection(self):

        self.selected = None

        self.legal_moves = []


    # ------------------------------------------------------
    # Main move selection function
    #
    # get_legal_moves(board, square)
    #
    # must be supplied by the chess engine
    #
    # Returns:
    #
    # ((source_row,source_col),
    #  (dest_row,dest_col))
    #
    # ------------------------------------------------------

    def get_move(self, get_legal_moves):

        self.clear_selection()


        while True:


            for event in pygame.event.get():


                if event.type == pygame.QUIT:

                    pygame.quit()

                    sys.exit()



                if event.type == pygame.MOUSEBUTTONDOWN:


                    square = self.screen_to_mailbox(event.pos)


                    if square is None:

                        continue



                    # ----------------------------------
                    # First click
                    # ----------------------------------

                    if self.selected is None:


                        if self.select_piece(square):


                            self.legal_moves = get_legal_moves(

                                self.board,

                                self.selected

                            )



                    # ----------------------------------
                    # Second click
                    # ----------------------------------

                    else:


                        if square in self.legal_moves:


                            move = (

                                self.selected,

                                square

                            )


                            self.clear_selection()

                            return move



                        else:


                            # Selecting another piece
                            if self.board[square[0]][square[1]] != 0:


                                if self.select_piece(square):

                                    self.legal_moves = get_legal_moves(

                                        self.board,

                                        self.selected

                                    )


                            else:

                                self.clear_selection()



            self.draw()

            self.clock.tick(FPS)

# ==========================================================
# EXAMPLE BOARD
# Replace this with your engine board
# ==========================================================

initial_board = [

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

[99,99,99,99,99,99,99,99,99,99,99,99]

]


# ==========================================================
# PLACEHOLDER ENGINE FUNCTION
#
# Replace this with your move generator
#
# Input:
#   board
#   selected mailbox square
#
# Output:
#   list of legal destination squares
#
# ==========================================================

def get_legal_moves(board, square):


    row, col = square


    # Example:
    # Allow a piece to move one square
    # in any direction.
    #
    # Replace this with your chess engine.


    moves = []


    directions = [

        (-1,-1),
        (-1,0),
        (-1,1),

        (0,-1),
        (0,1),

        (1,-1),
        (1,0),
        (1,1)

    ]


    for dr, dc in directions:


        r = row + dr
        c = col + dc


        if 2 <= r <= 9 and 2 <= c <= 9:

            moves.append((r,c))


    return moves


# ==========================================================
# MAIN PROGRAM
# ==========================================================

def main():


    gui = ChessGUI()


    board = initial_board


    while True:


        # Engine sends current board
        gui.set_board(board)



        # GUI waits for player move
        move = gui.get_move(
            get_legal_moves

        )



        source, destination = move


        sr, sc = source

        dr, dc = destination



        # --------------------------------------------------
        # Normally this is where your engine goes:
        #
        # board = make_move(board, move)
        #
        # --------------------------------------------------


        board[dr][dc] = board[sr][sc]

        board[sr][sc] = 0



# ----------------------------------------------------------

if __name__ == "__main__":

    main()