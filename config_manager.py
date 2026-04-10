# -*- coding: utf-8 -*-
"""
配置管理模块 - 保存和加载用户设置
"""
import json
import os


class ConfigManager:
    """配置管理器"""
    
    CONFIG_FILE = "app_config.json"
    
    def __init__(self):
        self.config = self.load_config()
    
    def get_config_path(self):
        """获取配置文件路径"""
        # 使用程序所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, self.CONFIG_FILE)
    
    def load_config(self):
        """加载配置"""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                pass
        return {}
    
    def save_config(self):
        """保存配置"""
        config_path = self.get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        return self.save_config()
    
    # 语言设置
    def get_language(self, default='zh_CN'):
        """获取保存的语言设置"""
        return self.get('language', default)
    
    def set_language(self, lang_code):
        """保存语言设置"""
        return self.set('language', lang_code)
    
    # 主题设置
    def get_theme(self, default='light'):
        """获取保存的主题设置"""
        return self.get('theme', default)
    
    def set_theme(self, theme_name):
        """保存主题设置"""
        return self.set('theme', theme_name)


# 全局配置管理器实例
config = ConfigManager()
