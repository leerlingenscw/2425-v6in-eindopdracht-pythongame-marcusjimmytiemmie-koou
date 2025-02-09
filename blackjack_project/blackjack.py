import pygame
import random
import os
import time

# Initialize Pygame
pygame.init()

# Window Configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
CARD_WIDTH, CARD_HEIGHT = 100, 150

# Colors
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# Create the game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack - VWO 6 Final Project")

# Load background
background = pygame.image.load("background.jpg") if os.path.exists("background.jpg") else None
if background:
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load Card Assets
CARD_BACK = pygame.image.load("cards/back.png") if os.path.exists("cards/back.png") else None
if CARD_BACK:
    CARD_BACK = pygame.transform.scale(CARD_BACK, (CARD_WIDTH, CARD_HEIGHT))

# Load all playing card images
CARD_IMAGES = {}
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

for suit in SUITS:
    for rank in RANKS:
        path = f"cards/{rank}_of_{suit}.png"
        if os.path.exists(path):
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            CARD_IMAGES[f"{rank}_of_{suit}"] = img

# Load Sound Effects
hit_sound = pygame.mixer.Sound("sounds/hit.wav") if os.path.exists("sounds/hit.wav") else None
win_sound = pygame.mixer.Sound("sounds/win.wav") if os.path.exists("sounds/win.wav") else None
lose_sound = pygame.mixer.Sound("sounds/lose.wav") if os.path.exists("sounds/lose.wav") else None
chip_sound = pygame.mixer.Sound("sounds/chip.wav") if os.path.exists("sounds/chip.wav") else None

# Font Configuration
font = pygame.font.Font(None, 36)

class CardDeck:
    """Represents a shuffled deck of cards."""
    def __init__(self):
        self.cards = [f"{rank}_of_{suit}" for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def draw_card(self):
        """Draw a card from the deck."""
        return self.cards.pop() if self.cards else None

class PlayerHand:
    """Represents a player's hand in the game."""
    def __init__(self):
        self.cards = []
        self.total_value = 0
        self.ace_count = 0

    def add_card(self, card):
        """Add a card and update the total value."""
        self.cards.append(card)
        rank = card.split('_')[0]

        if rank in ['jack', 'queen', 'king']:
            self.total_value += 10
        elif rank == 'ace':
            self.total_value += 11
            self.ace_count += 1
        else:
            self.total_value += int(rank)

        while self.total_value > 21 and self.ace_count:
            self.total_value -= 10
            self.ace_count -= 1

    def display(self, x, y, hide_first=False):
        """Render cards on screen."""
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                screen.blit(CARD_BACK, (x + i * 30, y))
            else:
                screen.blit(CARD_IMAGES[card], (x + i * 30, y))

def determine_winner(player, dealer):
    """Logic to determine the winner of the round."""
    if player.total_value > 21:
        return "Dealer Wins!"
    elif dealer.total_value > 21:
        return "Player Wins!"
    elif player.total_value == dealer.total_value:
        return "Tie!"
    elif player.total_value > dealer.total_value:
        return "Player Wins!"
    else:
        return "Dealer Wins!"

def display_text(content, x, y, color=WHITE):
    """Draw text on screen."""
    text_render = font.render(content, True, color)
    screen.blit(text_render, (x, y))

class BlackjackGame:
    """Main game logic."""
    def __init__(self):
        self.deck = CardDeck()
        self.player_hand = PlayerHand()
        self.dealer_hand = PlayerHand()
        self.player_balance = 1000
        self.bet_amount = 50
        self.is_playing = True
        self.player_turn = True
        self.round_over = False
        self.status_message = ""

        # Deal initial cards
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw_card())
            self.dealer_hand.add_card(self.deck.draw_card())

    def handle_event(self, event):
        """Process user inputs."""
        if event.type == pygame.QUIT:
            self.is_playing = False

        elif event.type == pygame.KEYDOWN:
            if self.player_turn and not self.round_over:
                if event.key == pygame.K_h:
                    self.player_hand.add_card(self.deck.draw_card())
                    if hit_sound:
                        hit_sound.play()
                    if self.player_hand.total_value > 21:
                        self.player_turn = False
                        self.round_over = True
                        self.status_message = "Dealer Wins!"
                elif event.key == pygame.K_s:
                    self.player_turn = False

            if not self.player_turn and not self.round_over:
                while self.dealer_hand.total_value < 17:
                    self.dealer_hand.add_card(self.deck.draw_card())
                    if hit_sound:
                        hit_sound.play()
                    time.sleep(0.5)

                self.round_over = True
                self.status_message = determine_winner(self.player_hand, self.dealer_hand)
                if "Player" in self.status_message:
                    self.player_balance += self.bet_amount
                    if win_sound:
                        win_sound.play()
                else:
                    self.player_balance -= self.bet_amount
                    if lose_sound:
                        lose_sound.play()

    def run(self):
        """Main game loop."""
        while self.is_playing:
            screen.fill(GREEN)

            if background:
                screen.blit(background, (0, 0))

            display_text(f"Balance: ${self.player_balance}", 20, 20)
            display_text(f"Bet: ${self.bet_amount}", 20, 50)

            self.player_hand.display(200, 400)
            self.dealer_hand.display(200, 100, hide_first=self.player_turn)

            display_text(self.status_message, SCREEN_WIDTH // 2 - 100, 50, WHITE)

            for event in pygame.event.get():
                self.handle_event(event)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()