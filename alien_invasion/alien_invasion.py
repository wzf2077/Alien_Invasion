import sys
from time import sleep

import pygame
import random
import atexit

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet

from menu import Menu
from level_system import LevelSystem
from particle_system import ParticleEffect


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # Initialize sound system
        pygame.mixer.init()
        self.sounds = {}
        self._load_sounds()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self.alien_bullets = pygame.sprite.Group()
        self.last_alien_shot_time = 0

        self._create_fleet()

        # Start Alien Invasion in an inactive state.
        self.game_active = False
        self.game_paused = False   #puase

        # Make the Play button.
        self.play_button = Button(self, "Play")

        # 添加菜单系统
        self.menu = Menu(self)
        
        # 添加关卡系统
        self.level_system = LevelSystem(self)

        # 添加FPS显示
        self.fps_font = pygame.font.SysFont(None, 36)
        self.last_fps = 0

        # 粒子效果系统
        self.particle_effect = ParticleEffect()

        # 屏幕抖动效果
        self.screen_shake = 0
        self.screen_shake_intensity = 0

        # 背景系统
        self.backgrounds = []
        self.current_background_y = 0
        self._load_backgrounds()

        # Register high score save on exit
        atexit.register(self._save_high_score_on_exit)

    def _load_backgrounds(self):
        """加载背景资源，优先动态图片，其次静态图片"""
        self.backgrounds = {
            'dynamic': [],
            'static': [],
            'fallback': self.settings.bg_color  # 纯色后备
        }
        
        # 尝试加载动态背景
        for bg_path in self.settings.background_types['dynamic']:
            try:
                # 注意：Pygame原生不支持GIF，需要额外处理
                # 这里简化处理，实际需要GIF解码库
                bg_image = self._load_animated_background(bg_path)
                if bg_image:
                    self.backgrounds['dynamic'].append(bg_image)
            except:
                pass
        
        # 如果动态背景加载失败，加载静态背景
        if not self.backgrounds['dynamic']:
            for bg_path in self.settings.background_types['static']:
                try:
                    bg_image = pygame.image.load(bg_path).convert()
                    bg_image = pygame.transform.scale(
                        bg_image, 
                        (self.settings.screen_width, self.settings.screen_height)
                    )
                    self.backgrounds['static'].append(bg_image)
                except:
                    pass

    def _load_animated_background(self, path):
        """加载动态背景（简化实现）"""
        # 实际项目中需要使用pygame_gif或类似库处理GIF
        # 这里返回静态图片作为占位符
        try:
            static_img = pygame.image.load(path.replace('.gif', '.png'))
            static_img = pygame.transform.scale(
                static_img, 
                (self.settings.screen_width, self.settings.screen_height)
            )
            return static_img
        except:
            return None

    def _draw_background(self, screen):
        """绘制背景，按优先级选择背景类型"""
        # 根据当前关卡选择背景索引
        current_level = min(self.stats.level - 1, 4)  # 假设最多5个关卡
        
        # 优先使用动态背景
        if self.backgrounds['dynamic']:
            bg_index = current_level % len(self.backgrounds['dynamic'])
            bg_image = self.backgrounds['dynamic'][bg_index]
            screen.blit(bg_image, (0, 0))
        # 其次使用静态背景
        elif self.backgrounds['static']:
            bg_index = current_level % len(self.backgrounds['static'])
            bg_image = self.backgrounds['static'][bg_index]
            screen.blit(bg_image, (0, 0))
        # 最后使用纯色背景
        else:
            screen.fill(self.backgrounds['fallback'])


    def _alien_fire_bullet(self):
        """Alien firing bullets logic."""
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_alien_shot_time > 
            self.settings.alien_fire_frequency and self.aliens):
            
            # Find bottom-most alien in each column to shoot
            aliens_by_column = {}
            for alien in self.aliens:
                col = alien.rect.centerx // 50  # Group by approximate column
                if col not in aliens_by_column or aliens_by_column[col].rect.bottom < alien.rect.bottom:
                    aliens_by_column[col] = alien
            
            # Let one random column shoot
            if aliens_by_column and len(self.alien_bullets) < self.settings.alien_bullets_allowed:
                import random
                shooting_alien = random.choice(list(aliens_by_column.values()))
                self._create_alien_bullet(shooting_alien)
                self.sounds['alien_shoot'].play()
                self.last_alien_shot_time = current_time

    def _update_alien_bullets(self):
        """Update position of alien bullets and remove old ones."""
        self.alien_bullets.update()
        
        # 删除超出屏幕的子弹
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        # 检测子弹与飞船的碰撞
        collisions = pygame.sprite.spritecollide(self.ship, self.alien_bullets, True)

        if collisions:
            # 触发屏幕抖动
            self.screen_shake = 10  # 抖动持续时间
            self.screen_shake_intensity = 5  # 抖动强度
            
            # 为每个击中的子弹添加护盾受损效果
            for bullet in collisions:
                self.particle_effect.create_shield_hit(
                    bullet.rect.centerx,
                    bullet.rect.centery
                )

            # 计算总伤害
            total_damage = len(collisions) * 25
            #处理累计伤害
            ship_destroyed = self.ship.hit_by_bullets(total_damage)

            if ship_destroyed:
                # 飞船被摧毁时添加大爆炸效果
                self.particle_effect.create_explosion(
                    self.ship.rect.centerx,
                    self.ship.rect.centery,
                    color=(255, 100, 0),
                    count=50
                )
                self._ship_hit()
            else:
                self.sounds['shield_hit'].play()

    def _save_high_score_on_exit(self):
        """Save high score when game exits."""
        self.stats.save_high_score()

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            self.menu.update_animation()

            if self.game_active and not self.game_paused:
                self.ship.update()

                if self.ship.destroy_animation['active']:
                    self.ship.update_destroy_animation()

                self._update_bullets()
                self._update_alien_bullets()
                self._update_aliens()
                self._alien_fire_bullet()
                self.particle_effect.update()

                if self.screen_shake > 0:
                    self.screen_shake -= 1

            self._update_screen()
            self.clock.tick(60)
            self.last_fps = int(self.clock.get_fps())

    def _check_events(self):
        """Respond to keypresses and mouse events."""    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # 游戏活跃且未暂停时，鼠标左键可以射击
                if self.game_active and not self.game_paused and event.button == 1:
                    self._fire_bullet()
                # 游戏不活跃或暂停时，检查播放按钮和菜单
                elif not self.game_active or self.game_paused:
                    self._check_play_button(mouse_pos)
                
            # 处理菜单事件 - 只有当游戏不活跃或暂停时
            if not self.game_active or self.game_paused:
                self.menu.handle_events(event)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Ensure high score is loaded
            self.stats._load_high_score()
            self.sb.prep_high_score()

            #Don't hide the mouse cursor.
            #pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应按键"""
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if self.game_active and not self.game_paused:
                self._fire_bullet()
        elif event.key == pygame.K_p:  # 暂停游戏
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.menu.active_menu = "pause"
                self.menu.selected_option = 0
                pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(False)
        elif event.key == pygame.K_ESCAPE:  # ESC键处理
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.menu.active_menu = "pause"
                self.menu.selected_option = 0
                pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(False)
        elif event.key == pygame.K_r:  # 新增R键重新开始
            if not self.game_active:  # 只在游戏非活跃时有效
                self._restart_game()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  # 新增D键支持
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:  # 新增A键支持
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.sounds['shoot'].play()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹-外星人碰撞"""
        # 移除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            self.sounds['explosion'].play()  # 播放爆炸音效
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                # 为每个被击中的外星人添加爆炸粒子效果
                for alien in aliens:
                    self.particle_effect.create_explosion(
                        alien.rect.centerx, 
                        alien.rect.centery
                    )
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # 销毁现有子弹并创建新舰队
            self.bullets.empty()
            
            # 检查是否还有下一关
            if self.stats.level < self.level_system.max_levels:
                # 增加关卡
                self.stats.level += 1
                self.sb.prep_level()
                
                # 加载新关卡设置
                self.level_system.load_level(self.stats.level)
                
                # 创建新舰队
                self._create_fleet()
                
                # 适当增加游戏速度
                self.settings.increase_speed()
            else:
                # 所有关卡已完成，显示胜利信息或重新开始
                self._show_victory_message()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # 开始摧毁动画
            self.ship.start_destroy_animation()
            
            # 等待动画完成
            animation_done = False
            while not animation_done:
                animation_done = self.ship.update_destroy_animation()
                self._update_screen()
                self.clock.tick(60)


            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            self.ship.reset_shield()

        else:
            self.game_active = False
            pygame.mouse.set_visible(True)  # 游戏结束时显示鼠标

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _create_fleet(self):
        """根据当前关卡创建不同形状的外星人舰队"""
        # 获取当前关卡
        current_level = self.stats.level
        
        # 清空现有外星人
        self.aliens.empty()
        
        # 根据关卡创建不同形状的舰队
        if current_level == 1:
            self._create_level1_fleet()
        elif current_level == 2:
            self._create_level2_fleet()
        elif current_level == 3:
            self._create_level3_fleet()
        elif current_level == 4:
            self._create_level4_fleet()
        else:
            # 默认使用第一关的配置
            self._create_level1_fleet()

    def _create_level1_fleet(self):
        """第一关：3x3方阵（9个外星人）"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # 3x3方阵
        rows, cols = 3, 3
        for row in range(rows):
            for col in range(cols):
                x = alien_width + 2 * alien_width * col
                y = alien_height + 2 * alien_height * row
                self._create_alien(x, y)

    def _create_level2_fleet(self):
        """第二关：金字塔形（18个外星人）"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # 金字塔形：1-2-3-4-3-2-1排列
        pattern = [1, 2, 3, 4, 3, 2, 1]
        for row, count in enumerate(pattern):
            for col in range(count):
                x = (self.settings.screen_width - count * 2 * alien_width) // 2 + 2 * alien_width * col
                y = alien_height + 2 * alien_height * row
                self._create_alien(x, y)

    def _create_level3_fleet(self):
        """第三关：菱形（27个外星人）"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # 菱形排列
        pattern = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        for row, count in enumerate(pattern):
            for col in range(count):
                x = (self.settings.screen_width - count * 2 * alien_width) // 2 + 2 * alien_width * col
                y = alien_height + 2 * alien_height * row
                self._create_alien(x, y)

    def _create_level4_fleet(self):
        """第四关：双线波浪形（36个外星人）"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # 双线波浪形排列
        for wave in range(2):
            for row in range(3):
                for col in range(6):
                    # 创建波浪效果
                    offset_x = 50 * wave
                    offset_y = 100 * wave
                    
                    x = alien_width + 2 * alien_width * col + offset_x
                    y = alien_height + 2 * alien_height * row + offset_y
                    
                    # 添加一些随机偏移创造波浪效果
                    if row % 2 == 0:
                        x += 20
                    else:
                        x -= 20
                        
                    self._create_alien(x, y)


    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        # 绘制滚动背景
        self._draw_background(self.screen)
        
        # 计算屏幕抖动偏移
        offset_x, offset_y = 0, 0
        if self.screen_shake > 0:
            offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        
        # 绘制游戏元素
        # 先绘制子弹
        for bullet in self.bullets.sprites():
            temp_bullet_rect = bullet.rect.copy()
            temp_bullet_rect.x += offset_x
            temp_bullet_rect.y += offset_y
            pygame.draw.rect(self.screen, bullet.color, temp_bullet_rect)

        # 绘制外星人子弹
        for bullet in self.alien_bullets.sprites():
            temp_bullet_rect = bullet.rect.copy()
            temp_bullet_rect.x += offset_x
            temp_bullet_rect.y += offset_y
            pygame.draw.rect(self.screen, bullet.color, temp_bullet_rect)
        
        # 绘制外星人
        for alien in self.aliens.sprites():
            temp_alien_rect = alien.rect.copy()
            temp_alien_rect.x += offset_x
            temp_alien_rect.y += offset_y
            self.screen.blit(alien.image, temp_alien_rect)
        
        # 绘制飞船（如果不在摧毁动画中）
        if not self.ship.destroy_animation['active']:
            temp_ship_rect = self.ship.rect.copy()
            temp_ship_rect.x += offset_x
            temp_ship_rect.y += offset_y
            self.screen.blit(self.ship.image, temp_ship_rect)
        else:
            # 绘制摧毁动画
            self.ship.draw_destroy_animation(self.screen, offset=(offset_x, offset_y))
        
        # 绘制护盾
        self.ship.draw_shield(self.screen, offset=(offset_x, offset_y))
        
        # 绘制粒子效果
        self.particle_effect.draw(self.screen)
        
        # 绘制UI元素
        self.sb.show_score(self.screen, offset=(offset_x, offset_y))
        
        # 显示FPS
        if self.menu.show_fps:
            fps_text = self.fps_font.render(f"FPS: {self.last_fps}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10 + offset_x, self.settings.screen_height - 40 + offset_y))
        
        # 绘制菜单或按钮
        if not self.game_active or self.game_paused:
            self.menu.draw(self.screen)
        elif not self.game_active:
            self.play_button.draw_button(self.screen, offset=(offset_x, offset_y))
        
        pygame.display.flip()

    def _load_sounds(self):
        """Load sound effects with fallback to silent placeholders."""
        sound_files = {
            'shoot': 'sounds/shoot.wav',
            'explosion': 'sounds/explosion.wav',
            'shield_hit': 'sounds/shield_hit.wav',
            'alien_shoot': 'sounds/alien_shoot.wav'  # 新增外星人射击音效
        }
        
        for name, filepath in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(filepath)
            except pygame.error:
                # Create silent sound as placeholder
                self.sounds[name] = pygame.mixer.Sound(buffer=bytes([]))

    def _create_alien_bullet(self, alien):
        """Create a new alien bullet and add it to the alien_bullets group."""
        if len(self.alien_bullets) < self.settings.alien_bullets_allowed:
            new_alien_bullet = AlienBullet(self, alien)
            self.alien_bullets.add(new_alien_bullet)

    def _show_victory_message(self):
        """显示通关胜利消息"""
        # 创建半透明背景
        s = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # 创建字体
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)
        
        # 渲染文本
        victory_text = font_large.render("恭喜通关！", True, (255, 215, 0))
        score_text = font_small.render(f"最终得分: {self.stats.score}", True, (255, 255, 255))
        restart_text = font_small.render("按R键重新开始游戏", True, (200, 200, 200))
        
        # 定位文本
        victory_rect = victory_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 50))
        score_rect = score_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 20))
        restart_rect = restart_text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 70))
        
        # 绘制文本
        self.screen.blit(victory_text, victory_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
        # 等待玩家按键
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # 按R键重新开始
                        waiting = False
                        self._restart_game()
                    elif event.key == pygame.K_q:  # 按Q键退出
                        pygame.quit()
                        sys.exit()

    def _restart_game(self):
        """重新开始游戏"""
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        
        # 清空所有对象
        self.bullets.empty()
        self.aliens.empty()
        self.alien_bullets.empty()
        
        # 重置关卡
        self.level_system.current_level = 1
        self.level_system.load_level(1)
        
        # 创建新舰队并居中飞船
        self._create_fleet()
        self.ship.center_ship()
        self.ship.reset_shield()
        
        # 重置游戏设置
        self.settings.initialize_dynamic_settings()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()