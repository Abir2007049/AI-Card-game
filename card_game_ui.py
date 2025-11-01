import pygame
import sys
import random
import math
from typing import List, Optional, Tuple, Callable
from main import (
    best_move_when_playing_first, 
    best_move_when_playing_second,
    evaluate_state,
    minimax
)

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_MARGIN = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
DARK_BLUE = (25, 25, 112)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)

# Table colors (for gradient)
TABLE_DARK = (9, 66, 48)
TABLE_LIGHT = (14, 109, 73)

# Fonts
font_large = pygame.font.Font(None, 40)
font_medium = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)
font_title = pygame.font.Font(None, 56)


def draw_vertical_gradient(surface: pygame.Surface, top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]):
    """Fill the surface with a vertical gradient from top_color to bottom_color."""
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], border_color: Tuple[int, int, int] = (0, 0, 0), radius: int = 16, border: int = 2):
    """Draw a rounded rectangle panel."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


class Button:
    def __init__(self, rect: pygame.Rect, label: str, bg=(40, 40, 40), fg=WHITE, hover_bg=(70, 70, 70)):
        self.rect = rect
        self.label = label
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.hovered = False

    def draw(self, surface):
        color = self.hover_bg if self.hovered else self.bg
        draw_panel(surface, self.rect, color, border_color=(180, 180, 180), radius=12, border=2)
        text = font_medium.render(self.label, True, self.fg)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def contains_point(self, pos):
        return self.rect.collidepoint(pos)

class Card:
    def __init__(self, value: int, x: int = 0, y: int = 0):
        self.value = value
        self.x = x
        self.y = y
        self.width = CARD_WIDTH
        self.height = CARD_HEIGHT
        self.selected = False
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
    def draw(self, screen, face_up=True, highlight=False):
        """Draw the card on screen"""
        # Shadow (alpha-safe)
        shadow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        screen.blit(shadow, (self.rect.x + 4, self.rect.y + 6))

        # Card background
        color = WHITE if face_up else BLUE
        if highlight:
            color = GOLD if face_up else LIGHT_GRAY

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        if face_up:
            # Card value
            text_color = RED if self.value > 20 else BLACK
            text = font_large.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
            
            # Small value in corners
            small_text = font_small.render(str(self.value), True, text_color)
            screen.blit(small_text, (self.rect.x + 8, self.rect.y + 6))
            screen.blit(small_text, (self.rect.right - 28, self.rect.bottom - 24))
        else:
            # Card back pattern
            pygame.draw.rect(screen, DARK_BLUE, 
                           (self.rect.x + 10, self.rect.y + 10, 
                            self.rect.width - 20, self.rect.height - 20))
    
    def contains_point(self, x, y):
        """Check if point is inside card"""
        return self.rect.collidepoint(x, y)
    
    def update_position(self, x, y):
        """Update card position"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class GameUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Card Duel - Minimax vs Human")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.human_cards = []
        self.ai_cards = []
        self.unseen_cards = []
        self.human_score = 0
        self.ai_score = 0
        self.round_num = 1
        self.first_player = "Human"
        self.game_phase = "menu"  # menu, human_turn, ai_turn, round_end, game_over
        self.selected_card = None
        self.human_played_card = None
        self.ai_played_card = None
        self.message = "Welcome to AI Card Duel!"
        self.ai_thinking = False
        self.played_values = set()

        # Animations and hover
        self.animations: List[dict] = []  # {card, tx, ty, speed, on_done}
        self.human_ready = False
        self.ai_ready = False
        self.hover_lift = 14
        self.hovered_card: Optional[Card] = None
        
        # UI Buttons
        self.btn_start = Button(pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 20, 200, 50), "Start Game")
        self.btn_restart = Button(pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 90, 200, 46), "Restart (R)")
        
        # UI positions
        self.human_hand_y = SCREEN_HEIGHT - 150
        self.ai_hand_y = 50
        self.play_area_y = SCREEN_HEIGHT // 2 - 60
        
    def setup_game(self):
        """Initialize a new game"""
        cards = list(range(1, 31))
        random.shuffle(cards)
        
        # Create card objects
        human_card_values = sorted(cards[:10])
        ai_card_values = sorted(cards[10:20])
        unseen_card_values = sorted(cards[20:])
        
        self.human_cards = []
        for i, value in enumerate(human_card_values):
            x = 50 + i * (CARD_WIDTH + CARD_MARGIN)
            y = self.human_hand_y
            self.human_cards.append(Card(value, x, y))
            
        self.ai_cards = []
        for i, value in enumerate(ai_card_values):
            x = 50 + i * (CARD_WIDTH + CARD_MARGIN)
            y = self.ai_hand_y
            self.ai_cards.append(Card(value, x, y))
            
        self.unseen_cards = [Card(value) for value in unseen_card_values]
        
        self.human_score = 0
        self.ai_score = 0
        self.round_num = 1
        self.first_player = "Human"
        self.game_phase = "human_turn" if self.first_player == "Human" else "ai_turn"
        self.message = f"Round {self.round_num} - {self.first_player} plays first!"
        self.human_ready = False
        self.ai_ready = False
        self.animations.clear()
        self.selected_card = None
        self.human_played_card = None
        self.ai_played_card = None
        self.played_values = set()
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_phase in ("setup", "menu"):
                    self.setup_game()
                elif event.key == pygame.K_r and self.game_phase == "game_over":
                    self.setup_game()
                elif event.key == pygame.K_ESCAPE:
                    self.game_phase = "menu"
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.game_phase == "menu":
                        if self.btn_start.contains_point(event.pos):
                            self.setup_game()
                    else:
                        self.handle_mouse_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_move(event.pos)
                    
        return True
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        
        if self.game_phase == "human_turn":
            # Check if clicking on a human card
            for card in self.human_cards:
                if card.contains_point(x, y):
                    self.selected_card = card
                    self.play_human_card(card)
                    break

    def handle_mouse_move(self, pos):
        if self.game_phase != "human_turn":
            if self.hovered_card:
                # restore
                self.hovered_card.update_position(self.hovered_card.x, self.human_hand_y)
                self.hovered_card = None
            return
        x, y = pos
        new_hover = None
        for card in self.human_cards:
            if card.contains_point(x, y):
                new_hover = card
                break
        if new_hover is not self.hovered_card:
            # restore previous
            if self.hovered_card:
                self.hovered_card.update_position(self.hovered_card.x, self.human_hand_y)
            self.hovered_card = new_hover
            if self.hovered_card:
                self.hovered_card.update_position(self.hovered_card.x, self.human_hand_y - self.hover_lift)
    
    def play_human_card(self, card):
        """Human plays a card"""
        if self.first_player == "Human":
            # Human plays first
            self.human_played_card = card
            self.human_cards.remove(card)
            self.layout_hand(self.human_cards, self.human_hand_y)
            # animate to play area
            hx, hy = self.get_play_positions()[0]
            self.animate_card_to(card, hx, hy, on_done=lambda: self._mark_ready("human"))
            self.game_phase = "ai_turn"
            self.message = "AI is thinking..."
            self.ai_thinking = True
        else:
            # Human responds to AI
            self.human_played_card = card
            self.human_cards.remove(card)
            self.layout_hand(self.human_cards, self.human_hand_y)
            hx, hy = self.get_play_positions()[0]
            self.animate_card_to(card, hx, hy, on_done=lambda: self._mark_ready("human"))
    
    def ai_turn(self):
        """AI makes its move"""
        if not self.ai_thinking:
            return
            
        ai_card_values = [card.value for card in self.ai_cards]
        human_card_values = [card.value for card in self.human_cards]
        
        if self.first_player == "AI":
            # AI plays first: build opponent pool from unknowns (no peeking at human hand)
            all_possible = set(range(1, 31))
            opp_pool = sorted(list(all_possible - set(ai_card_values) - self.played_values))
            best_value = best_move_when_playing_first(
                ai_card_values, opp_pool, 
                self.ai_score, self.human_score,
                depth=3, opp_hand_size=len(self.human_cards), samples=3
            )
        else:
            # AI responds to human
            best_value = best_move_when_playing_second(
                ai_card_values, self.human_played_card.value,
                self.ai_score, self.human_score,
                depth=3, opp_remaining_count=max(0, len(self.human_cards) - 1)
            )
        
        # Find and play the AI card
        for card in self.ai_cards:
            if card.value == best_value:
                self.ai_played_card = card
                self.ai_cards.remove(card)
                break
        self.layout_hand(self.ai_cards, self.ai_hand_y)
        
        ax, ay = self.get_play_positions()[1]
        self.animate_card_to(self.ai_played_card, ax, ay, on_done=lambda: self._mark_ready("ai"))

        if self.first_player == "AI":
            self.game_phase = "human_turn"
            self.message = f"AI played {self.ai_played_card.value}. Your turn!"
        self.ai_thinking = False
    
    def resolve_round(self):
        """Resolve the round and determine winner"""
        human_value = self.human_played_card.value
        ai_value = self.ai_played_card.value
        
        if human_value > ai_value:
            self.human_score += human_value + ai_value
            winner = "Human"
            self.first_player = "Human"
        elif ai_value > human_value:
            self.ai_score += human_value + ai_value
            winner = "AI"
            self.first_player = "AI"
        else:
            winner = "Tie"
            # Alternate first player on tie, to keep momentum
            self.first_player = "AI" if self.first_player == "Human" else "Human"
        
        # Record played cards for imperfect-information pool
        self.played_values.add(human_value)
        self.played_values.add(ai_value)
        
        self.message = f"Round {self.round_num}: {winner} wins! H:{human_value} vs AI:{ai_value}"
        self.round_num += 1
        
        # Reset played cards state
        self.human_played_card = None
        self.ai_played_card = None
        self.human_ready = False
        self.ai_ready = False

        # Next phase / round setup
        if self.round_num > 10:
            self.game_phase = "game_over"
            self.ai_thinking = False
            if self.human_score > self.ai_score:
                self.message = f"🎉 You Win! Final: You {self.human_score} - AI {self.ai_score}"
            elif self.ai_score > self.human_score:
                self.message = f"🤖 AI Wins! Final: AI {self.ai_score} - You {self.human_score}"
            else:
                self.message = f"🤝 Perfect Tie! Both scored {self.human_score}"
        else:
            self.game_phase = "human_turn" if self.first_player == "Human" else "ai_turn"
            self.message = f"Round {self.round_num} - {self.first_player} plays first!"
            # If AI starts, trigger thinking so update() calls ai_turn()
            self.ai_thinking = (self.first_player == "AI")

    def layout_hand(self, cards: List['Card'], y: int):
        """Reflow a hand horizontally with consistent spacing."""
        for i, card in enumerate(cards):
            target_x = 50 + i * (CARD_WIDTH + CARD_MARGIN)
            card.update_position(target_x, y)
    
    def draw_cards(self):
        """Draw all cards"""
        # Human hand
        for i, card in enumerate(self.human_cards):
            highlight = (card == self.selected_card)
            card.draw(self.screen, face_up=True, highlight=highlight)
        
        # AI hand (face down)
        for card in self.ai_cards:
            card.draw(self.screen, face_up=False)
        
        # Played cards
        if self.human_played_card:
            played_x = SCREEN_WIDTH // 2 - 100
            played_y = self.play_area_y + 50
            self.human_played_card.draw(self.screen, face_up=True)
            
        if self.ai_played_card:
            played_x = SCREEN_WIDTH // 2 + 20
            played_y = self.play_area_y - 50
            self.ai_played_card.draw(self.screen, face_up=True)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Background gradient (table felt)
        draw_vertical_gradient(self.screen, TABLE_DARK, TABLE_LIGHT)
        
        # Title
        title = font_title.render("AI Card Duel - Minimax Algorithm", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 25))
        self.screen.blit(title, title_rect)
        
        # Score panel
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 - 40, 440, 80)
        draw_panel(self.screen, panel_rect, (255, 255, 255,), border_color=(50, 50, 50), radius=16, border=2)
        score_text = font_large.render(f"You: {self.human_score}    AI: {self.ai_score}", True, BLACK)
        score_rect = score_text.get_rect(center=panel_rect.center)
        self.screen.blit(score_text, score_rect)
        
        # Round and turn info
        banner_rect = pygame.Rect(40, SCREEN_HEIGHT//2 - 70, 260, 44)
        draw_panel(self.screen, banner_rect, (0, 0, 0), border_color=(180, 180, 180), radius=12, border=2)
        round_text = font_medium.render(f"Round {self.round_num}/10", True, WHITE)
        fp_text = font_small.render(f"{self.first_player} plays first", True, LIGHT_GRAY)
        self.screen.blit(round_text, (banner_rect.x + 12, banner_rect.y + 6))
        self.screen.blit(fp_text, (banner_rect.x + 12, banner_rect.y + 22))
        
        # Message
        message_text = font_medium.render(self.message, True, WHITE)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(message_text, message_rect)
        
        # Labels
        human_label = font_medium.render("Your Cards (click to play)", True, WHITE)
        self.screen.blit(human_label, (50, self.human_hand_y - 30))
        
        ai_label = font_medium.render("AI Cards", True, WHITE)
        self.screen.blit(ai_label, (50, self.ai_hand_y - 30))
        
        # Instructions / Menus
        if self.game_phase == "menu":
            inst_text = font_medium.render("Welcome!", True, GOLD)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            self.screen.blit(inst_text, inst_rect)
            self.btn_start.hovered = self.btn_start.contains_point(pygame.mouse.get_pos())
            self.btn_start.draw(self.screen)
            hint = font_small.render("or press SPACE", True, LIGHT_GRAY)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint, hint_rect)
        elif self.game_phase == "game_over":
            inst_text = font_medium.render("Press R to restart", True, GOLD)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(inst_text, inst_rect)
            self.btn_restart.hovered = self.btn_restart.contains_point(pygame.mouse.get_pos())
            self.btn_restart.draw(self.screen)
        
        # AI thinking indicator
        if self.ai_thinking:
            thinking_text = font_medium.render("🤖 AI is calculating with minimax...", True, GOLD)
            thinking_rect = thinking_text.get_rect(center=(SCREEN_WIDTH // 2, self.play_area_y))
            self.screen.blit(thinking_text, thinking_rect)
    
    def update(self):
        """Update game state"""
        # Step animations
        self.step_animations()
        
        if self.game_phase == "ai_turn" and self.ai_thinking:
            self.ai_turn()

        # Auto-resolve when both cards have arrived
        if self.human_played_card and self.ai_played_card and self.human_ready and self.ai_ready:
            self.resolve_round()

    def step_animations(self):
        if not self.animations:
            return
        to_remove = []
        for anim in self.animations:
            card: Card = anim["card"]
            tx, ty = anim["tx"], anim["ty"]
            speed = anim.get("speed", 24)
            dx = tx - card.x
            dy = ty - card.y
            dist = math.hypot(dx, dy)
            if dist <= speed:
                card.update_position(tx, ty)
                to_remove.append(anim)
                cb: Optional[Callable] = anim.get("on_done")
                if cb:
                    cb()
            else:
                card.update_position(card.x + speed * dx / dist, card.y + speed * dy / dist)
        for a in to_remove:
            if a in self.animations:
                self.animations.remove(a)

    def animate_card_to(self, card: Card, x: int, y: int, speed: int = 28, on_done: Optional[Callable] = None):
        self.animations.append({"card": card, "tx": x, "ty": y, "speed": speed, "on_done": on_done})

    def _mark_ready(self, who: str):
        if who == "human":
            self.human_ready = True
        elif who == "ai":
            self.ai_ready = True

    def get_play_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        # human play position, ai play position
        return (SCREEN_WIDTH // 2 - 100, self.play_area_y + 50), (SCREEN_WIDTH // 2 + 20, self.play_area_y - 50)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            
            # Draw everything
            self.draw_ui()
            self.draw_cards()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    game = GameUI()
    game.run()

if __name__ == "__main__":
    main()