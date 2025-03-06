import pygame
import random
import os

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
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)

# Create the game screen in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()  # Get new screen size after switching to fullscreen

pygame.display.set_caption("Blackjack - VWO 6 Final Project")

# Load background
if not os.path.exists("background.jpg"):
    raise FileNotFoundError("Background image not found!")
background = pygame.transform.scale(pygame.image.load("background.jpg"), (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load Card Assets
if not os.path.exists("cards/back.png"):
    raise FileNotFoundError("Card back image not found!")
CARD_BACK = pygame.transform.scale(pygame.image.load("cards/back.png"), (CARD_WIDTH, CARD_HEIGHT))

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

# Font Configuration
font = pygame.font.Font(None, 36)
button_font = pygame.font.Font(None, 28)  # Smaller font for buttons
large_font = pygame.font.Font(None, 72)  # Larger font for winning message
title_font = pygame.font.Font(None, 100)  # Font for the main menu title

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
        self.is_bust = False  # Track if the hand is busted

    def add_card(self, card):
        """Add a card and update the total value."""
        self.cards.append(card)
        rank = card.split('_')[0]

        if rank in ['jack', 'queen', 'king']:
            self.total_value += 10
        elif rank == 'ace':
            self.ace_count += 1
            self.total_value += 11
        else:
            self.total_value += int(rank)

        while self.total_value > 21 and self.ace_count > 0:
            self.total_value -= 10
            self.ace_count -= 1

        if self.total_value > 21:
            self.is_bust = True  # Mark the hand as busted

    def display(self, x, y, hide_first=False, hide_all_except_first=False):
        """Render cards on screen."""
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                screen.blit(CARD_BACK, (x + i * 30, y))
            elif hide_all_except_first and i != 0:
                continue  # Skip rendering cards after the first one
            else:
                screen.blit(CARD_IMAGES[card], (x + i * 30, y))

    def clear_hand(self):
        """Clear the hand for a new round."""
        self.cards = []
        self.total_value = 0
        self.ace_count = 0
        self.is_bust = False

def determine_winner(player, dealer, game, split_hand=None):
    """Determine the winner and update winnings/losses for the previous round."""
    results = []
    multiple_hands = split_hand is not None  # Check if there are two hands

    def evaluate_hand(hand_name, player_hand):
        if player_hand.is_bust:
            game.previous_losses += game.bet_amount
            return f"{hand_name}Dealer Wins!"
        elif dealer.is_bust or player_hand.total_value > dealer.total_value:
            game.previous_winnings += game.bet_amount * 2
            game.player_balance += game.bet_amount * 2
            return f"{hand_name}Player Wins!"
        elif player_hand.total_value == dealer.total_value:
            game.player_balance += game.bet_amount
            return f"{hand_name}Tie!"
        else:
            game.previous_losses += game.bet_amount
            return f"{hand_name}Dealer Wins!"

    # Evaluate Hand 1
    results.append(evaluate_hand("Hand 1: " if multiple_hands else "", player))

    # Evaluate Hand 2 (if present)
    if split_hand:
        results.append(evaluate_hand("Hand 2: ", split_hand))

    # Check for mixed results
    if "Player Wins!" in results and "Dealer Wins!" in results:
        return "Split Result: One Win, One Loss"
    else:
        return " | ".join(results)

def display_text(content, x, y, color=WHITE, font_type=font):
    """Renders text on the screen with a transparent background."""
    text_render = font_type.render(content, True, color)
    screen.blit(text_render, (x, y))

def display_winning_animation():
    """Display a celebratory animation when the player wins."""
    screen.fill(GREEN)
    screen.blit(background, (0, 0))
    display_text("YOU WIN!", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, GOLD, large_font)
    pygame.display.flip()
    pygame.time.delay(1000)  # Show the animation for 1 second

def display_balance_change(amount):
    """Display the change in balance with green for wins and red for losses."""
    screen.fill(GREEN)
    screen.blit(background, (0, 0))
    color = GREEN if amount > 0 else RED
    text = f"+${amount}" if amount > 0 else f"-${abs(amount)}"
    display_text(text, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50, color, large_font)
    pygame.display.flip()
    pygame.time.delay(1000)  # Show the animation for 1 second

class BlackjackGame:
    def __init__(self):
        self.deck = CardDeck()
        self.player_hand = PlayerHand()
        self.dealer_hand = PlayerHand()
        self.split_hand = None
        self.active_hand = self.player_hand
        self.first_move = True
        self.can_split = True
        self.player_balance = 100
        self.bet_amount = 10
        self.original_bet = self.bet_amount
        self.previous_bet = self.bet_amount  # Voeg deze regel toe om de vorige inzet te onthouden
        self.is_playing = True
        self.player_turn = True
        self.round_over = False
        self.status_message = ""
        self.previous_winnings = 0
        self.previous_losses = 0

        # Deal initial cards
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw_card())
            self.dealer_hand.add_card(self.deck.draw_card())

    def handle_event(self, event):
        """Process user inputs."""
        if event.type == pygame.QUIT:
            self.is_playing = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check if the player clicked on a button
            if hit_rect.collidepoint(mouse_pos) and self.player_turn:
                self.active_hand.add_card(self.deck.draw_card())
                self.first_move = False  # Disable doubling down after hitting

                if self.active_hand.total_value > 21:  # Check if the active hand busts
                    self.active_hand.is_bust = True  # Mark the hand as busted

                    if self.split_hand and self.active_hand == self.player_hand:
                        # If the first hand busts and there is a second hand, switch to that hand
                        self.active_hand = self.split_hand
                        self.first_move = True  # Reset the first move for the second hand
                        self.status_message = "Hand 1 Busted! Switching to Hand 2."
                    else:
                        # If both hands are busted or there's no split, end the round
                        if self.split_hand and self.split_hand.is_bust:
                            self.status_message = "Both Hands Busted! Dealer Wins."
                        else:
                            self.status_message = "You Busted! Dealer Wins."
                        self.round_over = True

            elif stand_rect.collidepoint(mouse_pos):
                if self.split_hand and self.active_hand == self.player_hand:
                    # Player stands on the first hand, switch to the second hand
                    self.active_hand = self.split_hand
                    self.first_move = True  # Reset the first move for Hand 2
                    self.status_message = "Switching to Hand 2."
                else:
                    # Both hands are played, dealer's turn
                    self.player_turn = False
                    self.handle_dealer_turn()

            elif double_rect and double_rect.collidepoint(mouse_pos):  # Check if double_rect exists
                if self.first_move:  # Double down only possible on the first move
                    if self.bet_amount > self.player_balance:
                        self.status_message = "Not enough balance for double down! Brokie!"
                    else:
                        self.player_balance -= self.bet_amount
                        self.bet_amount *= 2
                        self.active_hand.add_card(self.deck.draw_card())
                        self.first_move = False
                        self.doubled_down = True
                        # Check if the hand is bust after doubling down
                        if self.active_hand.total_value > 21:
                            self.active_hand.is_bust = True
                            if self.split_hand and self.active_hand == self.player_hand:
                                self.active_hand = self.split_hand
                                self.first_move = True
                                self.status_message = "Hand 1 Busted! Switching to Hand 2."
                            elif self.split_hand and self.split_hand.is_bust:
                                self.status_message = "Both Hands Busted! Dealer Wins."
                                self.round_over = True
                            else:
                                self.status_message = "You Busted! Dealer Wins."
                                self.round_over = True
                        else:
                            # Nieuwe code toegevoegd
                            if self.split_hand and self.active_hand == self.player_hand:
                                self.active_hand = self.split_hand
                                self.first_move = True
                                self.status_message = "Doubled Down! Switching to Hand 2."
                            else:
                                self.player_turn = False
                                self.handle_dealer_turn()

            elif split_rect and split_rect.collidepoint(mouse_pos):
                if self.can_split and self.split_hand is None and self.player_balance >= self.bet_amount:
                    self.split_hand = PlayerHand()
                    card_to_move = self.player_hand.cards.pop()
                    self.split_hand.add_card(card_to_move)
                    self.player_hand.add_card(self.deck.draw_card())
                    self.split_hand.add_card(self.deck.draw_card())
                    self.player_balance -= self.bet_amount
                    self.bet_amount *= 2
                    self.can_split = False
                    self.status_message = "Hand split! Playing Hand 1 first."

    def handle_dealer_turn(self):
        """Handle the dealer's turn and determine the winner."""
        while self.dealer_hand.total_value < 17:
            self.dealer_hand.add_card(self.deck.draw_card())
            pygame.time.delay(200)  # Add a slight delay for realism

        self.round_over = True
        self.status_message = determine_winner(self.player_hand, self.dealer_hand, self, self.split_hand)
        if "Player Wins!" in self.status_message:
            display_winning_animation()  # Show winning animation if the player wins
        elif "Dealer Wins!" in self.status_message:
            display_balance_change(-self.bet_amount)  # Show loss animation
        else:
            display_balance_change(0)  # Show tie animation

        self.bet_amount = self.original_bet

    def run(self):
        """Main game loop with fully working Split, Double Down, and Insurance (Mouse Controlled)."""
        global hit_rect, stand_rect, double_rect, split_rect

        while self.is_playing:
            # Step 1: Bet Selection
            selecting_bet = True
            while selecting_bet:
                screen.fill(GREEN)
                screen.blit(background, (0, 0))

                self.can_split = True
                self.split_hand = None

                # Draw bet buttons
                bet_rect_plus = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 - 20, 40, 40))
                bet_rect_minus = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 20, 40, 40))
                start_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 60, 140, 50))

                # Display balance, previous winnings, and losses
                display_text(f"Balance: ${self.player_balance}", 20, 20, RED if self.player_balance == 0 else WHITE)
                display_text(f"Bet: ${self.bet_amount}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 50, WHITE)
                display_text("+", SCREEN_WIDTH // 2 + 95, SCREEN_HEIGHT // 2, BLACK)
                display_text("-", SCREEN_WIDTH // 2 - 105, SCREEN_HEIGHT // 2, BLACK)
                display_text("Start Round", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 75, BLACK, button_font)

                # Display balance change animation
                if self.previous_winnings > 0:
                    display_text(f"+${self.previous_winnings}", 20, 60, GREEN)
                elif self.previous_losses > 0:
                    display_text(f"-${self.previous_losses}", 20, 60, RED)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        selecting_bet = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if bet_rect_plus.collidepoint(mouse_pos) and self.bet_amount + 5 <= self.player_balance:
                            self.bet_amount += 5
                            self.previous_winnings = 0
                            self.previous_losses = 0
                        elif bet_rect_minus.collidepoint(mouse_pos) and self.bet_amount - 5 >= 5:
                            self.bet_amount -= 5
                            self.previous_winnings = 0
                            self.previous_losses = 0
                        elif start_rect.collidepoint(mouse_pos):
                            if self.bet_amount > self.player_balance:
                                self.status_message = "Niet genoeg saldo! Brokie!"
                            else:
                                selecting_bet = False
                                self.previous_bet = self.bet_amount  # Sla de huidige inzet op als de vorige inzet

            # Step 2: Start Round
            self.deck = CardDeck()
            self.player_hand = PlayerHand()
            self.dealer_hand = PlayerHand()
            self.split_hand = None
            self.active_hand = self.player_hand
            self.player_turn = True
            self.round_over = False
            self.doubled_down = False
            self.first_move = True
            self.previous_winnings = 0
            self.previous_losses = 0
            self.bet_amount = self.previous_bet  # Gebruik de vorige inzet in plaats van 10
            if self.player_balance >= self.bet_amount:
                self.player_balance -= self.bet_amount
            else:
                self.status_message = "Niet genoeg saldo! Brokie!"
                return

            # Initial cards deal
            for _ in range(2):
                self.player_hand.add_card(self.deck.draw_card())
                self.dealer_hand.add_card(self.deck.draw_card())


            # Step 3: Check Available Moves
            card1 = self.player_hand.cards[0].split('_')[0]
            card2 = self.player_hand.cards[1].split('_')[0]
            can_split = (len(self.player_hand.cards) == 2 and
                         ((card1 in ['10', 'jack', 'queen', 'king'] and card2 in ['10', 'jack', 'queen', 'king']) or
                          (card1 == card2)))

            # Step 4: Main Game Loop
            while not self.round_over:
                screen.fill(GREEN)
                screen.blit(background, (0, 0))

                # Draw action buttons
                hit_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 80, 100, 50))
                stand_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 80, 100, 50))
                double_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT - 80, 100, 50)) if self.first_move and not self.doubled_down else None
                split_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT - 80, 100, 50)) if can_split and self.split_hand is None else None

                # Display hands and totals
                dealer_x = SCREEN_WIDTH // 2 - (len(self.dealer_hand.cards) * 15)  # Center dealer's hand
                self.dealer_hand.display(dealer_x, 100, hide_first=self.player_turn, hide_all_except_first=self.player_turn)

                # Display the value of the first card during the player's turn
                if self.player_turn and not self.round_over:
                    first_card = self.dealer_hand.cards[0]
                    first_card_value = first_card.split('_')[0]
                    if first_card_value in ['jack', 'queen', 'king']:
                        first_card_value = 10
                    elif first_card_value == 'ace':
                        first_card_value = 11
                    else:
                        first_card_value = int(first_card_value)
                    display_text(f"Dealer Shows: {first_card_value}", dealer_x, 250, WHITE)
                elif not self.player_turn or self.round_over:
                    display_text(f"Dealer Total: {self.dealer_hand.total_value}", dealer_x, 250, WHITE)

                if self.split_hand:
                    # Display split hands below the dealer's hand
                    self.player_hand.display(SCREEN_WIDTH // 2 - 200, 400)
                    self.split_hand.display(SCREEN_WIDTH // 2 + 50, 400)
                    display_text(f"Hand 1: {self.player_hand.total_value}", SCREEN_WIDTH // 2 - 200, 550, WHITE)
                    display_text(f"Hand 2: {self.split_hand.total_value}", SCREEN_WIDTH // 2 + 50, 550, WHITE)

                    # Draw arrows to indicate the active hand
                    arrow_width = 20  # Width of the arrow
                    arrow_height = 10  # Height of the arrow
                    arrow_offset = 10  # Space between the arrow and the cards

                    if self.active_hand == self.player_hand:
                        # Draw arrow above Hand 1
                        pygame.draw.polygon(screen, YELLOW, [
                            (SCREEN_WIDTH // 2 - 200 + CARD_WIDTH, 390 - arrow_offset),  # Left base of the arrow
                            (SCREEN_WIDTH // 2 - 200 + CARD_WIDTH - arrow_width, 390 - arrow_offset - arrow_height),  # Left tip of the arrow
                            (SCREEN_WIDTH // 2 - 200 + CARD_WIDTH + arrow_width, 390 - arrow_offset - arrow_height)  # Right tip of the arrow
                        ])
                    elif self.active_hand == self.split_hand:
                        # Draw arrow above Hand 2
                        pygame.draw.polygon(screen, YELLOW, [
                            (SCREEN_WIDTH // 2 + 50 + CARD_WIDTH, 390 - arrow_offset),  # Left base of the arrow
                            (SCREEN_WIDTH // 2 + 50 + CARD_WIDTH - arrow_width, 390 - arrow_offset - arrow_height),  # Left tip of the arrow
                            (SCREEN_WIDTH // 2 + 50 + CARD_WIDTH + arrow_width, 390 - arrow_offset - arrow_height)  # Right tip of the arrow
                        ])
                else:
                    # Display single hand below the dealer's hand
                    self.player_hand.display(SCREEN_WIDTH // 2 - 75, 400)
                    display_text(f"Player Total: {self.player_hand.total_value}", SCREEN_WIDTH // 2 - 75, 550, WHITE)

                display_text(f"Balance: ${self.player_balance}", 20, 20, RED if self.player_balance == 0 else WHITE)
                display_text(f"Bet: ${self.bet_amount}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 130, WHITE)

                # Button Labels (centered on buttons)
                display_text("Hit", hit_rect.x + 25, hit_rect.y + 15, BLACK, button_font)
                display_text("Stand", stand_rect.x + 20, stand_rect.y + 15, BLACK, button_font)
                if double_rect:
                    display_text("Double", double_rect.x + 10, double_rect.y + 15, BLACK, button_font)
                if split_rect:
                    display_text("Split", split_rect.x + 25, split_rect.y + 15, BLACK, button_font)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        self.round_over = True
                        selecting_bet = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        if hit_rect.collidepoint(mouse_pos) and self.player_turn:
                            self.active_hand.add_card(self.deck.draw_card())
                            self.first_move = False  # Disable doubling down after hitting

                            if self.active_hand.total_value > 21:  # Check if the active hand busts
                                self.active_hand.is_bust = True  # Mark the hand as busted

                                if self.split_hand and self.active_hand == self.player_hand:
                                    # If the first hand busts and there is a second hand, switch to that hand
                                    self.active_hand = self.split_hand
                                    self.first_move = True  # Reset the first move for the second hand
                                    self.status_message = "Hand 1 Busted! Switching to Hand 2."
                                else:
                                    # If both hands are busted or there's no split, end the round
                                    if self.split_hand and self.split_hand.is_bust:
                                        self.status_message = "Both Hands Busted! Dealer Wins."
                                    else:
                                        self.status_message = "You Busted! Dealer Wins."
                                    self.round_over = True

                        elif stand_rect.collidepoint(mouse_pos):
                            if self.split_hand and self.active_hand == self.player_hand:
                                # Player stands on the first hand, switch to the second hand
                                self.active_hand = self.split_hand
                                self.first_move = True  # Reset the first move for Hand 2
                            else:
                                # Both hands are played, dealer's turn
                                self.player_turn = False
                                self.handle_dealer_turn()

                        elif double_rect and double_rect.collidepoint(mouse_pos):  # Check if double_rect exists
                            if self.first_move:  # Double down only possible on the first move
                                if self.bet_amount > self.player_balance:
                                    self.status_message = "Not enough balance for double down! Brokie!"
                                    if self.active_hand.is_bust: # Add this line
                                        if self.split_hand and self.active_hand == self.player_hand:
                                            self.active_hand = self.split_hand
                                            self.first_move = True
                                            self.status_message = "Hand 1 Busted! Switching to Hand 2."
                                        else:
                                            if self.split_hand and self.split_hand.is_bust:
                                                self.status_message = "Both Hands Busted! Dealer Wins."
                                            else:
                                                self.status_message = "You Busted! Dealer Wins."
                                            self.round_over = True
                                    else:
                                        self.player_turn = False
                                        self.handle_dealer_turn()
                                else:
                                    self.player_balance -= self.bet_amount
                                    self.bet_amount *= 2
                                    self.active_hand.add_card(self.deck.draw_card())
                                    self.first_move = False
                                    self.doubled_down = True
                                    self.player_turn = False
                                    self.handle_dealer_turn()

                        elif split_rect and split_rect.collidepoint(mouse_pos):  # Check if split_rect exists
                            if self.can_split and self.split_hand is None:
                                # Player splits, create second hand
                                self.split_hand = PlayerHand()

                                # Move the card to the second hand and update both hands
                                card_to_move = self.player_hand.cards.pop()
                                self.split_hand.add_card(card_to_move)

                                remaining_card = self.player_hand.cards[0]  # The card left in the original hand
                                self.player_hand.clear_hand()
                                self.player_hand.add_card(remaining_card)

                                # Add one new card to each hand
                                self.player_hand.add_card(self.deck.draw_card())  
                                self.split_hand.add_card(self.deck.draw_card())

                                # Double the bet for the second hand
                                self.player_balance -= self.bet_amount  # Deduct the bet for the second hand
                                self.bet_amount *= 2  # Double the bet

                                # Set active hand to the first hand and reset necessary flags
                                self.active_hand = self.player_hand
                                self.first_move = True  # Reset first_move for the first hand to allow doubling down
                                self.can_split = False  # Prevent splitting again after splitting

            # Step 5: Next Round or Exit
            waiting_for_next_round = True
            next_round_rect = None
            menu_rect = None
            exit_rect = None

            while waiting_for_next_round:
                screen.fill(GREEN)
                screen.blit(background, (0, 0))

                # Display the status message
                display_text(self.status_message, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, RED)
                
                # Display buttons for next round and main menu
                if self.player_balance > 0:
                    next_round_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 20, 140, 50))
                    display_text("Next Round", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 35, BLACK, button_font)
                    
                    menu_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 120, 140, 50))
                    display_text("Back to Menu", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 135, BLACK, button_font)
                
                if self.player_balance <= 0:
                    exit_rect = pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 35, 140, 50))
                    display_text("Exit Game", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 35, WHITE, button_font)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        waiting_for_next_round = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if next_round_rect and next_round_rect.collidepoint(mouse_pos):  #  Controleer eerst of het niet None is
                            waiting_for_next_round = False
                        elif menu_rect and menu_rect.collidepoint(mouse_pos):  #  Controleer of menu_rect bestaat
                            return  
                        elif exit_rect and exit_rect.collidepoint(mouse_pos):  #  Alleen als exit_rect bestaat
                            pygame.quit()
                            exit()

def main_menu():
    running = True
    while running:
        screen.fill(GREEN)
        screen.blit(background, (0, 0))

        # Display title
        display_text("Blackjack", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 200, WHITE, title_font)

        # Calculate button positions
        button_width, button_height = 140, 50
        play_button_x = SCREEN_WIDTH // 2 - button_width // 2
        play_button_y = SCREEN_HEIGHT // 2 - button_height // 2
        quit_button_x = SCREEN_WIDTH // 2 - button_width // 2
        quit_button_y = SCREEN_HEIGHT // 2 + 75

        # Draw buttons
        play_rect = pygame.draw.rect(screen, WHITE, (play_button_x, play_button_y, button_width, button_height))
        quit_rect = pygame.draw.rect(screen, RED, (quit_button_x, quit_button_y, button_width, button_height))

        # Display button text
        display_text("Play", play_button_x + 45, play_button_y + 15, BLACK, button_font)
        display_text("Quit", quit_button_x + 45, quit_button_y + 15, WHITE, button_font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_rect.collidepoint(mouse_pos):
                    game = BlackjackGame()
                    game.run()  # Start the game
                elif quit_rect.collidepoint(mouse_pos):
                    running = False

    pygame.quit()

if __name__ == "__main__":
    main_menu()