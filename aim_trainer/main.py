import pygame
from pygame import Vector2
from pygame.locals import *
import random
import os

RECT_SIZE = 70
RECT_TYPES = ["TELEPHONE", "KCAS", "KITTY"]
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
GAME_TIME = 60 * 1000
INTERVAL = 700
PADDING = 50
POINT_LIFE_TIME = 5 * 1000

MOVE_SPEED = 5
VECTOR_INTERVAL = 200
SURPRISE = False

SOUND_SCREAM = 'audio/scream.mp3'
SOUND_C4 = 'audio/c4_explode.mp3'
SOUND_WATER_DROP = 'audio/zvuk-odnoy-kapelki.mp3'
SOUND_SMART = 'audio/iphone.mp3'


class Point:
    def __init__(self, rect_list, difficulty):
        rand_number = random.randint(0, 100)
        if rand_number <= 80:
            self.type = RECT_TYPES[2]
        elif 80 < rand_number < 86:
            self.type = RECT_TYPES[1]
        else:
            self.type = RECT_TYPES[0]

        self.xd = 0
        self.yd = 0
        self.change_vector_time = 0

        while True:
            self.pos = Vector2(random.randint(RECT_SIZE//2, WINDOW_WIDTH-RECT_SIZE//2),
                               random.randint(PADDING, WINDOW_HEIGHT-RECT_SIZE//2))
            if self.type == "KITTY":
                self.image = pygame.image.load(f"img/kitty/{random.choice(os.listdir('img/kitty/'))}")
                self.image = pygame.transform.scale(self.image, (RECT_SIZE - difficulty, RECT_SIZE - difficulty))
            elif self.type == "TELEPHONE":
                self.image = pygame.image.load(f"img/smart/{random.choice(os.listdir('img/smart/'))}")
                self.image = pygame.transform.scale(self.image, (RECT_SIZE - difficulty, RECT_SIZE + 10 - difficulty))
            else:
                self.image = pygame.image.load(f"img/kcas/{random.choice(os.listdir('img/kcas/'))}")
                self.image = pygame.transform.scale(self.image, (RECT_SIZE + 10 - difficulty, RECT_SIZE - difficulty))

            self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

            self.spawn_time = pygame.time.get_ticks()

            if self.rect.collidelist(rect_list) == -1:
                break

    def draw(self, serf):
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        serf.blit(self.image, self.rect)

    def check_collision(self, pos):
        return self.rect.collidepoint(pos)

    def move(self):
        if pygame.time.get_ticks() - self.change_vector_time > VECTOR_INTERVAL:
            self.xd = random.choice((-1, 1))
            self.yd = random.choice((-1, 1))
            self.change_vector_time = pygame.time.get_ticks()
        while True:
            if self.check_wall(self.pos.x + self.xd * MOVE_SPEED, self.pos.y + self.yd * MOVE_SPEED):
                self.pos.x += self.xd * MOVE_SPEED
                self.pos.y += self.yd * MOVE_SPEED
                break
            else:
                self.xd = random.choice((-1, 1))
                self.yd = random.choice((-1, 1))

    def check_wall(self, new_x, new_y):
        if new_x > WINDOW_WIDTH - RECT_SIZE//2 or new_y > WINDOW_HEIGHT - RECT_SIZE//2 \
                or new_x < RECT_SIZE//2 or new_y < RECT_SIZE//2 :
            return False
        return True

    def check_life(self):
        self.move()
        return True if pygame.time.get_ticks() - self.spawn_time > POINT_LIFE_TIME else False


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self._pause = False
        self._menu = True
        self._clock = pygame.time.Clock()
        self.size = self.weight, self.height = WINDOW_WIDTH, WINDOW_HEIGHT
        self.points = []
        self.timer_point_event = pygame.USEREVENT + 1
        self.font = None
        self.score = 0
        self.right_clicks = 0
        self.clicks = 0
        self.game_status = 0

    def on_init(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("AIM TEST")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.points.append(Point([], 0))
        pygame.time.set_timer(self.timer_point_event, INTERVAL)
        self.font = pygame.font.SysFont('arial', 24)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._pause = False
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                if not self._pause:
                    self.pause()
                else:
                    self._pause = False
            if event.key == K_SPACE and not self._running:
                self._menu = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            self.clicks += 1
            for point in self.points:
                col_value = point.check_collision(pos)
                if col_value:
                    if point.type == RECT_TYPES[2]:
                        if event.button == 1:
                            self.score += 1
                            self.right_clicks += 1
                            self.play_sound(SOUND_WATER_DROP)
                        else:
                            continue
                    elif point.type == RECT_TYPES[0]:
                        if event.button == 3:
                            self.right_clicks += 1
                            self.score += 5
                            self.play_sound(SOUND_SMART)
                        else:
                            self.score -= 5
                    else:
                        self._running = False
                        self.game_status = 1
                    self.points.remove(point)

        if event.type == self.timer_point_event:
            pygame.time.set_timer(self.timer_point_event, INTERVAL - self.score * 3)
            self.points.append(Point([point.rect for point in self.points], (self.score // 10) * 1))

    def on_loop(self):
        for point in self.points:
            if point.check_life():
                self.points.remove(point)

    def on_render(self):
        #self._display_surf.fill((120, 200, 50))
        self.draw_bg("img/bg.jpg")
        self.draw_score()
        [point.draw(self._display_surf) for point in self.points]

        pygame.display.flip()

    def draw_bg(self, img_path):
        bg_image = pygame.image.load(img_path) #"img/kcas-bg.jpg"
        bg_image = pygame.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        rect = bg_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self._display_surf.blit(bg_image, rect)

    def draw_score(self):
        score_text = self.font.render(
            f'Score: {self.score} '
            f'Time: {60 - pygame.time.get_ticks()//1000} '
            f'Accuracy: {self.right_clicks / self.clicks if self.clicks != 0 else 0:.2f} '
            f'Speed: {pygame.time.get_ticks() / self.clicks if self.clicks != 0 else pygame.time.get_ticks():.0f}',
            True, (255, 255, 255), (255, 0, 0))
        text_rect = score_text.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, 12)
        self._display_surf.blit(score_text, text_rect)

    def pause(self):
        self._pause = True
        while self._pause:
            for event in pygame.event.get():
                self.on_event(event)

    def on_cleanup(self):
        self.draw_menu()
        pygame.quit()
    
    def play_sound(self, sound):
        sound = pygame.mixer.Sound(sound)
        sound.play()

    def draw_menu(self):
        if self.game_status == 1:
            self.draw_bg("img/kcas-bg.jpg")
            self.play_sound(SOUND_C4)
        elif SURPRISE:
            self.draw_bg("img/screamer.png")
            self.play_sound(SOUND_SCREAM)
        else:
            self._display_surf.fill(0)
        score_text = self.font.render(
            f'Score: {self.score} '
            f'Accuracy: {self.right_clicks / self.clicks if self.clicks != 0 else 0:.2f} '
            f'Speed: {pygame.time.get_ticks() / self.clicks if self.clicks != 0 else pygame.time.get_ticks():.0f}',
            True, (255, 255, 255), (0, 0, 0))
        text_rect = score_text.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self._display_surf.blit(score_text, text_rect)
        pygame.display.flip()
        while self._menu:
            for event in pygame.event.get():
                self.on_event(event)

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            if SURPRISE:
                if pygame.time.get_ticks() > 30 * 1000:
                    self._running = False
            if pygame.time.get_ticks() > GAME_TIME:
                self._running = False
            self._clock.tick(60)
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
