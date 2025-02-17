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
YELLOW = (255, 255, 0)

# Create the game screen in fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()  # Get new screen size after switching to fullscreen

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
            self.ace_count += 1
            self.total_value += 11
        else:
            self.total_value += int(rank)

        while self.total_value > 21 and self.ace_count > 0:
            self.total_value -= 10
            self.ace_count -= 1

    def display(self, x, y, hide_first=False):
        """Render cards on screen."""
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                screen.blit(CARD_BACK, (x + i * 30, y))
            else:
                screen.blit(CARD_IMAGES[card], (x + i * 30, y))

    def clear_hand(self):
        """Clear the hand for a new round."""
        self.cards = []
        self.total_value = 0
        self.ace_count = 0

def determine_winner(player, dealer, split_hand=None):
    """Bepaalt de winnaar per hand en toont correcte uitslagen voor beide handen."""
    results = []
    multiple_hands = split_hand is not None  # Check of er twee handen zijn

    def get_result(hand_name, player_hand):
        if player_hand.total_value > 21:
            return f"{hand_name}Dealer Wins!"
        elif dealer.total_value > 21 or player_hand.total_value > dealer.total_value:
            game.player_balance += game.bet_amount * 2  # Winst = dubbel de inzet
            return f"{hand_name}Player Wins!"
        elif player_hand.total_value == dealer.total_value:
            game.player_balance += game.bet_amount  # ✅ Gelijkspel = inzet terug
            return f"{hand_name}Tie!"
        else:
            return f"{hand_name}Dealer Wins!"

    # Hand 1 resultaat toevoegen
    result1 = get_result("Hand 1: " if multiple_hands else "", player)
    results.append(result1)

    # Hand 2 resultaat toevoegen (indien aanwezig)
    if split_hand:
        result2 = get_result("Hand 2: ", split_hand)
        results.append(result2)

    # Controleer of er gemengde resultaten zijn
    if "Player Wins!" in results and "Dealer Wins!" in results:
        return "Split Result: One Win, One Loss"
    else:
        return " | ".join(results)

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
        self.split_hand = None
        self.active_hand = self.player_hand
        self.first_move = True  # Houdt bij of dit de eerste zet is
        self.can_split = True   # Houdt bij of splitsen nog is toegestaan
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
                self.status_message = determine_winner(self.player_hand, self.dealer_hand, self.split_hand)
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
                display_text(f"Balance: ${self.player_balance}", 20, 20, RED if self.player_balance == 0 else WHITE)
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
                            if self.bet_amount > self.player_balance:  # Check of er genoeg saldo is
                                self.status_message = "Niet genoeg saldo!"
                            else:
                                selecting_bet = False


            # 🛑 Step 2: Start Round
            self.deck = CardDeck()
            self.player_hand = PlayerHand()
            self.dealer_hand = PlayerHand()
            self.split_hand = None
            self.active_hand = self.player_hand  # Track active hand
            self.player_turn = True
            self.round_over = False
            self.doubled_down = False
            self.first_move = True  # ✅ Track if it's the player's first move
            if self.player_balance >= self.bet_amount:
                self.player_balance -= self.bet_amount
            else:
                self.status_message = "Niet genoeg saldo!"
                return  # Stop de ronde als er te weinig saldo is


            # Initial cards deal
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
                display_text(f"Player Total (Hand 1): {self.player_hand.total_value}", 200, 550, WHITE)
                if self.split_hand:
                    display_text(f"Player Total (Hand 2): {self.split_hand.total_value}", 500, 550, WHITE)
                display_text(f"Dealer Total: {'?' if self.player_turn else self.dealer_hand.total_value}", 200, 250, WHITE)
                display_text(f"Balance: ${self.player_balance}", 20, 20)
                display_text(f"Bet: ${self.bet_amount}", SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 50, WHITE)

                # **Display active hand indicator only when splitting**
                if self.split_hand:
                    if self.active_hand == self.player_hand:
                        pygame.draw.rect(screen, (255, 0, 0), (200, 390, CARD_WIDTH * 2, CARD_HEIGHT), 5)  # Red border for Hand 1
                    elif self.active_hand == self.split_hand:
                        pygame.draw.rect(screen, (255, 0, 0), (500, 390, CARD_WIDTH * 2, CARD_HEIGHT), 5)  # Red border for Hand 2

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
                        selecting_bet = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        if bet_rect_plus.collidepoint(mouse_pos) and self.bet_amount + 50 <= self.player_balance:
                            self.bet_amount += 50
                        elif bet_rect_minus.collidepoint(mouse_pos) and self.bet_amount - 50 >= 50:
                            self.bet_amount -= 50
                        elif start_rect.collidepoint(mouse_pos):
                            if self.bet_amount > self.player_balance:
                                self.status_message = "Not enough balance!"
                                continue  # Blijf in de bet-selectie-loop
                            else:
                                self.player_balance -= self.bet_amount


                        if hit_rect.collidepoint(mouse_pos) and self.player_turn:
                            self.active_hand.add_card(self.deck.draw_card())

                            if self.active_hand.total_value > 21:  # Check of de actieve hand bust gaat
                                self.active_hand.is_bust = True  # Markeer de hand als bust

                                if self.split_hand and self.active_hand == self.player_hand:
                                    # Als de eerste hand bust gaat en er is een tweede hand, wissel naar die hand
                                    self.active_hand = self.split_hand
                                    self.first_move = True  # Reset de eerste zet voor de tweede hand
                                    self.status_message = "Hand 1 Busted! Switching to Hand 2."
                                else:
                                    # Als beide handen bust zijn of als er geen split is, verlies direct
                                    if self.split_hand and self.split_hand.is_bust:
                                        self.status_message = "Both Hands Busted! Dealer Wins."
                                    else:
                                        self.status_message = "You Busted! Dealer Wins."
                                    self.round_over = True



                        elif stand_rect.collidepoint(mouse_pos):
                            if self.split_hand and self.active_hand == self.player_hand:
                                # Speler heeft gestand op eerste hand, wissel naar tweede hand
                                self.active_hand = self.split_hand
                                self.first_move = True  # Reset eerste zet voor Hand 2
                            else:
                                # Beide handen zijn gespeeld, dealer is aan de beurt
                                self.player_turn = False
                                while self.dealer_hand.total_value < 17:
                                    self.dealer_hand.add_card(self.deck.draw_card())
                                self.round_over = True
                                self.status_message = determine_winner(self.player_hand, self.dealer_hand, self.split_hand)



                        elif double_rect and double_rect.collidepoint(mouse_pos):
                            if self.first_move:  # Double down only possible on first move
                                if self.bet_amount > self.player_balance:
                                    self.status_message = "Not enough balance for double down!"
                                else:
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
                            if self.can_split and self.split_hand is None:
                                self.split_hand = PlayerHand()
                                
                                # Verplaats de kaart naar de tweede hand en update beide handen opnieuw
                                card_to_move = self.player_hand.cards.pop()
                                self.split_hand.add_card(card_to_move)
                                
                                remaining_card = self.player_hand.cards[0]  # De kaart die achterblijft na split
                                self.player_hand.clear_hand()
                                self.player_hand.add_card(remaining_card)
                                
                                # Voeg nieuwe kaarten toe aan beide handen
                                self.player_hand.add_card(self.deck.draw_card())  
                                self.split_hand.add_card(self.deck.draw_card())  
                                
                                print(f"Hand 1: {self.player_hand.cards}, waarde: {self.player_hand.total_value}")
                                print(f"Hand 2: {self.split_hand.cards}, waarde: {self.split_hand.total_value}")
                                
                                self.active_hand = self.player_hand  
                                self.first_move = False  # Zorgt ervoor dat de hand niet opnieuw gesplitst kan worden
                                self.can_split = False  # Voorkomt dat er na een hit opnieuw gesplitst wordt

                        elif hit_rect and hit_rect.collidepoint(mouse_pos):
                            # Speler kiest om te hitten
                            if self.active_hand:
                                self.active_hand.add_card(self.deck.draw_card())
                                self.can_split = False  # Na een hit mag er niet meer gesplitst worden
  



            # In de BlackjackGame class, bij de 'Next Round' knop
            waiting_for_next_round = True
            next_round_rect = None  # ✅ Zorgt ervoor dat de variabele altijd bestaat
            menu_rect = None  # ✅ Zorgt ervoor dat deze variabele ook altijd bestaat
            exit_rect = None  # ✅ Exit-knop bestaat nu altijd, maar wordt alleen gebruikt indien nodig

            while waiting_for_next_round:
                screen.fill(GREEN)
                if background:
                    screen.blit(background, (0, 0))

                self.player_hand.display(200, 400)
                if self.split_hand:
                    self.split_hand.display(500, 400)
                self.dealer_hand.display(200, 100, hide_first=False)

                display_text(self.status_message, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, RED)
                
                if self.player_balance > 0:
                    next_round_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 20, 140, 50))
                    display_text("Next Round", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 35, BLACK)
                    
                    menu_rect = pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 120, 140, 50))
                    display_text("Back to Menu", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 135, BLACK)
                
                if self.player_balance <= 0:
                    exit_rect = pygame.draw.rect(screen, RED, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 35, 140, 50))
                    display_text("Exit Game", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 35, WHITE)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_playing = False
                        waiting_for_next_round = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if next_round_rect and next_round_rect.collidepoint(mouse_pos):  # ✅ Controleer eerst of het niet None is
                            waiting_for_next_round = False
                        elif menu_rect and menu_rect.collidepoint(mouse_pos):  # ✅ Controleer of menu_rect bestaat
                            return  
                        elif exit_rect and exit_rect.collidepoint(mouse_pos):  # ✅ Alleen als exit_rect bestaat
                            pygame.quit()
                            exit()



    def reset_round(self):
        """Reset all necessary variables for the next round."""
        self.player_hand.clear_hand()
        self.split_hand = None
        self.dealer_hand.clear_hand()
        self.first_move = True
        self.doubled_down = False
        self.round_over = False
        self.active_hand = self.player_hand
                        
        
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()