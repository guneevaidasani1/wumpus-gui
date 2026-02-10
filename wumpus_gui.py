"""
Wumpus World – Pygame GUI (Enhanced)
Cave-themed dungeon crawler with fullscreen support, parallax background,
humanoid player, menacing monsters, and atmospheric visual effects.

Controls:
  WASD / Arrow keys  – Move
  Enter / Space      – Shoot arrow in facing direction
  R                  – Restart game
  H                  – Toggle help overlay
  F11                – Toggle fullscreen
"""
import sys
import math
import random
import pygame
from wumpus_game import WumpusWorld, Agent, Direction, GameState, DIR_DELTA

# ─── Constants ───────────────────────────────────────────────────────────────
DEFAULT_WINDOW_W, DEFAULT_WINDOW_H = 1280, 720
FPS = 60
PANEL_WIDTH_RATIO = 0.28  # Panel takes 28% of window width

# Colors - Cave theme
COL_BG = (18, 18, 24)
COL_PANEL_BG = (28, 28, 38)
COL_GRID_LINE = (55, 55, 70)
COL_FOG = (38, 38, 50)
COL_FOG_PATTERN = (45, 45, 58)
COL_STONE = (90, 85, 78)
COL_STONE_LIGHT = (110, 104, 96)
COL_STONE_DARK = (70, 66, 60)
COL_EXPLORED_BORDER = (65, 62, 56)
COL_PLAYER_SKIN = (220, 180, 140)
COL_PLAYER_TUNIC = (80, 60, 140)
COL_PLAYER_OUTLINE = (30, 20, 60)
COL_PLAYER_HAIR = (100, 70, 40)
COL_WUMPUS = (140, 30, 30)
COL_WUMPUS_DARK = (80, 15, 15)
COL_WUMPUS_EYE = (255, 50, 50)
COL_WUMPUS_GLOW = (200, 40, 40)
COL_GOLD = (255, 215, 0)
COL_GOLD_SHINE = (255, 240, 150)
COL_PIT = (20, 20, 30)
COL_PIT_EDGE = (50, 45, 40)
COL_ARROW_ITEM = (180, 140, 80)
COL_ARROW_PROJ = (255, 220, 80)
COL_STENCH = (120, 180, 60)
COL_BREEZE = (100, 180, 240)
COL_GLITTER = (255, 230, 80)
COL_TEXT = (220, 220, 230)
COL_TEXT_DIM = (140, 140, 160)
COL_TEXT_GOLD = (255, 215, 0)
COL_TEXT_RED = (255, 80, 80)
COL_TEXT_GREEN = (80, 255, 120)
COL_MSG_BG = (30, 30, 45, 200)
COL_BUTTON = (60, 60, 80)
COL_BUTTON_HOVER = (80, 80, 110)
COL_BUTTON_TEXT = (220, 220, 230)
COL_SKULL = (200, 200, 210)
COL_WIN_GLOW = (255, 215, 0)
COL_CAVE_DEEP = (25, 20, 15)
COL_CAVE_MID = (40, 35, 28)
COL_STALACTITE = (60, 55, 48)
COL_TORCH_GLOW = (255, 180, 80)
COL_BLOOD = (120, 20, 20)


# ─── Particle System ─────────────────────────────────────────────────────────

