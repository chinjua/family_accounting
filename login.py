# -*- coding: utf-8 -*-
"""
登录模块 - 处理用户登录
"""
import wx
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import LANGUAGES, get_text, set_language, get_current_language, add_language_listener, remove_language_listener
from config_manager import config
from theme import THEMES, get_theme, add_theme_listener, remove_theme_listener


class LoginDialog(wx.Dialog):
    """登录对话框"""

    def __init__(self, parent=None):
        # 加载保存的语言设置
        saved_lang = config.get_language()
        if saved_lang in LANGUAGES:
            set_language(saved_lang)
        
        self.current_lang = get_current_language()
        super().__init__(parent, title=get_text('家庭记账系统') + " v0.2 - " + get_text('登录'), size=(380, 340))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.db = Database()
        self.user = None
        self.users = self.get_all_users()
        self.init_ui()
        self.Centre()
        
        # 添加语言切换监听
        add_language_listener(self.on_language_changed)
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
        theme = get_theme()
        self.SetBackgroundColour(theme['bg_color'])
        
        # 递归应用主题到所有控件（包括按钮）
        apply_theme_to_window(self, config.get_theme())
        
        # 应用透明度效果
        if theme.get('transparent', False):
            transparency = theme.get('transparency', 250)
            if hasattr(self, 'SetTransparent'):
                self.SetTransparent(transparency)
        else:
            if hasattr(self, 'SetTransparent'):
                self.SetTransparent(255)  # 完全不透明
        
        self.Refresh()
    
    def on_language_changed(self):
        """语言切换回调"""
        # 检查窗口是否已被删除
        if not self or not self.IsShown():
            return
        wx.CallAfter(self.refresh_ui)
    
    def get_all_users(self):
        """获取所有用户列表"""
        try:
            self.db.cursor.execute("SELECT username FROM users ORDER BY id")
            return [row[0] for row in self.db.cursor.fetchall()]
        except:
            return []
    
    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 顶部工具栏（语言选择 + 主题选择）
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 语言选择
        self.lang_choice = wx.Choice(panel, choices=[lang['native'] for lang in LANGUAGES.values()])
        lang_keys = list(LANGUAGES.keys())
        self.lang_choice.SetSelection(lang_keys.index(self.current_lang))
        self.lang_choice.Bind(wx.EVT_CHOICE, self.on_language_change)
        toolbar_sizer.Add(self.lang_choice)
        
        # 伸缩器
        toolbar_sizer.AddStretchSpacer()
        
        # 主题选择
        current_theme = config.get_theme()
        if get_current_language() == 'en_US':
            theme_names = [theme['name_en'] for theme in THEMES.values()]
        else:
            theme_names = [theme['name'] for theme in THEMES.values()]
        self.theme_choice = wx.Choice(panel, choices=theme_names)
        theme_keys = list(THEMES.keys())
        if current_theme in theme_keys:
            self.theme_choice.SetSelection(theme_keys.index(current_theme))
        self.theme_choice.Bind(wx.EVT_CHOICE, self.on_theme_change)
        toolbar_sizer.Add(self.theme_choice)
        
        main_sizer.Add(toolbar_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 标题（图标 + 文字）
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 程序图标
        try:
            self.logo_bitmap = wx.Bitmap("family_accounting.png", wx.BITMAP_TYPE_PNG)
            # 缩小图标尺寸
            self.logo_bitmap = self.logo_bitmap.GetSubBitmap(wx.Rect(0, 0, min(48, self.logo_bitmap.GetWidth()), min(48, self.logo_bitmap.GetHeight())))
            self.logo = wx.StaticBitmap(panel, bitmap=self.logo_bitmap)
            title_sizer.Add(self.logo, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        except:
            self.logo = wx.StaticBitmap(panel)
        
        # 标题文字
        self.title = wx.StaticText(panel, label=get_text('家庭记账系统'))
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title.SetFont(title_font)
        title_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(title_sizer, flag=wx.ALIGN_CENTER | wx.TOP, border=15)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=8)
        
        # 账户
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.user_label = wx.StaticText(panel, label=get_text('账户') + ":", size=(70, -1))
        choices = self.users if self.users else ["admin"]
        self.user_choice = wx.Choice(panel, choices=choices, size=(200, -1))
        if "admin" in choices:
            self.user_choice.SetStringSelection("admin")
        else:
            self.user_choice.SetSelection(0)
        user_sizer.Add(self.user_label, flag=wx.ALIGN_CENTER_VERTICAL)
        user_sizer.Add(self.user_choice, flag=wx.LEFT, border=10)
        main_sizer.Add(user_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=10)
        
        # 密码
        pwd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pwd_label = wx.StaticText(panel, label=get_text('密码') + ":", size=(70, -1))
        self.pwd_text = wx.TextCtrl(panel, size=(200, -1), style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        pwd_sizer.Add(self.pwd_label, flag=wx.ALIGN_CENTER_VERTICAL)
        pwd_sizer.Add(self.pwd_text, flag=wx.LEFT, border=10)
        main_sizer.Add(pwd_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=30)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=15)
        
        # 按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.register_btn = AquaButton(panel, label=get_text('注册'), size=(100, 35))
        self.login_btn = AquaButton(panel, label=get_text('登录'), size=(100, 35))
        self.cancel_btn = AquaButton(panel, label=get_text('取消'), size=(100, 35))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.register_btn, self.login_btn, self.cancel_btn]:
            btn.SetForegroundColour(btn_fg)

        self.register_btn.Bind(wx.EVT_BUTTON, self.on_register)
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.pwd_text.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        
        btn_sizer.Add(self.register_btn)
        btn_sizer.Add(self.login_btn, flag=wx.LEFT, border=10)
        btn_sizer.Add(self.cancel_btn, flag=wx.LEFT, border=10)
        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER)
        main_sizer.Add(wx.StaticText(panel, label=""), flag=wx.EXPAND, border=10)
        
        # 状态栏
        self.status_text = wx.StaticText(panel, label=f"{get_text('默认账户')}：admin，{get_text('密码')}：123456")
        self.status_text.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(self.status_text, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        panel.SetSizer(main_sizer)
        
        self.pwd_text.SetFocus()
    
    def on_language_change(self, event):
        """切换语言"""
        lang_keys = list(LANGUAGES.keys())
        selected_lang = lang_keys[self.lang_choice.GetSelection()]
        
        # 更新当前语言
        self.current_lang = selected_lang
        
        # 设置语言并保存到配置文件
        set_language(selected_lang)
        config.set_language(selected_lang)
        
        # 刷新界面
        self.refresh_ui()
    
    def on_theme_change(self, event):
        """切换主题"""
        theme_keys = list(THEMES.keys())
        selected_theme = theme_keys[self.theme_choice.GetSelection()]
        
        # 保存主题到配置文件
        config.set_theme(selected_theme)
        
        # 应用主题
        wx.CallAfter(self.apply_theme)
    
    def refresh_ui(self):
        """刷新界面文字"""
        try:
            # 检查窗口是否有效
            if not self or not self.IsShown():
                return
            
            # 直接使用 self.current_lang 获取翻译
            lang = self.current_lang
            
            self.SetTitle(get_text('家庭记账系统', lang) + " v0.2 - " + get_text('登录', lang))
            self.title.SetLabel(get_text('家庭记账系统', lang))
            self.user_label.SetLabel(get_text('账户', lang) + ":")
            self.pwd_label.SetLabel(get_text('密码', lang) + ":")
            
            # 更新按钮标签
            self.login_btn.SetLabel(get_text('登录', lang))
            self.register_btn.SetLabel(get_text('注册', lang))
            self.cancel_btn.SetLabel(get_text('取消', lang))
            
            # 刷新按钮
            self.login_btn.Refresh()
            self.register_btn.Refresh()
            self.cancel_btn.Refresh()
            
            self.status_text.SetLabel(get_text('默认账户', lang) + "：admin，" + get_text('密码', lang) + "：123456")
            
            # 更新语言下拉列表选择
            lang_keys = list(LANGUAGES.keys())
            self.lang_choice.SetSelection(lang_keys.index(self.current_lang))
            
            # 更新主题下拉列表
            if self.current_lang == 'en_US':
                theme_names = [theme['name_en'] for theme in THEMES.values()]
            else:
                theme_names = [theme['name'] for theme in THEMES.values()]
            self.theme_choice.Set(theme_names)
            theme_keys = list(THEMES.keys())
            current_theme = config.get_theme()
            if current_theme in theme_keys:
                self.theme_choice.SetSelection(theme_keys.index(current_theme))
            
            # 强制重新布局
            self.Layout()
        except Exception as e:
            pass
    
    def on_login(self, event):
        """登录按钮事件"""
        username = self.user_choice.GetStringSelection()
        password = self.pwd_text.GetValue()
        
        if not username or not password:
            wx.MessageBox(get_text('账户和密码不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        user = self.db.verify_user(username, password)
        if user:
            # 移除语言监听器
            remove_language_listener(self.on_language_changed)
            self.user = user
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(get_text('账户或密码错误'), get_text('错误'), wx.OK | wx.ICON_ERROR)
            self.pwd_text.SetValue("")
            self.pwd_text.SetFocus()
    
    def on_register(self, event):
        """注册按钮事件"""
        from register import RegisterDialog
        dlg = RegisterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            wx.MessageBox(get_text('注册成功'), get_text('提示'), wx.OK | wx.ICON_INFORMATION)
            self.users = self.get_all_users()
            self.user_choice.Set(self.users)
            if dlg.username in self.users:
                self.user_choice.SetStringSelection(dlg.username)
            self.pwd_text.SetValue("")
        dlg.Destroy()
    
    def on_cancel(self, event):
        """取消按钮事件"""
        # 移除语言监听器
        remove_language_listener(self.on_language_changed)
        self.EndModal(wx.ID_CANCEL)
    
    def get_user(self):
        """获取登录用户"""
        return self.user


if __name__ == "__main__":
    print(LoginDialog().ShowModal())
