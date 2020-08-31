import pygame
import os
import random
import time

pygame.font.init()

# Initialize screen
WIDTH, HEIGHT = 775, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')

# Load our images
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (WIDTH, HEIGHT))

# Lasers
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png')).convert_alpha()
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png')).convert_alpha()
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png')).convert_alpha()
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png')).convert_alpha()

# Spaceships
BLUE_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png')).convert_alpha()
GREEN_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png')).convert_alpha()
RED_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png')).convert_alpha()
# Player ship
YELLOW_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png')).convert_alpha()

# Hazards
FREEZE_HAZARD = pygame.image.load(os.path.join('assets', 'snowflake.png')).convert_alpha()


class Ship:
    """
    Abstract class that represents a ship in the game (player or enemy)
    """
    COOL_DOWN = 30  # cool down period of a half a second

    def __init__(self, x, y, health=100):
        """
        Initializes ship with specified x & y-coordinates and health. Initializes ship image
        to None, laser image to None, an empty list for lasers, and a cool down period to 0
        :param x: integer representing x-coordiante
        :param y: integer representing y-coordinate
        :param health: integer representing ship health
        """
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_count = 0

    def draw(self, screen):
        """
        Draws ships to screen, draws lasers to screen
        :param screen:
        :return:
        """
        screen.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(screen)

    def get_width(self):
        """
        Used to get the width of any ship
        :return: returns integer of the width of a ship
        """
        return self.ship_img.get_width()

    def get_height(self):
        """
         Used to get the height of any ship
        :return: returns integer of the height of a ship
        """
        return self.ship_img.get_height()

    def cool_down(self):
        """
        Counts the cool down period to know when new laser can be shot
        """
        if self.cool_down_count >= self.COOL_DOWN:
            self.cool_down_count = 0
        elif self.cool_down_count > 0:
            self.cool_down_count += 1

    def shoot(self):
        if self.cool_down_count == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            # self.cool_down_count = 0  This will make the lasers be able to continuously shoot
            self.cool_down_count = 1

    def move_lasers(self, velocity, object):
        """
        Moves enemy lasers
        :param velocity:
        :param object:
        :return:
        """
        # Call cool down to see if new laser can be shot
        self.cool_down()
        # Move all enemy lasers, delete them if they're off screen, reduce player health if collision occurs
        for laser in self.lasers:
            laser.move(velocity)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)


class Player(Ship):
    """
    Represents player ship
    """

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)  # Create mask for collision

    def draw(self, screen):
        super().draw(screen)
        self.health_bar(screen)

    def move_lasers(self, velocity, objects):
        """
        Move player lasers
        :param velocity:
        :param object:
        :return:
        """
        # Call cool down to see if new laser can be shot
        self.cool_down()
        # Move all enemy lasers, delete them if they're off screen, reduce player health if collision occurs
        for laser in self.lasers:
            laser.move(velocity)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def health_bar(self, screen):
        """
        Shows player's health bar on screen
        """
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(screen, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(Ship):
    """
    Represents enemy ships
    """

    def __init__(self, x, y, color, health=100):
        # Create hash table to determine which color enemy ship to use
        color_table = {
            'blue': (BLUE_SPACESHIP, BLUE_LASER),
            'green': (GREEN_SPACESHIP, GREEN_LASER),
            'red': (RED_SPACESHIP, RED_LASER)
        }
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = color_table[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move_enemy(self, velocity):
        """
        Moves enemy ships downward on screen
        :param velocity: integer representing how fast to move enemy ship
        :return:
        """
        self.y += velocity

    def shoot(self):
        if self.cool_down_count == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            # self.cool_down_count = 0  #This will make the lasers be able to continuously shoot
            self.cool_down_count = 1


class Laser:
    """
    Represent laser to be shot from ship (player or enemy)
    """

    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface((self.image))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, velocity):
        """
        Allows laser to move up or down across screen at given velocity
        :param velocity: float representing speed and direction of laser
        """
        self.y += velocity

    def is_off_screen(self, height):
        """
        Tells us if the laser is off the screen
        :param height: integer representing height of screen in pixels
        :return: boolean of True if laser is off screen and False otherwise
        """
        # return not (self.y <= height and self.y >= 0)
        return self.y > height or self.y < 0

    def collision(self, object):
        """
        UPDATE THIS DOC STRING
        Calls collide function
        :param object:
        :return:
        """
        return collide(self, object)


class Hazards:
    """
    Class for hazards that can occur in game
    """

    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.image = FREEZE_HAZARD
        self.mask = pygame.mask.from_surface(self.image)
        self.hazard_counter = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, velocity):
        """
        Allows hazard to downwards at given velocity
        :param velocity: float representing speed of hazard
        """
        self.y += velocity

    def update_hazard_counter(self):
        self.hazard_counter += 1

    def get_hazard_counter(self):
        return self.hazard_counter

    def get_hazard_type(self):
        return self.type

    # def is_off_screen(self, height):
    #     """
    #     Tells us if the hazard is off the screen
    #     :param height: integer representing height of screen in pixels
    #     :return: boolean of True if hazard is off screen and False otherwise
    #     """
    #     return self.y > height or self.y < 0


