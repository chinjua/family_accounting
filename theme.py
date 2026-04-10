# -*- coding: utf-8 -*-
"""
主题模块 - 定义应用程序的主题样式
"""
import wx

# 主题定义
THEMES = {
    'light': {
        'name': '浅色',
        'name_en': 'Light',
        # 背景色
        'bg_color': wx.Colour(240, 240, 240),
        'panel_bg': wx.Colour(245, 245, 245),
        'toolbar_bg': wx.Colour(235, 235, 235),
        # 文字颜色
        'fg_color': wx.Colour(0, 0, 0),
        'label_color': wx.Colour(60, 60, 60),
        'hint_color': wx.Colour(100, 100, 100),
        # 边框颜色
        'border_color': wx.Colour(200, 200, 200),
        # 表格颜色
        'grid_bg': wx.WHITE,
        'grid_header_bg': wx.Colour(220, 220, 220),
        'grid_header_fg': wx.Colour(0, 0, 0),
        'grid_alt_bg': wx.Colour(248, 248, 248),
        'grid_selection_bg': wx.Colour(70, 130, 180),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色
        'button_bg': wx.Colour(70, 130, 180),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(100, 149, 200),
        # 状态栏
        'statusbar_bg': wx.Colour(70, 130, 180),
        'statusbar_fg': wx.WHITE,
        # 卡片颜色
        'card_bg': wx.Colour(250, 250, 250),
        'card_border': wx.Colour(220, 220, 220),
    },
    'dark': {
        'name': '灰色',
        'name_en': 'Gray',
        # 背景色 - 中灰色
        'bg_color': wx.Colour(200, 200, 200),
        'panel_bg': wx.Colour(210, 210, 210),
        'toolbar_bg': wx.Colour(195, 195, 195),
        # 文字颜色
        'fg_color': wx.Colour(40, 40, 40),
        'label_color': wx.Colour(60, 60, 60),
        'hint_color': wx.Colour(100, 100, 100),
        # 边框颜色
        'border_color': wx.Colour(170, 170, 170),
        # 表格颜色
        'grid_bg': wx.Colour(220, 220, 220),
        'grid_header_bg': wx.Colour(195, 195, 195),
        'grid_header_fg': wx.Colour(40, 40, 40),
        'grid_alt_bg': wx.Colour(210, 210, 210),
        'grid_selection_bg': wx.Colour(70, 130, 180),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色
        'button_bg': wx.Colour(70, 130, 180),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(100, 149, 200),
        # 状态栏
        'statusbar_bg': wx.Colour(180, 180, 180),
        'statusbar_fg': wx.Colour(40, 40, 40),
        # 卡片颜色
        'card_bg': wx.Colour(205, 205, 205),
        'card_border': wx.Colour(170, 170, 170),
    },
    'blue': {
        'name': '蓝色',
        'name_en': 'Blue',
        # 背景色
        'bg_color': wx.Colour(230, 240, 250),
        'panel_bg': wx.Colour(235, 245, 255),
        'toolbar_bg': wx.Colour(200, 220, 240),
        # 文字颜色
        'fg_color': wx.Colour(0, 0, 0),
        'label_color': wx.Colour(50, 50, 100),
        'hint_color': wx.Colour(80, 80, 120),
        # 边框颜色
        'border_color': wx.Colour(180, 200, 220),
        # 表格颜色
        'grid_bg': wx.WHITE,
        'grid_header_bg': wx.Colour(200, 220, 240),
        'grid_header_fg': wx.Colour(0, 0, 80),
        'grid_alt_bg': wx.Colour(245, 250, 255),
        'grid_selection_bg': wx.Colour(0, 100, 180),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色
        'button_bg': wx.Colour(0, 100, 180),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(0, 130, 200),
        # 状态栏
        'statusbar_bg': wx.Colour(0, 80, 150),
        'statusbar_fg': wx.WHITE,
        # 卡片颜色
        'card_bg': wx.Colour(240, 248, 255),
        'card_border': wx.Colour(180, 200, 220),
    },
    'green': {
        'name': '绿色',
        'name_en': 'Green',
        # 背景色
        'bg_color': wx.Colour(230, 245, 230),
        'panel_bg': wx.Colour(235, 250, 235),
        'toolbar_bg': wx.Colour(200, 230, 200),
        # 文字颜色
        'fg_color': wx.Colour(0, 0, 0),
        'label_color': wx.Colour(50, 80, 50),
        'hint_color': wx.Colour(80, 110, 80),
        # 边框颜色
        'border_color': wx.Colour(180, 210, 180),
        # 表格颜色
        'grid_bg': wx.WHITE,
        'grid_header_bg': wx.Colour(200, 230, 200),
        'grid_header_fg': wx.Colour(0, 60, 0),
        'grid_alt_bg': wx.Colour(245, 252, 245),
        'grid_selection_bg': wx.Colour(76, 175, 80),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色
        'button_bg': wx.Colour(76, 175, 80),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(100, 190, 100),
        # 状态栏
        'statusbar_bg': wx.Colour(60, 140, 60),
        'statusbar_fg': wx.WHITE,
        # 卡片颜色
        'card_bg': wx.Colour(240, 252, 240),
        'card_border': wx.Colour(180, 210, 180),
    },
    'purple': {
        'name': '紫色',
        'name_en': 'Purple',
        # 背景色
        'bg_color': wx.Colour(240, 235, 245),
        'panel_bg': wx.Colour(245, 240, 250),
        'toolbar_bg': wx.Colour(220, 210, 230),
        # 文字颜色
        'fg_color': wx.Colour(0, 0, 0),
        'label_color': wx.Colour(80, 50, 80),
        'hint_color': wx.Colour(110, 80, 120),
        # 边框颜色
        'border_color': wx.Colour(200, 180, 210),
        # 表格颜色
        'grid_bg': wx.WHITE,
        'grid_header_bg': wx.Colour(220, 210, 230),
        'grid_header_fg': wx.Colour(60, 0, 80),
        'grid_alt_bg': wx.Colour(248, 245, 252),
        'grid_selection_bg': wx.Colour(156, 39, 176),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色
        'button_bg': wx.Colour(156, 39, 176),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(180, 60, 200),
        # 状态栏
        'statusbar_bg': wx.Colour(130, 30, 150),
        'statusbar_fg': wx.WHITE,
        # 卡片颜色
        'card_bg': wx.Colour(250, 245, 255),
        'card_border': wx.Colour(200, 180, 210),
    },
    'silver': {
        'name': '银白色',
        'name_en': 'Silver',
        # 背景色 - 银白色调
        'bg_color': wx.Colour(245, 245, 250),
        'panel_bg': wx.Colour(248, 248, 252),
        'toolbar_bg': wx.Colour(240, 240, 245),
        # 文字颜色
        'fg_color': wx.Colour(50, 50, 60),
        'label_color': wx.Colour(60, 60, 80),
        'hint_color': wx.Colour(120, 120, 140),
        # 边框颜色
        'border_color': wx.Colour(210, 210, 220),
        # 表格颜色
        'grid_bg': wx.WHITE,
        'grid_header_bg': wx.Colour(235, 235, 240),
        'grid_header_fg': wx.Colour(50, 50, 60),
        'grid_alt_bg': wx.Colour(250, 250, 255),
        'grid_selection_bg': wx.Colour(100, 149, 237),
        'grid_selection_fg': wx.WHITE,
        # AquaButton 颜色 - 钢蓝色调
        'button_bg': wx.Colour(100, 149, 237),
        'button_fg': wx.Colour(255, 255, 255),
        'button_hover_bg': wx.Colour(120, 160, 250),
        # 状态栏
        'statusbar_bg': wx.Colour(80, 120, 200),
        'statusbar_fg': wx.WHITE,
        # 卡片颜色
        'card_bg': wx.Colour(250, 250, 255),
        'card_border': wx.Colour(210, 210, 220),
    },
}

