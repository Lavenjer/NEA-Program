import pygame
import random
import heapq
import time
import math
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

#constants
grid_size = 10  #20x20 grid
cell_size = 84  #each cell is 20x20 pixels (always round down when changing the cell size in the function) y=814/x
screen_size = grid_size * cell_size
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

class Load: #Load each of the images and scale them to fit the screen or cell in the grid
    def images(self, cell_size, screen_size):
        """
        Loads and scales images from the assets folders.
        """
        assets_folders = ["./Assets/Tile Images", "./Assets/Menu Images"]

        # Load raw image paths
        tile_images_raw = self.load_assets(assets_folders[0])
        menu_images_raw = self.load_assets(assets_folders[1])

        # Scale the images
        tile_images = self.scale(tile_images_raw, cell_size)
        menu_images = self.scale(menu_images_raw, screen_size)

        return tile_images + menu_images

    def load_assets(self, assets_folder):
        """
        Reads all image file paths from the specified folder.
        """
        file_images = []
        try:
            for img_file in sorted(os.listdir(assets_folder)):
                try:
                    if img_file.endswith((".png", ".jpeg", ".jpg")):
                        # Append the full path of the image file
                        file_images.append(os.path.join(assets_folder, img_file)) #dynamically appends the list using os.path() to help make the program more portable
                except FileNotFoundError as e:
                    print(f"Error loading file {img_file}: {e}") #Error message printed when failing to load
                    self.placeholder()
        except Exception as e:
            print(f"Assets folder is not present: {e}")
            self.placeholder()
        return file_images
    
    def placeholder(self):
        """
        Handles the case that the menu images cannot be loaded. This method displays
        the placeholder menu screen to notify the player that the menu is unable to
        load and the game cannot continue.
        """
        screen.fill((0, 0, 255)) #Fills the entire screen with a blue colour
        pygame.font.init() #Initializes the font
        error_text = pygame.font.Font(None, 40) #creates a font for the text
        placeholder_menu_text = error_text.render(f"Image file(s) have failed to load. Please Check the files", True, (255, 255, 255)) #renders the font as a surface which can be drawn
        screen.blit(placeholder_menu_text, (50, 400)) #draws the surface "placeholder_menu_text" at the location
        pygame.display.update() #Updates the display so the screen can be seen
        start_error_display_duration = time.time() #Loop which allows the screen to be displayed for 5 seconds
        while time.time() - start_error_display_duration < 5: #Loop duration is 5 seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #Allow the user to quit the program while the screen si displayed
                    pygame.quit()
                    exit()
        pygame.quit()
        exit()


    def scale(self, file_images_raw, scaling):
        """
        Scales the raw images to the specified size.
        """
        scaled_images = []  # Initialize a list to store scaled images
        for img in file_images_raw:
            try:
                # Load the image and scale it
                loaded_image = pygame.image.load(img)
                scaled_image = pygame.transform.scale(loaded_image, (scaling, scaling)) #Scales the image to the scale in the parameter (cell_size or screen_size)
                scaled_images.append(scaled_image)
            except Exception as e:
                print(f"Error scaling image {img}: {e}") #Print error message if scaling fails
                # Add a placeholder image in case of an error
                placeholder = pygame.Surface((scaling, scaling))
                placeholder.fill((255, 0, 0))  # Red color for missing images
                scaled_images.append(placeholder) #Puts in a pure red image scaled to the scale factor as a placeholder
        return scaled_images

    #Draw each of the loaded images into their cell and scaled properly
    def entities(Goal, player, enemy, Buffs, images, cell_size): 
        """
        Scales and draws all the entities according to their variable cell sizes.
        """
        #screen.blit() draws a surface onto the screen; The surface being the scaled iamges.
        screen.blit(images[3], (Goal.x * cell_size, Goal.y * cell_size)) #Index 3 is the goal
        screen.blit(images[2], (player.x * cell_size, player.y * cell_size)) #Index 2 is the player ship
        screen.blit(images[5], (enemy.x * cell_size, enemy.y * cell_size)) #Index 5 is the enemy ship
        #Do the same for each buff present
        for Buff in Buffs: 
            screen.blit(images[6], (Buff.x * cell_size, Buff.y * cell_size)) #Index 6 is the clock buff

    #Unload the buffs by loading all the entities again but without loading the buffs
    def unloadBuff(Goal, player, enemy, Buffs, images, cell_size):
        """
        Re-scales and draws all the entities according to their variable cell sizes but without loading the buff.
        """
        screen.blit(images[3], (Goal.x * cell_size, Goal.y * cell_size)) #Index 3 is the goal
        screen.blit(images[2], (player.x * cell_size, player.y * cell_size)) #Index 2 is the player ship
        screen.blit(images[5], (enemy.x * cell_size, enemy.y * cell_size)) #Index 5 is the enemy ship

    #Draw each cell represented by the shortestpath tuple as the trail image to show the trail
    def loadTrail(shortestpath, cell_size, images):
        """
        Draws the shortest path in the maze using the alientrail.png images
        """
        for px, py in shortestpath:
                screen.blit(images[4], (px * cell_size, py * cell_size)) #Draws the trail image (Index 4 is the trail image).

