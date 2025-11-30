import pygame
import os

class Menu:
    """游戏菜单系统"""
    
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.screen_rect = self.screen.get_rect()
        
        # 菜单状态
        self.active_menu = "main"  # main, pause, settings, difficulty
        self.selected_option = 0
        
        # 字体设置
        self._load_fonts()
        
        # 菜单选项
        self.main_menu_options = ["开始游戏", "难度设置", "游戏设置", "退出游戏"]
        self.pause_menu_options = ["继续游戏", "游戏设置", "返回主菜单", "退出游戏"]
        self.settings_options = ["音乐音量", "音效音量", "显示FPS", "返回"]
        self.difficulty_options = ["简单", "普通", "困难", "返回"]
        
        # 设置值
        self.music_volume = 80
        self.sound_volume = 80
        self.show_fps = True
        
        # 难度设置
        self.difficulty_level = 1  # 0:简单, 1:普通, 2:困难
        
        # 动画系统
        self.animation_progress = 0
        self.animation_duration = 300
        self.last_animation_time = 0
        self.animation_type = None
        
        # 选项矩形列表
        self.option_rects = []
        
    def _load_fonts(self):
        """加载字体，优先使用系统中文字体"""
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
        
        self.title_font = None
        self.option_font = None
        self.small_font = None
        
        # 尝试加载系统中文字体
        for font_name in chinese_fonts:
            try:
                self.title_font = pygame.font.SysFont(font_name, 72)
                self.option_font = pygame.font.SysFont(font_name, 48)
                self.small_font = pygame.font.SysFont(font_name, 36)
                
                # 测试字体是否支持中文
                test_surface = self.title_font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    print(f"使用字体: {font_name}")
                    break
            except:
                continue
        
        # 如果系统中文字体都不可用，使用默认字体
        if self.title_font is None:
            self.title_font = pygame.font.SysFont(None, 72)
            self.option_font = pygame.font.SysFont(None, 48)
            self.small_font = pygame.font.SysFont(None, 36)
            print("使用默认字体")
            
            # 将菜单文本改为英文
            self.main_menu_options = ["Start Game", "Difficulty", "Settings", "Quit"]
            self.pause_menu_options = ["Resume", "Settings", "Main Menu", "Quit"]
            self.settings_options = ["Music Volume", "Sound Volume", "Show FPS", "Back"]
            self.difficulty_options = ["Easy", "Normal", "Hard", "Back"]
        
    def handle_events(self, event):
        """处理菜单事件"""
        if event.type == pygame.KEYDOWN:
            # 上下导航 - 支持方向键和WS键
            if event.key in [pygame.K_UP, pygame.K_w]:
                options = self.get_current_options()
                self.selected_option = (self.selected_option - 1) % len(options)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                options = self.get_current_options()
                self.selected_option = (self.selected_option + 1) % len(options)
            # 选择确认 - 支持回车键和空格键
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.select_option()
            # 设置调整 - 支持方向键和AD键
            elif event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d] and self.active_menu == "settings":
                self.adjust_setting(event.key)
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            mouse_pos = pygame.mouse.get_pos()
            options = self.get_current_options()
            
            # 检查点击了哪个选项
            if hasattr(self, 'option_rects') and len(self.option_rects) == len(options):
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        self.select_option()
                        break
    
    def adjust_setting(self, key):
        """调整设置值"""
        is_decrease = key in [pygame.K_LEFT, pygame.K_a]
        
        if self.selected_option == 0:  # 音乐音量
            if is_decrease:
                self.music_volume = max(0, self.music_volume - 10)
            else:
                self.music_volume = min(100, self.music_volume + 10)
            # 应用音量调整
            pygame.mixer.music.set_volume(self.music_volume / 100)
        elif self.selected_option == 1:  # 音效音量
            if is_decrease:
                self.sound_volume = max(0, self.sound_volume - 10)
            else:
                self.sound_volume = min(100, self.sound_volume + 10)
        elif self.selected_option == 2:  # 显示FPS
            self.show_fps = not self.show_fps
    
    def select_option(self):
        """选择菜单选项"""
        options = self.get_current_options()
        if not options:
            return
            
        selected = options[self.selected_option]
        
        if self.active_menu == "main":
            if selected in ["开始游戏", "Start Game"]:
                self.start_game()
            elif selected in ["难度设置", "Difficulty"]:
                self.active_menu = "difficulty"
                self.selected_option = self.difficulty_level
            elif selected in ["游戏设置", "Settings"]:
                self.active_menu = "settings"
                self.selected_option = 0
            elif selected in ["退出游戏", "Quit"]:
                pygame.quit()
                exit()
                
        elif self.active_menu == "pause":
            if selected in ["继续游戏", "Resume"]:
                self.ai_game.game_active = True
                self.ai_game.game_paused = False
                pygame.mouse.set_visible(False)
            elif selected in ["游戏设置", "Settings"]:
                self.active_menu = "settings"
                self.selected_option = 0
            elif selected in ["返回主菜单", "Main Menu"]:
                self.return_to_main_menu()
            elif selected in ["退出游戏", "Quit"]:
                pygame.quit()
                exit()
                
        elif self.active_menu == "settings":
            if selected in ["返回", "Back"]:
                if self.ai_game.game_active and self.ai_game.game_paused:
                    self.active_menu = "pause"
                else:
                    self.active_menu = "main"
                self.selected_option = 0
                
        elif self.active_menu == "difficulty":
            if selected in ["返回", "Back"]:
                if self.ai_game.game_active and self.ai_game.game_paused:
                    self.active_menu = "pause"
                    self.selected_option = 1
                else:
                    self.active_menu = "main"
                    self.selected_option = 1
            else:
                # 设置难度
                if selected in ["简单", "Easy"]:
                    self.difficulty_level = 0
                elif selected in ["普通", "Normal"]:
                    self.difficulty_level = 1
                elif selected in ["困难", "Hard"]:
                    self.difficulty_level = 2
                self.apply_difficulty()
    
    def get_current_options(self):
        """获取当前菜单选项"""
        if self.active_menu == "main":
            return self.main_menu_options
        elif self.active_menu == "pause":
            return self.pause_menu_options
        elif self.active_menu == "settings":
            return self.settings_options
        elif self.active_menu == "difficulty":
            return self.difficulty_options
        return []
    
    def start_game(self):
        """开始游戏"""
        self.ai_game.game_active = True
        self.ai_game.game_paused = False
        self.ai_game.stats.reset_stats()
        self.ai_game.sb.prep_score()
        self.ai_game.sb.prep_level()
        self.ai_game.sb.prep_ships()
        
        # 清空所有对象
        self.ai_game.bullets.empty()
        self.ai_game.aliens.empty()
        self.ai_game.alien_bullets.empty()
        
        # 创建新舰队并居中飞船
        self.ai_game._create_fleet()
        self.ai_game.ship.center_ship()
        self.ai_game.ship.reset_shield()
        
        # 隐藏鼠标
        pygame.mouse.set_visible(False)
        
        # 应用难度设置
        self.apply_difficulty()
    
    def return_to_main_menu(self):
        """返回主菜单"""
        self.ai_game.game_active = False
        self.ai_game.game_paused = False
        self.active_menu = "main"
        self.selected_option = 0
        pygame.mouse.set_visible(True)
    
    def apply_difficulty(self):
        """应用难度设置"""
        if self.difficulty_level == 0:  # 简单
            self.settings.ship_speed = 2.0
            self.settings.alien_speed = 0.5
            self.settings.alien_bullet_speed = 1.0
            self.settings.alien_fire_frequency = 2000
        elif self.difficulty_level == 1:  # 普通
            self.settings.ship_speed = 1.5
            self.settings.alien_speed = 1.0
            self.settings.alien_bullet_speed = 1.5
            self.settings.alien_fire_frequency = 1000
        elif self.difficulty_level == 2:  # 困难
            self.settings.ship_speed = 1.2
            self.settings.alien_speed = 1.5
            self.settings.alien_bullet_speed = 2.0
            self.settings.alien_fire_frequency = 500
    
    def update_animation(self):
        """更新菜单动画"""
        if self.animation_type is None:
            return
            
        current_time = pygame.time.get_ticks()
        if self.last_animation_time == 0:
            self.last_animation_time = current_time
            
        elapsed = current_time - self.last_animation_time
        self.animation_progress = min(elapsed / self.animation_duration, 1.0)
        
        if self.animation_progress >= 1.0:
            self.animation_type = None
            self.animation_progress = 0
    
    def start_animation(self, animation_type):
        """开始新动画"""
        self.animation_type = animation_type
        self.animation_progress = 0
        self.last_animation_time = pygame.time.get_ticks()
    
    def draw(self, screen):
        """绘制菜单"""
        # 半透明背景
        s = pygame.Surface((self.screen_rect.width, self.screen_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        # 绘制标题
        if self.active_menu == "main":
            title_text = "外星人入侵" if self.main_menu_options[0] == "开始游戏" else "Alien Invasion"
        elif self.active_menu == "pause":
            title_text = "游戏暂停" if self.pause_menu_options[0] == "继续游戏" else "Game Paused"
        elif self.active_menu == "settings":
            title_text = "游戏设置" if self.settings_options[0] == "音乐音量" else "Settings"
        elif self.active_menu == "difficulty":
            title_text = "难度设置" if self.difficulty_options[0] == "简单" else "Difficulty"
        else:
            title_text = "Menu"
            
        title = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_rect.centerx, 150))
        screen.blit(title, title_rect)
        
        # 绘制选项
        self.option_rects = []  # 重置选项矩形列表
        options = self.get_current_options()
        for i, option in enumerate(options):
            color = (255, 215, 0) if i == self.selected_option else (255, 255, 255)
            
            if self.active_menu == "settings":
                # 特殊处理设置选项
                if i == 0:
                    text = f"音乐音量: {self.music_volume}%" if options[0] == "音乐音量" else f"Music Volume: {self.music_volume}%"
                elif i == 1:
                    text = f"音效音量: {self.sound_volume}%" if options[0] == "音乐音量" else f"Sound Volume: {self.sound_volume}%"
                elif i == 2:
                    on_off = "开" if self.show_fps else "关" if options[0] == "音乐音量" else "On" if self.show_fps else "Off"
                    text = f"显示FPS: {on_off}" if options[0] == "音乐音量" else f"Show FPS: {on_off}"
                else:
                    text = option
            elif self.active_menu == "difficulty":
                # 特殊处理难度选项
                if i < 3:
                    prefix = "✓ " if i == self.difficulty_level else "  "
                    text = prefix + option
                else:
                    text = option
            else:
                text = option
                
            option_text = self.option_font.render(text, True, color)
            option_rect = option_text.get_rect(center=(self.screen_rect.centerx, 300 + i * 60))
            screen.blit(option_text, option_rect)
            
            # 保存选项矩形用于点击检测
            self.option_rects.append(option_rect)
            
            # 绘制选择指示器
            if i == self.selected_option:
                pygame.draw.polygon(screen, (255, 215, 0), [
                    (option_rect.left - 30, option_rect.centery),
                    (option_rect.left - 10, option_rect.centery - 10),
                    (option_rect.left - 10, option_rect.centery + 10)
                ])
        
        # 绘制操作提示
        if self.active_menu == "settings":
            hint_text = "使用左右方向键或AD键调整设置" if options[0] == "音乐音量" else "Use Left/Right or A/D to adjust"
        else:
            hint_text = "使用方向键或WS键选择，回车或空格确认" if (hasattr(self, 'main_menu_options') and self.main_menu_options[0] == "开始游戏") else "Use Arrow Keys or W/S to navigate, Enter/Space to select"
        
        hint = self.small_font.render(hint_text, True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.screen_rect.centerx, self.screen_rect.height - 50))
        screen.blit(hint, hint_rect)