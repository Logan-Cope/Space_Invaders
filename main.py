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

# Spaceship Images
BLUE_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png')).convert_alpha()
GREEN_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png')).convert_alpha()
RED_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png')).convert_alpha()
# Player ship
YELLOW_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png')).convert_alpha()

# Upgrade Images
HEALTH = pygame.image.load(os.path.join('assets', 'health.png')).convert_alpha()
FLAME_THROWER = pygame.image.load(os.path.join('assets', 'flame_thrower.png')).convert_alpha()

# Hazard Images
FREEZE_HAZARD = pygame.image.load(os.path.join('assets', 'snowflake.png')).convert_alpha()
BULLET_STORM = pygame.image.load(os.path.join('assets', 'bullet_storm.png')).convert_alpha()


class Ship:
    """
    Abstract class that represents a ship in the game (player or enemy) and includes a several
    methods: draw, get_width, get_height, cool_down, shoot, move_lasers, and set_flame_thrower
    """
    # cool down period of a half a second
    COOL_DOWN = 30

    def __init__(self, x, y, health=100):
        """
        Initializes ship with specified x & y-coordinates and health. Initializes ship image
        to None, laser image to None, an empty list for lasers, a cool down period to 0, and
        flame_thrower to False
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
        self.flame_thrower = False

    def draw(self, screen):
        """
        Draws ships to screen, draws lasers to screen
        :param screen: display screen to draw onto
        :return: None
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
        :return: None
        """
        if self.cool_down_count >= self.COOL_DOWN:
            self.cool_down_count = 0
        elif self.cool_down_count > 0:
            self.cool_down_count += 1

    def shoot(self):
        """
        Utilizes Laser class to initialize lasers of player and enemies. Also gives the
        flame thrower upgrade its functionality
        :return: None
        """
        if self.cool_down_count == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            # If flame thrower is equipped, allow for continuous lasers
            if self.flame_thrower:
                self.cool_down_count = 0
            else:
                self.cool_down_count = 1

    def set_flame_thrower(self, boolean):
        """
        Allows flame_thrower upgrade to be enacted by setting the flame_thrower attribute
        if True is passed in and then to end by setting it back to False if False is
        passed in
        :param boolean: True or False boolean which determines whether the flame_thrower
        upgrade should be set or not
        :return: None
        """
        if boolean:
            self.flame_thrower = True
        else:
            self.flame_thrower = False

    def move_lasers(self, velocity, object):
        """
        Moves enemy lasers downwards a the specified velocity
        :param velocity: Integer representing how fast laser should travel downwards
        :param object: Used to check if enemy laser has a collision with the player's ship
        :return: None
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
    Represents player's ship which includes methods to draw, move lasers, and a health bar
    """

    def __init__(self, x, y, health=100):
        """
        Initializes ship with specified x & y-coordinates and health. Initializes ship image
        to YELLOW_SPACESHIP, laser image to YELLOW_LASER, max health to specified parameter
        or default of 100 if no parameter passed in, and mask for collision purposes
        :param x: integer representing x-coordiante
        :param y: integer representing y-coordinate
        :param health: integer representing ship health
        """
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)  # Create mask for collision

    def draw(self, screen):
        """
        Draws ships to screen, draws health bar to screen
        :param screen: display screen to draw onto
        :return: None
        """
        super().draw(screen)
        self.health_bar(screen)

    def move_lasers(self, velocity, objects):
        """
        Move player lasers
        :param velocity: integer that determines how fast lasers move across the screen
        :param objects: objects to remove once they are hit by a laser
        :return: None
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
        :param screen: display screen to draw health bar onto
        :return None
        """
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(screen, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(Ship):
    """
    Represents player's ship which includes methods to move enemy and shoot
    """

    def __init__(self, x, y, color, health=100):
        """
        Initializes enemy ship with specified x & y-coordinates and health. Initializes ship image
        based on ship color and laser image based on ship color, health to specified parameter or
        default of 100 if no parameter passed in, and mask for collision purposes
        :param x: integer representing x-coordiante
        :param y: integer representing y-coordinate
        :param color:
        :param health: integer representing ship health
        """
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
        :return: None
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
    Represent laser to be shot from ship (player or enemy) with methods of draw, move,
    is_off_screen, and collision
    """

    def __init__(self, x, y, image):
        """
        Initializes laser with specified x & y-coordinates and initializes ship image
        to specified image, and mask for collision purposes
        :param x: integer representing x-coordiante
        :param y: integer representing y-coordinate
        :param image: laser image
        """
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface((self.image))

    def draw(self, screen):
        """
        Draws ships to screen, draws health bar to screen
        :param screen: display screen to draw onto
        :return: None
        """
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
        return self.y > height or self.y < 0

    def collision(self, object):
        """
        Use collide function
        :param object:
        :return: boolean
        """
        return collide(self, object)