def collide(object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None


# Game loop
def main(player_velocity=None):
    """
    Runs game loop including displaying to screen, checking for events, allowing movement
    of player, enemies, and lasers, checking for collisions
    :return:
    """
    running = True
    FPS = 60
    game_font = pygame.font.SysFont('comicsans', 30)
    game_over_font = pygame.font.SysFont('comicsans', 80)

    # Create player ship
    player = Player(275, 490)

    # Set velocities for player, enemies, and lasers
    player_velocity = 8

    # Set level and lives
    level = 0
    lives = 3

    # Set enemies, wave length and enemy velocity
    enemies = []
    wave_amount = 5
    enemy_velocity = 1

    # Set laser velocity
    laser_velocity = 4

    clock = pygame.time.Clock()

    # Define lost variable
    game_over = False
    game_over_count = 0

    # Create array for hazards, hash table for hazard effects, initialize hazard speed, and hazards per level
    # frozen = False
    #freeze = Hazards(300, 10, 'freeze')
    hazards = []
    hazard_effects = {'frozen': False, 'bullet_storm': False}
    hazard_velocity = 2
    hazards_per_level = 2

    # Initialize new level to True
    new_level = True

    def redisplay_window():
        """
        Displays background, player ship, enemies, and lasers on screen
        :return:
        """
        # Display background
        SCREEN.blit(BACKGROUND, (0, 0))
        # Display text
        level_text = game_font.render(f'Level: {level}', 1, (255, 255, 255))
        lives_text = game_font.render(f'Lives: {lives}', 1, (255, 255, 255))
        SCREEN.blit(lives_text, (10, 10))
        SCREEN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        # Draw hazards to screen
        for hazard in hazards:
            if hazard.get_hazard_type() == 'freeze':
                if not hazard_effects['frozen']:
                    hazard.draw(SCREEN)

        # Draw enemies to screen
        for enemy in enemies:
            enemy.draw(SCREEN)

        # Draw ships to screen
        player.draw(SCREEN)

        # Display Game Over text
        if game_over:
            game_over_text = game_over_font.render('GAME OVER', 1, (255, 255, 255))
            SCREEN.blit(game_over_text,
                        (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2 - game_over_text.get_height() / 2))

        pygame.display.update()

    while running:
        # Set frames per second
        clock.tick(FPS)

        # Draw to screen
        redisplay_window()

        # Check if player has lost the game
        if lives <= 0 or player.health <= 0:
            game_over = True
            game_over_count += 1

        # If player has lost, pause screen with game over message before going back to menu
        if game_over:
            if game_over_count > FPS * 3:
                running = False
            else:
                continue  # Don't let enemies or player move

        # If we have destroyed every enemy in level, go to next level
        if len(enemies) == 0:
            new_level = True
            level += 1
            wave_amount += 5
            # Spawn random color enemies
            for i in range(wave_amount):
                i = Enemy(random.randrange(25, WIDTH - 50), random.randrange(-1500, -100),
                          random.choice(['red', 'blue', 'green']))
                i.draw(SCREEN)
                enemies.append(i)

        # Initialize hazards
        if new_level:
            for i in range(hazards_per_level):
                i = Hazards(random.randrange(25, WIDTH - 50), random.randrange(-100, -1),
                            random.choice(['freeze']))
                i.draw(SCREEN)
                hazards.append(i)

        new_level = False

        # Check for game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        # Determine which keys are being pressed
        keys = pygame.key.get_pressed()
        # Allow player to move any direction as long as ship does not go off screen
        if keys[pygame.K_LEFT] and (player.x - player_velocity > 0):
            player.x -= player_velocity
            # Check for frozen hazard and disallow movement if this hazard has been enabled
            if hazard_effects['frozen']:
                player.x += player_velocity
        if keys[pygame.K_RIGHT] and (player.x + player_velocity < WIDTH - player.get_width()):
            player.x += player_velocity
            if hazard_effects['frozen']:
                player.x -= player_velocity
        if keys[pygame.K_UP] and (player.y - player_velocity > 0):
            player.y -= player_velocity
            if hazard_effects['frozen']:
                player.y += player_velocity
        if keys[pygame.K_DOWN] and (player.y + player_velocity < HEIGHT - player.get_height() - 20):
            player.y += player_velocity
            if hazard_effects['frozen']:
                player.y -= player_velocity
        # Shoot Laser
        if keys[pygame.K_SPACE]:
            player.shoot()
        player.move_lasers(-laser_velocity, enemies)

        # Create, move, and destroy enemies
        for enemy in enemies[:]:
            enemy.move_enemy(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            # Have enemy shoot ~once every 3 seconds
            # if random.randrange(0, 3 * FPS) == 1:
            #     enemy.shoot()
            if random.randrange(0, 3) == 1:
                enemy.shoot()
            # Collision between player and enemy
            if collide(player, enemy):
                player.health -= 10
                enemies.remove(enemy)
            # Check if enemy is off screen only if it hasn't collided with player
            elif enemy.y + enemy.get_height() >= HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # Create, move, and enact hazards
        for hazard in hazards:
            hazard.move(hazard_velocity)
            if collide(player, hazard):
                if hazard.get_hazard_type() == 'freeze':
                    hazard_effects['frozen'] = True

        # Make sure hazards are only in affect for a specified amount of time
        for hazard in hazards:
            if hazard_effects['frozen'] == True:
                hazard.update_hazard_counter()
            if hazard.get_hazard_counter() >= 3 * FPS:
                hazard_effects['frozen'] = False
                hazards.remove(hazard)


def main_menu():
    """
    Shows main menu upon starting game and after losing
    """
    menu_font = pygame.font.SysFont('comicsans', 60)
    running = True
    while running:
        SCREEN.blit(BACKGROUND, (0, 0))
        menu_text = menu_font.render("Press Any Key to Begin", 1, (255, 255, 255))
        SCREEN.blit(menu_text, (WIDTH / 2 - menu_text.get_width() / 2, HEIGHT / 2 - menu_text.get_height() / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                main()


main_menu()
