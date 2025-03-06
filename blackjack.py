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
background_path = "background.jpg"
if not os.path.exists(background_path):
    raise FileNotFoundError(f"Background image '{background_path}' not found!")
background = pygame.transform.scale(pygame.image.load(background_path), (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load Card Assets
card_back_path = "cards/back.png"
if not os.path.exists(card_back_path):
    raise FileNotFoundError(f"Card back image '{card_back_path}' not found!")
CARD_BACK = pygame.transform.scale(pygame.image.load(card_back_path), (CARD_WIDTH, CARD_HEIGHT))

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

# Card Flip Animation
def flip_card_animation(card, x, y):
    """Simulate a card flip animation."""
    for i in range(10):
        screen.blit(CARD_BACK, (x, y))
        pygame.display.flip()
        pygame.time.delay(50)
    screen.blit(CARD_IMAGES[card], (x, y))
    pygame.display.flip()

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

    def display(self, x, y, hide_second_card=False):
        """Render cards on screen."""
        for i, card in enumerate(self.cards):
            if hide_second_card and i == 1:
                # Hide the second card
                screen.blit(CARD_BACK, (x + i * 30, y))
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
            game.previous_losses += game.current_bet
            game.player_balance -= game.current_bet  # Deduct the bet if the player loses
            return f"{hand_name}Dealer Wins!"
        elif dealer.is_bust or player_hand.total_value > dealer.total_value:
            game.previous_winnings += game.current_bet * 2
            game.player_balance += game.current_bet * 2  # Add double the bet if the player wins
            return f"{hand_name}Player Wins!"
        elif player_hand.total_value == dealer.total_value:
            game.player_balance += game.current_bet  # Return the bet if it's a tie
            return f"{hand_name}Tie!"
        else:
            game.previous_losses += game.current_bet
            game.player_balance -= game.current_bet  # Deduct the bet if the player loses
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
        self.original_bet = 10  # Default bet amount (set during bet placement)
        self.current_bet = self.original_bet  # Current bet amount (can be doubled)
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

            if hit_rect.collidepoint(mouse_pos) and self.player_turn:
                self.active_hand.add_card(self.deck.draw_card())
                self.first_move = False  # Disable doubling down after hitting

                if self.active_hand.total_value > 21:  # Check if the active hand busts
                    self.active_hand.is_bust = True  # Mark the hand as busted

                    if self.split_hand and self.active_hand == self.player_hand:
                        self.active_hand = self.split_hand
                        self.first_move = True  # Reset the first move for the second hand
                        self.status_message = "Hand 1 Busted! Switching to Hand 2."
                    else:
                        if self.split_hand and self.split_hand.is_bust:
                            self.status_message = "Hand 2 Busted! Dealer Wins."
                        else:
                            self.status_message = "You Busted! Dealer Wins."
                        self.round_over = True

            elif stand_rect.collidepoint(mouse_pos):
                if self.split_hand and self.active_hand == self.player_hand:
                    self.active_hand = self.split_hand
                    self.first_move = True  # Reset the first move for Hand 2
                    self.status_message = "Switching to Hand 2."
                else:
                    self.player_turn = False
                    self.handle_dealer_turn()

            elif double_rect and double_rect.collidepoint(mouse_pos):  # Check if double_rect exists
                if self.first_move:  # Double down only possible on the first move
                    if self.player_balance < self.current_bet:  # Check if the player has enough balance
                        self.status_message = "Not enough balance for double down! Brokie!"
                    else:
                        self.player_balance -= self.current_bet  # Deduct the current bet
                        self.current_bet *= 2  # Double the current bet
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
                            else:
                                self.player_turn = False
                                self.handle_dealer_turn()
                        else:
                            if self.split_hand and self.active_hand == self.player_hand:
                                self.active_hand = self.split_hand
                                self.first_move = True
                                self.status_message = "Doubled Down! Switching to Hand 2."
                            else:
                                self.player_turn = False
                                self.handle_dealer_turn()

            elif split_rect and split_rect.collidepoint(mouse_pos):
                if self.can_split and self.split_hand is None and self.player_balance >= self.current_bet:
                    self.split_hand = PlayerHand()
                    card_to_move = self.player_hand.cards.pop()
                    self.split_hand.add_card(card_to_move)
                    remaining_card = self.player_hand.cards[0]  # The card left in the original hand
                    self.player_hand.clear_hand()  # Clear and reset the original hand
                    self.player_hand.add_card(remaining_card)
                    self.player_hand.add_card(self.deck.draw_card())
                    self.split_hand.add_card(self.deck.draw_card())
                    self.player_balance -= self.current_bet
                    self.current_bet *= 2
                    self.can_split = False
                    self.status_message = "Hand split! Playing Hand 1 first."

    def handle_dealer_turn(self):
        """Handle the dealer's turn and determine the winner."""
        # Reveal the hidden card with a flip animation
        flip_card_animation(self.dealer_hand.cards[1], SCREEN_WIDTH // 2 - 50 + 30, 100)  # Flip the second card

        # Dealer hits until reaching 17 or higher
        while self.dealer_hand.total_value < 17:
            new_card = self.deck.draw_card()
            self.dealer_hand.add_card(new_card)
            
            # Animate the new card being dealt
            for i in range(10):
                screen.blit(CARD_BACK, (SCREEN_WIDTH // 2 - 50 + (len(self.dealer_hand.cards) - 1) * 30, 100))
                pygame.display.flip()
                pygame.time.delay(50)
            
            screen.blit(CARD_IMAGES[new_card], (SCREEN_WIDTH // 2 - 50 + (len(self.dealer_hand.cards) - 1) * 30, 100))
            pygame.display.flip()
            pygame.time.delay(500)  # Add a slight delay for realism

            # Update dealer's total value display
            dealer_x = SCREEN_WIDTH // 2 - 50  # Center dealer's hand
            display_text(f"Dealer Total: {self.dealer_hand.total_value}", dealer_x, 250, WHITE)
            pygame.display.flip()

        self.round_over = True
        self.status_message = determine_winner(self.player_hand, self.dealer_hand, self, self.split_hand)
        if "Player Wins!" in self.status_message:
            display_winning_animation()  # Show winning animation if the player wins
        elif "Dealer Wins!" in self.status_message:
            display_balance_change(-self.current_bet)  # Show loss animation
        else:
            display_balance_change(0)  # Show tie animation

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
                display_text(f"Bet: ${self.original_bet}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 50, WHITE)
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
                        if bet_rect_plus.collidepoint(mouse_pos) and self.original_bet + 5 <= self.player_balance:
                            self.original_bet += 5  # Update original_bet
                            self.current_bet = self.original_bet  # Reset current_bet to original_bet
                            self.previous_winnings = 0
                            self.previous_losses = 0
                        elif bet_rect_minus.collidepoint(mouse_pos) and self.original_bet - 5 >= 5:
                            self.original_bet -= 5  # Update original_bet
                            self.current_bet = self.original_bet  # Reset current_bet to original_bet
                            self.previous_winnings = 0
                            self.previous_losses = 0
                        elif start_rect.collidepoint(mouse_pos):
                            if self.original_bet > self.player_balance:
                                self.status_message = "Not enough balance! Brokie!"
                            else:
                                selecting_bet = False

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
            self.current_bet = self.original_bet  # Reset current_bet to original_bet
            if self.player_balance >= self.current_bet:
                self.player_balance -= self.current_bet  # Deduct the bet at the start of the round
            else:
                self.status_message = "Not enough balance! Brokie!"
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
                dealer_x = SCREEN_WIDTH // 2 - 50  # Center dealer's hand
                self.dealer_hand.display(dealer_x, 100, hide_second_card=self.player_turn)

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
                display_text(f"Bet: ${self.current_bet}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 130, WHITE)

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
                                self.status_message = "Switching to Hand 2."
                            else:
                                # Both hands are played, dealer's turn
                                self.player_turn = False
                                self.handle_dealer_turn()

                        elif double_rect and double_rect.collidepoint(mouse_pos):  # Check if double_rect exists
                            if self.first_move:  # Double down only possible on the first move
                                if self.player_balance < self.current_bet:  # Check if the player has enough balance
                                    self.status_message = "Not enough balance for double down! Brokie!"
                                else:
                                    self.player_balance -= self.current_bet  # Deduct the current bet
                                    self.current_bet *= 2  # Double the current bet
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
                                        else:
                                            self.player_turn = False
                                            self.handle_dealer_turn()
                                    else:
                                        if self.split_hand and self.active_hand == self.player_hand:
                                            self.active_hand = self.split_hand
                                            self.first_move = True
                                            self.status_message = "Doubled Down! Switching to Hand 2."
                                        else:
                                            self.player_turn = False
                                            self.handle_dealer_turn()

                        elif split_rect and split_rect.collidepoint(mouse_pos):
                            if self.can_split and self.split_hand is None and self.player_balance >= self.current_bet:
                                self.split_hand = PlayerHand()
                                card_to_move = self.player_hand.cards.pop()
                                self.split_hand.add_card(card_to_move)
                                remaining_card = self.player_hand.cards[0]  # The card left in the original hand
                                self.player_hand.clear_hand()  # Clear and reset the original hand
                                self.player_hand.add_card(remaining_card)
                                self.player_hand.add_card(self.deck.draw_card())
                                self.split_hand.add_card(self.deck.draw_card())
                                self.player_balance -= self.current_bet
                                self.current_bet *= 2
                                self.can_split = False
                                self.status_message = "Hand split! Playing Hand 1 first."

            # Step 5: Next Round or Exit
            waiting_for_next_round = True
            next_round_rect = None
            menu_rect = None
            exit_rect = None

            while waiting_for_next_round:
                screen.fill(GREEN)
                screen.blit(background, (0, 0))

                # Display the final hands of the dealer and player on the left side
                dealer_x = 50  # Position dealer's hand on the left side
                self.dealer_hand.display(dealer_x, 100)  # Show all dealer cards
                display_text(f"Dealer Total: {self.dealer_hand.total_value}", dealer_x, 250, WHITE)

                if self.split_hand:
                    # Display split hands below the dealer's hand
                    self.player_hand.display(50, 400)  # Position Hand 1 on the left side
                    self.split_hand.display(50, 550)  # Position Hand 2 below Hand 1
                    display_text(f"Hand 1: {self.player_hand.total_value}", 50, 700, WHITE)
                    display_text(f"Hand 2: {self.split_hand.total_value}", 50, 730, WHITE)
                else:
                    # Display single hand below the dealer's hand
                    self.player_hand.display(50, 400)  # Position player's hand on the left side
                    display_text(f"Player Total: {self.player_hand.total_value}", 50, 550, WHITE)

                # Display the status message with smaller font
                smaller_font = pygame.font.Font(None, 48)  # Smaller font for winner text
                display_text(self.status_message, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, RED, smaller_font)

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
                        if next_round_rect and next_round_rect.collidepoint(mouse_pos):  # Check if next_round_rect exists
                            waiting_for_next_round = False
                        elif menu_rect and menu_rect.collidepoint(mouse_pos):  # Check if menu_rect exists
                            return  
                        elif exit_rect and exit_rect.collidepoint(mouse_pos):  # Check if exit_rect exists
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