import os

FPS = 30

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

DIRECTORY_PATH = os.path.dirname(__file__)

# SPRITES
KNIGHT_IDLE_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'knight', 'knight_idle', '')
KNIGHT_WALK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'knight', 'knight_walk', '')
KNIGHT_ATTACK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'knight', 'knight_attack', '')
KNIGHT_DEATH_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'knight', 'knight_death', '')

MELEE_SKELETON_WALK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelemelee', 'skelemelee_walk', '')
MELEE_SKELETON_ATTACK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelemelee', 'skelemelee_attack', '')
MELEE_SKELETON_DEATH_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelemelee', 'skelemelee_death', '')

RANGED_SKELETON_WALK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelerange', 'skelerange_walk', '')
RANGED_SKELETON_ATTACK_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelerange', 'skelerange_attack', '')
RANGED_SKELETON_DEATH_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sprites', 'skelerange', 'skelerange_death', '')

# FONTS
FONTS_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'fonts', '')

# MUSIC
SOUNDS_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'sounds', '')

# IMAGES
IMAGES_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'images', '')

# BACKGROUNDS
CASTLE_BACKGROUND_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'backgrounds', 'castle', '')
FOREST_BACKGROUND_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'backgrounds', 'forest', '')
CRYPTS_BACKGROUND_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'backgrounds', 'crypts', '')

# ICON
ICON_PATH = os.path.join(DIRECTORY_PATH, 'assets', 'icon.png')
