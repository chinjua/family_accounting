# -*- coding: utf-8 -*-
"""
注册模块 - 处理用户注册
"""
import wx
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text
from i18n_support import LanguageSupportMixin
from theme import get_theme, add_theme_listener


class RegisterDialog(wx.Dialog, LanguageSupportMixin):
    """注册对话框"""

    def __init__(self, parent=None):
        self.db = Database()
        self.username = None

        super().__init__(parent, title=get_text('注册新账户'), size=(350, 360))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.init_ui()
        self.setup_language_listener()
        self.Centre()
        
        # 添加主题切换监听
        add_theme_listener(self.on_theme_changed)
        # 应用主题
        self.apply_theme()
    
    def on_theme_changed(self, theme_name):
        """主题切换回调"""
        if not self or not self.IsShown():
            return
        wx.CallAfter(self.apply_theme)
    
    def apply_theme(self):
        """应用当前主题"""
        from theme import apply_theme_to_window
        from config_manager import config
        theme = get_theme()
        self.SetBackgroundColour(theme['bg_color'])
        # 递归应用主题到所有控件（包括按钮）
        apply_theme_to_window(self, config.get_theme())
        self.Refresh()
    
    def refresh_labels(self):
        """刷新界面文字"""
        self.SetTitle(get_text('注册新账户'))
        self.title.SetLabel(get_text('创建新账户'))
        self.user_label.SetLabel(f"{get_text('账户')}:")
        self.user_hint.SetLabel(f"({get_text('至少3个字符')})")
        self.pwd_label.SetLabel(f"{get_text('密码')}:")
        self.pwd_hint.SetLabel(f"({get_text('至少6个字符')})")
        self.confirm_label.SetLabel(f"{get_text('确认密码')}:")
        self.hint.SetLabel(get_text('注册后系统会为您创建默认的收支分类'))
        self.register_btn.SetLabel(get_text('注册'))
        self.cancel_btn.SetLabel(get_text('取消'))
        self.Layout()

    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 标题
        self.title = wx.StaticText(panel, label=get_text('创建新账户'))
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(title_font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER | wx.TOP, border=20)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=10)

        # 账户
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.user_label = wx.StaticText(panel, label=f"{get_text('账户')}:", size=(80, -1))
        self.user_text = wx.TextCtrl(panel, size=(200, -1))
        self.user_hint = wx.StaticText(panel, label=f"({get_text('至少3个字符')})")
        self.user_hint.SetForegroundColour(wx.Colour(128, 128, 128))
        user_sizer.Add(self.user_label, flag=wx.ALIGN_CENTER_VERTICAL)
        user_sizer.Add(self.user_text)
        main_sizer.Add(user_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        main_sizer.Add(self.user_hint, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=30)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=5)

        # 密码
        pwd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pwd_label = wx.StaticText(panel, label=f"{get_text('密码')}:", size=(80, -1))
        self.pwd_text = wx.TextCtrl(panel, size=(200, -1), style=wx.TE_PASSWORD)
        self.pwd_hint = wx.StaticText(panel, label=f"({get_text('至少6个字符')})")
        self.pwd_hint.SetForegroundColour(wx.Colour(128, 128, 128))
        pwd_sizer.Add(self.pwd_label, flag=wx.ALIGN_CENTER_VERTICAL)
        pwd_sizer.Add(self.pwd_text)
        main_sizer.Add(pwd_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        main_sizer.Add(self.pwd_hint, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=30)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=5)

        # 确认密码
        confirm_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.confirm_label = wx.StaticText(panel, label=f"{get_text('确认密码')}:", size=(80, -1))
        self.confirm_text = wx.TextCtrl(panel, size=(200, -1), style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        confirm_sizer.Add(self.confirm_label, flag=wx.ALIGN_CENTER_VERTICAL)
        confirm_sizer.Add(self.confirm_text)
        main_sizer.Add(confirm_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=15)

        # 提示
        self.hint = wx.StaticText(panel, label=get_text('注册后系统会为您创建默认的收支分类'))
        self.hint.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(self.hint, flag=wx.ALIGN_CENTER)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=10)

        # 按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.register_btn = AquaButton(panel, label=get_text('注册'), size=(90, 35))
        self.cancel_btn = AquaButton(panel, label=get_text('取消'), size=(90, 35))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        self.register_btn.SetForegroundColour(btn_fg)
        self.cancel_btn.SetForegroundColour(btn_fg)

        self.register_btn.Bind(wx.EVT_BUTTON, self.on_register)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.confirm_text.Bind(wx.EVT_TEXT_ENTER, self.on_register)

        btn_sizer.Add(self.register_btn)
        btn_sizer.Add(self.cancel_btn, flag=wx.LEFT, border=20)
        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=15)

        panel.SetSizer(main_sizer)

        self.user_text.SetFocus()

    def on_register(self, event):
        """注册按钮事件"""
        username = self.user_text.GetValue().strip()
        password = self.pwd_text.GetValue()
        confirm = self.confirm_text.GetValue()

        # 验证输入
        if not username:
            wx.MessageBox(get_text('账户和密码不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            self.user_text.SetFocus()
            return

        if not password:
            wx.MessageBox(get_text('账户和密码不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            self.pwd_text.SetFocus()
            return

        if password != confirm:
            wx.MessageBox(get_text('两次输入的密码不一致'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            self.confirm_text.SetValue("")
            self.confirm_text.SetFocus()
            return

        # 执行注册
        success, msg = self.db.register_user(username, password)
        if success:
            self.username = username
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(msg, get_text('注册失败'), wx.OK | wx.ICON_ERROR)
            self.user_text.SetFocus()

    def on_cancel(self, event):
        """取消按钮事件"""
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App()
    dlg = RegisterDialog()
    dlg.ShowModal()
    dlg.Destroy()
