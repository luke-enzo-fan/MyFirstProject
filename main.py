import pygame
import random
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Exploring The Universe")

WHITE = (255, 255, 255)
BASE_BG_COLOR = (0, 0, 30)
TEXT_COLOR = (255, 255, 255)
TEXT_BG_COLOR = (20, 20, 50)
BUTTON_COLOR = (0, 100, 200)
HOVER_COLOR = (100, 150, 255)

font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)

select_sound = pygame.mixer.Sound("../soundtrack/click.mp3")
explosion_sound = pygame.mixer.Sound("../soundtrack/explode.mp3")
pygame.mixer.music.load("../soundtrack/space.mp3")
pygame.mixer.music.play(-1)

player_idle = pygame.image.load('../images/player_walk_1.png')
player_walk_1 = pygame.image.load('../images/player_walk_1.png')
player_walk_2 = pygame.image.load('../images/player_walk_2.png')
black_hole_img = pygame.image.load('../images/black_hole.png')
neutron_star_img = pygame.image.load('../images/neutron_star.png')
exoplanet_img = pygame.image.load('../images/exoplanet.png')
dark_matter_img = pygame.image.load('../images/dark_matter.png')
asteroid_img = pygame.image.load("../images/asteroid.png")
planet1_img = pygame.image.load("../images/planet.png")
planet2_img = pygame.image.load("../images/planet2.png")
planet3_img = pygame.image.load("../images/planet3.png")
sun_img = pygame.image.load("../images/sun.png")
sun_img = pygame.transform.scale(sun_img, (800, 800))



options = {
    "Black Hole": "When a massive star dies, it becomes very dence and compact, becoming a black hole. Another way black holes form is when gas collapses directly which is the result of a even more massive black hole, 1000 to 100,000 times the mass pf the sun.",
    "Neutron Star": "Neutron Stars are formed when a star with less mass runs out of fuel. They crush together all protons and electrons into neutrons. Neutron Stars are usually found spinning uncontrollably with extreme magnetic fields.",
    "Exoplanet": "Exoplanets are planets that are habitable for humans that are outside out solar system. They are planets that have features similar to Earth.",
    "Dark Matter": "Dark matter makes up most of the mass of galaxies and galaxy clusters, and is responsible for the way galaxies are organized on grand scales. It works like an attractive force that holds our universe together. Dark matter interacts with gravity, but it doesn’t reflect, absorb, or emit light."
}

running = True
in_menu = True
selected_option = None
camera_x = 0
camera_y = 0
game_over = False
orbit_angle = 0

