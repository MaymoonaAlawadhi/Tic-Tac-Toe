import pygame
import sys
import random
import math

pygame.init()

# ---------- Window Settings ----------
WIDTH, HEIGHT = 700, 850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pastel Tic-Tac-Toe")

# ---------- Modern Pastel Color Scheme ----------
BACKGROUND = (250, 248, 245)  # Soft off-white
CARD_BG = (255, 255, 255)    # Pure white for cards
ACCENT_BG = (245, 243, 250)  # Very light lavender

# Pastel accent colors
PASTEL_BLUE = (173, 216, 230)    # Light blue
PASTEL_PINK = (255, 182, 193)    # Light pink
PASTEL_GREEN = (152, 251, 152)   # Light green
PASTEL_LAVENDER = (216, 191, 216) # Light lavender
PASTEL_CORAL = (255, 127, 127)   # Light coral
PASTEL_MINT = (170, 240, 209)    # Mint green

# Text colors
DARK_TEXT = (60, 60, 70)         # Dark gray for text
MEDIUM_TEXT = (100, 100, 110)    # Medium gray
LIGHT_TEXT = (150, 150, 160)     # Light gray

# Button colors
BUTTON_BG = (240, 240, 245)      # Very light gray
BUTTON_HOVER = (220, 220, 230)   # Slightly darker
BUTTON_ACTIVE = (200, 220, 240)  # Active state
BUTTON_BORDER = (210, 210, 220)  # Button border

# Game colors
PLAYER_COLOR = (100, 149, 237)   # Cornflower blue for X
AI_COLOR = (255, 105, 180)       # Hot pink for O
WIN_LINE = (255, 182, 193)       # Pastel pink for winning line
GRID_COLOR = (220, 220, 230)     # Light gray for grid

# ---------- Fonts ----------
try:
    # Modern sans-serif fonts
    title_font = pygame.font.Font(None, 72)
    sub_font = pygame.font.Font(None, 42)
    button_font = pygame.font.Font(None, 32)
    info_font = pygame.font.Font(None, 26)
    small_font = pygame.font.Font(None, 22)
except:
    # Fallback to system fonts
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    sub_font = pygame.font.SysFont("Arial", 42)
    button_font = pygame.font.Font(None, 32)
    info_font = pygame.font.SysFont("Arial", 26)
    small_font = pygame.font.SysFont("Arial", 22)

# ---------- Game Constants ----------
BOARD_SIZE = 550
CELL_SIZE = BOARD_SIZE // 3
BOARD_MARGIN = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = 130

PLAYER = "X"
AI = "O"
EMPTY = " "

board = [EMPTY] * 9
game_over = False
winner = None
difficulty = "hard"
first_player = "player"
current_turn = PLAYER

WIN_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

# ---------- Subtle Shadow Effect ----------
def draw_shadow(surface, rect, color, radius=0, offset=(2, 2), alpha=20):
    shadow_rect = pygame.Rect(rect.x + offset[0], rect.y + offset[1], 
                             rect.width, rect.height)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (*color, alpha), shadow_surf.get_rect(), 
                    border_radius=radius)
    surface.blit(shadow_surf, shadow_rect)

# ======================================================
#                 MODERN BUTTON CLASS
# ======================================================
class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_BG, hover_color=BUTTON_HOVER, 
                 func=None, is_toggle=False, icon=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.func = func
        self.is_toggle = is_toggle
        self.active = False
        self.icon = icon
        self.border_radius = 10
        
    def draw(self, surface=WIN):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos)
        
        # Choose color based on state
        if self.active and self.is_toggle:
            color = BUTTON_ACTIVE
            border_color = PLAYER_COLOR
            text_color = DARK_TEXT
        elif is_hovering:
            color = self.hover_color
            border_color = BUTTON_BORDER
            text_color = DARK_TEXT
        else:
            color = self.color
            border_color = BUTTON_BORDER
            text_color = MEDIUM_TEXT
        
        # Draw subtle shadow
        draw_shadow(surface, self.rect, (0, 0, 0), self.border_radius)
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        
        # Draw thin border
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=self.border_radius)
        
        # Draw text
        txt = button_font.render(self.text, True, text_color)
        text_x = self.rect.x + (self.rect.width - txt.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - txt.get_height()) // 2
        surface.blit(txt, (text_x, text_y))
        
        return is_hovering
    
    def click(self):
        if self.func:
            self.func()
        if self.is_toggle:
            self.active = True
        return True

