class LevelSystem:
    """关卡系统（空壳实现）"""
    
    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.current_level = 1
        self.max_levels = 4  # 将关卡上限改为4
        
    def load_level(self, level_number):
        """加载指定关卡"""
        self.current_level = level_number
        # 根据关卡设置不同的参数
        if level_number == 1:
            self.ai_game.settings.alien_speed = 1.0
            self.ai_game.settings.alien_points = 50
        elif level_number == 2:
            self.ai_game.settings.alien_speed = 1.2
            self.ai_game.settings.alien_points = 75
        elif level_number == 3:
            self.ai_game.settings.alien_speed = 1.5
            self.ai_game.settings.alien_points = 100
        elif level_number == 4:
            self.ai_game.settings.alien_speed = 1.8
            self.ai_game.settings.alien_points = 150
        
    def next_level(self):
        """进入下一关（空壳实现）"""
        if self.current_level < self.max_levels:
            self.current_level += 1
            self.load_level(self.current_level)
            return True
        return False
    
    def get_level_info(self):
        """获取当前关卡信息（空壳实现）"""
        return {
            "level": self.current_level,
            "name": f"第{self.current_level}关",
            "description": "关卡描述待添加"
        }