# 默认主题
DEFAULT_THEME = 'light'

# 主题切换回调函数列表
_theme_listeners = []

# AquaButton 实例列表
_aqua_buttons = []


def register_aqua_button(button):
    """注册 AquaButton 实例"""
    if button not in _aqua_buttons:
        _aqua_buttons.append(button)


def unregister_aqua_button(button):
    """取消注册 AquaButton 实例"""
    if button in _aqua_buttons:
        _aqua_buttons.remove(button)


def apply_theme_to_aqua_buttons():
    """应用主题到所有注册的 AquaButton"""
    theme = get_theme()
    for btn in _aqua_buttons[:]:  # 使用切片避免迭代时修改列表
        try:
            if btn:
                btn.SetBackgroundColour(theme['button_bg'])
                btn.SetForegroundColour(theme['button_fg'])
                btn.Refresh()
        except:
            pass


def add_theme_listener(callback):
    """添加主题切换监听器"""
    if callback not in _theme_listeners:
        _theme_listeners.append(callback)


def remove_theme_listener(callback):
    """移除主题切换监听器"""
    if callback in _theme_listeners:
        _theme_listeners.remove(callback)


def notify_theme_changed(theme_name):
    """通知所有监听器主题已切换"""
    for callback in _theme_listeners:
        try:
            callback(theme_name)
        except Exception:
            pass