class Tooltip:
    def __init__(self, text, font, max_width=250, typing_speed=30):
        self.full_text = text
        self.font = font
        self.max_width = max_width
        self.typing_speed = typing_speed
        self.start_time = pygame.time.get_ticks()
        self.rendered_lines = []

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        num_chars = int(elapsed / (1000 / self.typing_speed))
        visible_text = self.full_text[:num_chars]
        words = visible_text.split(' ')
        lines = []
        line = ''
        for word in words:
            test_line = line + word + ' '
            if self.font.size(test_line)[0] <= self.max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + ' '
        if line:
            lines.append(line)
        self.rendered_lines = lines

    def draw(self, surface, x, y):
        self.update()
        padding = 10
        line_height = self.font.get_height()
        box_width = self.max_width + padding * 2
        box_height = line_height * len(self.rendered_lines) + padding * 2
        box_rect = pygame.Rect(x - box_width // 2, y - box_height, box_width, box_height)
        pygame.draw.rect(surface, TEXT_BG_COLOR, box_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, box_rect, 2, border_radius=10)
        for i, line in enumerate(self.rendered_lines):
            text_surface = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text_surface, (box_rect.x + padding, box_rect.y + padding + i * line_height))

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 0.6
        self.size = 25
        self.velocity_x = 0
        self.velocity_y = 0
        self.alive = True
        self.image = player_idle
        self.angle = 0

    def move(self, keys):
        if not self.alive:
            return
        friction = 0.96
        if keys[pygame.K_a]:
            self.velocity_x -= 0.08
        if keys[pygame.K_d]:
            self.velocity_x += 0.08
        if keys[pygame.K_w]:
            self.velocity_y -= 0.08
        if keys[pygame.K_s]:
            self.velocity_y += 0.08
        self.velocity_x *= friction
        self.velocity_y *= friction
        self.x += self.velocity_x * self.speed
        self.y += self.velocity_y * self.speed

    def draw(self):
        if not self.alive:
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(mouse_y - HEIGHT//2, mouse_x - WIDTH//2))
        player_image = player_walk_1 if (self.velocity_x or self.velocity_y) and int(pygame.time.get_ticks() / 250) % 2 == 0 else player_idle
        rotated_image = pygame.transform.rotate(player_image, self.angle)
        new_rect = rotated_image.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(rotated_image, new_rect.topleft)

    def apply_gravity(self, obj_x, obj_y, option):
        dx = obj_x - self.x
        dy = obj_y - self.y
        distance = math.hypot(dx, dy)
        if option == "Black Hole":
            if distance < 60:
                explode_player()
            elif distance < 500:
                force = 0.075 / (distance + 1)
                self.velocity_x += dx * force
                self.velocity_y += dy * force
        elif option == "Neutron Star":
            if distance < 40:
                explode_player()
            elif distance < 250:
                force = 0.1 / (distance + 1)
                angle_offset = random.uniform(-0.5, 0.5)
                self.velocity_x += (dx + angle_offset) * force
                self.velocity_y += (dy + angle_offset) * force
        elif option == "Exoplanet":
            if distance < 80:
                explode_player()
            elif distance < 300:
                force = 0.02 / (distance + 1)
                self.velocity_x += dx * force
                self.velocity_y += dy * force
        elif option == "Dark Matter":
            if distance < 70:
                explode_player()
            elif distance < 250:
                shake_x = random.uniform(-1, 1)
                shake_y = random.uniform(-1, 1)
                self.velocity_x += shake_x * 1.3
                self.velocity_y += shake_y * 1.3

class Planet:
    def __init__(self, image, orbit_radius, speed, angle_offset=0):
        self.image = pygame.transform.scale(image, (80, 80))
        self.orbit_radius = orbit_radius + 120
        self.speed = speed
        self.angle = angle_offset
        self.x = 0
        self.y = 0
        #mom-code
        self.rect = self.image.get_rect()

    def update(self, center_x, center_y):
        self.angle += self.speed
        self.x = center_x + math.cos(self.angle) * self.orbit_radius
        self.y = center_y + math.sin(self.angle) * self.orbit_radius

    def draw(self):
        screen.blit(self.image, (self.x - camera_x - self.image.get_width()//2,
                                  self.y - camera_y - self.image.get_height()//2))

def explode_player():
    global player, game_over
    explosion_sound.play()
    for _ in range(10):
        debris_x = WIDTH // 2 + random.randint(-10, 10)
        debris_y = HEIGHT // 2 + random.randint(-10, 10)
        pygame.draw.circle(screen, (255, 50, 50), (debris_x, debris_y), random.randint(2, 5))
    pygame.display.update()
    pygame.time.delay(500)
    game_over = True
    player.alive = False

def reset_player():
    global player
    player = Player()
    player.x = object_x + 300
    player.y = object_y


object_x, object_y = 500, 500

def draw_animated_model(option):
    global orbit_angle
    if option in ("Exoplanet", "Dark Matter"):
        sun_rect = sun_img.get_rect(center=(object_x - camera_x, object_y - camera_y))
        screen.blit(sun_img, sun_rect)

    if option in ("Exoplanet", "Dark Matter"):
        orbit_angle += 0.01
        radius = 300
        phen_x = object_x + math.cos(orbit_angle) * radius
        phen_y = object_y + math.sin(orbit_angle) * radius
        img = exoplanet_img if option == "Exoplanet" else dark_matter_img
        phen_scaled = pygame.transform.scale(img, (150, 150))
        rect = phen_scaled.get_rect(center=(phen_x - camera_x, phen_y - camera_y))
        screen.blit(phen_scaled, rect)
    else:
        img = black_hole_img if option == "Black Hole" else neutron_star_img
        scaled = pygame.transform.scale(img, (800, 800))
        rect = scaled.get_rect(center=(object_x - camera_x, object_y - camera_y))
        screen.blit(scaled, rect)


def draw_minimap():
    minimap = pygame.Rect(WIDTH - 160, HEIGHT - 160, 150, 150)
    pygame.draw.rect(screen, (50, 50, 80), minimap)
    pygame.draw.rect(screen, WHITE, minimap, 2)
    scale = 0.05
    px = int(minimap.x + player.x * scale)
    py = int(minimap.y + player.y * scale)
    ox = int(minimap.x + object_x * scale)
    oy = int(minimap.y + object_y * scale)
    pygame.draw.circle(screen, WHITE, (px, py), 3)
    pygame.draw.circle(screen, (255, 0, 0), (ox, oy), 4)

class Asteroid:
    def __init__(self, x=None, y=None, size=180):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.randint(500, 800)
        self.x = x if x is not None else player.x + math.cos(angle) * radius
        self.y = y if y is not None else player.y + math.sin(angle) * radius
        self.speed = random.uniform(0.5, 1.5)
        self.angle = math.atan2(player.y - self.y, player.x - self.x)
        self.size = size
        self.health = self.size // 60
        self.image = pygame.transform.scale(asteroid_img, (self.size, self.size))

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        rect = self.image.get_rect(center=(self.x - camera_x, self.y - camera_y))
        screen.blit(self.image, rect)

    def hit(self):
        self.health -= 1
        return self.health <= 0

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.radius = 4

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x - camera_x), int(self.y - camera_y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.2, 0.7)) for _ in range(100)]
player = Player()
player.x = object_x + 600
player.y = object_y

asteroids = []
bullets = []
asteroid_spawn_timer = 0
tooltip = None