class Upgrades:
    """
     Class for upgrades that can occur in game
    """

    def __init__(self, x, y, type):
        hazard_image = {'health': HEALTH, 'flame_thrower': FLAME_THROWER}
        self.x = x
        self.y = y
        self.type = type
        self.image = hazard_image[type]
        self.mask = pygame.mask.from_surface(self.image)
        self.upgrade_counter = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, velocity):
        """
        Allows upgrade to move downwards at given velocity
        :param velocity: float representing speed of hazard
        """
        self.y += velocity

    def update_upgrade_counter(self):
        self.upgrade_counter += 1

    def get_upgrade_counter(self):
        return self.upgrade_counter

    def get_upgrade_type(self):
        return self.type

    def is_off_screen(self, height):
        """
        Tells us if the upgrade is off the screen
        :param height: integer representing height of screen in pixels
        :return: boolean of True if hazard is off screen and False otherwise
        """
        return self.y > height


class Hazards:
    """
    Class for hazards that can occur in game
    """

    def __init__(self, x, y, type):
        hazard_image = {'freeze': FREEZE_HAZARD, 'bullet_storm': BULLET_STORM}
        self.x = x
        self.y = y
        self.type = type
        self.image = hazard_image[type]
        self.mask = pygame.mask.from_surface(self.image)
        self.hazard_counter = 0

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, velocity):
        """
        Allows hazard to move downwards at given velocity
        :param velocity: float representing speed of hazard
        """
        self.y += velocity

    def update_hazard_counter(self):
        self.hazard_counter += 1

    def get_hazard_counter(self):
        return self.hazard_counter

    def get_hazard_type(self):
        return self.type

    def is_off_screen(self, height):
        """
        Tells us if the hazard is off the screen
        :param height: integer representing height of screen in pixels
        :return: boolean of True if hazard is off screen and False otherwise
        """
        return self.y > height


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

    # Create array for upgrades, hash table for upgrade effects, initialize upgrade speed, and upgrade types
    upgrades = []
    upgrade_types = ['health', 'flame_thrower']
    upgrade_effects = {'health': False, 'flame_thrower': False}
    upgrade_velocity = 2

    # Create array for hazards, hash table for hazard effects, initialize hazard speed, and hazards types
    hazards = []
    hazard_types = ['freeze', 'bullet_storm']
    hazard_effects = {'frozen': False, 'bullet_storm_activated': False}
    hazard_velocity = 1

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

        # Draw upgrades to screen
        for upgrade in upgrades:
            if upgrade.get_upgrade_type() == 'health':
                if not upgrade_effects['health']:
                    upgrade.draw(SCREEN)
            if upgrade.get_upgrade_type() == 'flame_thrower':
                if not upgrade_effects['flame_thrower']:
                    upgrade.draw(SCREEN)

        # Draw hazards to screen
        for hazard in hazards:
            if hazard.get_hazard_type() == 'freeze':
                if not hazard_effects['frozen']:
                    hazard.draw(SCREEN)
            if hazard.get_hazard_type() == 'bullet_storm':
                if not hazard_effects['bullet_storm_activated']:
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

        # Reset health if player loses life
        if player.health < 0 and not game_over:
            lives -= 1
            if lives > 0:
                player.health = 100
        # Check if player has lost the game
        if lives <= 0:
            game_over = True
            game_over_count += 1

        # If player has lost, pause screen with game over message before going back to menu
        if game_over:
            player.health = -1
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

        # Initialize upgrades
        if new_level:
            type_counter = 0
            for i in range(len(upgrade_types)):
                i = Upgrades(random.randrange(25, WIDTH - 50), random.randrange(-1800, -900),
                             upgrade_types[type_counter])
                i.draw(SCREEN)
                upgrades.append(i)
                type_counter += 1

            # Initialize hazards
            type_counter = 0
            for i in range(len(hazard_types)):
                i = Hazards(random.randrange(25, WIDTH - 50), random.randrange(-1000, -100), hazard_types[type_counter])
                i.draw(SCREEN)
                hazards.append(i)
                type_counter += 1
        new_level = False

        # Check for game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        # Determine which keys are being pressed
        keys = pygame.key.get_pressed()
        # Allow player to move any direction as long as ship does not go off screen
        if keys[pygame.K_LEFT] and (player.x - player_velocity > 0 - (player.get_width() / 2) - 4):
            player.x -= player_velocity
            # Check for frozen hazard and disallow movement if this hazard has been enabled
            if hazard_effects['frozen']:
                player.x += player_velocity
        if keys[pygame.K_RIGHT] and (player.x + player_velocity < WIDTH - (player.get_width() / 2)):
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
            # If bullet_storm hazard is activated, have enemies shoot extremely fast
            if hazard_effects['bullet_storm_activated']:
                if random.randrange(0, 3) == 1:
                    enemy.shoot()
            # If bullet_storm is not activated, have enemies shoot ~once every 3 seconds
            # if not hazard_effects['bullet_storm_activated']:
            else:
                if random.randrange(0, 3 * FPS) == 1:
                    enemy.shoot()

            # Collision between player and enemy
            if collide(player, enemy):
                player.health -= 10
                enemies.remove(enemy)
            # Check if enemy is off screen only if it hasn't collided with player
            elif enemy.y + enemy.get_height() >= HEIGHT:
                lives -= 1
                player.health = 100
                enemies.remove(enemy)

        # Move and enact upgrades
        for upgrade in upgrades:
            upgrade.move(upgrade_velocity)
            if collide(player, upgrade):
                # if player hits heart, increase health by 50 (up to 100)
                if upgrade.get_upgrade_type() == 'health':
                    if player.health < 50:
                        player.health += 50
                    else:
                        player.health = 100
                    upgrades.remove(upgrade)
                # if player hits flame thrower, set flame thrower effect to True
                if upgrade.get_upgrade_type() == 'flame_thrower':
                    upgrade_effects['flame_thrower'] = True
                    player.set_flame_thrower(True)

        # Make sure relevant upgrades are only in affect for specified amount of time
        for upgrade in upgrades:
            if upgrade.get_upgrade_type() == 'flame_thrower':
                if upgrade_effects['flame_thrower'] == True:
                    upgrade.update_upgrade_counter()
                # Allow player to use flamethrower for 5 seconds
                if upgrade.get_upgrade_counter() >= 5 * FPS:
                    player.set_flame_thrower(False)
                    upgrade_effects['flame_thrower'] = False
                    upgrades.remove(upgrade)

        # Move and enact hazards
        for hazard in hazards:
            hazard.move(hazard_velocity)
            if collide(player, hazard):
                if hazard.get_hazard_type() == 'freeze':
                    hazard_effects['frozen'] = True
                if hazard.get_hazard_type() == 'bullet_storm':
                    hazard_effects['bullet_storm_activated'] = True

        # Make sure relevant hazards are only in affect for a specified amount of time
        for hazard in hazards:
            if hazard.get_hazard_type() == 'freeze':
                if hazard_effects['frozen'] == True:
                    hazard.update_hazard_counter()
                # Freeze player for 3 seconds
                if hazard.get_hazard_counter() >= 3 * FPS:
                    hazard_effects['frozen'] = False
                    hazards.remove(hazard)
            elif hazard.get_hazard_type() == 'bullet_storm':
                if hazard_effects['bullet_storm_activated'] == True:
                    hazard.update_hazard_counter()
                # Bring bullet storm from enemies for 4 seconds
                if hazard.get_hazard_counter() >= 4 * FPS:
                    hazard_effects['bullet_storm_activated'] = False
                    hazards.remove(hazard)

        # # remove hazard if it has gone off screen
        # for hazard in hazards:
        #     if hazard.is_off_screen(HEIGHT):
        #         hazards.remove(hazard)


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