# ======================================================
#                  GAME LOGIC
# ======================================================
def draw_board():
    WIN.fill(BACKGROUND)
    
    # Draw header card
    header_rect = pygame.Rect(40, 20, WIDTH - 80, 80)
    draw_shadow(WIN, header_rect, (0, 0, 0), 15)
    pygame.draw.rect(WIN, CARD_BG, header_rect, border_radius=15)
    
    # Draw title
    title_text = "Tic-Tac-Toe"
    title_surf = title_font.render(title_text, True, DARK_TEXT)
    WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 45))
    
    # Draw board container with shadow
    board_container = pygame.Rect(BOARD_MARGIN - 15, BOARD_Y - 15, 
                                 BOARD_SIZE + 30, BOARD_SIZE + 30)
    draw_shadow(WIN, board_container, (0, 0, 0), 20, alpha=15)
    pygame.draw.rect(WIN, CARD_BG, board_container, border_radius=20)
    
    # Draw grid lines
    for i in range(1, 3):
        # Vertical lines
        x = BOARD_MARGIN + i * CELL_SIZE
        pygame.draw.line(WIN, GRID_COLOR, (x, BOARD_Y), 
                        (x, BOARD_Y + BOARD_SIZE), 3)
        
        # Horizontal lines
        y = BOARD_Y + i * CELL_SIZE
        pygame.draw.line(WIN, GRID_COLOR, (BOARD_MARGIN, y), 
                        (BOARD_MARGIN + BOARD_SIZE, y), 3)
    
    # Draw symbols with modern style
    for i in range(9):
        x = BOARD_MARGIN + (i % 3) * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_Y + (i // 3) * CELL_SIZE + CELL_SIZE // 2
        
        if board[i] == "X":
            # Draw modern X with shadow
            size = CELL_SIZE // 3.5
            offset = 3
            
            # Shadow
            pygame.draw.line(WIN, (*PLAYER_COLOR, 100), 
                           (x - size - offset, y - size - offset),
                           (x + size + offset, y + size + offset), 8)
            pygame.draw.line(WIN, (*PLAYER_COLOR, 100), 
                           (x + size + offset, y - size - offset),
                           (x - size - offset, y + size + offset), 8)
            
            # Main X
            pygame.draw.line(WIN, PLAYER_COLOR, 
                           (x - size, y - size), (x + size, y + size), 6)
            pygame.draw.line(WIN, PLAYER_COLOR, 
                           (x + size, y - size), (x - size, y + size), 6)
            
        elif board[i] == "O":
            # Draw modern O with shadow
            radius = CELL_SIZE // 3.5
            offset = 3
            
            # Shadow
            pygame.draw.circle(WIN, (*AI_COLOR, 100), (x, y), radius + offset, 8)
            
            # Main O
            pygame.draw.circle(WIN, AI_COLOR, (x, y), radius, 6)
    
    # Draw status card
    status_rect = pygame.Rect(40, BOARD_Y + BOARD_SIZE + 40, WIDTH - 80, 70)
    draw_shadow(WIN, status_rect, (0, 0, 0), 12)
    pygame.draw.rect(WIN, CARD_BG, status_rect, border_radius=12)
    
    # Draw game status
    if not game_over:
        turn_text = f"{'Your' if current_turn == PLAYER else 'AI'}'s Turn"
        turn_color = PLAYER_COLOR if current_turn == PLAYER else AI_COLOR
        turn_surf = sub_font.render(turn_text, True, turn_color)
        WIN.blit(turn_surf, (WIDTH//2 - turn_surf.get_width()//2, 
                            status_rect.y + 25))
    elif winner:
        result_text = f"{'You' if winner == PLAYER else 'AI'} Win!"
        result_color = PLAYER_COLOR if winner == PLAYER else AI_COLOR
        result_surf = sub_font.render(result_text, True, result_color)
        WIN.blit(result_surf, (WIDTH//2 - result_surf.get_width()//2, 
                              status_rect.y + 25))
    else:
        draw_text = "It's a Draw!"
        draw_surf = sub_font.render(draw_text, True, MEDIUM_TEXT)
        WIN.blit(draw_surf, (WIDTH//2 - draw_surf.get_width()//2, 
                            status_rect.y + 25))
    
    # Draw control panel
    panel_rect = pygame.Rect(40, HEIGHT - 160, WIDTH - 80, 120)
    draw_shadow(WIN, panel_rect, (0, 0, 0), 15)
    pygame.draw.rect(WIN, ACCENT_BG, panel_rect, border_radius=15)
    
    # Draw game info
    info_text = f"{difficulty.upper()} MODE  •  {first_player.upper()} STARTS"
    info_surf = info_font.render(info_text, True, MEDIUM_TEXT)
    WIN.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, panel_rect.y + 25))
    
    # Draw control buttons
    restart_btn.draw()
    menu_btn.draw()
    
    pygame.display.update()

