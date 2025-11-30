class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_limit = 3

        # Bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Alien bullet settings
        self.alien_bullet_width = 3
        self.alien_bullet_height = 15
        self.alien_bullet_color = (255, 50, 50)
        self.alien_bullets_allowed = 3

        # Alien settings
        self.fleet_drop_speed = 10

        # How quickly the game speeds up
        self.speedup_scale = 1.1
        # How quickly the alien point values increase
        self.score_scale = 1.5

        # 背景设置
        self.background_types = {
            'dynamic': [
                'images/backgrounds/dynamic_bg_1.gif',
                'images/backgrounds/dynamic_bg_2.gif',
                'images/backgrounds/dynamic_bg_3.gif',
                'images/backgrounds/dynamic_bg_4.gif'
            ],
            'static': [
                'images/backgrounds/static_bg_1.png',
                'images/backgrounds/static_bg_2.png',
                'images/backgrounds/static_bg_3.png',
                'images/backgrounds/static_bg_4.png'
            ]
        }

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 2.5
        self.alien_speed = 1.0

        # Alien bullet dynamic settings
        self.alien_bullet_speed = 1.5
        self.alien_fire_frequency = 1000  # ms between shots
        
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Scoring settings
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)