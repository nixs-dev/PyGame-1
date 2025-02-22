import pygame
import os
import random
from objects.hosts.Player import Player
from objects.hosts.monsters.Monster_Mushroom import Mushroom
from objects.hosts.monsters.Evil_Wolf import Wolf
from objects.hosts.bosses.Dragon import Dragon
from objects.Ground import Ground
from objects.GameOverFrame import GameOverFrame, TryAgainButton
from objects.WinnerFrame import WinnerFrame, PlayAgainButton
from objects.SkillIcon import SkillIcon


class Game:

    level = 1
    player = None
    skills_icons = {}
    current_player_code = ''
    current_scene_code = ''
    ground = None
    scene_song = None
    screen_size = [1024, 500]
    monsterAmount = 2
    monsters = []
    currentMonster = None
    gameEnd = False
    gameOver = None
    winner_frame = None
    tryAgainButton = None
    playAgainButton = None

    background_size = (screen_size[0] * 3, screen_size[1])
    parallaxBackgroundPosition = [0, 0]

    screen = None
    background = pygame.image.load('assets/general_sprites/background.png')
    background = pygame.transform.scale(background, background_size)
    canRun = True

    level_font = None

    def __init__(self, char_code, scene_code='default_scene'):
        pygame.init()

        self.screen = pygame.display.set_mode(self.screen_size)
        self.level = 1
        self.current_player_code = char_code
        self.current_scene_code = scene_code
        self.load_initial_world_data()

        while self.canRun:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.canRun = False

                self.player.check_cooldowns(event) if not self.gameEnd else 0
                self.tryAgainButton.check_click(event, self) if self.gameOver is not None else 0
                self.playAgainButton.check_click(event, self) if self.winner_frame is not None else 0

            self.parallax_update()
            self.draw_world()
            self.draw_level()

            ##OBJECTS ACTIONS###

            if not self.gameEnd:
                self.draw_player()
                self.draw_skills_icons()
                self.draw_monsters()
                self.check_collision()
                self.objets_movement()
            else:
                self.check_game_result()

            pygame.display.flip()
            pygame.time.Clock().tick(40)

        pygame.quit()

    def load_initial_world_data(self):
        self.level = self.level
        self.monsters = []
        self.currentMonster = None
        self.gameEnd = False
        self.gameOver = None
        self.winner_frame = None
        self.tryAgainButton = None
        self.playAgainButton = None
        self.canRun = True
        self.player = Player(self, self.current_player_code)

        self.skills_icons['damage_skill'] = SkillIcon(self.screen_size, 70, self.current_player_code, 'damage_skill')
        self.skills_icons['scape_skill'] = SkillIcon(self.screen_size, 10, self.current_player_code, 'scape_skill')

        self.level_font = pygame.font.Font('assets/fonts/Collegiate.ttf', 30)
        self.ground = Ground(self.screen_size)
        self.load_monsters()
        self.start_scene_song()

    def next_level(self):
        self.level += 1
        self.load_initial_world_data()

    def check_game_result(self):
        if len(self.monsters) == 0:
            self.draw_winner_frame()
        else:
            self.draw_game_over()

    def start_scene_song(self):
        self.scene_song.stop() if self.scene_song is not None else 0

        songs_path = 'assets/scenes_songs/'
        song = ''

        for s in os.listdir(songs_path):
            if s.split('.')[0] == self.current_scene_code:
                song = songs_path + s
                break

        self.scene_song = pygame.mixer.Sound(song)
        self.scene_song.play(loops=10)
        self.scene_song.set_volume(0.3)

    def parallax_update(self):
        self.parallaxBackgroundPosition[0] -= 5

        if -self.parallaxBackgroundPosition[0] + self.screen_size[0] >= self.background_size[0]:
            self.parallaxBackgroundPosition[0] = 0

    def draw_game_over(self):
        self.gameOver = GameOverFrame(self.screen_size)
        self.tryAgainButton = TryAgainButton(self.screen_size)

        self.screen.blit(self.gameOver.surf, self.gameOver.rect)
        self.screen.blit(self.tryAgainButton.surf, self.tryAgainButton.rect)

    def draw_winner_frame(self):
        self.winner_frame = WinnerFrame(self.screen_size)
        self.playAgainButton = PlayAgainButton(self.screen_size)

        self.screen.blit(self.winner_frame.surf, self.winner_frame.rect)
        self.screen.blit(self.playAgainButton.surf, self.playAgainButton.rect)

    def load_monsters(self):
        avaible_monsters = [Wolf]

        for i in range(0, self.monsterAmount):
            random_monster = random.randint(0, len(avaible_monsters)-1)
            new_monster = avaible_monsters[random_monster](self)
            self.monsters.append(new_monster)

    def check_collision(self):
        self.player.onTheGround = pygame.sprite.collide_rect(self.player, self.ground)

        if self.currentMonster:
            self.player.lose_life() if pygame.sprite.collide_rect(self.currentMonster, self.player) else 0
            self.currentMonster.onTheGround = pygame.sprite.collide_rect(self.currentMonster, self.ground)

            for skill in self.player.actived_skills:
                if pygame.sprite.collide_rect(self.currentMonster, skill) and skill.damage > 0:
                    skill.destroy()
                    self.currentMonster.die()
                    break

    def objets_movement(self):
        self.player.fall_due_gravity()
        
        if self.currentMonster:
            self.currentMonster.fallDueGravity()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.player.update_state(1, -1)
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.player.update_state(-1, -1)
        else:
            if keys[pygame.K_UP]:
                self.player.update_state(0, -1)
            elif keys[pygame.K_RIGHT]:
                self.player.update_state(1, 0)
            elif keys[pygame.K_LEFT]:
                self.player.update_state(-1, 0)
            else:
                self.player.update_state(0, 0)

        if keys[pygame.K_q]:
            self.player.use_skill('damage_skill')
        elif keys[pygame.K_f]:
            self.player.use_skill('scape_skill')

        if self.currentMonster:
            self.currentMonster.update_state()

    def draw_world(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.background, self.parallaxBackgroundPosition)
        self.screen.blit(self.ground.surf, self.ground.rect)

    def draw_monsters(self):
        try:
            self.currentMonster = self.monsters[0]
            self.screen.blit(self.currentMonster.surf, self.currentMonster.rect)
        except IndexError:
            self.gameEnd = True

    def draw_player(self):
        if not self.player.flipped:
            self.screen.blit(self.player.surf, self.player.rect)
        else:
            self.screen.blit(pygame.transform.flip(self.player.surf, True, False), self.player.rect)

        for i in self.player.lifes:
            self.screen.blit(i.surf, i.rect)

        for i in self.player.actived_skills:
            i.blit_skill()

    def draw_level(self):
        text_coordinates = [self.screen_size[0]//2, 10]

        level_text = self.level_font.render(str(self.level), True, (255, 0, 255))
        text_rect = level_text.get_rect(x=text_coordinates[0], y=text_coordinates[1])

        self.screen.blit(level_text, text_rect)

    def draw_skills_icons(self):
        for key in self.skills_icons:
            self.screen.blit(self.skills_icons[key].surf, self.skills_icons[key].rect)
