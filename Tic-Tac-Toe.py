import pygame
import sys
import random
import math

pygame.init()

# Window settings
width, height = 700, 850  # Optimized height to fit on screen
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tic-Tac-Toe")

# Colors — pastel palette
background = (250, 248, 245)  # Soft off-white
card_bg = (255, 255, 255)    # Pure white for cards
accent_bg = (245, 243, 250)  # Very light lavender

# Pastel accent colors
blue = (173, 216, 230)    # Light blue
pink = (255, 182, 193)    # Light pink
green = (152, 251, 152)   # Light green
lavender = (216, 191, 216) # Light lavender
coral = (255, 127, 127)   # Light coral
mint = (170, 240, 209)    # Mint green

# Text colors
dark_text = (60, 60, 70)         # Dark gray for text
medium_text = (100, 100, 110)    # Medium gray
light_text = (150, 150, 160)     # Light gray

# Button colors
button_bg = (240, 240, 245)      # Very light gray
button_hover = (220, 220, 230)   # Slightly darker
button_active = (200, 220, 240)  # Active state
button_border = (210, 210, 220)  # Button border

# Game colors
player_color = (100, 149, 237)   # Cornflower blue for X
ai_color = (255, 105, 180)       # Hot pink for O
win_line = (255, 182, 193)       # Pastel pink for winning line
grid_color = (220, 220, 230)     # Light gray for grid

# Fonts
try:
    # Try modern sans-serif fonts
    title_font = pygame.font.Font(None, 72)
    sub_font = pygame.font.Font(None, 42)
    button_font = pygame.font.Font(None, 32)
    info_font = pygame.font.Font(None, 26)
    small_font = pygame.font.Font(None, 22)
except:
    # Fall back to system fonts
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    sub_font = pygame.font.SysFont("Arial", 42)
    button_font = pygame.font.Font(None, 32)
    info_font = pygame.font.SysFont("Arial", 26)
    small_font = pygame.font.SysFont("Arial", 22)

# Game constants
board_size = 480  # Reduced from 550 to make room
cell_size = board_size // 3
board_margin = (width - board_size) // 2
board_y = 120  # Slightly higher

player = "X"
ai = "O"
empty = " "

board = [empty] * 9
game_over = False
winner = None
difficulty = "hard"
first_player = "player"
current_turn = player

win_combos = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

# Subtle shadow helper
def draw_shadow(surface, rect, color, radius=0, offset=(2, 2), alpha=20):
    shadow_rect = pygame.Rect(rect.x + offset[0], rect.y + offset[1], 
                             rect.width, rect.height)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (*color, alpha), shadow_surf.get_rect(), 
                    border_radius=radius)
    surface.blit(shadow_surf, shadow_rect)

# Button class
class Button:
    def __init__(self, x, y, w, h, text, color=button_bg, hover_color=button_hover, 
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
        
    def draw(self, surface=win):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos)
        
        # Choose color based on state
        if self.active and self.is_toggle:
            color = button_active
            border_color = player_color
            text_color = dark_text
        elif is_hovering:
            color = self.hover_color
            border_color = button_border
            text_color = dark_text
        else:
            color = self.color
            border_color = button_border
            text_color = medium_text
        
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

