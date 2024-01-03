import random

import pygame

import constants
import helper


class Enemy(pygame.sprite.Sprite):
    """ Base class for all enemy types. """
    display = None

    # time elapsed for constant animation speed
    time_elapsed = 0

    # how fast the sprite updates
    loop_interval = 100  # 0.1 s

    # movement speeds
    change_x = 0
    change_y = 0

    def __init__(self, score, tier):
        super().__init__()
        # how much the enemy is worth
        self.score = score

        # word on top of the enemy
        self.word = self.display.generate_word(tier)
        self.word_sprite_form = self.get_text_sprite()

    def move(self):
        # move the enemy
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # move word over the enemy
        for word in self.word_sprite_form:
            word.rect.x += self.change_x
            word.rect.y += self.change_y

    def get_text_sprite(self):
        """ Creates sprite form of word for enemies. """
        text_sprite = helper.Text(self.word,
                                  constants.FONTS_PATH + '8bitoperator.ttf',
                                  pygame.color.Color('White'),
                                  18,
                                  self.rect.x + self.rect.w / 2, self.rect.y,
                                  orientation='center')
        text_group = pygame.sprite.GroupSingle()
        text_group.add(text_sprite)
        return text_group

    def create_score_indicator(self):
        """ Score that pops up around enemy on death. """
        text_sprite = helper.Score(f'{int(self.score * self.display.score_multiplier_text)}',
                                   constants.FONTS_PATH + '8bitoperator.ttf',
                                   pygame.color.Color('White'),
                                   18,
                                   self.rect.x, self.rect.y,
                                   orientation='center')
        text_sprite.enemy = self
        self.display.score_indicators.add(text_sprite)

    def dead(self):
        """ Player enemy death animation. """
        self.display.player.enemies_killed += 1

        # word is no longer visible above the enemy when dead
        self.word_sprite_form.empty()

        # for every fifth enemy killed
        if self.display.player.enemies_killed % 5 == 0:
            # players should get more score per enemy killed
            self.display.score_multiplier_text += 0.25
            self.display.score_multiplier_text_sprite = self.display.get_score_multiplier_text()

            # enemy spawn rate should increase, cap it out at 1000 ms
            if not self.display.enemy_spawn_interval >= 1000:
                self.display.enemy_spawn_interval -= 25

        # amount of score gained above enemy after death, update this to screen
        self.create_score_indicator()


class Projectile(Enemy):
    def __init__(self, enemy):
        # enemy that shot the projectile
        self.enemy = enemy

        # image of the projectile
        self.image = pygame.Surface((0, 0))

        # rect of the projectile
        self.rect = self.image.get_rect()

        # set start
        self.rect.x = self.enemy.rect.x + 32  # x point of arrow on sprite image
        self.rect.y = self.enemy.rect.y + 64  # y point of arrow on sprite image

        # set speed, change_x and change_y are by default 0
        self.change_x = -8

        super().__init__(8, "easy.txt")

    def update(self):
        # move the enemy
        self.move()

        # if the projectile has 'collided' (not through rect/mask) with the player
        if self.rect.x + self.rect.w <= self.display.player.rect.x + self.display.player.rect.w:
            self.display.player.update_health(-1)
            self.display.projectiles.remove(self)

        # if the player cannot see the projectile anymore
        if self.rect.x + self.rect.w >= constants.SCREEN_WIDTH or self.rect.y - self.rect.h <= 0:
            self.display.projectiles.remove(self)

    def dead(self):
        """ Projectile gets knocked away. """
        super().dead()
        self.change_x = random.randint(64, 80)
        self.change_y = -random.randint(48, 64)


