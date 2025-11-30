import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a float for the ship's exact horizontal position.
        self.x = float(self.rect.x)

        # Movement flags; start with a ship that's not moving.
        self.moving_right = False
        self.moving_left = False

        # Shield properties
        self.shield_strength = 100
        self.max_shield = 100
        self.shield_recharge_rate = 0.01

        self.destroy_animation = {
            'active': False,
            'progress': 0,
            'duration': 1000,  # 动画持续1秒
            'start_time': 0,
            'particles_created': False
        }

    def start_destroy_animation(self):
        """开始摧毁动画"""
        self.destroy_animation['active'] = True
        self.destroy_animation['progress'] = 0
        self.destroy_animation['start_time'] = pygame.time.get_ticks()
        self.destroy_animation['particles_created'] = False
        
    def update_destroy_animation(self):
        """更新摧毁动画状态"""
        if not self.destroy_animation['active']:
            return False
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.destroy_animation['start_time']
        self.destroy_animation['progress'] = min(elapsed / self.destroy_animation['duration'], 1.0)
        
        # 在动画中途创建粒子效果
        if (not self.destroy_animation['particles_created'] and 
            self.destroy_animation['progress'] > 0.3):
            self.ai_game.particle_effect.create_explosion(
                self.rect.centerx, self.rect.centery, 
                color=(255, 100, 0), count=100
            )
            self.destroy_animation['particles_created'] = True
            
        # 动画结束
        if self.destroy_animation['progress'] >= 1.0:
            self.destroy_animation['active'] = False
            return True  # 动画完成
            
        return False
    
    def draw_destroy_animation(self, screen, offset=(0, 0)):
        """绘制摧毁动画"""
        if not self.destroy_animation['active']:
            return
            
        offset_x, offset_y = offset
        progress = self.destroy_animation['progress']
        
        # 缩放效果
        scale = 1.0 + progress * 0.5
        width = int(self.rect.width * scale)
        height = int(self.rect.height * scale)
        
        # 透明度变化
        alpha = int(255 * (1 - progress))
        
        # 创建缩放后的飞船图像
        scaled_image = pygame.transform.scale(self.image, (width, height))
        scaled_image.set_alpha(alpha)
        
        # 计算位置（保持居中）
        x = self.rect.centerx - width // 2 + offset_x
        y = self.rect.centery - height // 2 + offset_y
        
        screen.blit(scaled_image, (x, y))

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on movement flags."""
        # Update the ship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
            
        # Update rect object from self.x.
        self.rect.x = self.x

        # Recharge shield
        if self.shield_strength < self.max_shield:
            self.shield_strength = min(self.max_shield, 
                                    self.shield_strength + self.shield_recharge_rate)

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def hit_by_bullets(self, damage):
        """Handle ship being hit by bullet. Return True if ship should be destroyed."""
        new_shield = self.shield_strength - damage
    
        if new_shield > 0:
            self.shield_strength = new_shield
            return False
        else:
            self.shield_strength = 0
            return True

    def draw_shield(self, screen, offset=(0, 0)):
        """Draw shield indicator."""
        offset_x, offset_y = offset
        if self.shield_strength > 0:
            # Simple shield bar above ship
            shield_width = 50
            shield_height = 5
            bar_x = self.rect.centerx - shield_width // 2 + offset_x
            bar_y = self.rect.top - 10 + offset_y
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), 
                            (bar_x, bar_y, shield_width, shield_height))
            
            # Shield level
            fill_width = int(shield_width * (self.shield_strength / self.max_shield))
            pygame.draw.rect(screen, (0, 100, 255), 
                            (bar_x, bar_y, fill_width, shield_height))
            
    def reset_shield(self):
        self.shield_strength = self.max_shield