#Handles all the audio within the game
class Audio:
    """
    Handles all the audio in the game
    """
    #Initialize the sounds 
    def __init__(self):
        """
        Initialize local variables and load the sound files
        """
        pygame.mixer.init()
        try:
            self.win_sound = pygame.mixer.Sound("./Assets/Audio files/WinSound.mp3") 
            self.buff_sound = pygame.mixer.Sound("./Assets/Audio files/BuffSound.mp3")
        except FileNotFoundError as e:
            print(f"Sound file(s) not found: {e}") #Print debug in case the sounds fail to load
            self.win_sound = None
            self.buff_sound = None

    #Play the main theme indefinitely
    def play_soundtrack(self):
        """
        Play the main soundtrack. This is loaded into the pygame.mixer.music() library function rather than the pygame.mixer.Sound() 
        library function since the Sound() one loads multiple audio tracks and takes more memory. music() is a more static library function
        which conserves memory. It's used for the longer tracks such as this
        """
        try:
            pygame.mixer.music.load("./Assets/Audio files/FunkySounds.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1) #.play(-1) means it will play indefinitely until stopped
        except Exception as e:
            print(f"Soundtrack not found: {e}") #Print debug in case soundtrack doesnt load

    #Play the loss sound effect
    def play_loss(self):
        """
        Play loss soundtrack. This is loaded into the pygame.mixer.music() library function rather than the pygame.mixer.Sound() 
        library function since the Sound() one loads multiple audio tracks and takes more memory. music() is a more static library function
        which conserves memory. It's used for the longer tracks such as this
        """
        try:
            pygame.mixer.music.load("./Assets/Audio files/ScarySounds.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(1) #.play(1) means it will play only once
        except Exception as e:
            print(f"Loss sound not found: {e}") #Print debug in case loss track doesnt load

    #Stop the music in use (loss sound or main theme). These are put into the pygame.mixer.music library section instead of the pygame.mixer.Sound library section since only one music track can be loaded at a time and the 2 longest audio tracks are loaded into them to save processing power
    def stop(self):
        """
        stops the soundtrack and unloads it to save memory
        """
        pygame.mixer.stop()
        pygame.mixer.music.unload()
    
    def play_win(self):
        """
        plays the win sound
        """
        try:
            self.win_sound.play()
        except:
            print("Win sound is not present")

    def play_buff(self):
        """
        plays the sound when getting a buff
        """
        try:
            self.buff_sound.play()
        except:
            print("Buff sound is not present")

#Handles all the menu and tutorial pages
class Menu:
    #Initialize all the local variables
    def __init__(self, images):
        """
        Initialize local variables for the Menu
        """
        self.menu_image = 7 #Index 7 is the start of the menu images in the images array
        self.images = images
        self.in_loop = True
        self.choice = True
    
    def show_menu(self):
        """
        Shows 2 similar looking menu images which flicker between eachother at short intervals to imitate a draw or plaful effect for the
        target audience. The self.images list is ordered in a way that the image that is similar to the other is the next index. Thus
        self.images[self.menu_image] and self.images[self.menu_image + 1] is used.
        """
        clock = pygame.time.Clock()
        self.in_loop = True
        while self.in_loop:
            for event in pygame.event.get(): #Gets all the input events in pygame.
                if event.type == pygame.QUIT: #If the user closes the tab then pygame closes and the program exits
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN: #Runs when any key press event occurs
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN): #If the user clicks enter or return the loop stops and they can advance
                        self.in_loop = False
            current_menu = self.images[self.menu_image] if int(time.time() * 5) % 2 == 0 else self.images[self.menu_image + 1] #Switches between two similar frames of a menu image
            screen.blit(current_menu, (0, 0)) #Draws the menu onto the screen
            pygame.display.update() #Updates the display to show the changes
            clock.tick(60)

    def ask_difficulty_and_debug(self):
        """
        This is nearly identical to the show_menu() method except that this is where you can access the hidden debug mode which must require
        another input option. A sound cue is given when the debug mode is set to either true or false using the methods in the Audio class.
        This specific menu screen also handles the difficulty choice which affects the function which dictates the time, maze properties, and buff bonus.
        """
        #Initializes all the variables and objects needed
        debug_sound = Audio()
        clock = pygame.time.Clock()
        self.in_loop = True
        self.debug_mode = False

        while self.in_loop:
            for event in pygame.event.get(): #Gets all the input events in pygame.
                if event.type == pygame.QUIT: #If the user closes the tab then pygame closes and the program exits
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN: #Runs when any key press event occurs
                    if event.key == pygame.K_h: #When the player clicks h, hard difficulty is chosen
                        self.choice = False
                        self.in_loop = False
                    if event.key == pygame.K_e: #When the player clicks e, easy difficulty is chosen
                        self.choice = True
                        self.in_loop = False
                    if event.key == pygame.K_d: #When the player clicks d, debug mode is toggled on with two different sounds when toggled on or off
                        if self.debug_mode == False:
                            self.debug_mode = True
                            debug_sound.play_win()
                        elif self.debug_mode == True:
                            self.debug_mode = False
                            debug_sound.play_buff()

            current_difficultymenu = self.images[9] if int(time.time() * 5) % 2 == 0 else self.images[10] #Draws the difficulty menu using the same method as the menus
            screen.blit(current_difficultymenu, (0, 0))
            pygame.display.update()
            clock.tick(60)
        return self.choice
    
    def ask_yes_or_no(self, YNindex):
        """
        This is used for all the yes or no menu screens.
        """
        clock = pygame.time.Clock()
        self.in_loop = True
        while self.in_loop:
            for event in pygame.event.get(): #Gets all the input events in pygame.
                if event.type == pygame.QUIT: #If the user closes the tab then pygame closes and the program exits
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN: #Runs when any key press event occurs
                    if event.key == pygame.K_y: #The user inputs y for Yes
                        self.choiceYN = True
                        self.in_loop = False
                    if event.key == pygame.K_n: #The user inputs n for No
                        self.choiceYN = False
                        self.in_loop = False

            current_difficultymenu = self.images[YNindex] if int(time.time() * 5) % 2 == 0 else self.images[YNindex + 1] #The same method is used for drawing the the yes or no screens.
            screen.blit(current_difficultymenu, (0, 0))
            pygame.display.update()
            clock.tick(60)
        return self.choiceYN
    
    def show_high_scores(self, score_file):
        """
        This method reads the scores.txt file and updates the top score if surpassed. It then draws the scores onto the score menu. This
        screen also flicks between two similar images.
        """
        # Load the high scores screen image (index 27)
        high_scores_image = self.images[27]

        # Read scores from the text file
        try:
            with open(score_file, "r") as file:
                lines = file.readlines()
                current_score = lines[0].strip()  # First line: Current score
                top_score = lines[1].strip()      # Second line: Top score
                file.close()
                error = False
        except (FileNotFoundError, IndexError):
            # Handle missing file or insufficient lines in the file
            current_score = "0"
            top_score = "0"

        # Set up the font
        font = pygame.font.Font(None, 100)  # Default font, size 50

        # Render the scores as text
        current_score_text = font.render(f"Current Score: {current_score}", True, (255, 255, 255))  # White color
        top_score_text = font.render(f"Top Score: {top_score}", True, (255, 255, 255))  # White color

        # Display the high scores screen
        clock = pygame.time.Clock()
        self.in_loop = True
        while self.in_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.in_loop = False  # Exit the high scores screen

            # Blit the high scores image
            screen.blit(high_scores_image, (0, 0))

            # Blit the scores onto the screen
            screen.blit(current_score_text, (100, 700))  # Position for current score
            screen.blit(top_score_text, (100, 400))      # Position for top score

            # Update the display
            pygame.display.update()
            clock.tick(60)
    
    def run_menu(self):
        """
        Utilizes the previous methods to run through the full starting menu.
        """
        self.show_menu()
        self.menu_image = self.menu_image + 6 #skips to the explain1(1) image since difficultymenu and tutorial images will be shown
        self.choice = self.ask_difficulty_and_debug()
        YNindex = 11 #Index for first tutorial image
        self.choiceYN = self.ask_yes_or_no(YNindex)
        if self.choiceYN == True:
            while self.menu_image < 22: #Displays every "explain" image for the tutorial until index 21 which is the final one
                self.show_menu()
                self.menu_image = self.menu_image + 2
        return self.choice, self.debug_mode
    
    def run_win_menu(self):
        """
        Utilizes the other previous methods to run the ending menu while asking the player if they would like to
        continue or not.
        """
        ##23 24
        self.menu_image = 23 #Index for the win screen
        self.show_menu()
        self.show_high_scores("scores.txt")
        YNindex = 25 #Index for the continue screen
        self.choiceYN = self.ask_yes_or_no(YNindex)
        if self.choiceYN == False:
            pygame.quit()
            exit()

class Maze:
    """
    Handles all the methods relating to mazes.
    """
    def __init__(self, grid_size):
        """
        Generates a grid using the maze generation method
        """
        self.grid = self.gen(grid_size)

    def gen(self, grid_size):
        """
        Creates a maze using the Depth First Search algorithm. The algorithm is a 2d grid
        which starts at a random position and creates paths to neighbour cells. this makes sure that
        the entire mze is fully connected and not disjointed (all walls connected). The grid size
        is dictated by the grid_size.

        index 1 = Wall
        index 0 = path
        """
        stack = [] #Stack to keep track of the current path in the DFS
        visited = set() #Set to keep track of the visited cells
        maze = [[1] * grid_size for _ in range(grid_size)] #Initializes the grid with walls (image 1)

        #Starting at a random position
        start_x = random.randint(0, grid_size - 1)
        start_y = random.randint(0, grid_size - 1)
        stack.append((start_x, start_y))
        visited.add((start_x, start_y))
        maze[start_y][start_x] = 0 #Starting cell becomes a path (image 0)

        while stack:
            x, y = stack[-1] #Fetch current cell
            random.shuffle(directions) #randomizes the direction 
            moved = False
            for directionx, directiony in directions: #Attempt to go to neighbour cell
                neighbourx, neighboury = x + directionx * 2, y + directiony * 2
                if 0 <= neighbourx < grid_size and 0 <= neighboury < grid_size and (neighbourx, neighboury) not in visited: #Check if neighbour is within bounds and isnt visited
                    #Create a path to the neighbour by setting cells as path (image 0)
                    maze[neighboury][neighbourx] = 0
                    maze[y + directiony][x + directionx] = 0
                    visited.add((neighbourx, neighboury))
                    stack.append((neighbourx, neighboury))
                    moved = True
                    break

            if not moved: #If moving isnt possible then backtrack
                stack.pop()
        return maze
    
    def randfreespot(self, *excluded, grid_size):
        """
        finds a random free spot that isnt in the excluded set and isnt a wall
        """
        excluded_set = set(excluded)
        free_spots = [
            (x, y)
            for y in range(grid_size) 
            for x in range(grid_size) 
            if self.grid[y][x] == 0 and (x, y) not in excluded_set
        ]
        return random.choice(free_spots)

    def solve(self, start, goal, grid_size):
        """
        Solves the maze using Dijkstra's shortest path algorithm. The algorithm determines
        the shortest path between the starting position and the goals position.
        """
        priorityqueue = [] #Stores cells with their weightage (distance)
        heapq.heappush(priorityqueue, (0, start)) #Push the starting position as 0
        distances = {start: 0} #Dictionary which stores the shortest distance to each cell
        previous = {} #Disctionary that stores the previous cell int he shortest path

        while priorityqueue:
            current_dist, current = heapq.heappop(priorityqueue) #Fetch the cell with the smallest weight (distance)
            
            #When the goal is reached, reconstruct the path
            if current == goal:
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                return path[::-1] #Reverses the path so its from start position to goal position

            x, y = current #Current cell position

            #Visit neighbour cells
            for dx, dy in directions:
                nx, ny = x + dx, y + dy #Position of neighbouring cells
                if 0 <= nx < grid_size and 0 <= ny < grid_size and self.grid[ny][nx] == 0: #Check if neighbour is in the bounds and is a path
                    new_dist = current_dist + 1 #Calculate new distance
                    if (nx, ny) not in distances or new_dist < distances[(nx, ny)]: #Check if neighbour cell has not been visited or the shortest path is determined
                        distances[(nx, ny)] = new_dist #Update weight (distance)
                        heapq.heappush(priorityqueue, (new_dist, (nx, ny))) #Add neighbour to priority queue
                        previous[(nx, ny)] = current #Update previous cell
        return [] #If no path found then empty list is returned
    
class Difficulty:
    """
    Handles the balancing for both difficulty settings
    """
    def __init__(self, choice):
        """
        Initializes the maximum and minimum grid sizes for the respective difficulties
        """
        if choice == True: #easy difficulty
            self.max_grid_size = 60
            self.min_grid_size = 10
        else: #hard difficulty
            self.max_grid_size = 90
            self.min_grid_size = 15
    
    def set_values(self, wins):
        """
        Handles the maze size increase for both difficulties. It will take 50 wins on both difficulties to reach their maximum grid size.
        """
        #Increases the grid size with a calculated increment
        increment = (self.max_grid_size - self.min_grid_size) / 50  #50 levels to reach max grid size
        grid_size = min(self.max_grid_size, max(self.min_grid_size, int(self.min_grid_size + wins * increment))) #The grid size increases by the minimum grid size plus the wins multiplied by the increment. The cap for this is the max grid size

        # Calculate cell size using the equation: cell_size = 841 / grid_size (truncated)
        cell_size = math.floor(841 / grid_size)

        return grid_size, cell_size, #max_time

    def scale_time(self, wins, choice, shortestpath):
        """
        Handles the time increase in relation to the shortest path length and wins for each difficulty
        """
        time_addition_easy, time_addition_hard, time_multiplier_easy, time_multiplier_hard, pathcount = self.set_time_calculation_constants(shortestpath)
        if choice == True:
            max_time = self.calculate_time(time_addition_easy, time_multiplier_easy, wins, pathcount)
        elif choice == False:
            max_time = self.calculate_time(time_addition_hard, time_multiplier_hard, wins, pathcount)
        return max_time

    def calculate_time(self, time_addition, time_multiplier, wins, pathcount):
        """
        Performs all the calculations for each difficulty while making sure the time increase caps out at 20 wins
        """
        if wins <=20:
            max_time = (pathcount * 0.15) + time_addition  + time_addition * (time_multiplier * wins)
        elif wins > 20:
            max_time = (pathcount * 0.15) + time_addition  + time_addition * (time_multiplier * 20)
        return max_time

    def set_time_calculation_constants(self, shortestpath):
        """
        Initializes the local constants used within this class to calculate both the easy and hard time increase with just one method.
        """
        pathcount = 0
        pathcount = len(shortestpath)
        time_addition_easy = 10
        time_addition_hard = 5
        time_multiplier_easy = 0.2
        time_multiplier_hard = 0.1
        return time_addition_easy, time_addition_hard, time_multiplier_easy, time_multiplier_hard, pathcount
    
class Entity:
    """
    Handles the entities in the maze
    """
    def __init__(self, maze, *excluded, grid_size):
        """
        Creates an entity in the maze
        """
        self.x, self.y = maze.randfreespot(*excluded, grid_size=grid_size)
        self.shortest_path = []

    def move(self, maze, dx, dy, grid_size):
        """
        Allows an entitiy to move (only the player moves)
        """
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size and maze.grid[ny][nx] == 0: #Checks if the intended cell to mvoe into is in the range and isnt a wall
            self.x, self.y = nx, ny

class Input:
    """
    Handles all the inputs the user makes
    """
    def __init__(self, game):
        """
        allows the methods to use the local variables from the Game class.
        """
        self.game = game
    
    def hotkeys(self, images):
        """
        Handles the hotkeys the player can use and the case where they quit the program so they quit it gracefully.
        """
        for event in pygame.event.get(): #Gets all the events in pygame.
            if event.type == pygame.QUIT: #If the user closes the tab then pygame closes and the program exits
                self.game.running = False
            if event.type == pygame.KEYDOWN: #Runs when any key press event occurs
                if event.key == pygame.K_m: #Shows the menu again (able to re-acces the tutorial)
                    self.game.music.stop()
                    menu = Menu(self.game.images)
                    Menu.run_menu(menu)
                    self.game.reset(images)  # Reset the current game state
                    self.game.music.play_soundtrack()
                if self.game.debug_mode == True: #Allows access to debug hotkeys
                    self.debug_hotkeys(event)

    def debug_hotkeys(self, event):
        """
        Handles the hotkeys used for debugging when debug mode is toggled on.
        All of the debug hotkeys are as follows:
        -r: Resets game state
        -t: Toggles showing the shortest path
        -q: Increases wins by 1
        -e: Decreases wins by 1
        -y: Increases the time by 10
        -x: Decreases the time by 10
        -u: Prints the player position
        -i: Prints the enemy position
        -j: Prints the goal position
        -k: Prints the buff position(s)
        """
        if event.type == pygame.KEYDOWN: #Runs when any key press event occurs
            if event.key == pygame.K_r: #Resets the game state when pressing r
                self.game.reset(images)
                self.game.music.stop()
                self.game.music.play_soundtrack()
            if event.key == pygame.K_t: #Shows the shortest path with a trail (This is toggleable) when pressing t
                    self.game.shortestpath = self.game.maze.solve(
                        (self.game.enemy.x, self.game.enemy.y),
                        (self.game.Goal.x, self.game.Goal.y), 
                        self.game.grid_size,
                    )
                    if self.game.show_trail == False:
                        self.game.show_trail = True
                    elif self.game.show_trail == True:
                        self.game.show_trail = False
            if event.key == pygame.K_q: #Increments the wins by 1 when pressing q
                self.game.wins = self.game.wins + 1
            if event.key == pygame.K_e: #Decrements the wins by 1 when pressing e
                if self.game.wins > 0:
                    self.game.wins = self.game.wins - 1
            if event.key == pygame.K_y: #Increments the time by 10 when pressing y
                self.game.time = self.game.time + 10
            if event.key == pygame.K_x: #Decrements the time by 10 when pressing x
                self.game.time = self.game.time - 10
            if event.key == pygame.K_u: #Prints the players current position on the grid when pressing u
                print("-------------------------------------")
                print(f"player_x: {self.game.player.x}")
                print(f"player_y: {self.game.player.y}")
                print("-------------------------------------")
            if event.key == pygame.K_i: #Prints the enemys current position on the grid when pressing i
                print("-------------------------------------")
                print(f"enemy_x: {self.game.enemy.x}")
                print(f"enemy_y: {self.game.enemy.y}")
                print("-------------------------------------")
            if event.key == pygame.K_j: #Prints the goals current position on the grid when pressing j
                print("-------------------------------------")
                print(f"Goal_x: {self.game.Goal.x}")
                print(f"Goal_y: {self.game.Goal.y}")
                print("-------------------------------------")
            if event.key == pygame.K_k: #Prints the current position of all the buffs present when pressing k
                c = 0
                print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
                for buff in self.game.Buffs:
                    c = c + 1
                    print("-------------------------------------")
                    print(f"Buff[{c}]: X = {buff.x} Y = {buff.y}")
                    print("-------------------------------------")
                print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
    
    def handle_movement(self):
        """
        Handles all the movement input from the player to allow them to travel in the maze
        """
        keys = pygame.key.get_pressed() #Fetches all the key inputs
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.game.player.move(self.game.maze, -1, 0, self.game.grid_size) #The player moves left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            self.game.player.move(self.game.maze, 1, 0, self.game.grid_size) #The player moves right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.game.player.move(self.game.maze, 0, -1, self.game.grid_size) #The player moves up
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.game.player.move(self.game.maze, 0, 1, self.game.grid_size) #The player mvoes down
        


class Game:
    """
    Handles the main game loop and all the methods needed to run the program
    """
    def __init__(self, images, difficultychoice, debug_mode):
        """
        Initialize all the local variables and instantiates some objects to use later
        """
        self.images = images
        self.difficultychoice = difficultychoice
        self.debug_mode = debug_mode
        self.difficulty = Difficulty(self.difficultychoice)

        # Initialize game state
        self.setup_game_state()

        # Initialize maze and entities
        self.setup_entities()

        # Initialize audio
        self.music = Audio()

        # Input handler
        self.input_handler = Input(self)

    def setup_game_state(self):
        """
        Initialize game state variables.
        """
        self.score = 0
        self.running = True
        self.wins = 0
        self.loss = 0
        self.max_time = 30
        self.timer = 0
        self.show_trail = False
        self.clock = pygame.time.Clock()

    def setup_entities(self):
        """
        Initialize the maze, player, goal, enemy, and buffs.
        """
        self.grid_size = 10
        self.cell_size = 84
        self.maze = Maze(self.grid_size)
        self.player = Entity(self.maze, grid_size=self.grid_size)
        self.Goal = Entity(self.maze, (self.player.x, self.player.y), grid_size=self.grid_size)
        self.Buffs = []
        self.enemy = Entity(self.maze, (self.Goal.x, self.Goal.y), grid_size=self.grid_size)
        self.enemy.x, self.enemy.y = self.player.x, self.player.y
        self.shortestpath = self.maze.solve(
            (self.enemy.x, self.enemy.y), (self.Goal.x, self.Goal.y), self.grid_size
        )

        # Add an initial buff
        new_buff = Entity(
            self.maze, (self.player.x, self.player.y), (self.Goal.x, self.Goal.y), grid_size=self.grid_size
        )
        self.Buffs.append(new_buff)

    def reset(self, images):
        """
        Resets the game state.
        """
        menu = Menu(self.images)
        self.handle_win()
        self.grid_size, self.cell_size, = self.difficulty.set_values(self.wins)
        self.reset_values()
        self.handle_buff_count()

    def handle_buff_count(self):
        """
        Handles the generation of buffs based on the wins 
        """
        count = 0
        count = count + 1
        if self.wins > 4: #Adds an extra buff past 5 wins
            count = count + 1
        wincount = self.wins // 10
        if wincount >= 1 and wincount <= 5: #Increments the count for every 10 wins 
            count = count + wincount
        elif wincount > 5:
            count = count + 5
        while count != 0: #Creates a new buff for every count that accumulated in the previous statements
            new_buff = Entity(self.maze, (self.player.x, self.player.y), (self.Goal.x, self.Goal.y), *self.shortestpath, grid_size=self.grid_size)
            self.Buffs.append(new_buff)
            count = count - 1
        self.max_time = self.difficulty.scale_time(self.wins, self.difficultychoice, self.shortestpath)
        self.time = time.time()

    def reset_values(self):
        """
        Resets the game state's values.
        """
        self.images_instance = Load()
        self.images = self.images_instance.images(self.cell_size, (self.grid_size * self.cell_size))
        self.maze = Maze(self.grid_size)
        self.player = Entity(self.maze, grid_size=self.grid_size)
        self.Goal = Entity(self.maze, (self.player.x, self.player.y), grid_size=self.grid_size)
        self.Buffs = []
        self.enemy = Entity(self.maze, (self.player.x, self.player.y), (self.Goal.x, self.Goal.y), grid_size=self.grid_size)
        self.enemy.x, self.enemy.y = self.player.x, self.player.y
        self.shortestpath = self.maze.solve((self.enemy.x, self.enemy.y), (self.Goal.x, self.Goal.y), self.grid_size)

    def handle_win(self):
        """
        Handles the case in which the player wins at level 30. It then updates the top score if beaten and
        uses a text file to store the information
        """
        if self.wins == 31:
            # Read the current top score from the file
            try:
                with open("scores.txt", "r") as file:
                    lines = file.readlines()
                    top_score = int(lines[1].strip()) if len(lines) > 1 else 0
                    file.close()  # Explicitly close the file after reading
            except (FileNotFoundError, ValueError, IndexError):
                # Handle missing file or invalid data
                top_score = 0

            # Update the top score if the current score is higher
            top_score = max(self.score, top_score)

            # Write the current score and updated top score to the file
            with open("scores.txt", "w") as file:
                file.write(f"{self.score}\n")  # First line: Current score
                file.write(f"{top_score}\n")  # Second line: Top score
                file.close()  # Explicitly close the file after writing

            # Show the high scores screen
            menu.run_win_menu()

    def handle_loss(self):
        """
        Handles the case when the player loses. It shows the shortest path and cancels any input except for quitting
        """
        if self.timer == 0:
                self.loss = self.loss + 1
                self.music.stop()
                self.music.play_loss()
                settime = time.time()
                audiotime = 0
                self.shortestpath = self.maze.solve((self.enemy.x, self.enemy.y), (self.Goal.x, self.Goal.y), self.grid_size)
                Load.loadTrail(self.shortestpath, self.cell_size, self.images)
                pygame.display.update()
                while audiotime < 12: #Plays the audio until it finishes and shows the trail during this time and halts any input until it ends
                    audiotime = time.time() - settime
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                    pygame.time.delay(100) #Delay to save processing power. Otherwise it will urn as fast as it possibly can and lag.
                self.music.stop()
                self.reset(images)
                self.music.play_soundtrack()

    def handle_buff(self):
        """
        Dynamically gives time for collecting the buff. The time given is based on the amount of wins to a limit and the difficulty
        """
        for Buff in self.Buffs: #Goes through each buff in the tuple self.Buffs
            if self.player.x == Buff.x and self.player.y == Buff.y: #Case when the player gets the buff
                self.Buffs.remove(Buff) #Pops the Buff object from the self.Buffs tuple
                self.score = self.score + 400 #Grants score for getting a buff
                if self.difficultychoice == True: #Easy difficulty
                    self.time = self.time + min(30, 10 + 10 * (0.1 * self.wins)) #Dynamically gives bonus time based on the wins until the limit
                elif self.difficultychoice == False: #Hard difficulty
                    self.time = self.time + min(25, 5 + 10 * (0.1 * self.wins)) #Dynamically gives bonus time based on the wins until the limit
                Load.unloadBuff(self.Goal, self.player, self.enemy, self.Buffs, self.images, self.cell_size)
                self.music.play_buff()

    def draw_grid(self):
        """
        Draws the grid with the tile images. If the player toggles show trail in debug mode, it also draws the trail
        """
        for y in range(self.grid_size): #Selects each cell top to bottom, left to right
            for x in range(self.grid_size):
                if self.maze.grid[y][x] == 1: #If grid position is 1, Draw the scaled path image onto the cell position
                    screen.blit(self.images[0], (x * self.cell_size, y * self.cell_size))
                else: #If grid position isnt 1, Draw the scaled wall time image onto the cell position
                    screen.blit(self.images[1], (x * self.cell_size, y * self.cell_size))
        if self.show_trail == True: #If the show_trail is toggled from the debug menu, Load the trail and draw it using the alien trail images.
            Load.loadTrail(self.shortestpath, self.cell_size, self.images)
            pygame.display.update() #Update the display to show the changes made

    def render_game(self):
        """
        Renders the game with entities and the grid
        """
        self.draw_grid()
        Load.entities(self.Goal, self.player, self.enemy, self.Buffs, self.images, self.cell_size)

    def handle_goal(self):
        """
        Handles the case when the player reaches the goal. Gives score for winning
        """
        if (self.player.x, self.player.y) == (self.Goal.x, self.Goal.y): #Case when player reaches the goal
            self.music.play_win()
            self.wins = self.wins + 1
            self.score = self.score + 1000
            self.reset(images)

    def update_timer_and_stats(self):
        """
        Updates the status of the current level by showing the level, score, and timer
        """
        self.timer = max(0, self.max_time + (self.time - time.time()))
        fps = self.clock.get_fps()
        pygame.display.set_caption(
            f"(Level: {self.wins})(Time remaining: {self.timer:.1f})(Score: {self.score})(FPS: {fps:.0f})"
            ) #Displays the wins, timer, and score

    def run(self, images):
        """
        The main game loop. This loops many times per second so a delay is added to control the processes
        """
        self.music.play_soundtrack()
        self.time = time.time()
        while self.running:
            pygame.time.delay(100)
            #Handle input
            self.input_handler.hotkeys(images)
            self.input_handler.handle_movement()

            #Handle events
            self.handle_goal()
            self.render_game()
            self.handle_buff()
            self.update_timer_and_stats()

            #Handle loss if any  
            self.handle_loss()
            pygame.display.update()
            self.clock.tick(60)
screen = pygame.display.set_mode((screen_size, screen_size)) #Set the screen size
pygame.display.set_caption("maze game v1.0") #Set the caption
images_instance = Load()
images = images_instance.images(cell_size, screen_size)
menu = Menu(images)
difficultychoice, debug_mode = Menu.run_menu(menu)
game = Game(images, difficultychoice, debug_mode)
game.run(images)