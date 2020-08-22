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
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))

# Spaceships
BLUE_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))
GREEN_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
RED_SPACESHIP  = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
# Player ship
YELLOW_SPACESHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.pnG'))


class Ship:
    """
    Abstract class that represents a ship in the game (player or enemy)
    """

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
        self.cool_down_period = 0

    def draw(self, screen):
        """
        Draws ship to screen
        :param window:
        :return:
        """
        screen.blit(self.ship_img, (self.x, self.y))

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


class Player(Ship):
    """
    Represents player ship
    """
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)     # Create mask for collision


class Enemy(Ship):
    """
    Represents enemy ships
    """
    # Create hash map to determine which color enemy ship to use


    def __init__(self, x, y, color, health=100):
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

class Laser:
    """
    Represent laser to be shot from ship (player or enemy)
    """


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
    player = Player(275, 510)

    # Set velocities for player, enemies, and lasers
    player_velocity = 5

    # Set level and lives
    level = 0
    lives = 3

    # Set enemies, wave length and enemy velocity
    enemies = []
    wave_amount = 5
    enemy_velocity = 1

    clock = pygame.time.Clock()

    # Define lost variable
    game_over = False
    game_over_count = 0

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

        # Draw enemies to screen
        for enemy in enemies:
            enemy.draw(SCREEN)

        # Draw ships to screen
        player.draw(SCREEN)

        # Display Game Over text
        if game_over:
            game_over_text = game_over_font.render('GAME OVER', 1, (255, 255,255))
            SCREEN.blit(game_over_text, (WIDTH/2 - game_over_text.get_width()/2, HEIGHT/2 - game_over_text.get_height()/2))



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
                continue   # Don't let enemies or player move

        # If we have destroyed every enemy in level, go to next level
        if len(enemies) == 0:
            level += 1
            wave_amount += 5
            for i in range(wave_amount):
                i = Enemy(random.randrange(25, WIDTH - 25), random.randrange(-1500, -100), random.choice(['red', 'blue', 'green']))
                i.draw(SCREEN)
                enemies.append(i)


        # Check for game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Determine which keys are being pressed
        keys = pygame.key.get_pressed()
        # Allow player to move any direction as long as ship does not go off screen
        if keys[pygame.K_LEFT] and (player.x - player_velocity > 0):
            player.x -= player_velocity
            # ship.x += 5  use so ship can't move left
        if keys[pygame.K_RIGHT] and (player.x + player_velocity < WIDTH - player.get_width()):
            player.x += player_velocity
        if keys[pygame.K_UP] and (player.y - player_velocity > 0):
            player.y -= player_velocity
        if keys[pygame.K_DOWN] and (player.y + player_velocity < HEIGHT - player.get_height()):
            player.y += player_velocity

        for enemy in enemies[:]:
            enemy.move_enemy(enemy_velocity)
            if enemy.y + enemy.get_height() >= HEIGHT:
                lives -= 1
                enemies.remove(enemy)



main()
