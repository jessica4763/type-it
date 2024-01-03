import os

import pygame

import constants


knight_idle_frames = []
knight_walk_frames = []
knight_attack_frames = []
knight_death_frames = []

melee_skeleton_walk_frames = []
melee_skeleton_attack_frames = []
melee_skeleton_death_frames = []

ranged_skeleton_walk_frames = []
ranged_skeleton_attack_frames = []
ranged_skeleton_death_frames = []


def get_font(text, font, font_size, color, x, y, orientation):
    text_font = pygame.font.Font(font, font_size)
    text_surface = text_font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if orientation == 'center':
        text_rect.center = (x, y)
    elif orientation == 'topleft':
        text_rect.topleft = (x, y)
    elif orientation == 'topright':
        text_rect.topright = (x, y)

    return text_surface, text_rect


def get_sprite_frames():
    sprites = (
        {'path': constants.KNIGHT_IDLE_PATH,            'frames': knight_idle_frames},
        {'path': constants.KNIGHT_WALK_PATH,            'frames': knight_walk_frames},
        {'path': constants.KNIGHT_ATTACK_PATH,          'frames': knight_attack_frames},
        {'path': constants.KNIGHT_DEATH_PATH,           'frames': knight_death_frames},
        {'path': constants.MELEE_SKELETON_WALK_PATH,    'frames': melee_skeleton_walk_frames},
        {'path': constants.MELEE_SKELETON_ATTACK_PATH,  'frames': melee_skeleton_attack_frames},
        {'path': constants.MELEE_SKELETON_DEATH_PATH,   'frames': melee_skeleton_death_frames},
        {'path': constants.RANGED_SKELETON_WALK_PATH,   'frames': ranged_skeleton_walk_frames},
        {'path': constants.RANGED_SKELETON_ATTACK_PATH, 'frames': ranged_skeleton_attack_frames},
        {'path': constants.RANGED_SKELETON_DEATH_PATH,  'frames': ranged_skeleton_death_frames}
    )

    for sprite in sprites:
        for image in sorted(os.listdir(sprite['path'])):
            frame = pygame.image.load(sprite['path'] + image).convert()
            frame.set_colorkey(pygame.color.Color('White'))
            sprite['frames'].append(frame)


class Image(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        # image of sprite
        self.image = pygame.image.load(constants.IMAGES_PATH + image).convert_alpha()

        # rect of sprite
        self.rect = self.image.get_rect()


class Text(pygame.sprite.Sprite):
    """ Static text. E.g. Words that do not move. """
    def __init__(self, word, font, color, font_size, x, y, *, orientation):
        super().__init__()
        # to change the size of the text later on
        self.word = word
        self.font = font
        self.color = color
        self.size = font_size
        self.base_size = font_size
        self.orientation = orientation

        # position of the text
        self.x = x
        self.y = y

        self.image, self.rect = self.get_text()

    def get_text(self):
        return get_font(self.word, self.font, self.size, self.color, self.x, self.y, self.orientation)

    def update(self):
        # if text has been enlarged
        if self.size != self.base_size:
            # make the text smaller and smaller until it reaches its base size
            self.size = max(self.size - 1, self.base_size)

            self.image, self.rect = self.get_text()


class Score(Text):
    """ Active text. E.g. Words that move themselves. """
    display = None

    def __init__(self, score, font, font_size, color, x, y, *, orientation):
        super().__init__('+' + score, font, font_size, color, x, y, orientation=orientation)
        # the score to be added incrementally
        self.score = int(score)

        # the score to be reached
        self.target_score = self.display.score_text + self.score

        # the time when the enemy dies
        self.lifetime_call_time = pygame.time.get_ticks()

    def check_lifetime(self):
        """ How long the text should remain around the enemy before disappearing. """
        if pygame.time.get_ticks() - self.lifetime_call_time >= 1000 and self.display.score_text + self.score >= self.target_score:
            self.display.score_indicators.remove(self)

    def update(self):
        self.check_lifetime()
        self.rect.x -= 1
        self.rect.y -= 1

        # adds score incrementally until reaching the target score
        if self.display.score_text >= self.target_score:
            self.display.score_text = self.target_score
        else:
            self.display.score_text += 4

        self.display.score_text_sprite.sprite.word = 'score: ' + str(self.display.score_text)
        self.display.score_text_sprite.sprite.image, self.display.score_text_sprite.sprite.rect = self.display.score_text_sprite.sprite.get_text()


class BackgroundSprite(pygame.sprite.Sprite):
    """ Each layer of the background. """
    replaced = False

    def __init__(self, path, image_name, layer, scroll_speed):
        super().__init__()
        self.image = pygame.image.load(path + image_name).convert_alpha()
        self.rect = self.image.get_rect()

        # ensures that background layers are drawn in order 
        self._layer = layer

        # Used when we want to make a copy of the current layer
        self.path = path
        self.image_name = image_name
        self.scroll_speed = scroll_speed

        # applies lighting to different layers
        filter = pygame.Surface((self.image.get_width(), self.image.get_height()))
        filter.fill(pygame.color.Color('Black'))
        filter.set_alpha(96 // (int(self.image_name[0]) + 1))
        self.image.blit(filter, (0, 0))

        # only layers with scroll speeds that are not integers need this
        self.scroll_by = 0

    def scroll_layer(self):
        """ Account for the fact that float values are truncated when updating rect position. """
        # just update position if scroll_speed is already an integer
        if self.scroll_speed.is_integer():
            self.rect.x -= self.scroll_speed
        else:
            self.scroll_by += self.scroll_speed
            # only update position when scroll_by is an integer
            if self.scroll_by.is_integer():
                self.rect.x -= self.scroll_by
                self.scroll_by = 0

    @property
    def layer(self):
        return self._layer


class Background(BackgroundSprite):
    """ Holds all layers of background and causes parallax effect. """
    display = None

    def __init__(self, path):
        # all layers to call draw on
        self.layers = pygame.sprite.LayeredUpdates()

        # scroll speed for each layer
        self.scroll_speeds = {
            '0.png': 0.00,
            '1.png': 0.25,
            '2.png': 0.50,
            '3.png': 1.00,
            '4.png': 2.00,
            '5.png': 3.00
        }

        for layer_number, image_name in enumerate(sorted(os.listdir(path))):
            layer = BackgroundSprite(path, image_name, layer_number, self.scroll_speeds[image_name])
            self.layers.add(layer)

    def parallax(self):
        """ Adds a parallax effect to the background. """
        if self.display.player.attack_frame:
            return
        
        # move the player if the player is not attacking or no enemies are attacking the player
        for enemy in self.display.enemies:
            if enemy.is_attacking:
                return
        
        for layer in self.layers:
            # extend the layer if it no longer fully covers the screen
            if layer.rect.x + layer.rect.w <= constants.SCREEN_WIDTH and not layer.replaced:
                layer.replaced = True
                new_layer = BackgroundSprite(layer.path, layer.image_name, layer.layer, layer.scroll_speed)
                new_layer.rect.x = layer.rect.x + layer.rect.w
                self.layers.add(new_layer)
            # move the layer if not extending it; scrolling makes placing a copy in the perfect position more difficult
            elif layer.scroll_speed > 0:
                layer.scroll_layer()

            # remove the layer if it is no longer visible 
            if layer.rect.x + layer.rect.w <= 0:
                self.layers.remove(layer)

        # moves enemies along with the background
        for enemy in self.display.enemies:
            scroll_speed = list(self.scroll_speeds.values())[-1]
            enemy.rect.x -= scroll_speed
            for word in enemy.word_sprite_form:
                word.rect.x -= scroll_speed