planet1 = Planet(planet1_img, orbit_radius=200, speed=0.01)
planet2 = Planet(planet2_img, orbit_radius=300, speed=0.008, angle_offset=math.pi/2)
planet3 = Planet(planet3_img, orbit_radius=400, speed=0.006, angle_offset=math.pi)
planets = [planet1, planet2, planet3]


while running:
    screen.fill(BASE_BG_COLOR)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not in_menu and not game_over:
            if event.button == 1:
                angle = math.atan2(mouse_y - HEIGHT//2, mouse_x - WIDTH//2)
                bullets.append(Bullet(player.x, player.y, angle))

    keys = pygame.key.get_pressed()
    player.move(keys)
    camera_x = player.x - WIDTH // 2
    camera_y = player.y - HEIGHT // 2
    asteroid_spawn_timer += 1
    if asteroid_spawn_timer > 100 and not in_menu and not game_over:
        asteroids.append(Asteroid())
        asteroid_spawn_timer = 0

    for i, star in enumerate(stars):
        x, y, speed = star
        stars[i] = (x, y + speed, speed)
        if y > HEIGHT:
            stars[i] = (random.randint(0, WIDTH), -1, random.uniform(0.2, 0.7))
        pygame.draw.circle(screen, WHITE, (x, y), 1)

    if in_menu:
        title = font.render("Exploring The Universe", True, TEXT_COLOR)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))
        instructions = small_font.render("Use arrow keys to move. Click to select.", True, TEXT_COLOR)
        screen.blit(instructions, (20, HEIGHT - 40))
        for i, option in enumerate(options.keys()):
            box_rect = pygame.Rect(WIDTH // 2 - 150, 200 + i * 100, 300, 80)
            pygame.draw.rect(screen, (70, 70, 100), box_rect, border_radius=20)
            text_surf = font.render(option, True, TEXT_COLOR)
            screen.blit(text_surf, (box_rect.x + 10, box_rect.y + 10))
            if box_rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                select_sound.play()
                selected_option = option
                in_menu = False
    elif game_over:
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, ((WIDTH - game_over_text.get_width()) // 2, HEIGHT // 2 - 40))
        retry_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 20, 140, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, retry_button, border_radius=10)
        retry_text = small_font.render("Restart", True, TEXT_COLOR)
        screen.blit(retry_text, (retry_button.x + 25, retry_button.y + 10))
        if retry_button.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
            select_sound.play()
            reset_player()
            bullets.clear()
            asteroids.clear()
            game_over = False
            player.alive = True
        pygame.display.update()
        continue
    else:
        draw_animated_model(selected_option)

        if selected_option in ["Black Hole", "Neutron Star"]:
            center_x, center_y = object_x - camera_x, object_y - camera_y
        elif selected_option in ["Dark Matter", "Exoplanet"]:
            center_x, center_y = object_x - camera_x, object_y - camera_y
            sun_rect = sun_img.get_rect(center=(center_x, center_y))
            screen.blit(sun_img, sun_rect)

        for planet in planets:
            planet.update(object_x, object_y)
            # update its rect so tooltips/collisions align
            planet.rect.center = (planet.x - camera_x, planet.y - camera_y)
            # draw the planet at its computed position
            planet.draw()


        if selected_option:
            object_screen_x = object_x - camera_x
            object_screen_y = object_y - camera_y
            obj_rect = pygame.Rect(object_screen_x - 100, object_screen_y - 100, 200, 200)
            if obj_rect.collidepoint(mouse_x, mouse_y):
                if tooltip is None:
                    tooltip = Tooltip(options[selected_option], small_font)
            else:
                tooltip = None
            if tooltip:
                tooltip.draw(screen, object_screen_x, object_screen_y - 80)
                pygame.time.delay(50)

        player.apply_gravity(object_x, object_y, selected_option)
        player.draw()

    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()

    for asteroid in asteroids[:]:
        asteroid.move()
        asteroid.draw()
        dx = asteroid.x - player.x
        dy = asteroid.y - player.y
        if math.hypot(dx, dy) < 40 and player.alive:
            explode_player()
        for bullet in bullets[:]:
            if asteroid.image.get_rect(center=(asteroid.x - camera_x, asteroid.y - camera_y)).colliderect(bullet.get_rect()):
                bullets.remove(bullet)
                if asteroid.hit():
                    asteroids.remove(asteroid)
                    if asteroid.size > 60:
                        for _ in range(2):
                            asteroids.append(Asteroid(asteroid.x, asteroid.y, asteroid.size // 2))
                    break


                for planet in planets:
                    planet.update(center_x, center_y)
                planet.draw()

    exit_button = pygame.Rect(WIDTH - 100, 20, 80, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, exit_button, border_radius=10)
    exit_text = small_font.render("Exit", True, TEXT_COLOR)
    screen.blit(exit_text, (exit_button.x + 10, exit_button.y + 10))
    if exit_button.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
        select_sound.play()
        in_menu = True
        selected_option = None
        reset_player()
        bullets.clear()
        asteroids.clear()

        draw_minimap()

    pygame.display.update()

pygame.quit()