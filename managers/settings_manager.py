import json
import os

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.filename):
            return self.get_default_settings()
        
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Error loading settings, using defaults.")
            return self.get_default_settings()

    def get_default_settings(self):
        return {
            "volume": 100,
            "mobile_controls": True
        }

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except IOError:
            print("Error saving settings.")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