# Game logic
def draw_board():
    win.fill(background)
    
    # Draw the header card
    header_rect = pygame.Rect(40, 20, width - 80, 80)
    draw_shadow(win, header_rect, (0, 0, 0), 15)
    pygame.draw.rect(win, card_bg, header_rect, border_radius=15)
    
    # Draw the title
    title_text = "Tic-Tac-Toe"
    title_surf = title_font.render(title_text, True, dark_text)
    win.blit(title_surf, (width//2 - title_surf.get_width()//2, 45))
    
    # Draw the board container with a shadow
    board_container = pygame.Rect(board_margin - 15, board_y - 15, 
                                 board_size + 30, board_size + 30)
    draw_shadow(win, board_container, (0, 0, 0), 20, alpha=15)
    pygame.draw.rect(win, card_bg, board_container, border_radius=20)
    
    # Draw the grid lines
    for i in range(1, 3):
        # Vertical lines
        x = board_margin + i * cell_size
        pygame.draw.line(win, grid_color, (x, board_y), 
                        (x, board_y + board_size), 3)
        
        # Horizontal lines
        y = board_y + i * cell_size
        pygame.draw.line(win, grid_color, (board_margin, y), 
                        (board_margin + board_size, y), 3)
    
    # Draw the board symbols
    for i in range(9):
        x = board_margin + (i % 3) * cell_size + cell_size // 2
        y = board_y + (i // 3) * cell_size + cell_size // 2
        
        if board[i] == "X":
            # Draw the X with a shadow
            size = cell_size // 3.5
            offset = 3
            
            # Shadow for the X
            pygame.draw.line(win, (*player_color, 100), 
                           (x - size - offset, y - size - offset),
                           (x + size + offset, y + size + offset), 8)
            pygame.draw.line(win, (*player_color, 100), 
                           (x + size + offset, y - size - offset),
                           (x - size - offset, y + size + offset), 8)
            
            # Main X strokes
            pygame.draw.line(win, player_color, 
                           (x - size, y - size), (x + size, y + size), 6)
            pygame.draw.line(win, player_color, 
                           (x + size, y - size), (x - size, y + size), 6)
            
        elif board[i] == "O":
            # Draw the O with a shadow
            radius = cell_size // 3.5
            offset = 3
            
            # Shadow for the O
            pygame.draw.circle(win, (*ai_color, 100), (x, y), radius + offset, 8)
            
            # Main O circle
            pygame.draw.circle(win, ai_color, (x, y), radius, 6)
    
    # Draw the enhanced status card (compact but clear)
    status_rect = pygame.Rect(40, board_y + board_size + 30, width - 80, 85)
    draw_shadow(win, status_rect, (0, 0, 0), 12)
    pygame.draw.rect(win, card_bg, status_rect, border_radius=12)
    
    # Show current game status with enhanced, clearer text
    if not game_over:
        # Show whose turn it is - MAIN STATUS
        if current_turn == player:
            turn_text = "PLAYER'S TURN (X)"
            turn_color = player_color
        else:
            turn_text = "AI'S TURN (O)"
            turn_color = ai_color
            
        turn_surf = sub_font.render(turn_text, True, turn_color)
        win.blit(turn_surf, (width//2 - turn_surf.get_width()//2, 
                            status_rect.y + 10))
        
        # Add a helpful indicator text
        if current_turn == player:
            indicator_text = "Click on an empty cell to play"
        else:
            indicator_text = "AI is thinking..."
        indicator_surf = small_font.render(indicator_text, True, light_text)
        win.blit(indicator_surf, (width//2 - indicator_surf.get_width()//2, 
                                 status_rect.y + 55))
    elif winner:
        # Show winner announcement - CLEAR RESULT
        if winner == player:
            result_text = "PLAYER WINS!"
            result_color = player_color
            celebration = "Congratulations!"
        else:
            result_text = "AI WINS!"
            result_color = ai_color
            celebration = "Better luck next time!"
            
        result_surf = sub_font.render(result_text, True, result_color)
        win.blit(result_surf, (width//2 - result_surf.get_width()//2, 
                              status_rect.y + 10))
        
        # Add celebration/encouragement text
        celebration_surf = small_font.render(celebration, True, medium_text)
        win.blit(celebration_surf, (width//2 - celebration_surf.get_width()//2, 
                                   status_rect.y + 55))
    else:
        # Show draw message - CLEAR TIE
        draw_text = "IT'S A DRAW!"
        draw_surf = sub_font.render(draw_text, True, medium_text)
        win.blit(draw_surf, (width//2 - draw_surf.get_width()//2, 
                            status_rect.y + 10))
        
        # Add secondary text
        tie_text = "Good game! Play again?"
        tie_surf = small_font.render(tie_text, True, light_text)
        win.blit(tie_surf, (width//2 - tie_surf.get_width()//2, 
                           status_rect.y + 55))
    
    # Draw the control panel
    panel_rect = pygame.Rect(40, height - 145, width - 80, 105)
    draw_shadow(win, panel_rect, (0, 0, 0), 15)
    pygame.draw.rect(win, accent_bg, panel_rect, border_radius=15)
    
    # Show game info
    info_text = f"{difficulty.upper()} MODE  •  {first_player.upper()} STARTS"
    info_surf = info_font.render(info_text, True, medium_text)
    win.blit(info_surf, (width//2 - info_surf.get_width()//2, panel_rect.y + 20))
    
    # Draw control buttons
    restart_btn.draw()
    menu_btn.draw()
    
    pygame.display.update()

def reset_game():
    global board, game_over, winner, current_turn
    board = [empty] * 9
    game_over = False
    winner = None
    current_turn = player if first_player == "player" else ai

def available_moves(b): 
    return [i for i, v in enumerate(b) if v == empty]

def check_winner(b):
    for a, c, d in win_combos:
        if b[a] != empty and b[a] == b[c] == b[d]:
            return b[a], (a, c, d)
    return None, None

def is_full(b): 
    return all(c != empty for c in b)

def evaluate(b):
    w, _ = check_winner(b)
    if w == ai: return +1
    if w == player: return -1
    return 0

def minimax(b, depth, maximizing, alpha, beta):
    w, _ = check_winner(b)
    if w or is_full(b): return evaluate(b), None

    if maximizing:
        best_score, best_move = -math.inf, None
        for m in available_moves(b):
            b[m] = ai
            score, _ = minimax(b, depth + 1, False, alpha, beta)
            b[m] = empty
            if score > best_score:
                best_score, best_move = score, m
            alpha = max(alpha, best_score)
            if beta <= alpha: break
        return best_score, best_move

    else:
        best_score, best_move = math.inf, None
        for m in available_moves(b):
            b[m] = player
            score, _ = minimax(b, depth + 1, True, alpha, beta)
            b[m] = empty
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
    ax = board_margin + (a % 3) * cell_size + cell_size // 2
    ay = board_y + (a // 3) * cell_size + cell_size // 2
    cx = board_margin + (c % 3) * cell_size + cell_size // 2
    cy = board_y + (c // 3) * cell_size + cell_size // 2
    
    # Draw winning line with shadow
    line_thickness = 8
    offset = 3
    
    # Shadow
    pygame.draw.line(win, (*win_line, 150), 
                    (ax + offset, ay + offset), 
                    (cx + offset, cy + offset), 
                    line_thickness + 2)
    
    # Main line
    pygame.draw.line(win, win_line, (ax, ay), (cx, cy), line_thickness)

# ======================= GAME LOOP ==========================
restart_btn = Button(width - 210, height - 95, 160, 45, "Restart", 
                    mint, green, reset_game)

menu_btn = Button(50, height - 95, 160, 45, "Menu", 
                 lavender, pink, lambda: None)

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
        if current_turn == ai and not game_over:
            pygame.time.delay(350)
            move = ai_pick()
            if move is not None:
                board[move] = ai
                current_turn = player

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
                if not game_over and current_turn == player:
                    x, y = mouse_pos
                    # Check if click is within board
                    if (board_margin <= x < board_margin + board_size and 
                        board_y <= y < board_y + board_size):
                        # Convert to board coordinates
                        col = (x - board_margin) // cell_size
                        row = (y - board_y) // cell_size
                        idx = row * 3 + col
                        if 0 <= idx < 9 and board[idx] == empty:
                            board[idx] = player
                            current_turn = ai

        pygame.display.update()

# Choose who starts
def choose_first_screen():
    win.fill(background)
    
    # Draw the title card
    title_card = pygame.Rect(40, 60, width - 80, 120)
    draw_shadow(win, title_card, (0, 0, 0), 20)
    pygame.draw.rect(win, card_bg, title_card, border_radius=20)
    
    # Title
    title = "Who Starts?"
    title_surf = title_font.render(title, True, dark_text)
    win.blit(title_surf, (width//2 - title_surf.get_width()//2, 100))
    
    # Create the option cards
    player_card = pygame.Rect(width//2 - 260, 250, 240, 200)
    ai_card = pygame.Rect(width//2 + 20, 250, 240, 200)
    
    # Draw cards with shadows
    for card in [player_card, ai_card]:
        draw_shadow(win, card, (0, 0, 0), 15)
        pygame.draw.rect(win, card_bg, card, border_radius=15)
        pygame.draw.rect(win, button_border, card, 1, border_radius=15)
    
    # Player option display
    pygame.draw.circle(win, player_color, (player_card.centerx, player_card.centery - 30), 40)
    player_x = player_card.centerx
    player_y = player_card.centery - 30
    size = 25
    pygame.draw.line(win, card_bg, (player_x - size, player_y - size), 
                    (player_x + size, player_y + size), 6)
    pygame.draw.line(win, card_bg, (player_x + size, player_y - size), 
                    (player_x - size, player_y + size), 6)
    
    player_text = button_font.render("You Start", True, dark_text)
    win.blit(player_text, (player_card.centerx - player_text.get_width()//2, 
                          player_card.centery + 40))
    
    # AI option display
    pygame.draw.circle(win, ai_color, (ai_card.centerx, ai_card.centery - 30), 40, 6)
    
    ai_text = button_font.render("AI Starts", True, dark_text)
    win.blit(ai_text, (ai_card.centerx - ai_text.get_width()//2, 
                      ai_card.centery + 40))
    
    # Create invisible buttons on top of the cards
    player_btn = Button(player_card.x, player_card.y, player_card.width, 
                       player_card.height, "", func=set_player_first)
    ai_btn = Button(ai_card.x, ai_card.y, ai_card.width, 
                   ai_card.height, "", func=set_ai_first)
    
    # Back button
    back_btn = Button(40, height - 100, 200, 50, "Back to Menu", 
                     lavender, pink, main_menu)
    
    buttons = [player_btn, ai_btn, back_btn]
    
    while True:
        # Update hover effects for the cards
        mouse_pos = pygame.mouse.get_pos()
        
        # Redraw cards to show hover state
        for i, card in enumerate([player_card, ai_card]):
            is_hover = card.collidepoint(mouse_pos)
            color = button_hover if is_hover else card_bg
            
            draw_shadow(win, card, (0, 0, 0), 15)
            pygame.draw.rect(win, color, card, border_radius=15)
            pygame.draw.rect(win, button_border, card, 1, border_radius=15)
            
            # Redraw the symbols on each card
            if i == 0:  # Player card
                pygame.draw.circle(win, player_color, (card.centerx, card.centery - 30), 40)
                pygame.draw.line(win, card_bg, (card.centerx - 25, card.centery - 55), 
                                (card.centerx + 25, card.centery - 5), 6)
                pygame.draw.line(win, card_bg, (card.centerx + 25, card.centery - 55), 
                                (card.centerx - 25, card.centery - 5), 6)
                player_text = button_font.render("You Start", True, dark_text)
                win.blit(player_text, (card.centerx - player_text.get_width()//2, 
                                      card.centery + 40))
            else:  # AI card
                pygame.draw.circle(win, ai_color, (card.centerx, card.centery - 30), 40, 6)
                ai_text = button_font.render("AI Starts", True, dark_text)
                win.blit(ai_text, (card.centerx - ai_text.get_width()//2, 
                                  card.centery + 40))
        
        # Draw other UI elements
        title_card = pygame.Rect(40, 60, width - 80, 120)
        pygame.draw.rect(win, card_bg, title_card, border_radius=20)
        title_surf = title_font.render(title, True, dark_text)
        win.blit(title_surf, (width//2 - title_surf.get_width()//2, 100))
        
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

# Main menu
def main_menu():
    # Create menu buttons
    easy_btn = Button(width//2 - 220, 280, 200, 60, "Easy", 
                     mint, green, set_easy, is_toggle=True)
    medium_btn = Button(width//2 - 220, 360, 200, 60, "Medium", 
                       blue, lavender, set_medium, is_toggle=True)
    hard_btn = Button(width//2 - 220, 440, 200, 60, "Hard", 
                     pink, coral, set_hard, is_toggle=True)
    quit_btn = Button(width//2 - 220, 540, 200, 60, "Quit", 
                     button_bg, button_hover, quit_game)
    
    # Set active button based on current difficulty
    if difficulty == "easy":
        easy_btn.active = True
    elif difficulty == "medium":
        medium_btn.active = True
    else:
        hard_btn.active = True
    
    menu_buttons = [easy_btn, medium_btn, hard_btn, quit_btn]
    
    # Create decorative elements for the menu
    circles = []
    for _ in range(8):
        circles.append({
            'x': random.randint(50, width - 50),
            'y': random.randint(100, 200),
            'radius': random.randint(10, 30),
            'color': random.choice([blue, pink, green, 
                                   lavender, mint]),
            'speed': random.uniform(0.2, 0.5),
            'direction': random.choice([-1, 1])
        })
    
    while True:
        win.fill(background)
        
        # Draw floating decorative circles
        for circle in circles:
            circle['x'] += circle['speed'] * circle['direction']
            if circle['x'] < 50 or circle['x'] > width - 50:
                circle['direction'] *= -1
            
            alpha = 30 + int(math.sin(pygame.time.get_ticks() * 0.001) * 10)
            color_with_alpha = (*circle['color'], alpha)
            
            circle_surf = pygame.Surface((circle['radius'] * 2, circle['radius'] * 2), 
                                        pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, color_with_alpha, 
                             (circle['radius'], circle['radius']), circle['radius'])
            win.blit(circle_surf, (circle['x'] - circle['radius'], 
                                  circle['y'] - circle['radius']))
        
        # Draw the title card
        title_card = pygame.Rect(40, 40, width - 80, 180)
        draw_shadow(win, title_card, (0, 0, 0), 25)
        pygame.draw.rect(win, card_bg, title_card, border_radius=25)
        
        # Draw the title
        title = "Tic-Tac-Toe"
        title_surf = title_font.render(title, True, dark_text)
        win.blit(title_surf, (width//2 - title_surf.get_width()//2, 80))
        
        # Draw the subtitle
        subtitle = "Select Difficulty"
        subtitle_surf = sub_font.render(subtitle, True, medium_text)
        win.blit(subtitle_surf, (width//2 - subtitle_surf.get_width()//2, 160))
        
        # Draw a decorative line
        line_y = 200
        pygame.draw.line(win, blue, (width//2 - 80, line_y), 
                        (width//2 + 80, line_y), 2)
        
        # Draw the menu buttons
        for btn in menu_buttons:
            btn.draw()
        
        # Draw the footer text
        footer_text = "A minimalist pastel experience"
        footer_surf = small_font.render(footer_text, True, light_text)
        win.blit(footer_surf, (width//2 - footer_surf.get_width()//2, height - 40))
        
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

# ========================= RUN ==============================
if __name__ == "__main__":
    main_menu()