def reset_game():
    global board, game_over, winner, current_turn
    board = [EMPTY] * 9
    game_over = False
    winner = None
    current_turn = PLAYER if first_player == "player" else AI

def available_moves(b): 
    return [i for i, v in enumerate(b) if v == EMPTY]

def check_winner(b):
    for a, c, d in WIN_COMBOS:
        if b[a] != EMPTY and b[a] == b[c] == b[d]:
            return b[a], (a, c, d)
    return None, None

def is_full(b): 
    return all(c != EMPTY for c in b)

def evaluate(b):
    w, _ = check_winner(b)
    if w == AI: return +1
    if w == PLAYER: return -1
    return 0

def minimax(b, depth, maximizing, alpha, beta):
    w, _ = check_winner(b)
    if w or is_full(b): return evaluate(b), None

    if maximizing:
        best_score, best_move = -math.inf, None
        for m in available_moves(b):
            b[m] = AI
            score, _ = minimax(b, depth + 1, False, alpha, beta)
            b[m] = EMPTY
            if score > best_score:
                best_score, best_move = score, m
            alpha = max(alpha, best_score)
            if beta <= alpha: break
        return best_score, best_move

    else:
        best_score, best_move = math.inf, None
        for m in available_moves(b):
            b[m] = PLAYER
            score, _ = minimax(b, depth + 1, True, alpha, beta)
            b[m] = EMPTY
            if score < best_score:
                best_score, best_move = score, m
            beta = min(beta, best_score)
            if beta <= alpha: break
        return best_score, best_move

def ai_pick():
    if difficulty == "easy":
        return random.choice(available_moves(board))
    if difficulty == "medium":
        if random.random() < 0.6:
            return minimax(board, 0, True, -math.inf, math.inf)[1]
        return random.choice(available_moves(board))
    return minimax(board, 0, True, -math.inf, math.inf)[1]

