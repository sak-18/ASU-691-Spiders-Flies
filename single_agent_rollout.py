import pygame
import sys
import time
import random

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
flies = [(1, 7), (2, 3), (4, 6), (8, 2), (8, 8)]  # Coordinates now represent (row, column)/(x, y)
spiders = [(6, 0), (6, 0)]  # Two spiders starting at adjacent positions

# Initialize flies_eaten array to track eaten flies
flies_eaten = [False] * len(flies)

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

# Function to perform a 1-step lookahead rollout simulation for both spiders
def rollout(new_spiders):
    rollout_spiders = new_spiders[:]
    total_cost = 0
    rollout_flies_eaten = flies_eaten[:]
    
    # Check for fly captures
    for i, rollout_spider in enumerate(rollout_spiders):
        for j, fly in enumerate(flies):
            if fly == rollout_spider and not rollout_flies_eaten[j]:
                rollout_flies_eaten[j] = True

    while not all(rollout_flies_eaten):
        print("Spider positions:", rollout_spiders)
        for spider_index, spider in enumerate(rollout_spiders):
            min_cost = float('inf')
            closest_fly_index = None
            
            for i, fly in enumerate(flies):
                if rollout_flies_eaten[i]:
                    continue
                
                distance = manhattan_distance(spider, fly)
                print(f"Spider {spider_index} to fly {i} distance:", distance)
                
                if distance < min_cost:
                    min_cost = distance
                    closest_fly_index = i

            if closest_fly_index is not None:
                closest_fly = flies[closest_fly_index]
                if spider[0] < closest_fly[0]:
                    rollout_spiders[spider_index] = (spider[0] + 1, spider[1])
                elif spider[0] > closest_fly[0]:
                    rollout_spiders[spider_index] = (spider[0] - 1, spider[1])
                elif spider[1] < closest_fly[1]:
                    rollout_spiders[spider_index] = (spider[0], spider[1] + 1)
                elif spider[1] > closest_fly[1]:
                    rollout_spiders[spider_index] = (spider[0], spider[1] - 1)
                
                if rollout_spiders[spider_index] == closest_fly:
                    rollout_flies_eaten[closest_fly_index] = True
                
                total_cost += 1
        
    print("Final spider positions:", rollout_spiders)
    return total_cost


# Function to move the spiders considering all possibilities
# Function to move the spiders based on the best rollout cost after 1-step lookahead
def move_spiders():
    cur_pos_spider_0 = spiders[0]
    cur_pos_spider_1 = spiders[1]
    min_cost = float('inf')
    best_move_spider_0 = None
    best_move_spider_1 = None
    
    for move_0 in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_pos_0 = (cur_pos_spider_0[0] + move_0[0], cur_pos_spider_0[1] + move_0[1])
        if 0 <= new_pos_0[0] < GRID_COLS and 0 <= new_pos_0[1] < GRID_ROWS and new_pos_0 not in spiders:
            for move_1 in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_pos_1 = (cur_pos_spider_1[0] + move_1[0], cur_pos_spider_1[1] + move_1[1])
                if 0 <= new_pos_1[0] < GRID_COLS and 0 <= new_pos_1[1] < GRID_ROWS and new_pos_1 not in spiders:
                    lookahead_spiders = [new_pos_0, new_pos_1]
                    rollout_cost = rollout(lookahead_spiders)
                    
                    if rollout_cost < min_cost:
                        best_move_spider_0 = move_0
                        best_move_spider_1 = move_1
                        min_cost = rollout_cost

    # Apply the best moves
    if best_move_spider_0:
        spiders[0] = (cur_pos_spider_0[0] + best_move_spider_0[0], cur_pos_spider_0[1] + best_move_spider_0[1])
    if best_move_spider_1:
        spiders[1] = (cur_pos_spider_1[0] + best_move_spider_1[0], cur_pos_spider_1[1] + best_move_spider_1[1])


# Main loop
running = True
total_cost = 0  # To be compared with other programs, increment by one with each move
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen with a white background
    screen.fill((255, 255, 255))
    
    # Draw the game board
    draw_board()
    
    draw_agents()
    
    # Refresh the display
    pygame.display.flip()

    # Pause for a moment to control the speed of the simulation
    time.sleep(1)

    # Move the spiders
    move_spiders()
    
    total_cost += 2 #because one step by each spider

    # Check for fly captures
    for i, spider in enumerate(spiders):
        for j, fly in enumerate(flies):
            if fly == spider and not flies_eaten[j]:
                flies_eaten[j] = True

    # Check if all flies have been eaten
    if all(flies_eaten):
        running = False
        # Clear the screen with a white background
        screen.fill((255, 255, 255))
    
        # Draw the game board
        draw_board()
        
        draw_agents()
        
        # Refresh the display
        pygame.display.flip()
        
        time.sleep(3)
        

print("Total cost:", total_cost)

# Quit Pygame
pygame.quit()
sys.exit()
