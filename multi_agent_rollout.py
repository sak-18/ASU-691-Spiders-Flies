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

# Function to perform a 1-step lookahead rollout simulation for a specific spider
# Input: Current state of the spiders, current spider to start the rollout
# Returns: Cost for the rollout from the provided state of spiders
def rollout(spiders, spider_index):
    rollout_spiders = spiders[:]
    total_cost = 0
    rollout_flies_eaten = flies_eaten[:]

    # Check for fly captures
    for i, rollout_spider in enumerate(rollout_spiders):
        for j, fly in enumerate(flies):
            if fly == rollout_spider and not rollout_flies_eaten[j]:
                rollout_flies_eaten[j] = True

    #print("============================Rollout=========================")
    while not all(rollout_flies_eaten):
        spider = rollout_spiders[spider_index]
        min_cost = float('inf')
        closest_fly_index = None
        #time.sleep(0.1)
        print(f"Rollout step: Spider {spider_index}, Current position: {spider}, Rollout flies eaten: {rollout_flies_eaten}, Total cost: {total_cost}")

        for i, fly in enumerate(flies):
            if rollout_flies_eaten[i]:
                continue
            
            distance = manhattan_distance(spider, fly)
            
            if distance < min_cost:
                min_cost = distance
                closest_fly_index = i
            elif distance == min_cost and abs(flies[closest_fly_index][0] - spider[0]) < abs(flies[i][0] - spider[0]):
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
        
        spider_index = (spider_index + 1) % len(spiders)
    
    return total_cost

def move_spider(spider_index):
    #print("============================Lookahead States =========================")
    cur_pos = spiders[spider_index][:]
    select_move = None
    min_cost = float('inf')
    
    for move in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_pos = (cur_pos[0] + move[0], cur_pos[1] + move[1])
        if 0 <= new_pos[0] < GRID_COLS and 0 <= new_pos[1] < GRID_ROWS and new_pos not in spiders:
            lookahead_spiders = spiders[:]
            lookahead_spiders[spider_index] = new_pos
            rollout_cost = rollout(lookahead_spiders, spider_index)
            
            if rollout_cost < min_cost:
                select_move = move
                min_cost = rollout_cost
            elif rollout_cost == min_cost and move[0] != 0:  # Preference for horizontal moves over vertical direction
                select_move = move

    if select_move:
        updated_spider = (cur_pos[0] + select_move[0], cur_pos[1] + select_move[1])
        updated_spiders = spiders[:]
        updated_spiders[spider_index] = updated_spider
        return updated_spiders
    else:
        return spiders  # Return the current spider's location if no valid move is found

# # Function to move the current spider based on the best rollout cost after 1-step lookahead
# # Input: Current spider
# # Output: Spider's new updated position
# def move_spider(spider_index):
#     cur_pos = spiders[spider_index][:]
#     select_move = None
#     min_cost = float('inf')
    
#     for move in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
#         new_pos = (cur_pos[0] + move[0], cur_pos[1] + move[1])
#         if 0 <= new_pos[0] < GRID_COLS and 0 <= new_pos[1] < GRID_ROWS and new_pos not in spiders:
#             lookahead_spiders = spiders[:]
#             lookahead_spiders[spider_index] = new_pos
#             rollout_cost = rollout(lookahead_spiders, spider_index)
            
#             if rollout_cost < min_cost:
#                 select_move = move
#                 min_cost = rollout_cost
#             elif rollout_cost == min_cost and move[0] != 0:
#                 select_move = move

#     if select_move:
#         updated_spider = (cur_pos[0] + select_move[0], cur_pos[1] + select_move[1])
#         updated_spiders = spiders[:]
#         updated_spiders[spider_index] = updated_spider
#         return updated_spiders
#     else:
#         return spiders  # Return the current spider's location if no valid move is found

# Main loop
running = True
total_cost = 0  # To be compared with other programs, increment by one with each move
spider_index = 0  # Start with the first spider
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

    # Move the spider
    spiders = move_spider(spider_index)
    
    total_cost += 1
    
    # Alternate between spiders
    spider_index = (spider_index + 1) % len(spiders)  

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
