import pygame.display
from pygame import *

images_right = ['run12.png', 'run22.png', 'run32.png']
images_l = ['run12.png', 'run22.png', 'run32.png']
images_jump = ['jump2.png']
platform_image = 'plat.png'
bullet_img = 'pyla.png'

BULLET_SPEED = 7

class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (sprite_width, sprite_height))
        self.rect = self.image.get_rect()
        self.rect.x = sprite_position_x
        self.rect.y = sprite_position_y
        self.width = sprite_width
        self.height = sprite_height
        self.speed = sprite_speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def bad(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
class Platform(GameSprite):
    def __init__(self, sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height):
        super().__init__(sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, 0)
class PlayerBase(GameSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_ground = True
        self.jumps_remaining = 100
        self.jump_remaining = 0

    def handle_events(self):
        raise NotImplementedError("Subclasses must implement handle_events method")

    def move(self):
        raise NotImplementedError("Subclasses must implement move method")
class Zombie(GameSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.health = 100
        self.direction = 1
        self.original_image = self.image

    def update(self, bullets):
        if pygame.sprite.spritecollideany(self, bullets):
            self.health -= 50
            if self.health <= 0:
                self.kill()

    def move(self, platforms):
        previous_direction = self.direction
        self.rect.x += self.speed * self.direction
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.rect.right >= platform.rect.right or self.rect.left <= platform.rect.left:
                    self.direction *= -1
                    break
        if self.direction != previous_direction:
            if self.direction == 1:
                self.image = pygame.transform.flip(self.original_image, False, False)  # Направо
            else:
                self.image = pygame.transform.flip(self.original_image, True, False)  # Налево
            self.rect = self.image.get_rect(center=self.rect.center)
class Player(PlayerBase):
    def __init__(self, sprite_images_right, sprite_images_s, sprite_image_s, sprite_image_s_left, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed, bullets_group):
        super().__init__(sprite_images_right[0], sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed)
        self.bullets_group = bullets_group
        self.image_jump = transform.scale(image.load(sprite_images_s[0]), (sprite_width, sprite_height))
        self.images_right = [transform.scale(image.load(img), (sprite_width, sprite_height)) for img in sprite_images_right]
        self.images_s = [transform.scale(image.load(img), (sprite_width, sprite_height)) for img in sprite_images_s]
        self.image_s = transform.scale(image.load(sprite_image_s), (sprite_width, sprite_height))
        self.image_left = transform.flip(transform.scale(image.load(sprite_image_s_left), (sprite_width, sprite_height)), True, False)
        self.index = 0
        self.direction = "right"
        self.is_moving = False
        self.animation_speed = 6
        self.frame_counter = 0
        self.gravity = 1.5
        self.jump_height = 200
        self.jumps_remaining = 100
        self.jump_remaining = 0
        self.start_x = sprite_position_x
        self.start_y = sprite_position_y
        self.on_ground = True


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.shoot(pygame.key.get_pressed())
                elif event.key == pygame.K_DOWN:
                    pass
    def update(self, zombies):
        if pygame.sprite.spritecollide(self, zombies, False):
            game_over_font = font.Font(None, 100)
            game_over_text = game_over_font.render('Вы проиграли', True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(window_width / 2, window_height / 2))
            window.blit(game_over_text, game_over_rect)
            display.update()
            pygame.time.delay(5000)
            quit()

    def move(self, platforms):
        keys = key.get_pressed()
        new_x = self.rect.x
        new_y = self.rect.y

        collisions = sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.rect.bottom <= platform.rect.top and self.jump_remaining == 0:
                self.on_ground = True
                self.jumps_remaining = 100

        if keys[K_LEFT]:
            new_x -= self.speed
            self.direction = "left"
            self.is_moving = True
        elif keys[K_RIGHT]:
            new_x += self.speed
            self.direction = "right"
            self.is_moving = True
        elif keys[K_UP] and self.jumps_remaining > 0 and self.on_ground:
            self.jump_remaining = self.jump_height
            self.on_ground = False
            self.jumps_remaining -= 1
            self.jump_remaining = self.jump_height
        elif keys[K_DOWN]:
            if not any(platform.rect.colliderect(self.rect) for platform in platforms):
                new_y += self.speed
        else:
            self.is_moving = False

        if any(platform.rect.colliderect(self.rect) for platform in platforms):
            self.on_ground = True

        if self.jump_remaining > 0:
            new_y -= self.speed
            self.jump_remaining -= self.speed

        if not any(platform.rect.colliderect(self.rect) for platform in platforms):
            new_y += self.gravity

        if 0 <= new_x <= window_width - self.width:
            self.rect.x = new_x

        if 0 <= new_y <= window_height - self.height:
            self.rect.y = new_y
        else:
            self.rect.y = window_height - self.height

        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.index += 1
            if self.is_moving:
                if self.direction == "left":
                    if self.index >= len(self.images_s):
                        self.index = 0
                    self.image = transform.flip(self.images_s[self.index], True, False)
                else:
                    if self.index >= len(self.images_right):
                        self.index = 0
                    self.image = self.images_right[self.index]
            else:
                if self.direction == "left":
                    self.image = self.image_left
                else:
                    self.image = self.image_s

    def shoot(self, keys):
        if keys[pygame.K_SPACE]:
            if self.direction == "left":
                bullet_direction = -1
            else:
                bullet_direction = 1
            bullet = Bullet(self.rect.right, self.rect.centery, bullet_direction)
            all_sprites.add(bullet)
            bullets.add(bullet)
class Player2(PlayerBase):
    def __init__(self, sprite_images_right, sprite_images_s, sprite_image_s, sprite_image_s_left, sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed, bullets_group):
        super().__init__(sprite_images_right[0], sprite_position_x, sprite_position_y, sprite_width, sprite_height, sprite_speed)
        self.bullets_group = bullets_group
        self.image_jump = transform.scale(image.load(sprite_images_s[0]), (sprite_width, sprite_height))
        self.images_right = [transform.scale(image.load(img), (sprite_width, sprite_height)) for img in sprite_images_right]
        self.images_s = [transform.scale(image.load(img), (sprite_width, sprite_height)) for img in sprite_images_s]
        self.image_s = transform.scale(image.load(sprite_image_s), (sprite_width, sprite_height))
        self.image_left = transform.flip(transform.scale(image.load(sprite_image_s_left), (sprite_width, sprite_height)), True, False)
        self.index = 0
        self.direction = "right"
        self.is_moving = False
        self.animation_speed = 6
        self.frame_counter = 0
        self.gravity = 1.5
        self.jump_height = 200
        self.jumps_remaining = 100
        self.jump_remaining = 0
        self.start_x = sprite_position_x
        self.start_y = sprite_position_y
        self.on_ground = True
        self.can_shoot = True
        self.shoot_cooldown = 0.3
        self.last_shot_time = 0

    def handle_events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            self.shoot(keys)

    def update(self, zombies):
        if pygame.sprite.spritecollide(self, zombies, False):
            game_over_font = font.Font(None, 100)
            game_over_text = game_over_font.render('Вы проиграли', True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(window_width / 2, window_height / 2))
            window.blit(game_over_text, game_over_rect)
            display.update()
            pygame.time.delay(5000)
            quit()

    def move2(self, platform):
        keys = key.get_pressed()
        new_x = self.rect.x
        new_y = self.rect.y

        collisions = sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.rect.bottom <= platform.rect.top and self.jump_remaining == 0:
                self.on_ground = True
                self.jumps_remaining = 100

        if keys[K_a]:
            new_x -= self.speed
            self.direction = "left"
            self.is_moving = True
        elif keys[K_d]:
            new_x += self.speed
            self.direction = "right"
            self.is_moving = True
        elif keys[K_w] and self.jumps_remaining > 0 and self.on_ground:
            self.jump_remaining = self.jump_height
            self.on_ground = False
            self.jumps_remaining -= 1
            self.jump_remaining = self.jump_height
        elif keys[K_s]:
            if not any(platform.rect.colliderect(self.rect) for platform in platforms):
                new_y += self.speed
        else:
            self.is_moving = False

        if any(platform.rect.colliderect(self.rect) for platform in platforms):
            self.on_ground = True

        if self.jump_remaining > 0:
            new_y -= self.speed
            self.jump_remaining -= self.speed

        if not any(platform.rect.colliderect(self.rect) for platform in platforms):
            new_y += self.gravity

        if 0 <= new_x <= window_width - self.width:
            self.rect.x = new_x

        if 0 <= new_y <= window_height - self.height:
            self.rect.y = new_y
        else:
            self.rect.y = window_height - self.height

        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.index += 1
            if self.is_moving:
                if self.direction == "left":
                    if self.index >= len(self.images_s):
                        self.index = 0
                    self.image = transform.flip(self.images_s[self.index], True, False)
                else:
                    if self.index >= len(self.images_right):
                        self.index = 0
                    self.image = self.images_right[self.index]
            else:
                if self.direction == "left":
                    self.image = self.image_left
                else:
                    self.image = self.image_s

    def shoot(self, keys):
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_shot_time >= self.shoot_cooldown and keys[pygame.K_b]:
            if keys[pygame.K_a]:
                direction = -1
            elif keys[pygame.K_d]:
                direction = 1
            else:
                direction = 1
            if self.direction == "left":
                direction *= -1

            bullet = Bullet(self.rect.right, self.rect.centery, direction)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.last_shot_time = current_time
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.transform.scale(image.load(bullet_img), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = x + 20 * direction
        self.rect.centery = y + 10
        self.speed = BULLET_SPEED * direction

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > window_width or self.rect.right < 0:
            self.kill()
        else:
            hit_zombies = pygame.sprite.spritecollide(self, zombies, False)
            if hit_zombies:
                for zombie in hit_zombies:
                    zombie.health -= 50
                    if zombie.health <= 0:
                        zombie.kill()
                self.kill()

class Cup(GameSprite):
    def __init__(self, sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, cup_number):
        super().__init__(sprite_image, sprite_position_x, sprite_position_y, sprite_width, sprite_height, 0)
        self.cup_number = cup_number
    def update(self, player):
        if self.rect.colliderect(player.rect):
            return self.cup_number
        return None


def display_menu():
    global menu_index
    menu_font = font.Font(None, 50)
    menu_options = ['Грати', 'Вийти']
    menu_texts = [menu_font.render(option, True, (0, 0, 0)) for option in menu_options]
    option_rects = [text.get_rect(center=(window_width/2.1, window_height/2 + index*50)) for index, text in enumerate(menu_texts)]

    menu = True
    while menu:
        for e in event.get():
            if e.type == QUIT:
                pygame.quit()
                quit()
            if e.type == KEYDOWN:
                if e.key == K_UP:
                    menu_index = (menu_index - 1) % len(menu_options)
                elif e.key == K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_options)
                elif e.key == K_RETURN:
                    if menu_index == 0:  # Play
                        menu = False
                        return True
                    elif menu_index == 1:  # Quit
                        pygame.quit()
                        quit()
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for index, rect in enumerate(option_rects):
                        if rect.collidepoint(mouse_pos):
                            menu_index = index
                            if menu_index == 0:
                                menu = False
                                return True
                            elif menu_index == 1:
                                pygame.quit()
                                quit()

        window.fill(background_color)
        for index, text in enumerate(menu_texts):
            window.blit(text, option_rects[index])
        display.update()

pygame.init()
window_height = 700
window_width = 1200
background_color = (200, 255, 255)
pygame.display.set_caption("LVL 1")
bullets = pygame.sprite.Group()
window = display.set_mode((window_width, window_height))
window.fill(background_color)

plat = Platform(platform_image, 0, 670, 1200, 28)
plat2 = Platform(platform_image, 0, 540, 1050, 25)
plat3 = Platform(platform_image, 150, 420, 1050, 25)
plat4 = Platform(platform_image, 0, 290, 1050, 25)
plat5 = Platform(platform_image, 150, 170, 1050, 25)

plat6 = Platform(platform_image, 600, 310, 50, 130)

player = Player(images_right, images_l, 'stay2.png', 'stay2.png', 1100, 10, 75, 90, 4, bullets)
player2 = Player2(images_right, images_l, 'stay2.png', 'stay2.png', 50, 580, 75, 90, 4, bullets)
game = True
clock = time.Clock()
FPS = 60

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites.add(plat, plat2, plat3, plat4, plat5, plat6)
platforms.add(plat, plat2, plat3, plat4, plat5, plat6)

zombie1 = Zombie('zombi1.png', 100, 210, 75, 90, 3)
zombie2 = Zombie('zombi1.png', 700, 340, 75, 90, 3)
zombie4 = Zombie('zombi1.png', 450, 340, 75, 90, 3)
zombie3 = Zombie('zombi1.png', 700, 460, 75, 90, 3)

cup1 = Cup('kyb.png', 650, 340, 75, 75, 1)
cup2 = Cup('kyb.png', 500, 340, 75, 75, 2)
all_sprites.add(cup1, cup2)

zombies = pygame.sprite.Group()
zombies.add(zombie1, zombie2,zombie3, zombie4)
all_sprites.add(zombie1, zombie2, zombie3, zombie4)

pygame.mixer.music.load('music.mp3')
mixer_music.set_volume(0.02)
pygame.mixer.music.play(-1)
menu_index = 0
while True:
    if display_menu():
        break

background_color = (200, 255, 255)
red_color = (255, 0, 0)

while game:
    player.handle_events()
    player2.handle_events()
    bullets.update()
    window.fill(background_color)

    player.move(platforms)
    player.reset()

    player2.move2(plat)
    player2.reset()

    for zombie in zombies:
        zombie.move(platforms)
        zombie.update(bullets)
        window.blit(zombie.image, zombie.rect)

    if pygame.sprite.spritecollide(player, zombies, False):
        game_over_font = font.Font(None, 100)
        game_over_text = game_over_font.render('Игрок 1 пал в бою', True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(window_width / 2, window_height / 2))
        window.fill(red_color)
        window.blit(game_over_text, game_over_rect)
        display.update()
        pygame.time.delay(2000)
        game = False

    if pygame.sprite.spritecollide(player2, zombies, False):
        game_over_font = font.Font(None, 100)
        game_over_text = game_over_font.render('Игрок 2 пал в бою', True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(window_width / 2, window_height / 2))
        window.fill(red_color)
        window.blit(game_over_text, game_over_rect)
        display.update()
        pygame.time.delay(2000)
        game = False

    cup1_touch = cup1.update(player)
    cup2_touch = cup2.update(player2)

    if cup1_touch == 1 and cup2_touch == 2:
        game_over_font = font.Font(None, 100)
        game_over_text = game_over_font.render('Вы прошли уровень!', True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(window_width / 2, window_height / 2))
        window.fill(red_color)
        window.blit(game_over_text, game_over_rect)
        display.update()
        pygame.time.delay(2000)
        game = False

    platforms.draw(window)
    plat.bad()
    plat2.bad()
    plat3.bad()
    plat4.bad()
    plat5.bad()
    bullets.draw(window)
    all_sprites.draw(window)
    display.update()
    clock.tick(60)


