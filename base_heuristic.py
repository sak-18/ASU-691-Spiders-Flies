import pygame
import sys
import time

# Define constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 80
GRID_ROWS, GRID_COLS = 10, 10
EATEN_FLY_COLOR = (255, 0, 0)  # Red for indicating an eaten fly
BOARD_COLOR = (255, 255, 255)  # White for the board
BORDER_COLOR = (0, 0, 0)  # Black for the border
SPIDER_IMAGE = pygame.image.load('assets/spider.png')  # Load spider image
FLY_IMAGE = pygame.image.load('assets/fly.png')  # Load fly image

# Define initial positions of flies and spiders
flies = [(1, 7), (2, 3), (4, 6), (8, 2), (8, 8)]  # Coordinates now represent (row, column)/(y, x)
spiders = [(6, 0), (6, 0)]  # Two spiders starting at the same position
flies_eaten = [False] * len(flies)  # Initialize all flies as not eaten

# Scale spider image to 100% of the grid size
SPIDER_IMAGE = pygame.transform.scale(SPIDER_IMAGE, (int(1 * GRID_SIZE), int(1 * GRID_SIZE)))

# Scale fly image to roughly 80% of the grid size
FLY_IMAGE = pygame.transform.scale(FLY_IMAGE, (int(0.8 * GRID_SIZE), int(0.8 * GRID_SIZE)))

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spider and Flies")

# Function to calculate Manhattan distance between two points
def manhattan_distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

# Function to draw the board
def draw_board():
    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.rect(screen, BORDER_COLOR, (x, y, GRID_SIZE, GRID_SIZE), 1)
            # Check if a fly has been eaten at this position
            for i, fly in enumerate(flies):
                if fly == (x // GRID_SIZE, y // GRID_SIZE) and flies_eaten[i]:
                    pygame.draw.rect(screen, EATEN_FLY_COLOR, (x, y, GRID_SIZE, GRID_SIZE))

# Function to draw the spiders and flies on the grid
def draw_agents():
    for spider in spiders:
        screen.blit(SPIDER_IMAGE, (spider[0]*GRID_SIZE, spider[1]*GRID_SIZE))
    for i, fly in enumerate(flies):
        if not flies_eaten[i]:
            screen.blit(FLY_IMAGE, (fly[0]*GRID_SIZE + int(0.1 * GRID_SIZE), fly[1]*GRID_SIZE + int(0.1 * GRID_SIZE)))

# Function to move the spiders based on the base heuristic
def move_spiders():
    cost = 0
    for i, spider in enumerate(spiders):
        min_distance = float('inf')
        closest_fly_index = -1
        for j, fly in enumerate(flies):
            if not flies_eaten[j]:
                distance = manhattan_distance(spider, fly)
                if distance < min_distance or (distance == min_distance and abs(spider[0] - fly[0]) < abs(spider[1] - fly[1])):
                    min_distance = distance
                    closest_fly_index = j
        
        if closest_fly_index < 0:
            return
        # Move towards the closest fly
        closest_fly = flies[closest_fly_index]
        if spider[0] < closest_fly[0]:
            spiders[i] = (spider[0] + 1, spider[1])  # Move right
        elif spider[0] > closest_fly[0]:
            spiders[i] = (spider[0] - 1, spider[1])  # Move left
        elif spider[1] < closest_fly[1]:
            spiders[i] = (spider[0], spider[1] + 1)  # Move down
        elif spider[1] > closest_fly[1]:
            spiders[i] = (spider[0], spider[1] - 1)  # Move up
        cost+=1
    
    return cost

# Main loop
running = True
total_cost = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Move spiders based on multiagent rollout algorithm
    total_cost += move_spiders()
    
    # Check for fly captures
    for i, spider in enumerate(spiders):
        for j, fly in enumerate(flies):
            if fly == spider and not flies_eaten[j]:
                flies_eaten[j] = True
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw the board
    draw_board()

    # Draw the spiders and flies
    draw_agents()
    
    # Update the display
    pygame.display.flip()

    # Introduce a delay of 0.5 seconds
    time.sleep(1)

    # Check if all flies are eaten
    if all(flies_eaten):
        running = False
        time.sleep(3)

print(total_cost)

# Quit Pygame
pygame.quit()
sys.exit()