class Particle:
    """Floating dust particle for atmosphere."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, -0.1)
        self.life = random.randint(100, 300)
        self.max_life = self.life
        self.size = random.randint(1, 3)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life) * 0.3)
        if alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 200, 180, alpha), (self.size, self.size), self.size)
            surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


# ─── Sprite Drawing Functions ────────────────────────────────────────────────

def draw_stone_tile(surface, rect):
    """Draw enhanced stone brick floor tile with cracks and moss."""
    x, y, w, h = rect
    # Base stone with gradient
    for i in range(h):
        t = i / h
        col = tuple(int(COL_STONE[j] * (0.9 + t * 0.2)) for j in range(3))
        pygame.draw.line(surface, col, (x, y + i), (x + w, y + i))
    
    # Brick pattern
    brick_h = max(h // 4, 4)
    brick_w = max(w // 3, 6)
    for row in range(5):
        ry = y + row * brick_h
        offset = brick_w // 2 if row % 2 else 0
        for col in range(-1, 5):
            bx = x + col * brick_w + offset
            br = pygame.Rect(bx + 1, ry + 1, brick_w - 2, brick_h - 2)
            br = br.clip(pygame.Rect(rect))
            if br.w > 0 and br.h > 0:
                pygame.draw.rect(surface, COL_STONE_LIGHT, br)
                pygame.draw.rect(surface, COL_STONE_DARK, br, 1)
    
    # Random cracks
    if random.random() < 0.3:
        crack_x = x + random.randint(w // 4, 3 * w // 4)
        crack_y = y + random.randint(h // 4, 3 * h // 4)
        pygame.draw.line(surface, COL_STONE_DARK, 
                        (crack_x, crack_y), 
                        (crack_x + random.randint(-w//3, w//3), crack_y + random.randint(-h//3, h//3)), 1)


def draw_fog_tile(surface, rect, tick):
    """Draw deep mysterious fog with swirling animation."""
    x, y, w, h = rect
    pygame.draw.rect(surface, COL_FOG, rect)
    # Swirling fog
    for i in range(10):
        phase = tick * 0.02 + i * 0.6
        fx = x + int((math.sin(phase) * 0.5 + 0.5) * w)
        fy = y + int((math.cos(phase * 0.7) * 0.5 + 0.5) * h)
        r = 4 + int(math.sin(tick * 0.03 + i) * 2)
        fog_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fog_surf, (*COL_FOG_PATTERN, 80), (r, r), r)
        surface.blit(fog_surf, (fx - r, fy - r))


def draw_player(surface, cx, cy, size, facing, tick):
    """Draw humanoid adventurer character."""
    s = size
    
    # Walking bob animation
    bob = int(math.sin(tick * 0.15) * 2)
    cy += bob
    
    # Direction offsets
    dx, dy = DIR_DELTA[facing]
    
    # Legs
    leg_offset = int(math.sin(tick * 0.2) * 3)
    pygame.draw.rect(surface, COL_PLAYER_TUNIC, 
                    (cx - s//6 + leg_offset, cy + s//6, s//8, s//3), border_radius=2)
    pygame.draw.rect(surface, COL_PLAYER_TUNIC, 
                    (cx + s//12 - leg_offset, cy + s//6, s//8, s//3), border_radius=2)
    
    # Body/Tunic
    body_rect = pygame.Rect(cx - s//3, cy - s//4, s * 2//3, s//2)
    pygame.draw.rect(surface, COL_PLAYER_TUNIC, body_rect, border_radius=4)
    pygame.draw.rect(surface, COL_PLAYER_OUTLINE, body_rect, 2, border_radius=4)
    
    # Belt
    pygame.draw.rect(surface, COL_PLAYER_OUTLINE, (cx - s//3, cy, s * 2//3, 3))
    
    # Arms
    arm_angle = math.sin(tick * 0.2) * 0.3
    # Left arm
    arm_x = cx - s//3 + int(math.cos(arm_angle) * s//4)
    arm_y = cy + int(math.sin(arm_angle) * s//4)
    pygame.draw.line(surface, COL_PLAYER_SKIN, (cx - s//3, cy - s//8), (arm_x, arm_y), 4)
    # Right arm (holding torch/sword)
    arm_x2 = cx + s//3 + int(math.cos(-arm_angle) * s//4)
    arm_y2 = cy + int(math.sin(-arm_angle) * s//4)
    pygame.draw.line(surface, COL_PLAYER_SKIN, (cx + s//3, cy - s//8), (arm_x2, arm_y2), 4)
    
    # Torch in hand
    torch_glow = int(abs(math.sin(tick * 0.1)) * 20)
    torch_surf = pygame.Surface((s, s), pygame.SRCALPHA)
    pygame.draw.circle(torch_surf, (*COL_TORCH_GLOW, 100 + torch_glow), (s//2, s//2), s//3)
    surface.blit(torch_surf, (arm_x2 - s//2, arm_y2 - s//2))
    pygame.draw.circle(surface, COL_GOLD, (arm_x2, arm_y2), 3)
    
    # Head
    head_r = s//4
    pygame.draw.circle(surface, COL_PLAYER_SKIN, (cx, cy - s//3), head_r)
    pygame.draw.circle(surface, COL_PLAYER_OUTLINE, (cx, cy - s//3), head_r, 2)
    
    # Hair
    pygame.draw.circle(surface, COL_PLAYER_HAIR, (cx, cy - s//3 - head_r//2), head_r//2)
    
    # Face - eyes looking in direction
    eye_cx = cx + dx * (head_r // 3)
    eye_cy = cy - s//3 + dy * (head_r // 3)
    pygame.draw.circle(surface, (255, 255, 255), (eye_cx - 4, eye_cy), 3)
    pygame.draw.circle(surface, (255, 255, 255), (eye_cx + 4, eye_cy), 3)
    pygame.draw.circle(surface, (0, 0, 0), (eye_cx - 4 + dx * 2, eye_cy + dy * 2), 2)
    pygame.draw.circle(surface, (0, 0, 0), (eye_cx + 4 + dx * 2, eye_cy + dy * 2), 2)
    
    # Direction arrow indicator
    arrow_x = cx + dx * (s//2 + 6)
    arrow_y = cy + dy * (s//2 + 6)
    arrow_bob = int(math.sin(tick * 0.1) * 2)
    arrow_x += dx * arrow_bob
    arrow_y += dy * arrow_bob
    if facing == Direction.UP:
        pts = [(arrow_x, arrow_y - 6), (arrow_x - 5, arrow_y + 3), (arrow_x + 5, arrow_y + 3)]
    elif facing == Direction.DOWN:
        pts = [(arrow_x, arrow_y + 6), (arrow_x - 5, arrow_y - 3), (arrow_x + 5, arrow_y - 3)]
    elif facing == Direction.LEFT:
        pts = [(arrow_x - 6, arrow_y), (arrow_x + 3, arrow_y - 5), (arrow_x + 3, arrow_y + 5)]
    else:
        pts = [(arrow_x + 6, arrow_y), (arrow_x - 3, arrow_y - 5), (arrow_x - 3, arrow_y + 5)]
    pygame.draw.polygon(surface, COL_ARROW_PROJ, pts)


def draw_wumpus(surface, cx, cy, size, tick):
    """Draw menacing demon/beast Wumpus."""
    s = size * 3 // 4
    
    # Breathing animation
    breath = int(math.sin(tick * 0.05) * 3)
    s += breath
    
    # Red glow aura
    glow_size = s + 10 + int(abs(math.sin(tick * 0.08)) * 5)
    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*COL_WUMPUS_GLOW, 40), (glow_size, glow_size), glow_size)
    surface.blit(glow_surf, (cx - glow_size, cy - glow_size))
    
    # Hulking body
    body_pts = [
        (cx, cy - s//2),
        (cx + s//2, cy - s//4),
        (cx + s//2, cy + s//3),
        (cx + s//4, cy + s//2),
        (cx - s//4, cy + s//2),
        (cx - s//2, cy + s//3),
        (cx - s//2, cy - s//4),
    ]
    pygame.draw.polygon(surface, COL_WUMPUS, body_pts)
    pygame.draw.polygon(surface, COL_WUMPUS_DARK, body_pts, 3)
    
    # Horns
    horn_left = [(cx - s//3, cy - s//2), (cx - s//2, cy - s), (cx - s//4, cy - s//2)]
    horn_right = [(cx + s//3, cy - s//2), (cx + s//2, cy - s), (cx + s//4, cy - s//2)]
    pygame.draw.polygon(surface, COL_WUMPUS_DARK, horn_left)
    pygame.draw.polygon(surface, COL_WUMPUS_DARK, horn_right)
    
    # Glowing eyes with pulse
    eye_glow = int(abs(math.sin(tick * 0.1)) * 30)
    eye_size = s//6 + eye_glow // 10
    pygame.draw.circle(surface, COL_WUMPUS_EYE, (cx - s//4, cy - s//6), eye_size)
    pygame.draw.circle(surface, COL_WUMPUS_EYE, (cx + s//4, cy - s//6), eye_size)
    pygame.draw.circle(surface, (255, 255, 100), (cx - s//4, cy - s//6), eye_size//2)
    pygame.draw.circle(surface, (255, 255, 100), (cx + s//4, cy - s//6), eye_size//2)
    
    # Open maw with fangs
    mouth_pts = [(cx - s//5, cy + s//8), (cx, cy + s//4), (cx + s//5, cy + s//8)]
    pygame.draw.polygon(surface, (50, 10, 10), mouth_pts)
    # Fangs
    fang_pts = [
        [(cx - s//6, cy + s//8), (cx - s//8, cy + s//3), (cx - s//12, cy + s//8)],
        [(cx + s//12, cy + s//8), (cx + s//8, cy + s//3), (cx + s//6, cy + s//8)]
    ]
    for fang in fang_pts:
        pygame.draw.polygon(surface, (255, 255, 255), fang)


def draw_dead_wumpus(surface, cx, cy, size, tick):
    """Draw dead Wumpus with arrow sticking out."""
    s = size * 3 // 4
    
    # Blood splatter on ground
    for i in range(5):
        angle = i * 1.3
        bx = cx + int(math.cos(angle) * s//2)
        by = cy + int(math.sin(angle) * s//2)
        br = s//6 + i % 3
        pygame.draw.circle(surface, COL_BLOOD, (bx, by), br)
    
    # Collapsed body (lying down)
    body_rect = pygame.Rect(cx - s//2, cy - s//6, s, s//3)
    pygame.draw.ellipse(surface, COL_WUMPUS_DARK, body_rect)
    pygame.draw.ellipse(surface, COL_WUMPUS, body_rect.inflate(-4, -4))
    
    # Dead head
    head_r = s//4
    pygame.draw.circle(surface, COL_WUMPUS, (cx - s//4, cy - s//8), head_r)
    pygame.draw.circle(surface, COL_WUMPUS_DARK, (cx - s//4, cy - s//8), head_r, 2)
    
    # X eyes (dead)
    eye_x, eye_y = cx - s//4, cy - s//8
    pygame.draw.line(surface, (0, 0, 0), (eye_x - 8, eye_y - 8), (eye_x - 2, eye_y - 2), 2)
    pygame.draw.line(surface, (0, 0, 0), (eye_x - 2, eye_y - 8), (eye_x - 8, eye_y - 2), 2)
    pygame.draw.line(surface, (0, 0, 0), (eye_x + 2, eye_y - 8), (eye_x + 8, eye_y - 2), 2)
    pygame.draw.line(surface, (0, 0, 0), (eye_x + 8, eye_y - 8), (eye_x + 2, eye_y - 2), 2)
    
    # Arrow sticking out
    arrow_x = cx + s//4
    arrow_y = cy
    pygame.draw.line(surface, COL_ARROW_ITEM, (arrow_x - s//3, arrow_y - s//4), (arrow_x + s//6, arrow_y), 4)
    # Arrowhead
    pygame.draw.polygon(surface, (220, 180, 100), [
        (arrow_x + s//6, arrow_y), 
        (arrow_x + s//6 - 6, arrow_y - 4), 
        (arrow_x + s//6 - 6, arrow_y + 4)
    ])
    # Fletching
    pygame.draw.line(surface, (200, 100, 60), (arrow_x - s//3, arrow_y - s//4), (arrow_x - s//3 + 5, arrow_y - s//4 + 5), 2)


def draw_gold(surface, cx, cy, size, tick):
    """Draw gold treasure with dramatic sparkle."""
    s = size // 3
    # Rotating light rays
    for i in range(6):
        angle = tick * 0.05 + i * 1.047
        ray_len = s + int(abs(math.sin(tick * 0.08 + i)) * s//2)
        ex = cx + int(math.cos(angle) * ray_len)
        ey = cy + int(math.sin(angle) * ray_len)
        pygame.draw.line(surface, COL_GOLD_SHINE, (cx, cy), (ex, ey), 2)
    
    # Coins
    for i, (ox, oy) in enumerate([(0, 0), (-s//2, s//4), (s//2, s//4)]):
        glint = int(math.sin(tick * 0.08 + i) * 30)
        col = tuple(min(255, c + glint) for c in COL_GOLD)
        pygame.draw.ellipse(surface, col, (cx + ox - s//2, cy + oy - s//3, s, s * 2//3))
        pygame.draw.ellipse(surface, (200, 170, 0), (cx + ox - s//2, cy + oy - s//3, s, s * 2//3), 2)


def draw_pit(surface, cx, cy, size):
    """Draw abyssal pit with depth and inner glow."""
    s = size * 2 // 5
    # Outer shadow rings
    for i in range(3):
        ring_s = s + i * 4
        pygame.draw.ellipse(surface, COL_PIT_EDGE, (cx - ring_s - 3, cy - ring_s//2 - 2, ring_s * 2 + 6, ring_s + 4))
    # Main pit
    pygame.draw.ellipse(surface, COL_PIT, (cx - s, cy - s//2, s * 2, s))
    # Inner depths with purple glow
    for i in range(3):
        depth_s = s * (3 - i) // 4
        alpha = 50 + i * 30
        depth_surf = pygame.Surface((depth_s * 2, depth_s), pygame.SRCALPHA)
        pygame.draw.ellipse(depth_surf, (40, 20, 60, alpha), (0, 0, depth_s * 2, depth_s))
        surface.blit(depth_surf, (cx - depth_s, cy - depth_s//2))


def draw_arrow_item(surface, cx, cy, size):
    """Draw an arrow pickup item."""
    s = size // 3
    pygame.draw.line(surface, COL_ARROW_ITEM, (cx - s, cy + s//2), (cx + s//2, cy - s), 4)
    ax, ay = cx + s//2, cy - s
    pygame.draw.polygon(surface, (220, 180, 100), [(ax, ay), (ax - 6, ay + 4), (ax - 3, ay + 7)])
    fx, fy = cx - s, cy + s//2
    pygame.draw.line(surface, (200, 100, 60), (fx, fy), (fx + 5, fy + 5), 2)
    pygame.draw.line(surface, (200, 100, 60), (fx, fy), (fx + 6, fy - 3), 2)


def draw_percept_icon(surface, cx, cy, size, percept, tick):
    """Draw percept indicator icons with glow halos."""
    s = max(size // 5, 6)
    if percept == "Stench":
        # Glow halo
        glow_surf = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COL_STENCH, 60), (s * 3 // 2, s * 3 // 2), s)
        surface.blit(glow_surf, (cx - s * 3 // 2, cy - s * 3 // 2))
        # Wavy lines
        for i in range(3):
            wave = int(math.sin(tick * 0.08 + i * 1.5) * 3)
            pygame.draw.circle(surface, COL_STENCH, (cx + (i - 1) * (s // 2), cy + wave), 2)
        font_tiny = pygame.font.SysFont("segoeui", max(s + 2, 10), bold=True)
        txt = font_tiny.render("S", True, COL_STENCH)
        surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif percept == "Breeze":
        # Glow halo
        glow_surf = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COL_BREEZE, 60), (s * 3 // 2, s * 3 // 2), s)
        surface.blit(glow_surf, (cx - s * 3 // 2, cy - s * 3 // 2))
        # Swirl
        for i in range(4):
            angle = tick * 0.06 + i * 1.57
            bx = cx + int(math.cos(angle) * s)
            by = cy + int(math.sin(angle) * s)
            pygame.draw.circle(surface, COL_BREEZE, (bx, by), 2)
        font_tiny = pygame.font.SysFont("segoeui", max(s + 2, 10), bold=True)
        txt = font_tiny.render("B", True, COL_BREEZE)
        surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif percept == "Glitter":
        # Sparkle
        for i in range(5):
            angle = tick * 0.1 + i * 1.26
            gx = cx + int(math.cos(angle) * s)
            gy = cy + int(math.sin(angle) * s)
            pygame.draw.circle(surface, COL_GLITTER, (gx, gy), 3)


def draw_skull(surface, cx, cy, size):
    """Draw a skull icon for game-over."""
    s = size // 2
    pygame.draw.circle(surface, COL_SKULL, (cx, cy - s//6), s//2)
    pygame.draw.rect(surface, COL_SKULL, (cx - s//3, cy, s * 2//3, s//3), border_radius=2)
    pygame.draw.circle(surface, (40, 40, 50), (cx - s//5, cy - s//5), s//6)
    pygame.draw.circle(surface, (40, 40, 50), (cx + s//5, cy - s//5), s//6)
    pygame.draw.polygon(surface, (40, 40, 50), [(cx, cy + s//10), (cx - 2, cy + s//5), (cx + 2, cy + s//5)])


# ─── Main Game Class ─────────────────────────────────────────────────────────

class WumpusGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((DEFAULT_WINDOW_W, DEFAULT_WINDOW_H), pygame.RESIZABLE)
        pygame.display.set_caption("🏰 Wumpus World – Dungeon Adventure")
        self.clock = pygame.time.Clock()
        self.tick_count = 0
        self.is_fullscreen = False

        # Fonts
        self.font_title = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 16)
        self.font_small = pygame.font.SysFont("segoeui", 13)
        self.font_large = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_msg = pygame.font.SysFont("segoeui", 18, bold=True)

        # Game state
        self.world_size = 4
        self.num_pits = 3
        self.world = WumpusWorld(size=self.world_size, num_pits=self.num_pits)
        self.agent = Agent(self.world)
        self.show_help = False
        self.screen_shake = 0
        self.gold_flash = 0

        # Button rects
        self.btn_restart = pygame.Rect(0, 0, 0, 0)
        self.btn_help = pygame.Rect(0, 0, 0, 0)
        self.slider_rect = pygame.Rect(0, 0, 0, 0)
        self.dragging_slider = False

        # Background and particles
        self.bg_surface = None
        self.bg_needs_update = True
        self.particles = []

    def _create_bg(self):
        """Create a cave-themed parallax background."""
        w, h = self.screen.get_size()
        surf = pygame.Surface((w, h))
        
        # Layer 1: Deep cave radial gradient
        center_x, center_y = w // 2, h // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        for y in range(h):
            for x in range(0, w, 4):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                t = min(dist / max_dist, 1.0)
                r = int(25 * (1 - t) + 15 * t)
                g = int(20 * (1 - t) + 12 * t)
                b = int(15 * (1 - t) + 10 * t)
                pygame.draw.line(surf, (r, g, b), (x, y), (x + 3, y))
        
        # Layer 2: Stalactites at top
        for i in range(8):
            x = int((i + 0.5) * w / 8)
            height = 30 + (i % 3) * 20
            width = 15 + (i % 2) * 10
            points = [
                (x, 0),
                (x - width // 2, height // 3),
                (x - width // 4, height),
                (x + width // 4, height),
                (x + width // 2, height // 3)
            ]
            pygame.draw.polygon(surf, COL_STALACTITE, points)
            pygame.draw.polygon(surf, COL_CAVE_DEEP, points, 2)
        
        # Layer 2: Stalagmites at bottom
        for i in range(6):
            x = int((i + 0.7) * w / 6)
            height = 40 + (i % 3) * 15
            width = 18 + (i % 2) * 8
            points = [
                (x, h),
                (x - width // 2, h - height // 3),
                (x - width // 4, h - height),
                (x + width // 4, h - height),
                (x + width // 2, h - height // 3)
            ]
            pygame.draw.polygon(surf, COL_STALACTITE, points)
            pygame.draw.polygon(surf, COL_CAVE_DEEP, points, 2)
        
        # Vignette overlay
        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(min(w, h) // 3):
            alpha = int((i / (min(w, h) / 3)) * 120)
            pygame.draw.rect(vignette, (0, 0, 0, min(alpha, 120)), (i, i, w - 2*i, h - 2*i), 3)
        surf.blit(vignette, (0, 0))
        
        return surf

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((DEFAULT_WINDOW_W, DEFAULT_WINDOW_H), pygame.RESIZABLE)
        self.bg_needs_update = True

    @property
    def window_size(self):
        """Get current window dimensions."""
        return self.screen.get_size()
    
    @property
    def panel_x(self):
        """Calculate panel X position based on window width."""
        w, h = self.window_size
        return int(w * (1 - PANEL_WIDTH_RATIO))
    
    @property
    def panel_w(self):
        """Calculate panel width based on window width."""
        w, h = self.window_size
        return int(w * PANEL_WIDTH_RATIO)
    
    @property
    def grid_area_w(self):
        """Calculate grid area width."""
        return self.panel_x - 20
    
    @property
    def grid_area_h(self):
        """Calculate grid area height."""
        w, h = self.window_size
        return h - 20

    def restart(self):
        self.world = WumpusWorld(size=self.world_size, num_pits=self.num_pits)
        self.agent = Agent(self.world)
        self.screen_shake = 0
        self.gold_flash = 0
        self.particles = []

    # ─── Grid Calculations ──────────────────────────────────────────────
    @property
    def cell_size(self):
        max_cells = self.world.size
        return min(self.grid_area_w // max_cells, self.grid_area_h // max_cells)

    def grid_origin(self):
        cs = self.cell_size
        total_w = cs * self.world.size
        total_h = cs * self.world.size
        ox = 10 + (self.grid_area_w - total_w) // 2
        oy = 10 + (self.grid_area_h - total_h) // 2
        return ox, oy

    def cell_rect(self, r, c):
        ox, oy = self.grid_origin()
        cs = self.cell_size
        return pygame.Rect(ox + c * cs, oy + r * cs, cs, cs)

    # ─── Drawing ─────────────────────────────────────────────────────────
    def draw(self):
        # Update background if needed
        if self.bg_needs_update or self.bg_surface is None:
            self.bg_surface = self._create_bg()
            self.bg_needs_update = False
        
        # Shake offset
        sx, sy = 0, 0
        if self.screen_shake > 0:
            sx = random.randint(-3, 3)
            sy = random.randint(-3, 3)
            self.screen_shake -= 1

        self.screen.blit(self.bg_surface, (sx, sy))
        
        # Spawn particles randomly
        if random.random() < 0.3:
            w, h = self.window_size
            self.particles.append(Particle(random.randint(0, w), random.randint(0, h)))
        
        # Update and draw particles
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw(self.screen)
        
        self._draw_grid(sx, sy)
        self._draw_panel()
        self._draw_message()

        if self.gold_flash > 0:
            flash_surf = pygame.Surface(self.window_size, pygame.SRCALPHA)
            alpha = int(self.gold_flash * 4)
            flash_surf.fill((255, 215, 0, min(alpha, 80)))
            self.screen.blit(flash_surf, (0, 0))
            self.gold_flash -= 1

        if self.agent.state in (GameState.DEAD_WUMPUS, GameState.DEAD_PIT):
            self._draw_game_over()
        elif self.agent.state == GameState.WIN:
            self._draw_win_screen()

        if self.show_help:
            self._draw_help_overlay()

        pygame.display.flip()

    def _draw_grid(self, sx, sy):
        cs = self.cell_size
        ox, oy = self.grid_origin()

        for r in range(self.world.size):
            for c in range(self.world.size):
                rect = self.cell_rect(r, c)
                rect.x += sx
                rect.y += sy
                explored = (r, c) in self.agent.explored

                if explored:
                    draw_stone_tile(self.screen, (rect.x, rect.y, rect.w, rect.h))
                    pygame.draw.rect(self.screen, COL_EXPLORED_BORDER, rect, 1)
                else:
                    draw_fog_tile(self.screen, (rect.x, rect.y, rect.w, rect.h), self.tick_count)
                    pygame.draw.rect(self.screen, COL_GRID_LINE, rect, 1)

                # Draw cell contents if explored
                if explored:
                    cell = self.world.cell_at(r, c)
                    center_x = rect.x + cs // 2
                    center_y = rect.y + cs // 2
                    icon_size = cs * 2 // 3

                    if cell == "W":
                        draw_wumpus(self.screen, center_x, center_y, icon_size, self.tick_count)
                    elif cell == "G":
                        draw_gold(self.screen, center_x, center_y, icon_size, self.tick_count)
                    elif cell == "P":
                        draw_pit(self.screen, center_x, center_y, icon_size)
                    elif cell == "A":
                        draw_arrow_item(self.screen, center_x, center_y, icon_size)

                    # Percept indicators in corners
                    percepts = self.world.get_percepts((r, c))
                    for pi, p in enumerate(percepts):
                        corner_x = rect.x + cs - 14
                        corner_y = rect.y + 10 + pi * 16
                        draw_percept_icon(self.screen, corner_x, corner_y, cs, p, self.tick_count)

                    # Dead wumpus marker
                    if self.agent.killed_wumpus_pos == (r, c):
                        draw_dead_wumpus(self.screen, center_x, center_y, icon_size, self.tick_count)

        # Draw player on top
        pr = self.cell_rect(self.agent.pos[0], self.agent.pos[1])
        pr.x += sx
        pr.y += sy
        
        # Torch glow around player
        glow_size = cs + int(abs(math.sin(self.tick_count * 0.08)) * 10)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COL_TORCH_GLOW, 60), (glow_size, glow_size), glow_size)
        self.screen.blit(glow_surf, (pr.x + cs//2 - glow_size, pr.y + cs//2 - glow_size))
        
        draw_player(self.screen, pr.x + cs // 2, pr.y + cs // 2, cs * 2 // 3,
                     self.agent.facing, self.tick_count)

        # Arrow trail animation
        if self.agent.arrow_anim_timer > 0 and self.agent.arrow_trail:
            progress = 1.0 - (self.agent.arrow_anim_timer / 30)
            max_idx = int(progress * len(self.agent.arrow_trail))
            for i in range(min(max_idx + 1, len(self.agent.arrow_trail))):
                ar, ac = self.agent.arrow_trail[i]
                arect = self.cell_rect(ar, ac)
                arect.x += sx
                arect.y += sy
                arrow_cx = arect.x + cs // 2
                arrow_cy = arect.y + cs // 2
                glow_surf = pygame.Surface((cs, cs), pygame.SRCALPHA)
                glow_alpha = max(30, 200 - i * 50)
                pygame.draw.circle(glow_surf, (*COL_ARROW_PROJ, glow_alpha),
                                   (cs // 2, cs // 2), cs // 4)
                self.screen.blit(glow_surf, (arect.x, arect.y))
                pygame.draw.circle(self.screen, COL_ARROW_PROJ, (arrow_cx, arrow_cy), 4)

    def _draw_panel(self):
        """Draw the HUD side panel."""
        w, h = self.window_size
        px = self.panel_x + 15
        py = 20

        # Title
        title = self.font_title.render("⚔ Wumpus World", True, COL_TEXT)
        self.screen.blit(title, (px, py))
        py += 35

        # Separator
        pygame.draw.line(self.screen, COL_GRID_LINE, (px, py), (px + self.panel_w - 35, py))
        py += 12

        # Score
        score_txt = self.font_body.render(f"Score: {self.agent.score}", True, COL_TEXT_GOLD)
        self.screen.blit(score_txt, (px, py))
        py += 28

        # Position & Facing
        pos_txt = self.font_small.render(
            f"Position: ({self.agent.pos[0]}, {self.agent.pos[1]})  Facing: {self.agent.facing.value.upper()}",
            True, COL_TEXT_DIM
        )
        self.screen.blit(pos_txt, (px, py))
        py += 24

        # Separator
        pygame.draw.line(self.screen, COL_GRID_LINE, (px, py), (px + self.panel_w - 35, py))
        py += 12

        # Inventory
        inv_title = self.font_body.render("Inventory", True, COL_TEXT)
        self.screen.blit(inv_title, (px, py))
        py += 22
        gold_status = "✅ Gold" if self.agent.has_gold else "❌ Gold"
        gold_col = COL_TEXT_GREEN if self.agent.has_gold else COL_TEXT_DIM
        self.screen.blit(self.font_small.render(gold_status, True, gold_col), (px + 8, py))
        py += 18
        arrow_status = "✅ Arrow" if self.agent.has_arrow else "❌ Arrow"
        arrow_col = COL_TEXT_GREEN if self.agent.has_arrow else COL_TEXT_DIM
        self.screen.blit(self.font_small.render(arrow_status, True, arrow_col), (px + 8, py))
        py += 24

        # Separator
        pygame.draw.line(self.screen, COL_GRID_LINE, (px, py), (px + self.panel_w - 35, py))
        py += 12

        # Percepts
        percepts_title = self.font_body.render("Percepts", True, COL_TEXT)
        self.screen.blit(percepts_title, (px, py))
        py += 22
        percepts = self.world.get_percepts(self.agent.pos)
        if percepts:
            for p in percepts:
                icon = {"Stench": "💨", "Breeze": "🌀", "Glitter": "✨"}.get(p, "")
                col = {
                    "Stench": COL_STENCH, "Breeze": COL_BREEZE, "Glitter": COL_GLITTER
                }.get(p, COL_TEXT)
                self.screen.blit(self.font_small.render(f"{icon} {p}", True, col), (px + 8, py))
                py += 18
        else:
            self.screen.blit(self.font_small.render("  Nothing detected", True, COL_TEXT_DIM), (px + 8, py))
            py += 18
        py += 14

        # Separator
        pygame.draw.line(self.screen, COL_GRID_LINE, (px, py), (px + self.panel_w - 35, py))
        py += 12

        # World size slider
        size_label = self.font_body.render(f"World Size: {self.world_size}×{self.world_size}", True, COL_TEXT)
        self.screen.blit(size_label, (px, py))
        py += 24
        slider_w = self.panel_w - 50
        slider_x = px
        self.slider_rect = pygame.Rect(slider_x, py, slider_w, 12)
        # Track
        pygame.draw.rect(self.screen, COL_GRID_LINE, self.slider_rect, border_radius=6)
        # Fill
        t = (self.world_size - 4) / 4  # 4 to 8
        fill_w = int(t * slider_w)
        pygame.draw.rect(self.screen, COL_PLAYER_TUNIC, (slider_x, py, max(fill_w, 6), 12), border_radius=6)
        # Knob
        knob_x = slider_x + fill_w
        pygame.draw.circle(self.screen, COL_TEXT, (knob_x, py + 6), 8)
        pygame.draw.circle(self.screen, COL_PLAYER_TUNIC, (knob_x, py + 6), 6)
        py += 28

        # Restart button
        btn_w, btn_h = self.panel_w - 50, 32
        self.btn_restart = pygame.Rect(px, py, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        btn_col = COL_BUTTON_HOVER if self.btn_restart.collidepoint(mouse_pos) else COL_BUTTON
        pygame.draw.rect(self.screen, btn_col, self.btn_restart, border_radius=6)
        pygame.draw.rect(self.screen, COL_GRID_LINE, self.btn_restart, 1, border_radius=6)
        rtxt = self.font_body.render("🔄 Restart", True, COL_BUTTON_TEXT)
        self.screen.blit(rtxt, (self.btn_restart.centerx - rtxt.get_width() // 2,
                                self.btn_restart.centery - rtxt.get_height() // 2))
        py += 42

        # Help button
        self.btn_help = pygame.Rect(px, py, btn_w, btn_h)
        btn_col2 = COL_BUTTON_HOVER if self.btn_help.collidepoint(mouse_pos) else COL_BUTTON
        pygame.draw.rect(self.screen, btn_col2, self.btn_help, border_radius=6)
        pygame.draw.rect(self.screen, COL_GRID_LINE, self.btn_help, 1, border_radius=6)
        htxt = self.font_body.render("❓ Help (H)", True, COL_BUTTON_TEXT)
        self.screen.blit(htxt, (self.btn_help.centerx - htxt.get_width() // 2,
                                self.btn_help.centery - htxt.get_height() // 2))
        py += 50

        # Game status
        state_labels = {
            GameState.PLAYING: ("🎮 Playing...", COL_TEXT_DIM),
            GameState.WIN: ("🏆 YOU WIN!", COL_TEXT_GOLD),
            GameState.DEAD_WUMPUS: ("💀 Dead - Wumpus", COL_TEXT_RED),
            GameState.DEAD_PIT: ("💀 Dead - Pit", COL_TEXT_RED),
        }
        label, col = state_labels[self.agent.state]
        state_txt = self.font_body.render(label, True, col)
        self.screen.blit(state_txt, (px, py))

    def _draw_message(self):
        """Draw status message at bottom of grid area."""
        if self.agent.message_timer > 0 and self.agent.message:
            msg_surf = self.font_msg.render(self.agent.message, True, COL_TEXT)
            w, h = self.window_size
            mx = 10 + self.grid_area_w // 2 - msg_surf.get_width() // 2
            my = h - 40
            # Background
            bg_rect = pygame.Rect(mx - 12, my - 6, msg_surf.get_width() + 24, msg_surf.get_height() + 12)
            bg_surf = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
            bg_surf.fill((30, 30, 45, 200))
            self.screen.blit(bg_surf, (bg_rect.x, bg_rect.y))
            pygame.draw.rect(self.screen, COL_GRID_LINE, bg_rect, 1, border_radius=4)
            self.screen.blit(msg_surf, (mx, my))

    def _draw_game_over(self):
        """Draw game-over overlay."""
        w, h = self.window_size
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Text
        go_txt = self.font_large.render("GAME OVER", True, COL_TEXT_RED)
        self.screen.blit(go_txt, (w // 2 - go_txt.get_width() // 2, h // 2 - 50))

        reason = "Eaten by the Wumpus!" if self.agent.state == GameState.DEAD_WUMPUS else "Fell into a pit!"
        r_txt = self.font_body.render(reason, True, COL_TEXT)
        self.screen.blit(r_txt, (w // 2 - r_txt.get_width() // 2, h // 2))

        restart_txt = self.font_body.render("Press R to restart", True, COL_TEXT_DIM)
        self.screen.blit(restart_txt, (w // 2 - restart_txt.get_width() // 2, h // 2 + 35))

        score_txt = self.font_body.render(f"Final Score: {self.agent.score}", True, COL_TEXT_GOLD)
        self.screen.blit(score_txt, (w // 2 - score_txt.get_width() // 2, h // 2 + 60))

    def _draw_win_screen(self):
        """Draw win overlay."""
        w, h = self.window_size
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        glow = int(abs(math.sin(self.tick_count * 0.05)) * 40)
        overlay.fill((0, 0, 0, 130))
        self.screen.blit(overlay, (0, 0))

        win_txt = self.font_large.render("🏆 YOU WIN! 🏆", True,
                                          tuple(min(255, c + glow) for c in COL_WIN_GLOW))
        self.screen.blit(win_txt, (w // 2 - win_txt.get_width() // 2, h // 2 - 50))

        score_txt = self.font_body.render(f"Final Score: {self.agent.score}", True, COL_TEXT_GOLD)
        self.screen.blit(score_txt, (w // 2 - score_txt.get_width() // 2, h // 2 + 10))

        restart_txt = self.font_body.render("Press R to restart", True, COL_TEXT_DIM)
        self.screen.blit(restart_txt, (w // 2 - restart_txt.get_width() // 2, h // 2 + 45))

    def _draw_help_overlay(self):
        """Draw help/instructions overlay."""
        w, h = self.window_size
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        cx, cy = w // 2, 60
        lines = [
            ("🏰 Wumpus World – How to Play", self.font_title, COL_TEXT_GOLD),
            ("", None, None),
            ("Movement:", self.font_body, COL_TEXT),
            ("  W / ↑  –  Move Up", self.font_small, COL_TEXT_DIM),
            ("  A / ←  –  Move Left", self.font_small, COL_TEXT_DIM),
            ("  S / ↓  –  Move Down", self.font_small, COL_TEXT_DIM),
            ("  D / →  –  Move Right", self.font_small, COL_TEXT_DIM),
            ("", None, None),
            ("Actions:", self.font_body, COL_TEXT),
            ("  Enter / Space  –  Shoot arrow (in facing direction)", self.font_small, COL_TEXT_DIM),
            ("  R              –  Restart game", self.font_small, COL_TEXT_DIM),
            ("  H              –  Toggle this help", self.font_small, COL_TEXT_DIM),
            ("  F11            –  Toggle fullscreen", self.font_small, COL_TEXT_DIM),
            ("", None, None),
            ("Symbols:", self.font_body, COL_TEXT),
            ("  👹 Wumpus – Deadly monster (kill with arrow)", self.font_small, COL_WUMPUS),
            ("  ✨ Gold – Collect and return to start to win", self.font_small, COL_GOLD),
            ("  🕳️ Pit – Instant death", self.font_small, COL_TEXT_RED),
            ("  🏹 Arrow – Pickup to shoot or auto-defend vs Wumpus", self.font_small, COL_ARROW_ITEM),
            ("", None, None),
            ("Percepts (warning on adjacent cells):", self.font_body, COL_TEXT),
            ("  💨 Stench – Wumpus nearby!", self.font_small, COL_STENCH),
            ("  🌀 Breeze – Pit nearby!", self.font_small, COL_BREEZE),
            ("  ✨ Glitter – Gold here!", self.font_small, COL_GLITTER),
            ("", None, None),
            ("Goal: Find the gold and return to start (bottom-left)!", self.font_body, COL_TEXT_GREEN),
            ("", None, None),
            ("Press H to close", self.font_small, COL_TEXT_DIM),
        ]

        for text, font, color in lines:
            if font is None:
                cy += 8
                continue
            surf = font.render(text, True, color)
            self.screen.blit(surf, (cx - surf.get_width() // 2, cy))
            cy += surf.get_height() + 4

    # ─── Event Handling ──────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                self.bg_needs_update = True

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.agent.move(Direction.UP)
                    if self.agent.state in (GameState.DEAD_WUMPUS, GameState.DEAD_PIT):
                        self.screen_shake = 20
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.agent.move(Direction.DOWN)
                    if self.agent.state in (GameState.DEAD_WUMPUS, GameState.DEAD_PIT):
                        self.screen_shake = 20
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.agent.move(Direction.LEFT)
                    if self.agent.state in (GameState.DEAD_WUMPUS, GameState.DEAD_PIT):
                        self.screen_shake = 20
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.agent.move(Direction.RIGHT)
                    if self.agent.state in (GameState.DEAD_WUMPUS, GameState.DEAD_PIT):
                        self.screen_shake = 20
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.agent.shoot()
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if self.show_help:
                        self.show_help = False
                    else:
                        return False

                # Trigger gold flash
                if self.agent.has_gold and self.gold_flash == 0:
                    self.gold_flash = 30

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_restart.collidepoint(event.pos):
                    self.restart()
                elif self.btn_help.collidepoint(event.pos):
                    self.show_help = not self.show_help
                elif self.slider_rect.collidepoint(event.pos):
                    self.dragging_slider = True
                    self._update_slider(event.pos[0])

            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = False

            if event.type == pygame.MOUSEMOTION and self.dragging_slider:
                self._update_slider(event.pos[0])

        return True

    def _update_slider(self, mouse_x):
        """Update world size from slider position."""
        t = (mouse_x - self.slider_rect.x) / max(self.slider_rect.w, 1)
        t = max(0.0, min(1.0, t))
        new_size = int(4 + t * 4)
        new_size = max(4, min(8, new_size))
        if new_size != self.world_size:
            self.world_size = new_size
            self.num_pits = max(1, new_size - 1)
            self.restart()

    # ─── Main Loop ───────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.agent.tick()
            self.draw()
            self.tick_count += 1
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    game = WumpusGUI()
    game.run()
