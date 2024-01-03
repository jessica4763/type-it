import pygame

import helper


class Player(pygame.sprite.Sprite):
    # the current display
    display = None

    # time elapsed for constant animation speed
    time_elapsed = 0

    # how fast the sprite updates
    loop_interval = 100  # 0.1 s

    # all frames
    idle_frames = helper.knight_idle_frames
    move_frames = helper.knight_walk_frames
    attack_frames = helper.knight_attack_frames
    death_frames = helper.knight_death_frames

    # the current frames for each of animations
    idle_frame = 0
    move_frame = 0
    attack_frame = 0
    death_frame = 0

    # player health
    base_health = 10
    health = base_health

    # target if player has one
    target = None

    # to keek track of scores and multipliers
    enemies_killed = 0

    def __init__(self):
        super().__init__()

        # the starting frame -> this will change as the game runs
        self.image = self.move_frames[self.move_frame]

        # rect of the starting frame
        self.rect = self.image.get_rect()

        # starting position
        self.rect.x = 150
        self.rect.y = 300

        # contains player healthbar
        self.healthbar = self.update_healthbar()

    def loop_animation(self):
        """ Advances animation. """
        self.time_elapsed += self.display.time
        while self.time_elapsed >= self.loop_interval:
            if self.health <= 0:
                self.death_frame += 1
            elif self.target:
                self.attack_frame += 1
            else:
                for enemy in self.display.enemies:
                    if enemy.is_attacking and \
                       enemy not in self.display.dead_enemies:
                        self.idle_frame += 1
                        break
                else:
                    self.move_frame += 1

            # take away one frame from amount of frames to advance, in the form of time
            self.time_elapsed -= self.loop_interval

        # loop the idle frame if at end of animation
        if self.idle_frame > len(self.idle_frames) - 1:
            self.idle_frame = 0

        # loop the move frame if at end of animation
        if self.move_frame > len(self.move_frames) - 1:
            self.move_frame = 0

        # end the death frame at its last frame if the end of the animation is reached
        if self.death_frame > len(self.death_frames) - 1:
            self.death_frame = self.death_frame - 1

            # fade screen to black
            self.display.death = True

        # loop the attack frame if at end of animation
        if self.attack_frame >= len(self.attack_frames) - 1:
            self.attack_frame = 0
            self.target = None

    def update(self):
        """ Update the sprite. """
        self.loop_animation()

        # DYING
        if self.health <= 0:
            self.image = self.death_frames[self.death_frame]
        # ATTACKING
        elif self.target:
            self.image = self.attack_frames[self.attack_frame]
            if self.attack_frame == 6:
                self.target.dead()
                self.attack_frame += 1
                self.display.score_text_sprite.sprite.size = int(self.display.score_text_sprite.sprite.size * 1.5)

                # shake the screen
                self.display.offset = self.display.shake()
        else:
            # IDLING
            for enemy in self.display.enemies:
                if enemy.is_attacking and \
                   enemy not in self.display.dead_enemies:
                    self.image = self.idle_frames[self.idle_frame]
                    break
            # MOVING
            else:
                self.image = self.move_frames[self.move_frame]

        # set new rect to adjust the new y position
        old_rect = self.rect
        self.rect = self.image.get_rect()
        self.rect.x = old_rect.x
        self.rect.y = old_rect.y
        self.rect.x += old_rect.w - self.rect.w
        self.rect.y += old_rect.h - self.rect.h

    def update_health(self, health):
        """" Updates player hp. """
        self.health += health
        self.healthbar = self.update_healthbar()

    def update_healthbar(self):
        """ Updates healthbar according to player health. """
        healthbar_group = pygame.sprite.Group()

        # creates a sprite object with custom surface, rect, and mask attributes
        healthbar = helper.Image('healthbar.png')
        healthbar.rect.x = 640
        healthbar.rect.y = 16
        healthbar_group.add(healthbar)

        if self.health > 0:
            health = helper.Image('health.png')
            health_width = round((health.rect.w / self.base_health) * self.health)
            health_height = health.image.get_height()
            cropped = pygame.Surface((health_width, health_height), pygame.SRCALPHA)
            cropped.blit(health.image, (0, 0))
            health.image = cropped
            health.rect.center = healthbar.rect.center
            healthbar_group.add(health)

        return healthbar_group