def draw_winning_line(combo):
    if not combo:
        return
    
    a, b, c = combo
    # Convert board positions to screen coordinates
    ax = BOARD_MARGIN + (a % 3) * CELL_SIZE + CELL_SIZE // 2
    ay = BOARD_Y + (a // 3) * CELL_SIZE + CELL_SIZE // 2
    cx = BOARD_MARGIN + (c % 3) * CELL_SIZE + CELL_SIZE // 2
    cy = BOARD_Y + (c // 3) * CELL_SIZE + CELL_SIZE // 2
    
    # Draw winning line with shadow
    line_thickness = 8
    offset = 3
    
    # Shadow
    pygame.draw.line(WIN, (*WIN_LINE, 150), 
                    (ax + offset, ay + offset), 
                    (cx + offset, cy + offset), 
                    line_thickness + 2)
    
    # Main line
    pygame.draw.line(WIN, WIN_LINE, (ax, ay), (cx, cy), line_thickness)

# ======================================================
#                GAME LOOP
# ======================================================
restart_btn = Button(WIDTH - 210, HEIGHT - 110, 160, 45, "Restart", 
                    PASTEL_MINT, PASTEL_GREEN, reset_game)

menu_btn = Button(50, HEIGHT - 110, 160, 45, "Menu", 
                 PASTEL_LAVENDER, PASTEL_PINK, lambda: None)

def game_loop():
    global board, game_over, winner, current_turn
    reset_game()
    
    # Reset menu button function
    def go_to_menu():
        main_menu()
    
    menu_btn.func = go_to_menu

    while True:
        draw_board()

        # AI move
        if current_turn == AI and not game_over:
            pygame.time.delay(350)
            move = ai_pick()
            if move is not None:
                board[move] = AI
                current_turn = PLAYER

        # Check for winner
        w, combo = check_winner(board)
        if w:
            game_over = True
            winner = w
            draw_winning_line(combo)
            pygame.display.update()
        elif is_full(board):
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check button clicks
                if restart_btn.rect.collidepoint(mouse_pos):
                    reset_game()
                    continue
                    
                if menu_btn.rect.collidepoint(mouse_pos):
                    main_menu()
                    return
                
                # Handle board click
                if not game_over and current_turn == PLAYER:
                    x, y = mouse_pos
                    # Check if click is within board
                    if (BOARD_MARGIN <= x < BOARD_MARGIN + BOARD_SIZE and 
                        BOARD_Y <= y < BOARD_Y + BOARD_SIZE):
                        # Convert to board coordinates
                        col = (x - BOARD_MARGIN) // CELL_SIZE
                        row = (y - BOARD_Y) // CELL_SIZE
                        idx = row * 3 + col
                        if 0 <= idx < 9 and board[idx] == EMPTY:
                            board[idx] = PLAYER
                            current_turn = AI

        pygame.display.update()

# ======================================================
#     MODERN SCREEN: CHOOSE FIRST PLAYER
# ======================================================
def choose_first_screen():
    WIN.fill(BACKGROUND)
    
    # Draw title card
    title_card = pygame.Rect(40, 60, WIDTH - 80, 120)
    draw_shadow(WIN, title_card, (0, 0, 0), 20)
    pygame.draw.rect(WIN, CARD_BG, title_card, border_radius=20)
    
    # Title
    title = "Who Starts?"
    title_surf = title_font.render(title, True, DARK_TEXT)
    WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 100))
    
    # Create option cards
    player_card = pygame.Rect(WIDTH//2 - 260, 250, 240, 200)
    ai_card = pygame.Rect(WIDTH//2 + 20, 250, 240, 200)
    
    # Draw cards with shadows
    for card in [player_card, ai_card]:
        draw_shadow(WIN, card, (0, 0, 0), 15)
        pygame.draw.rect(WIN, CARD_BG, card, border_radius=15)
        pygame.draw.rect(WIN, BUTTON_BORDER, card, 1, border_radius=15)
    
    # Player option
    pygame.draw.circle(WIN, PLAYER_COLOR, (player_card.centerx, player_card.centery - 30), 40)
    player_x = player_card.centerx
    player_y = player_card.centery - 30
    size = 25
    pygame.draw.line(WIN, CARD_BG, (player_x - size, player_y - size), 
                    (player_x + size, player_y + size), 6)
    pygame.draw.line(WIN, CARD_BG, (player_x + size, player_y - size), 
                    (player_x - size, player_y + size), 6)
    
    player_text = button_font.render("You Start", True, DARK_TEXT)
    WIN.blit(player_text, (player_card.centerx - player_text.get_width()//2, 
                          player_card.centery + 40))
    
    # AI option
    pygame.draw.circle(WIN, AI_COLOR, (ai_card.centerx, ai_card.centery - 30), 40, 6)
    
    ai_text = button_font.render("AI Starts", True, DARK_TEXT)
    WIN.blit(ai_text, (ai_card.centerx - ai_text.get_width()//2, 
                      ai_card.centery + 40))
    
    # Create invisible buttons over cards
    player_btn = Button(player_card.x, player_card.y, player_card.width, 
                       player_card.height, "", func=set_player_first)
    ai_btn = Button(ai_card.x, ai_card.y, ai_card.width, 
                   ai_card.height, "", func=set_ai_first)
    
    # Back button
    back_btn = Button(40, HEIGHT - 100, 200, 50, "Back to Menu", 
                     PASTEL_LAVENDER, PASTEL_PINK, main_menu)
    
    buttons = [player_btn, ai_btn, back_btn]
    
    while True:
        # Update card hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Redraw cards with hover effect
        for i, card in enumerate([player_card, ai_card]):
            is_hover = card.collidepoint(mouse_pos)
            color = BUTTON_HOVER if is_hover else CARD_BG
            
            draw_shadow(WIN, card, (0, 0, 0), 15)
            pygame.draw.rect(WIN, color, card, border_radius=15)
            pygame.draw.rect(WIN, BUTTON_BORDER, card, 1, border_radius=15)
            
            # Redraw symbols
            if i == 0:  # Player card
                pygame.draw.circle(WIN, PLAYER_COLOR, (card.centerx, card.centery - 30), 40)
                pygame.draw.line(WIN, CARD_BG, (card.centerx - 25, card.centery - 55), 
                                (card.centerx + 25, card.centery - 5), 6)
                pygame.draw.line(WIN, CARD_BG, (card.centerx + 25, card.centery - 55), 
                                (card.centerx - 25, card.centery - 5), 6)
                player_text = button_font.render("You Start", True, DARK_TEXT)
                WIN.blit(player_text, (card.centerx - player_text.get_width()//2, 
                                      card.centery + 40))
            else:  # AI card
                pygame.draw.circle(WIN, AI_COLOR, (card.centerx, card.centery - 30), 40, 6)
                ai_text = button_font.render("AI Starts", True, DARK_TEXT)
                WIN.blit(ai_text, (card.centerx - ai_text.get_width()//2, 
                                  card.centery + 40))
        
        # Draw other elements
        title_card = pygame.Rect(40, 60, WIDTH - 80, 120)
        pygame.draw.rect(WIN, CARD_BG, title_card, border_radius=20)
        title_surf = title_font.render(title, True, DARK_TEXT)
        WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 100))
        
        back_btn.draw()
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        btn.click()
                        return

