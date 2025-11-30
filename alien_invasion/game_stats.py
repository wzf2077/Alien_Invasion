import json
import os


class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()

        # High score should never be reset.
        self.high_score_file = 'high_score.json'
        self._load_high_score()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _load_high_score(self):
        """Load high score from file."""
        try:
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, 'r') as f:
                    data = json.load(f) 
                    self.high_score = data.get('high_score', 0)
            else:
                self.high_score = 0
        except (json.JSONDecodeError, IOError):
            self.high_score = 0

    def save_high_score(self):
        """Save high score to file."""
        try:
            # 先加载现有数据（如果有），然后更新high_score字段
            if os.path.exists(self.high_score_file):
                with open(self.high_score_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            data['high_score'] = self.high_score
            data['save_time'] = time.time()  # 可选：更新时间戳

            with open(self.high_score_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            print("Warning: Could not save high score")

    def check_high_score(self):
        """Check to see if there's a new high score."""
        if self.score > self.high_score:
            self.high_score = self.score
            return True
        return False