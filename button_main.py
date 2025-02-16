import pygame
from blackjack import BlackjackGame  # Zorg ervoor dat dit correct wordt geïmporteerd

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption('Blackjack Menu')

def main_menu():
    running = True
    while running:
        screen.fill((0, 100, 0))  # Groen menu-achtergrond

        # Knop voor het starten van Blackjack
        play_rect = pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 25, 140, 50))
        quit_rect = pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 50, 140, 50))

        font = pygame.font.Font(None, 38)
        text_play = font.render("Play Blackjack", True, (0, 0, 0))
        text_quit = font.render("Quit", True, (0, 0, 0))
        screen.blit(text_play, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 10))
        screen.blit(text_quit, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 65))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(mouse_pos):
                    game = BlackjackGame()
                    game.run()  # Start het spel
                elif quit_rect.collidepoint(mouse_pos):
                    running = False

    pygame.quit()

if __name__ == "__main__":
    main_menu()
