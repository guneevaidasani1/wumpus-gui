import random


class WumpusWorld:
    def __init__(self , size = 4 , num_pits= 3):
        self.size = size
        self.grid = [['' for i in range(size)]  for i in range(size)]
        self.agent_pos = (0,0)
        self.place_elements()
    def place_elements(self , num_pits = 3 , size = 4):
        cells = [(x,y) for x in range(size) for y in range(size) if(x,y) != self.agent_pos]
        random.shuffle(cells)
        wumpus_coords = cells.pop()
        self.grid[wumpus_coords[0]][wumpus_coords[1]] = 'W'
        gold = cells.pop()
        self.grid[gold[0]][gold[1]] = 'G'
        arrow = cells.pop()
        self.grid[arrow[0]][arrow[1]] = 'A'
        for i in range(num_pits): 
            pit = cells.pop() 
            self.grid[pit[0]][pit[1]] = 'P'
    def get_percepts(self,pos):
        x,y = pos
        percepts = []
        if 'G' in self.grid[x][y]:
            percepts.append('Glitter')
        if any('P' in self.grid[i][j] for i,j in self.get_neighbors(x, y)): 
            percepts.append('Breeze') 
        if any('W' in self.grid[i][j] for i,j in self.get_neighbors(x, y)): 
            percepts.append('Stench')
        return percepts
    def get_neighbors(self, x, y): 
        neighbors = [] 
        for a, b in [(-1,0),(1,0),(0,-1),(0,1)]: 
            i, j = x+a, y+b 
            if 0 <= i < self.size and 0 <= j < self.size: 
                neighbors.append((i, j)) 
        return neighbors
    
    
class Agent:
    def __init__(self, world):
        self.world = world
        self.pos = (0, 0)
        self.has_gold = False
        self.explored = {(0,0)}
        self.has_arrow = False
        self.game_over = False

    def move(self, direction):
        if self.game_over:
            return
        x,y = self.pos
        if direction == 'up' and x>0:
            self.pos = (x-1,y)
        elif direction == "down" and x < self.world.size - 1:
            self.pos = (x+1,y)
        elif direction == 'left' and y > 0:
            self.pos = (x,y-1)
        elif direction == 'right' and y < self.world.size - 1:
            self.pos = (x,y+1)
        else:
            print("Invalid move!")
            return
        self.explored.add(self.pos)
        percepts = self.world.get_percepts(self.pos)
        print(f"Moved to {self.pos}, percepts: {percepts}") 
        cell = self.world.grid[self.pos[0]][self.pos[1]] 
        if cell == 'W':
            if self.has_arrow:
                print("You killed the Wumpus")
                self.world.grid[self.pos[0]][self.pos[1]] = ''
            else:
                print(" You were eaten by the Wumpus, Game Over.") 
                self.game_over = True
        elif cell == 'P': 
            print(" You fell into a pit Game Over.") 
            self.game_over = True
        elif cell == 'G': 
            self.has_gold = True 
            print(" You found the gold ")
        elif cell == 'A':
            self.has_arrow = True
            self.world.grid[self.pos[0]][self.pos[1]] = ''
            print("You found an arrow")

def printboard(world,agent,explored):
    for x in range(world.size):
        row = []
        for y in range(world.size):
            if(x,y) == agent.pos:
                row.append("A")
            elif (x,y) in explored:
                row.append('.')
            else:
                row.append('?')
        print(' '.join(row))
    print()

world = WumpusWorld(size=4, num_pits=3)
agent = Agent(world)
start_percepts = world.get_percepts(agent.pos) 
print(f"Starting at {agent.pos}, percepts: {start_percepts}")
while not agent.has_gold and not agent.game_over:
    printboard(world, agent, agent.explored)
    move = input("Enter move (up/down/left/right): ")
    agent.move(move)
