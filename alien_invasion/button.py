import pygame.font


class Button:
    """A class to build buttons for the game."""

    def __init__(self, ai_game, msg):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set the dimensions and properties of the button.
        self.width, self.height = 200, 50
        self.button_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)

        # Build the button's rect object and center it.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # The button message needs to be prepped only once.
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turn msg into a rendered image and center text on the button."""
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self, screen, offset=(0, 0)):
        """Draw blank button and then draw message."""
        offset_x, offset_y = offset
        temp_rect = self.rect.copy()
        temp_rect.x += offset_x
        temp_rect.y += offset_y
        screen.fill(self.button_color, temp_rect)
        
        temp_msg_rect = self.msg_image_rect.copy()
        temp_msg_rect.x += offset_x
        temp_msg_rect.y += offset_y
        screen.blit(self.msg_image, temp_msg_rect)