class Skeleton(Enemy):
    """ Base class for all enemy types. """
    # current frame
    move_frame = 0
    attack_frame = 0
    death_frame = 0

    # currently doing - moving is the default frame
    is_dying = False
    is_attacking = False

    def __init__(self, walk_path, attack_path, die_path, tier, speed_x, speed_y, first_y, second_y, score, attack_at):
        self.attack_at = attack_at

        # frame management
        self.move_frames = walk_path
        self.attack_frames = attack_path
        self.death_frames = die_path

        # how fast the enemy moves
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.change_x = self.speed_x
        self.change_y = self.speed_y

        # currently the starting frame -> this will change as the game runs
        self.image = self.move_frames[self.move_frame]

        # gets rect of image
        self.rect = self.image.get_rect()
        self.rect.x = constants.SCREEN_WIDTH  # always right edge of screen
        self.rect.y = random.randint(first_y, second_y)  # depends on if enemy is flying or on the ground

        # momentary slash effect displayed on death
        self.slash_image = pygame.image.load(constants.IMAGES_PATH + 'slash.png').convert_alpha()
        self.slash_rect = self.slash_image.get_rect()
        self.slashed = False

        super().__init__(score, tier)

    def dead(self):
        """ Player enemy death animation. """
        super().dead()
        self.is_dying = True
        self.display.enemies.remove(self)
        self.display.dead_enemies.add(self)
        self.change_x = random.randint(64, 80)
        self.change_y = random.randint(48, 64) * -1

    def loop_animation(self):
        """ Advances the animation. """
        self.time_elapsed += self.display.time
        while self.time_elapsed > self.loop_interval:
            if self.is_dying:
                self.death_frame += 1
            elif self.is_attacking:
                self.attack_frame += 1
            else:
                self.move_frame += 1

            self.time_elapsed -= self.loop_interval

        # loop the move frame if at end of animation
        if self.move_frame > len(self.move_frames) - 1:
            self.move_frame = 0

        # loop the move frame if at end of animation
        if self.attack_frame > len(self.attack_frames) - 1:
            self.attack_frame = 0

            # attack only once if the enemy is ranged and it isn't right next to the player
            if isinstance(self, Ranged) and not self.rect.x + self.rect.w <= self.display.player.rect.x + self.display.player.rect.x:
                self.is_attacking = False

        # loop the move frame if at end of animation
        if self.death_frame > len(self.death_frames) - 1:
            self.death_frame = len(self.death_frames) - 1

    def update(self):
        """ Updates the player. """
        # move the enemy
        self.move()

        # advance the amimation
        self.loop_animation()

        # DYING
        if self.is_dying:
            self.image = self.death_frames[self.death_frame]
            if self.rect.x + self.rect.w >= constants.SCREEN_WIDTH or \
               self.rect.y - self.rect.h <= 0:
                self.display.dead_enemies.remove(self)
        # ATTACKING
        elif self.is_attacking:
            self.image = self.attack_frames[self.attack_frame]
            self.change_x = 0
            self.change_y = 0
            if self.attack_frame == self.attack_at:
                self.attack_frame += 1

                # release word 'arrow'
                if isinstance(self, Ranged):
                    self.display.projectiles.add(Projectile(self))
                else:
                    self.display.player.update_health(-1)
        # MOVING
        else:
            self.image = self.move_frames[self.move_frame]
            self.change_x = self.speed_x
            self.change_y = self.speed_y

        # set new position given difference in rect dimensions
        old_rect = self.rect
        self.rect = self.image.get_rect()
        self.rect.x = old_rect.x
        self.rect.y = old_rect.y
        self.rect.x += old_rect.w - self.rect.w
        self.rect.y += old_rect.h - self.rect.h


class Melee(Skeleton):
    def update(self):
        super().update()
        # always attack if close enough to player that rect is touching (range of enemy for melee)
        if self.rect.x <= self.display.player.rect.x + self.display.player.rect.w +   0:  # 0 -> attack range
            self.is_attacking = True


class Ranged(Skeleton):
    def update(self):
        super().update()
        # always attack if in range of enemy
        if self.rect.x <= self.display.player.rect.x + self.display.player.rect.w + 256:  # 256 -> attack range
            self.is_attacking = True

        # every frame there is a 1 in 256 chance of attacking
        if random.randint(1, 256) == 256 and \
           self.rect.x + self.rect.w <= constants.SCREEN_WIDTH:
            self.is_attacking = True
