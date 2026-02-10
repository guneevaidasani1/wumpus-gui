"""
Wumpus World – Game Engine
Refactored for GUI integration. Import-friendly, no top-level game loop.
"""
import random
from enum import Enum


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class GameState(Enum):
    PLAYING = "playing"
    WIN = "win"
    DEAD_WUMPUS = "dead_wumpus"
    DEAD_PIT = "dead_pit"


# Direction vectors -----------------------------------------------------------
DIR_DELTA = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}


class WumpusWorld:
    """The world grid: places Wumpus, gold, pits, and arrows."""

    def __init__(self, size=4, num_pits=3):
        self.size = size
        self.num_pits = num_pits
        self.grid: list[list[str]] = []
        self.wumpus_alive = True
        self.wumpus_pos: tuple[int, int] | None = None
        self.reset()

    # --- setup ---------------------------------------------------------------
    def reset(self):
        size = self.size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.wumpus_alive = True
        cells = [
            (r, c) for r in range(size) for c in range(size) if (r, c) != (size - 1, 0)
        ]
        random.shuffle(cells)

        # Place wumpus
        wp = cells.pop()
        self.grid[wp[0]][wp[1]] = "W"
        self.wumpus_pos = wp

        # Place gold
        gp = cells.pop()
        self.grid[gp[0]][gp[1]] = "G"

        # Place arrow pickup
        ap = cells.pop()
        self.grid[ap[0]][ap[1]] = "A"

        # Place pits
        for _ in range(min(self.num_pits, len(cells))):
            pp = cells.pop()
            self.grid[pp[0]][pp[1]] = "P"

    # --- queries -------------------------------------------------------------
    def get_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors

    def get_percepts(self, pos):
        r, c = pos
        percepts = []
        cell = self.grid[r][c]
        if cell == "G":
            percepts.append("Glitter")
        if any(self.grid[nr][nc] == "P" for nr, nc in self.get_neighbors(r, c)):
            percepts.append("Breeze")
        if any(self.grid[nr][nc] == "W" for nr, nc in self.get_neighbors(r, c)):
            percepts.append("Stench")
        return percepts

    def cell_at(self, r, c):
        return self.grid[r][c]


class Agent:
    """Player agent with facing direction, inventory, and scoring."""

    START_POS_OFFSET = -1  # computed from world size

    def __init__(self, world: WumpusWorld):
        self.world = world
        start = (world.size - 1, 0)
        self.pos = start
        self.facing = Direction.UP
        self.has_gold = False
        self.has_arrow = False
        self.explored: set[tuple[int, int]] = {start}
        self.state = GameState.PLAYING
        self.score = 0
        self.message = ""
        self.message_timer = 0  # frames remaining for message display
        self.arrow_trail: list[tuple[int, int]] = []  # for animation
        self.arrow_anim_timer = 0
        self.killed_wumpus_pos: tuple[int, int] | None = None

    # --- helpers -------------------------------------------------------------
    def _set_message(self, msg: str, duration: int = 120):
        self.message = msg
        self.message_timer = duration

    def tick(self):
        """Call once per frame to decay timers."""
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.arrow_anim_timer > 0:
            self.arrow_anim_timer -= 1

    # --- actions -------------------------------------------------------------
    def move(self, direction: Direction) -> bool:
        """Move the agent. Returns True if the move was valid."""
        if self.state != GameState.PLAYING:
            return False

        self.facing = direction
        dr, dc = DIR_DELTA[direction]
        nr, nc = self.pos[0] + dr, self.pos[1] + dc

        if not (0 <= nr < self.world.size and 0 <= nc < self.world.size):
            self._set_message("Can't move there!", 60)
            return False

        self.pos = (nr, nc)
        self.explored.add(self.pos)
        self.score -= 1

        # Check cell contents
        cell = self.world.cell_at(nr, nc)
        percepts = self.world.get_percepts(self.pos)

        if cell == "W":
            if self.has_arrow:
                # auto-defend: kill wumpus on contact if you have arrow
                self.has_arrow = False
                self.world.grid[nr][nc] = ""
                self.world.wumpus_alive = False
                self.killed_wumpus_pos = (nr, nc)
                self.score += 500
                self._set_message("⚔️ You killed the Wumpus in combat!", 180)
            else:
                self.state = GameState.DEAD_WUMPUS
                self._set_message("💀 Eaten by the Wumpus! GAME OVER", 999)
        elif cell == "P":
            self.state = GameState.DEAD_PIT
            self._set_message("💀 Fell into a pit! GAME OVER", 999)
        elif cell == "G":
            self.has_gold = True
            self.world.grid[nr][nc] = ""
            self.score += 1000
            self._set_message("✨ You found the GOLD! Return to start!", 180)
        elif cell == "A":
            self.has_arrow = True
            self.world.grid[nr][nc] = ""
            self.score += 0
            self._set_message("🏹 Picked up an arrow!", 120)
        else:
            # percept messages
            if percepts:
                self._set_message("  ".join(f"⚠️ {p}" for p in percepts), 90)
            else:
                self.message = ""
                self.message_timer = 0

        # Win condition: have gold and back at start
        start = (self.world.size - 1, 0)
        if self.has_gold and self.pos == start:
            self.state = GameState.WIN
            self.score += 1000
            self._set_message("🏆 YOU WIN! Escaped with the gold!", 999)

        return True

    def shoot(self) -> bool:
        """Shoot an arrow in the facing direction. Returns True if arrow was fired."""
        if self.state != GameState.PLAYING:
            return False
        if not self.has_arrow:
            self._set_message("❌ No arrow to shoot!", 90)
            return False

        self.has_arrow = False
        self.score -= 10
        dr, dc = DIR_DELTA[self.facing]
        r, c = self.pos

        # Build trail for animation
        trail = []
        hit = False
        while True:
            r, c = r + dr, c + dc
            if not (0 <= r < self.world.size and 0 <= c < self.world.size):
                break
            trail.append((r, c))
            if self.world.cell_at(r, c) == "W":
                hit = True
                break

        self.arrow_trail = trail
        self.arrow_anim_timer = 30  # frames

        if hit:
            self.world.grid[r][c] = ""
            self.world.wumpus_alive = False
            self.killed_wumpus_pos = (r, c)
            self.score += 500
            self._set_message("🎯 Your arrow hit the Wumpus! It's dead!", 180)
        else:
            self._set_message("🏹 Arrow missed... it flew into darkness.", 120)

        return True
