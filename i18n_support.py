# -*- coding: utf-8 -*-
"""
国际化支持模块 - 为窗口和对话框提供语言切换支持
"""
import wx
from i18n import get_text, add_language_listener, remove_language_listener


class LanguageSupportMixin:
    """语言切换支持混入类
    
    在 wx.Dialog 或 wx.Frame 子类中使用此混入，可以自动响应语言切换事件
    
    使用方法：
    1. 继承此类（作为第一个基类）
    2. 实现 refresh_labels() 方法更新界面文字
    3. 在 __init__ 中调用 setup_language_listener()
    """
    
    def setup_language_listener(self):
        """设置语言监听器，在 __init__ 中调用"""
        self._language_callback = lambda: wx.CallAfter(self._on_language_changed)
        add_language_listener(self._language_callback)
        
        # 绑定销毁事件，确保正确清理监听器
        if hasattr(self, 'Bind'):
            self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)
    
    def _on_language_changed(self):
        """语言切换回调"""
        if self and hasattr(self, 'refresh_labels'):
            try:
                # 检查窗口是否仍然有效
                if hasattr(self, 'IsShown'):
                    self.refresh_labels()
            except Exception as e:
                pass
    
    def _on_destroy(self, event):
        """窗口销毁时移除监听器"""
        if hasattr(self, '_language_callback'):
            remove_language_listener(self._language_callback)
        event.Skip()
    
    def refresh_labels(self):
        """刷新界面文字，子类必须实现此方法
        
        在此方法中更新所有需要翻译的界面文字：
        - 标题
        - 按钮文字
        - 标签文字
        - 列标题等
        """
        raise NotImplementedError("子类必须实现 refresh_labels() 方法")


class TranslatableDialog(wx.Dialog, LanguageSupportMixin):
    """支持语言切换的对话框基类
    
    使用示例：
    class MyDialog(TranslatableDialog):
        def __init__(self, parent):
            super().__init__(parent, title=get_text('我的对话框'))
            self.init_ui()
            self.setup_language_listener()
            self.Centre()
        
        def init_ui(self):
            # 创建界面控件...
            pass
        
        def refresh_labels(self):
            self.SetTitle(get_text('我的对话框'))
            # 更新其他控件...
    """
    
    def __init__(self, parent=None, title="", size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        super().__init__(parent, title=title, size=size, style=style)


class TranslatableFrame(wx.Frame, LanguageSupportMixin):
    """支持语言切换的窗口基类
    
    使用示例与 TranslatableDialog 类似
    """
    
    def __init__(self, parent=None, title="", size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        super().__init__(parent, title=title, size=size, style=style)
