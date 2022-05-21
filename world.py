import pygame
import pickle
from pygame import mixer
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
FPS = 60

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer")

# define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# define game variables
tile_size = 40
game_over = 0
main_menu = True
level = 1
max_levels = 2
score = 0

# define colours
white = (255, 255, 255)
blue = (0, 0, 255)

# load images
sky_img = pygame.transform.scale(pygame.image.load('Assets/bg.png'), (screen_width, screen_height))
sun_img = pygame.transform.scale(pygame.image.load('Assets/sun.png'), (50 * 1.5, 50 * 1.5))
cloud1_img = pygame.transform.scale(pygame.image.load('Assets/cloud1.png'), (128 * 1.5, 71 * 1.5))
cloud2_img = pygame.transform.scale(pygame.image.load('Assets/cloud2.png'), (128 * 1.5, 71 * 1.5))
restart_img = pygame.transform.scale(pygame.image.load('Assets/restart_btn.png'), ((120 * 2), (42 * 2)))
start_img = pygame.image.load('Assets/start_btn.png')
exit_img = pygame.image.load('Assets/exit_btn.png')

# load sounds
pygame.mixer.music.load('Assets/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_sound = pygame.mixer.Sound('Assets/coin.wav')
coin_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound('Assets/jump.wav')
jump_sound.set_volume(0.5)
game_over_sound = pygame.mixer.Sound('Assets/game_over.wav')
game_over_sound.set_volume(0.5)


def draw_text(text, font, text_collour, x, y):
    img = font.render(text, True, text_collour)
    screen.blit(img, (x, y))


# function to reset level
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    # load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouse over and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            # get pressed keys
            key = pygame.key.get_pressed()
            # jump
            if key[pygame.K_SPACE] and self.jumped is False and self.on_ground is True:
                jump_sound.play()
                self.velY = -15
                self.jumped = True
            if key[pygame.K_SPACE] is False:
                self.jumped = False
            # move left
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            # move right
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] is False and key[pygame.K_d] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.velY += 1
            if self.velY > 10:
                self.velY = 10
            dy += self.velY

            # check for collision
            self.on_ground = False
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground (jumping)
                    if self.velY < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.velY = 0
                    # check if above the ground (falling)
                    elif self.velY >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.velY = 0
                        self.on_ground = True

            # check for collision with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_sound.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_sound.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 15

        # draw player onto screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'Assets/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('Assets/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velY = 0
        self.jumped = False
        self.direction = 0


class World:
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load('Assets/dirt.png')
        grass_img = pygame.image.load('Assets/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 10)
                    blob_group.add(blob)
                if tile == 4:
                    lava = Lava(col_count * tile_size, row_count * tile_size + tile_size // 2)
                    lava_group.add(lava)
                if tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size - (tile_size // 2))
                    coin_group.add(coin)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('Assets/blob.png'), (tile_size, tile_size - 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter > 80):
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 120)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# dummy coin for showing score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# buttons
restart_button = Button(screen_width // 2 - 120, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2 - 100, start_img)
exit_button_menu = Button(screen_width // 2 + 150, screen_height // 2 - 100, exit_img)
exit_button = Button(screen_width // 2 - 120, screen_height // 2 - 100, pygame.transform.scale(exit_img, (240, 100)))

run = True
while run:

    clock.tick(FPS)

    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    screen.blit(cloud1_img, (screen_width / 3, screen_height / 3.5))
    screen.blit(cloud2_img, (screen_width / 1.5, screen_height / 5))

    if main_menu is True:
        if exit_button_menu.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            # update score
            # check if a coin has been collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_sound.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # if player has died
        if game_over == -1:
            if exit_button.draw():
                run = False
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # if player has completed level
        if game_over == 1:
            # reset game and go to next level
            level += 1
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("YOU WIN!", font, blue, (screen_width // 2) - 120, screen_height // 2)
                # restart game
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