def set_player_first():
    global first_player
    first_player = "player"
    game_loop()

def set_ai_first():
    global first_player
    first_player = "ai"
    game_loop()

# ======================================================
#                 MODERN MAIN MENU
# ======================================================
def main_menu():
    # Create menu buttons
    easy_btn = Button(WIDTH//2 - 220, 280, 200, 60, "Easy", 
                     PASTEL_MINT, PASTEL_GREEN, set_easy, is_toggle=True)
    medium_btn = Button(WIDTH//2 - 220, 360, 200, 60, "Medium", 
                       PASTEL_BLUE, PASTEL_LAVENDER, set_medium, is_toggle=True)
    hard_btn = Button(WIDTH//2 - 220, 440, 200, 60, "Hard", 
                     PASTEL_PINK, PASTEL_CORAL, set_hard, is_toggle=True)
    quit_btn = Button(WIDTH//2 - 220, 540, 200, 60, "Quit", 
                     BUTTON_BG, BUTTON_HOVER, quit_game)
    
    # Set active button based on current difficulty
    if difficulty == "easy":
        easy_btn.active = True
    elif difficulty == "medium":
        medium_btn.active = True
    else:
        hard_btn.active = True
    
    menu_buttons = [easy_btn, medium_btn, hard_btn, quit_btn]
    
    # Draw decorative elements
    circles = []
    for _ in range(8):
        circles.append({
            'x': random.randint(50, WIDTH - 50),
            'y': random.randint(100, 200),
            'radius': random.randint(10, 30),
            'color': random.choice([PASTEL_BLUE, PASTEL_PINK, PASTEL_GREEN, 
                                   PASTEL_LAVENDER, PASTEL_MINT]),
            'speed': random.uniform(0.2, 0.5),
            'direction': random.choice([-1, 1])
        })
    
    while True:
        WIN.fill(BACKGROUND)
        
        # Draw animated floating circles
        for circle in circles:
            circle['x'] += circle['speed'] * circle['direction']
            if circle['x'] < 50 or circle['x'] > WIDTH - 50:
                circle['direction'] *= -1
            
            alpha = 30 + int(math.sin(pygame.time.get_ticks() * 0.001) * 10)
            color_with_alpha = (*circle['color'], alpha)
            
            circle_surf = pygame.Surface((circle['radius'] * 2, circle['radius'] * 2), 
                                        pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, color_with_alpha, 
                             (circle['radius'], circle['radius']), circle['radius'])
            WIN.blit(circle_surf, (circle['x'] - circle['radius'], 
                                  circle['y'] - circle['radius']))
        
        # Draw title card
        title_card = pygame.Rect(40, 40, WIDTH - 80, 180)
        draw_shadow(WIN, title_card, (0, 0, 0), 25)
        pygame.draw.rect(WIN, CARD_BG, title_card, border_radius=25)
        
        # Draw title
        title = "Tic-Tac-Toe"
        title_surf = title_font.render(title, True, DARK_TEXT)
        WIN.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 80))
        
        # Draw subtitle
        subtitle = "Select Difficulty"
        subtitle_surf = sub_font.render(subtitle, True, MEDIUM_TEXT)
        WIN.blit(subtitle_surf, (WIDTH//2 - subtitle_surf.get_width()//2, 160))
        
        # Draw decorative line
        line_y = 200
        pygame.draw.line(WIN, PASTEL_BLUE, (WIDTH//2 - 80, line_y), 
                        (WIDTH//2 + 80, line_y), 2)
        
        # Draw buttons
        for btn in menu_buttons:
            btn.draw()
        
        # Draw footer
        footer_text = "A minimalist pastel experience"
        footer_surf = small_font.render(footer_text, True, LIGHT_TEXT)
        WIN.blit(footer_surf, (WIDTH//2 - footer_surf.get_width()//2, HEIGHT - 40))
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for btn in menu_buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        if btn.is_toggle:
                            # Deactivate other toggle buttons
                            for other_btn in menu_buttons:
                                if other_btn != btn and other_btn.is_toggle:
                                    other_btn.active = False
                        btn.click()
                        return

def set_easy():
    global difficulty
    difficulty = "easy"
    choose_first_screen()

def set_medium():
    global difficulty
    difficulty = "medium"
    choose_first_screen()

def set_hard():
    global difficulty
    difficulty = "hard"
    choose_first_screen()

def quit_game():
    pygame.quit()
    sys.exit()

# ======================================================
#                      RUN
# ======================================================
if __name__ == "__main__":
    main_menu()