def get_theme(theme_name=None):
    """获取主题配置"""
    if theme_name is None:
        from config_manager import config
        theme_name = config.get('theme', DEFAULT_THEME)
    
    if theme_name not in THEMES:
        theme_name = DEFAULT_THEME
    
    return THEMES[theme_name]


def apply_theme_to_window(window, theme_name=None):
    """为主题应用主题"""
    theme = get_theme(theme_name)
    
    # 设置窗口背景色
    window.SetBackgroundColour(theme['bg_color'])
    
    # 递归应用到所有子控件
    for child in window.GetChildren():
        apply_theme_to_control(child, theme)


def apply_theme_to_control(control, theme):
    """为主题应用单个控件"""
    try:
        # 获取控件类型
        class_name = control.GetClassName()
        
        # 根据控件类型应用不同样式
        if class_name in ('wxWindow', 'wxPanel', 'wxScrolledWindow'):
            control.SetBackgroundColour(theme['bg_color'])
            control.SetForegroundColour(theme['fg_color'])
        
        elif class_name == 'wxStaticText':
            # 保留特定颜色的静态文本
            fg = control.GetForegroundColour()
            if not _is_hint_color(fg):
                control.SetForegroundColour(theme['fg_color'])
        
        elif class_name == 'wxButton':
            # 设置按钮背景色（支持 AquaButton）
            control.SetBackgroundColour(theme['button_bg'])
            control.SetForegroundColour(theme['button_fg'])
        
        elif class_name == 'wxTextCtrl':
            control.SetBackgroundColour(theme['panel_bg'])
            control.SetForegroundColour(theme['fg_color'])
        
        elif class_name == 'wxChoice':
            control.SetBackgroundColour(theme['panel_bg'])
            control.SetForegroundColour(theme['fg_color'])
        
        elif class_name == 'wxStaticBox':
            control.SetForegroundColour(theme['label_color'])
        
        elif class_name == 'wxCheckBox':
            control.SetForegroundColour(theme['fg_color'])
        
        elif class_name == 'wxRadioButton':
            control.SetForegroundColour(theme['fg_color'])
        
        # 递归处理子控件
        if hasattr(control, 'GetChildren'):
            for child in control.GetChildren():
                apply_theme_to_control(child, theme)
    
    except Exception:
        pass


def _is_hint_color(color):
    """判断是否为提示颜色（浅色，不应被主题覆盖）"""
    # 灰色系通常为提示文字
    r, g, b = color.Red(), color.Green(), color.Blue()
    return (r == g == b) and (r < 150)


def apply_theme_to_grid(grid, theme):
    """为主题应用网格控件"""
    # 设置网格背景
    grid.SetDefaultCellBackgroundColour(theme['grid_bg'])
    grid.SetDefaultCellTextColour(theme['fg_color'])
    grid.SetLabelBackgroundColour(theme['grid_header_bg'])
    grid.SetLabelTextColour(theme['grid_header_fg'])
    grid.SetSelectionBackground(theme['grid_selection_bg'])
    grid.SetSelectionForeground(theme['grid_selection_fg'])
    
    # 刷新网格
    grid.Refresh()


def get_button_colors(theme_name=None):
    """获取按钮颜色配置"""
    theme = get_theme(theme_name)
    return {
        'bg': theme['button_bg'],
        'fg': theme['button_fg'],
        'hover_bg': theme['button_hover_bg'],
    }


def get_statusbar_colors(theme_name=None):
    """获取状态栏颜色配置"""
    theme = get_theme(theme_name)
    return {
        'bg': theme['statusbar_bg'],
        'fg': theme['statusbar_fg'],
    }


def get_grid_colors(theme_name=None):
    """获取表格颜色配置"""
    theme = get_theme(theme_name)
    return {
        'bg': theme['grid_bg'],
        'header_bg': theme['grid_header_bg'],
        'header_fg': theme['grid_header_fg'],
        'alt_bg': theme['grid_alt_bg'],
        'selection_bg': theme['grid_selection_bg'],
        'selection_fg': theme['grid_selection_fg'],
    }


def get_card_colors(theme_name=None):
    """获取卡片颜色配置"""
    theme = get_theme(theme_name)
    return {
        'bg': theme['card_bg'],
        'border': theme['card_border'],
    }
