import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

LIGHT_SQUARE = (240,217,181)
DARK_SQUARE = (181, 136, 99)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

def drawBoard(surface):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE

            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            pygame.draw.rect(surface, color, rect)


def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Render graphics
        drawBoard(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap frame rate at 60 FPS
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()