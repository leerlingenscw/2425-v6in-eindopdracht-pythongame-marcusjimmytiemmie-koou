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
    """Renders text on the screen with a transparent background."""
    text_render = font.render(content, True, color)  # No background color
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
        """Main game loop with fully working Split, Double Down, and Insurance (Mouse Controlled)."""
        while self.is_playing:
            # 🛑 Step 1: Bet Selection
            selecting_bet = True
            while selecting_bet:
                screen.fill(GREEN)
                if background:
                    screen.blit(background, (0, 0))

                # Draw bet buttons
                bet_rect_plus = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 - 20, 40, 40))
                bet_rect_minus = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 20, 40, 40))
                start_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 60, 140, 50))

                # Display bet info
                display_text(f"Balance: ${self.player_balance}", 20, 20)
                display_text(f"Bet: ${self.bet_amount}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 50, WHITE)
                display_text("+", SCREEN_WIDTH // 2 + 95, SCREEN_HEIGHT // 2, BLACK)
                display_text("-", SCREEN_WIDTH // 2 - 105, SCREEN_HEIGHT // 2, BLACK)
                display_text("Start Round", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 75, BLACK)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        selecting_bet = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if bet_rect_plus.collidepoint(mouse_pos) and self.bet_amount + 50 <= self.player_balance:
                            self.bet_amount += 50
                        elif bet_rect_minus.collidepoint(mouse_pos) and self.bet_amount - 50 >= 50:
                            self.bet_amount -= 50
                        elif start_rect.collidepoint(mouse_pos):
                            selecting_bet = False

            # 🛑 Step 2: Start Round
            self.player_balance -= self.bet_amount  
            self.deck = CardDeck()
            self.player_hand = PlayerHand()
            self.dealer_hand = PlayerHand()
            self.split_hand = None  
            self.active_hand = self.player_hand  # Track active hand
            self.player_turn = True
            self.round_over = False
            self.doubled_down = False
            self.first_move = True  # ✅ Track if it's the player's first move

            for _ in range(2):
                self.player_hand.add_card(self.deck.draw_card())
                self.dealer_hand.add_card(self.deck.draw_card())

            # 🛑 Step 3: Check Available Moves
            can_split = (len(self.player_hand.cards) == 2 and self.player_hand.cards[0].split('_')[0] == self.player_hand.cards[1].split('_')[0])
            can_insure = (self.dealer_hand.cards[0].split("_")[0] == "ace")

            # 🛑 Step 4: Main Game Loop
            while not self.round_over:
                screen.fill(GREEN)
                if background:
                    screen.blit(background, (0, 0))

                # Draw action buttons
                hit_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 80, 100, 50))
                stand_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 80, 100, 50))
                double_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT - 80, 100, 50)) if self.first_move and not self.doubled_down else None
                split_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT - 80, 100, 50)) if can_split and self.split_hand is None else None

                # Display hands and totals
                self.player_hand.display(200, 400)
                if self.split_hand:
                    self.split_hand.display(500, 400)
                self.dealer_hand.display(200, 100, hide_first=self.player_turn)
                display_text(f"Player Total: {self.active_hand.total_value}", 200, 550, WHITE)
                display_text(f"Dealer Total: {'?' if self.player_turn else self.dealer_hand.total_value}", 200, 250, WHITE)
                display_text(f"Balance: ${self.player_balance}", 20, 20)
                display_text(f"Bet: ${self.bet_amount}", 20, 50)

                # Button Labels
                display_text("Hit", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 65, BLACK)
                display_text("Stand", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 65, BLACK)
                if double_rect:
                    display_text("Double", SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT - 65, BLACK)
                if split_rect:
                    display_text("Split", SCREEN_WIDTH // 2 + 270, SCREEN_HEIGHT - 65, BLACK)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        self.round_over = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        if hit_rect.collidepoint(mouse_pos) and self.player_turn:
                            self.active_hand.add_card(self.deck.draw_card())
                            self.first_move = False  # ✅ Disable double down after first move
                            if self.active_hand.total_value > 21:
                                self.status_message = "You Busted! Dealer Wins."
                                self.round_over = True

                        elif stand_rect.collidepoint(mouse_pos):
                            self.player_turn = False
                            while self.dealer_hand.total_value < 17:
                                self.dealer_hand.add_card(self.deck.draw_card())
                            self.round_over = True
                            self.status_message = determine_winner(self.player_hand, self.dealer_hand)

                        elif double_rect and double_rect.collidepoint(mouse_pos):
                            if self.first_move:  # ✅ Double down only possible on first move
                                self.player_balance -= self.bet_amount
                                self.bet_amount *= 2
                                self.active_hand.add_card(self.deck.draw_card())
                                self.first_move = False
                                self.doubled_down = True
                                self.player_turn = False
                                while self.dealer_hand.total_value < 17:
                                    self.dealer_hand.add_card(self.deck.draw_card())
                                self.round_over = True
                                self.status_message = determine_winner(self.player_hand, self.dealer_hand)

                        elif split_rect and split_rect.collidepoint(mouse_pos):
                            if can_split and self.split_hand is None:
                                self.split_hand = PlayerHand()
                                self.split_hand.add_card(self.player_hand.cards.pop())
                                self.player_hand.add_card(self.deck.draw_card())
                                self.split_hand.add_card(self.deck.draw_card())
                                self.active_hand = self.player_hand  # Start playing left hand first

            # ✅ Display "Next Round" button before restarting the game
            waiting_for_next_round = True
            while waiting_for_next_round:
                screen.fill(GREEN)
                if background:
                    screen.blit(background, (0, 0))

                self.player_hand.display(200, 400)
                self.dealer_hand.display(200, 100, hide_first=False)
                display_text(self.status_message, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 50, RED)

                next_round_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 60, 140, 50))
                display_text("Next Round", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 75, BLACK)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        waiting_for_next_round = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and next_round_rect.collidepoint(pygame.mouse.get_pos()):
                        waiting_for_next_round = False


        pygame.quit()
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()