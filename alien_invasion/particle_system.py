import pygame
import random
from pygame.sprite import Sprite

class Particle(Sprite):
    """单个粒子类"""
    def __init__(self, x, y, color, speed_range, size_range, lifetime_range):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.speed = random.uniform(speed_range[0], speed_range[1])
        self.direction = random.uniform(0, 2 * 3.14159)  # 随机方向
        self.size = random.uniform(size_range[0], size_range[1])
        self.lifetime = random.uniform(lifetime_range[0], lifetime_range[1])
        self.max_lifetime = self.lifetime
        
        # 创建粒子表面
        self.image = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (int(self.size), int(self.size)), int(self.size))
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        """更新粒子状态"""
        self.lifetime -= 1
        if self.lifetime <= 0:
            return False  # 粒子死亡
        
        # 移动粒子
        self.x += self.speed * pygame.math.Vector2(1, 0).rotate(self.direction * 180/3.14159).x
        self.y += self.speed * pygame.math.Vector2(1, 0).rotate(self.direction * 180/3.14159).y
        
        # 根据生命周期调整透明度
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.image.set_alpha(alpha)
        
        # 更新位置
        self.rect.center = (int(self.x), int(self.y))
        
        return True  # 粒子存活

class ParticleEffect:
    """粒子效果管理器"""
    def __init__(self):
        self.particles = pygame.sprite.Group()
    
    def create_explosion(self, x, y, color=(255, 200, 0), count=30):
        """创建爆炸效果"""
        for _ in range(count):
            particle = Particle(
                x, y, 
                color, 
                speed_range=(1, 5),
                size_range=(1, 4),
                lifetime_range=(10, 40)
            )
            self.particles.add(particle)
    
    def create_sparkle(self, x, y, color=(255, 255, 255), count=15):
        """创建火花效果"""
        for _ in range(count):
            particle = Particle(
                x, y,
                color,
                speed_range=(0.5, 2),
                size_range=(1, 2),
                lifetime_range=(5, 20)
            )
            self.particles.add(particle)
    
    def create_shield_hit(self, x, y, count=20):
        """创建护盾受损效果"""
        for _ in range(count):
            particle = Particle(
                x, y,
                (100, 200, 255),  # 蓝色护盾颜色
                speed_range=(0.5, 2),
                size_range=(1, 3),
                lifetime_range=(10, 30)
            )
            self.particles.add(particle)
    
    def update(self):
        """更新所有粒子"""
        for particle in self.particles.copy():
            if not particle.update():
                self.particles.remove(particle)
    
    def draw(self, screen):
        """绘制所有粒子"""
        self.particles.draw(screen)