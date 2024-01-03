import random
import itertools as it

import pygame

import constants
import helper
import player
import enemy


class Display:
    """ Handles drawing and game mechanics. """
    # black screen for fade
    death = False
    transition = False
    faded = False

    # how transparent the background is. 0 -> fully tranasparent, 255 -> fully opaque
    fade_alpha = 0
    fade_surface = pygame.Surface((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

    # fill surface with transition color (black)
    fade_surface.fill(pygame.color.Color('Black'))

    # manages enemy spawns
    enemy_spawn_interval = 4096
    enemy_spawn_call_time = pygame.time.get_ticks()

    # manages type of enemies and their attributes
    possible_enemies = {
        'Melee Skeleton':  ['Melee', helper.melee_skeleton_walk_frames, helper.melee_skeleton_attack_frames, helper.melee_skeleton_death_frames, 'hard.txt', -2, 0, (240, 320), 32, 4],
        'Ranged Skeleton':  ['Ranged', helper.ranged_skeleton_walk_frames, helper.ranged_skeleton_attack_frames, helper.ranged_skeleton_death_frames, 'hard.txt', -2, 0, (240, 320), 32, 4],
    }

    # time since last call of clock.tick()
    time = 0

    # displacement of screen for shake
    offset = it.repeat((0, 0))

    def __init__(self, view, screen):
        # the surface of the screen + the screen
        self.view = view
        self.screen = screen

        # all backgrounds for all levels; add to this list if adding new levels
        self.backgrounds = [
            helper.Background(constants.CASTLE_BACKGROUND_PATH),
            helper.Background(constants.FOREST_BACKGROUND_PATH),
            helper.Background(constants.CRYPTS_BACKGROUND_PATH)
        ]

        # score needed for next level; add to this dictionary if adding new levels
        self.backgrounds_checkpoints = {
            0: self.backgrounds[0],
            2048: self.backgrounds[1],
            4096: self.backgrounds[2]
        }

        self.current_checkpoint = 0

        # current background based on current level
        self.background = self.backgrounds[self.current_checkpoint]

        # the player
        self.player = player.Player()

        # sprite group form to use draw method
        self.player_sf = pygame.sprite.GroupSingle()
        self.player_sf.add(self.player)

        # projectiles on the screen
        self.projectiles = pygame.sprite.Group()

        # displays added scores of dead enemies
        self.score_indicators = pygame.sprite.Group()

        # all enemies
        self.enemies = pygame.sprite.Group()
        self.dead_enemies = pygame.sprite.Group()

        # player kills enemies and gets a higher score
        self.score_text = 0
        self.score_text_sprite = self.get_score_text()

        # the more enemies killed the more score each new enemy gives
        self.score_multiplier_text = 1
        self.score_multiplier_text_sprite = self.get_score_multiplier_text()

        # player answers
        self.typed_text = ''
        self.typed_text_sprite = self.get_typed_text()

        # sets display attribute for other classes
        player.Player.display = self
        helper.Score.display = self
        helper.Background.display = self
        enemy.Enemy.display = self
        enemy.Projectile.display = self

        # all level sounds
        self.keypress_basic = pygame.mixer.Sound(constants.SOUNDS_PATH + '\keypress_1.wav')
        self.keypress_submit = pygame.mixer.Sound(constants.SOUNDS_PATH + '\keypress_2.wav')

    def reset(self):
        """ Screen fades on death with reset stats. """
        if self.death or self.transition:
            # check if screen has faded in and out - return if so
            if self.faded and self.fade_alpha == 0:
                self.death = False
                self.transition = False
                self.faded = False
                self.fade_alpha = 0
                return
            elif not self.faded:
                self.fade_alpha = min(self.fade_alpha + 255 / 17, 255)
            else:
                self.fade_alpha = max(self.fade_alpha - 255 / 17, 0)

            # once the screen has turned fully opaque
            if self.fade_alpha >= 255:
                # fade in immediately
                self.faded = True

                # IF the player died reset all stats
                if self.death:
                    # reset all text
                    self.score_text = 0
                    self.score_multiplier_text = 1
                    self.typed_text = ''
                    self.score_text_sprite = self.get_score_text()
                    self.score_multiplier_text_sprite = self.get_score_multiplier_text()
                    self.typed_text_sprite = self.get_typed_text()

                    # reset all enemies
                    self.enemies.empty()
                    self.projectiles.empty()
                    self.dead_enemies.empty()

                    # reset player health
                    self.player.health = 0
                    self.player.update_health(self.player.base_health)

                # If the background is transitioning to a new one
                elif self.transition:
                    self.background = self.backgrounds_checkpoints[self.current_checkpoint]

                    self.typed_text = ''
                    self.typed_text_sprite = self.get_typed_text()  # DO YOU NEED THIS?

        self.fade_surface.set_alpha(self.fade_alpha)

    def shake(self):
        """ Generator returning offset of screen, creating a 'shake' effect. """
        shake_direction = -1
        for _ in range(0, 2):
            for shake_amount in range(0, 16, 4):
                yield (shake_amount * shake_direction, 0)
            for shake_amount in range(16, 0, 4):
                yield (shake_amount * shake_direction, 0)

            # reverse shake direction
            shake_direction *= -1

        # steady screen after shake by yielding (0, 0), until next call
        while True:
            yield (0, 0)

    @staticmethod
    def generate_word(filename):
        """ Generates random word for enemies. """
        with open(filename, 'r') as f:
            contents_of_file = f.read()

        lines = contents_of_file.splitlines()
        line_number = random.randint(0, len(lines) - 1)
        return lines[line_number]

    def get_score_text(self):
        score_text_sprite = helper.Text(f'score: {self.score_text}',
                                        constants.FONTS_PATH + '8bitoperator.ttf',
                                        pygame.color.Color('White'),
                                        24,
                                        640, 72,
                                        orientation='topleft')
        score_text = pygame.sprite.GroupSingle()
        score_text.add(score_text_sprite)
        return score_text

    def get_score_multiplier_text(self):
        score_multiplier_text_sprite = helper.Text(f'x{self.score_multiplier_text}',
                                                   constants.FONTS_PATH + '8bitoperator.ttf',
                                                   pygame.color.Color('White'),
                                                   24,
                                                   640, 108,
                                                   orientation='topleft')
        score_multiplier_text = pygame.sprite.GroupSingle()
        score_multiplier_text.add(score_multiplier_text_sprite)
        return score_multiplier_text

    def get_typed_text(self):
        typed_text_sprite = helper.Text(self.typed_text,
                                        constants.FONTS_PATH + '8bitoperator.ttf',
                                        pygame.color.Color('White'),
                                        48,
                                        constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2,
                                        orientation='center')
        typed_text = pygame.sprite.GroupSingle()
        typed_text.add(typed_text_sprite)
        return typed_text

    def press_key(self, key):
        """ Handles all typing mechanics. """
        # cannot type when transitioning to new level or dying
        if not (self.death or self.transition):
            # manage player input
            if key == 'return':   # submit typed_text, if it matches with enemies the enemies are deleted
                self.keypress_submit.play()
                for enemy in self.enemies:
                    if enemy.word == self.typed_text:
                        self.player.target = enemy
                        break

                for projectile in self.projectiles:
                    if projectile.word == self.typed_text:
                        self.player.target = projectile
                        break

                self.typed_text = ''
            elif key == 'backspace':  # delete last letter in string
                self.keypress_basic.play()
                self.typed_text = self.typed_text[:-1]
            else:
                self.keypress_basic.play()
                self.typed_text += key

            self.typed_text_sprite = self.get_typed_text()

    def update(self):
        """ Updates everything. """
        # checks fade to black
        self.reset()

        # updates all things on the screen
        self.player_sf.update()
        self.enemies.update()
        self.projectiles.update()
        self.dead_enemies.update()
        self.score_indicators.update()
        self.score_text_sprite.update()

        # spawns enemies
        if pygame.time.get_ticks() - self.enemy_spawn_call_time >= self.enemy_spawn_interval:
            enemy_key = random.choice(tuple(self.possible_enemies.keys()))
            enemy_values = self.possible_enemies[enemy_key]

            # create an enemy with the given attributes
            class_name = getattr(enemy, enemy_values[0])
            
            enemy_sprite = class_name(
                enemy_values[1],     # walk path
                enemy_values[2],     # attack path
                enemy_values[3],     # death path
                enemy_values[4],     # tier
                enemy_values[5],     # speed x
                enemy_values[6],     # speed y
                enemy_values[7][0],  # y range 1
                enemy_values[7][1],  # y range 2
                enemy_values[8],     # score
                enemy_values[9]      # attack at
            )

            self.enemies.add(enemy_sprite)
            self.enemy_spawn_call_time = pygame.time.get_ticks()

        # reverse to check the highest scores first
        for checkpoint in reversed(list(self.backgrounds_checkpoints.keys())):
            if self.score_text > checkpoint:
                self.current_checkpoint = checkpoint

                # transition if it's not the current background
                if self.background != self.backgrounds_checkpoints[self.current_checkpoint]:
                    self.transition = True

                # do not check further when a score has been met - it is guaranteed to be the highest one
                break

    def draw(self):
        """ Draws everything. """
        self.background.parallax()
        self.background.layers.draw(self.screen)

        # draws player and player healthbar
        self.player.healthbar.draw(self.screen)
        self.player_sf.draw(self.screen)

        for projectile in self.projectiles:
            projectile.word_sprite_form.draw(self.screen)

        for enemy_sprite in self.enemies:
            enemy_sprite.word_sprite_form.draw(self.screen)

        # draws all enemies, both dead and alive
        self.enemies.draw(self.screen)
        self.dead_enemies.draw(self.screen)

        # draws enemy stuff
        self.score_indicators.draw(self.screen)

        # draws the projectiles on the screen
        self.projectiles.draw(self.screen)

        # draw slash effect for a moment
        for enemy_sprite in self.dead_enemies:
            if not enemy_sprite.slashed:
                y_offset = enemy_sprite.slash_rect.h - enemy_sprite.rect.h
                self.screen.blit(enemy_sprite.slash_image, (enemy_sprite.rect.x - enemy_sprite.slash_rect.w, enemy_sprite.rect.y - y_offset / 2))
                enemy.slashed = True

        # draws all static text in the level
        self.typed_text_sprite.draw(self.screen)
        self.score_text_sprite.draw(self.screen)
        self.score_multiplier_text_sprite.draw(self.screen)

        # black screen that is by default fully transparent unless fade is active
        self.screen.blit(self.fade_surface, (0, 0))
