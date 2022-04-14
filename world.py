import pygame

pygame.init()

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer")

# load images
sky_img = pygame.transform.scale(pygame.image.load('Assets/bg.png'), (screen_width, screen_height))
sun_img = pygame.transform.scale(pygame.image.load('Assets/sun.png'), (50*1.5, 50*1.5))
cloud1_img = pygame.transform.scale(pygame.image.load('Assets/cloud1.png'), (128*1.5, 71*1.5))
cloud2_img = pygame.transform.scale(pygame.image.load('Assets/cloud2.png'), (128*1.5, 71*1.5))

run = True
while run:

    screen.blit(sky_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    screen.blit(cloud1_img, (screen_width/3, screen_height/3.5))
    screen.blit(cloud2_img, (screen_width/1.5, screen_height/ 5))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
