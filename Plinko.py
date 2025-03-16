import pygame
import random

WIDTH, HEIGHT = 1400, 900
GRAVITY = 0.02
DAMPING = 0.8
PANEL_WIDTH = 300
GAME_WIDTH = WIDTH - PANEL_WIDTH

settings = {
    "balls": 10,
    "rows": 15,
    "language": "English",
    "min_balls": 1,
    "max_balls": 50,
    "min_rows": 1,
    "max_rows": 15,
    "start_money": 50000,
    "current_bet": 1000,
    "money": 50000,
    "input_active": False
}

texts = {
    "English": {
        "play": "Play",
        "reset": "Reset",
        "money": "Money",
        "bet": "Current Bet",
        "multiplier": "Multiplier",
        "balls": "Balls",
        "all_in": "All In",
        "half": "Half",
        "double": "Double"
    },
    "Magyar": {
        "play": "Játék",
        "reset": "Újrakezd",
        "money": "Összeg",
        "bet": "Aktuális tét",
        "multiplier": "Szorzó",
        "balls": "Labdák",
        "all_in": "Mindent felteszek",
        "half": "Fél",
        "double": "Dupla"
    }
}

class Board(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (102, 0, 204), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = radius

class Slot(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, multiplier):
        super().__init__()
        self.image = pygame.Surface((width-2, height-2))
        color = (34, 139, 34)
        self.image.fill(color)
        
        border_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (0,0,0), (0,0,width,height), 2)
        self.image.blit(border_surface, (0,0))
        
        self.rect = self.image.get_rect(topleft=(x+1, y+1))
        self.multiplier = multiplier
        self.font = pygame.font.Font(None, 24)
        text = self.font.render(f"{multiplier}x", True, (255, 255, 255))
        self.image.blit(text, (self.image.get_width()//2 - text.get_width()//2, 
                          self.image.get_height()//2 - text.get_height()//2))

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, bet_per_ball):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = 0
        self.radius = radius
        self.pos = pygame.Vector2(x, y)
        self.stopped = False
        self.multiplier_applied = False
        self.bet_per_ball = bet_per_ball

    def update(self, obstacles, slots):
        if not self.stopped:
            self.speed_y += GRAVITY
            self.pos.x += self.speed_x
            self.pos.y += self.speed_y

            for obstacle in obstacles:
                self.handle_obstacle_collision(obstacle)

            if self.pos.x < PANEL_WIDTH + self.radius:
                self.pos.x = PANEL_WIDTH + self.radius
                self.speed_x *= -DAMPING
            elif self.pos.x > WIDTH - self.radius:
                self.pos.x = WIDTH - self.radius
                self.speed_x *= -DAMPING
                
            if self.pos.y < self.radius:
                self.pos.y = self.radius
                self.speed_y *= -DAMPING
            elif self.pos.y > HEIGHT - self.radius:
                self.pos.y = HEIGHT - self.radius
                self.speed_y *= -DAMPING

            self.apply_multiplier(slots)
            self.rect.center = self.pos

    def handle_obstacle_collision(self, obstacle):
        distance = self.pos.distance_to(obstacle.rect.center)
        if distance < self.radius + obstacle.radius:
            collision_vector = self.pos - obstacle.rect.center
            collision_vector.normalize_ip()
            
            overlap = (self.radius + obstacle.radius) - distance
            self.pos += collision_vector * overlap
            
            dot_product = self.speed_x * collision_vector.x + self.speed_y * collision_vector.y
            self.speed_x = (-2 * dot_product * collision_vector.x + self.speed_x) * DAMPING
            self.speed_y = (-2 * dot_product * collision_vector.y + self.speed_y) * DAMPING

    def apply_multiplier(self, slots):
        if not self.multiplier_applied:
            for slot in slots:
                if self.rect.colliderect(slot.rect):
                    settings["money"] += int(self.bet_per_ball * slot.multiplier)
                    self.multiplier_applied = True
                    self.kill()
                    break

def create_balls(num_balls):
    bet_per_ball = settings["current_bet"] / num_balls
    return [
        Ball(
            x=PANEL_WIDTH + GAME_WIDTH//2 + random.randint(-2, 2),
            y=HEIGHT*0.14,
            radius=8,
            bet_per_ball=bet_per_ball
        ) for _ in range(num_balls)
    ]

def create_board(rows):
    obstacles = pygame.sprite.Group()
    radius = 7
    vertical_spacing = radius * 2 + 30
    horizontal_spacing = radius * 2 + 45
    
    start_y = HEIGHT * 0.2
    center_x = PANEL_WIDTH + GAME_WIDTH//2

    for row in range(min(rows, settings["max_rows"])):
        num_cols = row + 3
        start_x = center_x - (num_cols//2 * horizontal_spacing)
        
        for col in range(num_cols):
            x = start_x + col * horizontal_spacing
            y = start_y + row * vertical_spacing
            
            if row % 2 == 1:
                x += horizontal_spacing / 2
            
            obstacles.add(Board(x, y, radius))
    
    return obstacles

def create_slots():
    slots = pygame.sprite.Group()
    slot_height = 40
    num_slots = 11
    slot_margin = 2
    slot_width = (GAME_WIDTH - (num_slots-1)*slot_margin) // num_slots
    multipliers = [0.2, 0.3, 0.4, 0.7, 2, 5, 2, 0.7, 0.4, 0.3, 0.2]
    
    radius = 7
    start_y = HEIGHT * 0.2
    vertical_spacing = radius * 2 + 30
    rows = settings["rows"]
    last_row_y = start_y + (rows - 1) * vertical_spacing
    slot_y = last_row_y + 30
    
    for i in range(num_slots):
        x = PANEL_WIDTH + i * (slot_width + slot_margin)
        slots.add(Slot(x, slot_y, slot_width, slot_height, multipliers[i]))
    
    return slots

def draw_panel(screen, font):
    panel = pygame.Surface((PANEL_WIDTH, HEIGHT))
    panel.fill((40, 40, 40))
    language = settings["language"]
    txt = texts[language]
    y_offset = 20

    money_text = font.render(f"{txt['money']}: {settings['money']}", True, (255, 215, 0))
    panel.blit(money_text, (20, y_offset))
    y_offset += 60

    bet_text = font.render(f"{txt['bet']}:", True, (255, 255, 255))
    panel.blit(bet_text, (20, y_offset))
    input_rect = pygame.Rect(20, y_offset + 40, 160, 40)
    pygame.draw.rect(panel, (100, 100, 100) if settings["input_active"] else (70, 70, 70), input_rect)
    bet_input = font.render(str(settings["current_bet"]), True, (255, 255, 255))
    panel.blit(bet_input, (input_rect.x + 10, input_rect.y + 10))
    y_offset += 100

    button_height = 40
    btn_spacing = 10
    
    all_in_btn = pygame.Rect(20, y_offset, PANEL_WIDTH-40, button_height)
    pygame.draw.rect(panel, (255, 165, 0), all_in_btn)
    all_in_text = font.render(txt["all_in"], True, (0, 0, 0))
    panel.blit(all_in_text, (all_in_btn.x + (all_in_btn.width - all_in_text.get_width())//2, all_in_btn.y + 10))
    y_offset += button_height + btn_spacing
    
    half_btn = pygame.Rect(20, y_offset, PANEL_WIDTH-40, button_height)
    pygame.draw.rect(panel, (255, 165, 0), half_btn)
    half_text = font.render(txt["half"], True, (0, 0, 0))
    panel.blit(half_text, (half_btn.x + (half_btn.width - half_text.get_width())//2, half_btn.y + 10))
    y_offset += button_height + btn_spacing
    
    double_btn = pygame.Rect(20, y_offset, PANEL_WIDTH-40, button_height)
    pygame.draw.rect(panel, (255, 165, 0), double_btn)
    double_text = font.render(txt["double"], True, (0, 0, 0))
    panel.blit(double_text, (double_btn.x + (double_btn.width - double_text.get_width())//2, double_btn.y + 10))
    y_offset += button_height + btn_spacing + 20

    balls_text = font.render(f"{txt['balls']}: {settings['balls']}", True, (255, 255, 255))
    panel.blit(balls_text, (20, y_offset))
    balls_minus_rect = pygame.Rect(20, y_offset + 40, 50, 40)
    balls_plus_rect = pygame.Rect(90, y_offset + 40, 50, 40)
    pygame.draw.rect(panel, (70, 70, 70), balls_minus_rect)
    pygame.draw.rect(panel, (70, 70, 70), balls_plus_rect)
    panel.blit(font.render("-", True, (255,255,255)), (balls_minus_rect.x+20, balls_minus_rect.y+10))
    panel.blit(font.render("+", True, (255,255,255)), (balls_plus_rect.x+20, balls_plus_rect.y+10))
    y_offset += 100

    rows_text = font.render(f"Rows: {settings['rows']}", True, (255, 255, 255))
    panel.blit(rows_text, (20, y_offset))
    rows_minus_rect = pygame.Rect(20, y_offset + 40, 50, 40)
    rows_plus_rect = pygame.Rect(90, y_offset + 40, 50, 40)
    pygame.draw.rect(panel, (70, 70, 70), rows_minus_rect)
    pygame.draw.rect(panel, (70, 70, 70), rows_plus_rect)
    panel.blit(font.render("-", True, (255,255,255)), (rows_minus_rect.x+20, rows_minus_rect.y+10))
    panel.blit(font.render("+", True, (255,255,255)), (rows_plus_rect.x+20, rows_plus_rect.y+10))
    y_offset += 100

    play_btn = pygame.Rect(20, HEIGHT-320, PANEL_WIDTH-40, 60)
    pygame.draw.rect(panel, (0, 200, 0), play_btn)
    play_text = font.render(txt["play"], True, (255, 255, 255))
    panel.blit(play_text, (play_btn.x + 40, play_btn.y + 15))

    reset_btn = pygame.Rect(20, HEIGHT-240, PANEL_WIDTH-40, 60)
    pygame.draw.rect(panel, (200, 0, 0), reset_btn)
    reset_text = font.render(txt["reset"], True, (255, 255, 255))
    panel.blit(reset_text, (reset_btn.x + 40, reset_btn.y + 15))

    screen.blit(panel, (0, 0))
    return {
        "bet_input": input_rect,
        "play": play_btn,
        "reset": reset_btn,
        "all_in": all_in_btn,
        "half": half_btn,
        "double": double_btn,
        "balls_minus": balls_minus_rect,
        "balls_plus": balls_plus_rect,
        "rows_minus": rows_minus_rect,
        "rows_plus": rows_plus_rect
    }

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Plinko Casino")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    obstacles = create_board(settings["rows"])
    slots = create_slots()
    balls = pygame.sprite.Group()
    pending_balls = []
    next_spawn_time = 0
    running = True
    game_active = False
    
    while running:
        clock.tick(144)
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()
        buttons = draw_panel(screen, font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["all_in"].collidepoint(mouse_pos) and settings["money"] > 0:
                    settings["current_bet"] = settings["money"]
                    
                if buttons["half"].collidepoint(mouse_pos) and settings["current_bet"] > 1:
                    settings["current_bet"] = max(1, settings["current_bet"] // 2)
                    
                if buttons["double"].collidepoint(mouse_pos):
                    new_bet = settings["current_bet"] * 2
                    if new_bet <= settings["money"]:
                        settings["current_bet"] = new_bet

                if buttons["bet_input"].collidepoint(mouse_pos):
                    settings["input_active"] = True
                else:
                    settings["input_active"] = False

                if buttons["play"].collidepoint(mouse_pos) and not game_active:
                    if settings["money"] >= settings["current_bet"] and settings["balls"] > 0:
                        settings["money"] -= settings["current_bet"]
                        game_active = True
                        pending_balls = create_balls(settings["balls"])
                        next_spawn_time = pygame.time.get_ticks()
                        balls = pygame.sprite.Group()

                if buttons["reset"].collidepoint(mouse_pos):
                    game_active = False
                    obstacles = create_board(settings["rows"])
                    slots = create_slots()
                    settings["money"] = 50000

                if buttons["balls_minus"].collidepoint(mouse_pos):
                    settings["balls"] = max(settings["min_balls"], settings["balls"]-1)
                if buttons["balls_plus"].collidepoint(mouse_pos):
                    settings["balls"] = min(settings["max_balls"], settings["balls"]+1)
                
                if buttons["rows_minus"].collidepoint(mouse_pos):
                    settings["rows"] = max(settings["min_rows"], settings["rows"]-1)
                    obstacles = create_board(settings["rows"])
                    slots = create_slots()
                if buttons["rows_plus"].collidepoint(mouse_pos):
                    settings["rows"] = min(settings["max_rows"], settings["rows"]+1)
                    obstacles = create_board(settings["rows"])
                    slots = create_slots()

            if event.type == pygame.KEYDOWN and settings["input_active"]:
                if event.key == pygame.K_RETURN:
                    settings["input_active"] = False
                elif event.key == pygame.K_BACKSPACE:
                    settings["current_bet"] = settings["current_bet"] // 10
                else:
                    if event.unicode.isdigit():
                        settings["current_bet"] = settings["current_bet"] * 10 + int(event.unicode)

        if game_active:
            current_time = pygame.time.get_ticks()
            if pending_balls and current_time >= next_spawn_time:
                ball = pending_balls.pop(0)
                balls.add(ball)
                next_spawn_time = current_time + 500
            
            balls.update(obstacles, slots)
            
            if not pending_balls and not balls:
                game_active = False

        obstacles.draw(screen)
        slots.draw(screen)
        balls.draw(screen)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()