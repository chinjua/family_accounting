# -*- coding: utf-8 -*-
"""
主窗口模块 - 应用程序主界面
"""
import wx
import wx.adv
import webbrowser
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from account_manager import AccountManagePanel
from recycle_bin import RecycleBinPanel
from import_export import ImportExportPanel
from statistics import StatisticsPanel
from user_manager import UserManageDialog, ChangeOwnPasswordDialog
from i18n import LANGUAGES, get_text, set_language, get_current_language, add_language_listener, remove_language_listener
from config_manager import config
from theme import THEMES, add_theme_listener, remove_theme_listener, apply_theme_to_window, apply_theme_to_grid, get_theme, notify_theme_changed


class PasswordConfirmDialog(wx.Dialog):
    """密码确认对话框"""
    
    def __init__(self, parent, username, users=None):
        super().__init__(parent, title=get_text('确认身份'), size=(350, 190))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.current_username = username
        self.users = users or [username]
        
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 账户名下拉列表
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_label = wx.StaticText(panel, label=f"{get_text('账户')}:")
        self.user_choice = wx.Choice(panel, choices=self.users, size=(200, -1))
        self.user_choice.SetStringSelection(username)
        self.user_choice.Bind(wx.EVT_CHOICE, self.on_user_changed)
        user_sizer.Add(user_label, flag=wx.ALIGN_CENTER_VERTICAL)
        user_sizer.Add(self.user_choice, flag=wx.LEFT, border=10)
        main_sizer.Add(user_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=15)
        
        # 提示
        self.hint = wx.StaticText(panel, label=f"{get_text('请输入账户')} '{username}' {get_text('的密码')}")
        main_sizer.Add(self.hint, flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        
        # 密码输入
        self.pwd_text = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        
        # 添加语言切换监听
        from i18n import add_language_listener
        add_language_listener(self.on_language_changed)
        main_sizer.Add(self.pwd_text, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        
        # 按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = AquaButton(panel, label=get_text('确定'), size=(80, 30))
        self.cancel_btn = AquaButton(panel, label=get_text('取消'), size=(80, 30))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.ok_btn, self.cancel_btn]:
            btn.SetForegroundColour(btn_fg)
        
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.pwd_text.Bind(wx.EVT_TEXT_ENTER, self.on_ok)
        
        btn_sizer.Add(self.ok_btn)
        btn_sizer.Add(self.cancel_btn, flag=wx.LEFT, border=20)
        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        panel.SetSizer(main_sizer)
        self.pwd_text.SetFocus()
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
        theme = get_theme()
        self.SetBackgroundColour(theme['bg_color'])
        # 递归应用主题到所有控件（包括按钮）
        apply_theme_to_window(self, config.get_theme())
        self.Refresh()
    
    def on_user_changed(self, event):
        """切换账户名时更新提示"""
        selected_user = self.user_choice.GetStringSelection()
        self.hint.SetLabel(f"{get_text('请输入账户')} '{selected_user}' {get_text('的密码')}")
        self.pwd_text.SetValue("")
        self.pwd_text.SetFocus()
    
    def on_language_changed(self):
        """语言切换回调"""
        try:
            if self and self.IsShown():
                self.SetTitle(get_text('确认身份'))
                user_label = self.GetChildren()[0].GetChildren()[0]  # user_label
                user_label.SetLabel(f"{get_text('账户')}:")
                self.hint.SetLabel(f"{get_text('请输入账户')} '{self.user_choice.GetStringSelection()}' {get_text('的密码')}")
                self.ok_btn.SetLabel(get_text('确定'))
                self.cancel_btn.SetLabel(get_text('取消'))
                self.Layout()
        except:
            pass
    
    def on_ok(self, event):
        self.EndModal(wx.ID_OK)
    
    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
    
    def get_username(self):
        return self.user_choice.GetStringSelection()
    
    def get_password(self):
        return self.pwd_text.GetValue()


class MainFrame(wx.Frame):
    """主窗口"""

    def __init__(self, user):
        # 加载保存的语言设置
        saved_lang = config.get_language()
        if saved_lang in LANGUAGES:
            set_language(saved_lang)
        
        self.current_lang = get_current_language()
        title = f"{get_text('家庭记账系统')} v0.1 - {user['username']}"
        super().__init__(None, title=title, size=(1000, 650))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.user = user
        self.db = Database()
        self.user_id = user['id']
        
        self.init_ui()
        self.Centre()
        
        # 添加语言切换监听
        add_language_listener(self.on_language_changed)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def on_language_changed(self):
        """语言切换回调"""
        if not self or not self.IsShown():
            return
        self.current_lang = get_current_language()
        wx.CallAfter(self.refresh_ui)
    
    def init_ui(self):
        """初始化界面"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏（3列：账户信息、收入、支出、结余）
        self.CreateStatusBar(4)
        self.SetStatusWidths([-2, -1, -1, -1])
        self.SetStatusText(f"{get_text('当前账户')}: {self.user['username']}", 0)
        self.SetStatusText("", 1)
        self.SetStatusText("", 2)
        self.SetStatusText("", 3)
        
        # 创建面板
        panel = wx.Panel(self)
        self.panel = panel
        
        # 顶部工具栏（按钮 + 语言选择）
        toolbar = wx.Panel(panel)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 添加、编辑、删除按钮（左侧）
        self.add_btn = AquaButton(toolbar, label=get_text('添加'), size=(90, 30))
        self.edit_btn = AquaButton(toolbar, label=get_text('编辑'), size=(90, 30))
        self.refresh_btn = AquaButton(toolbar, label=get_text('刷新'), size=(90, 30))
        self.delete_btn = AquaButton(toolbar, label=get_text('删除'), size=(90, 30))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.add_btn, self.edit_btn, self.refresh_btn, self.delete_btn]:
            btn.SetForegroundColour(btn_fg)

        toolbar_sizer.Add(self.add_btn)
        toolbar_sizer.Add(self.edit_btn, flag=wx.LEFT, border=10)
        toolbar_sizer.Add(self.refresh_btn, flag=wx.LEFT, border=10)
        toolbar_sizer.Add(self.delete_btn, flag=wx.LEFT, border=10)
        
        toolbar.SetSizer(toolbar_sizer)
        
        # 绑定按钮事件
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_record_from_toolbar)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit_record_from_toolbar)
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh_selection)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_record_from_toolbar)
        
        # 使用Notebook实现标签页
        self.notebook = wx.Notebook(panel)
        
        # 绑定Notebook页面切换事件
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_page_changed)
        
        # 收支记录页面
        self.account_panel = AccountManagePanel(self.notebook, self.user_id, self.db)
        self.notebook.AddPage(self.account_panel, get_text('收支记录'))
        
        # 延迟更新状态栏统计，确保UI完全初始化
        wx.CallAfter(self.account_panel.update_stats)
        
        # 统计页面
        self.statistics_panel = StatisticsPanel(self.notebook, self.user_id, self.db)
        self.notebook.AddPage(self.statistics_panel, get_text('统计分析'))
        
        # 回收站页面
        self.recycle_panel = RecycleBinPanel(self.notebook, self.user_id, self.db)
        self.notebook.AddPage(self.recycle_panel, get_text('回收站'))
        
        # 导入导出页面
        self.import_export_panel = ImportExportPanel(self.notebook, self.user_id, self.db)
        self.notebook.AddPage(self.import_export_panel, get_text('导入导出'))
        
        # 布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(toolbar, flag=wx.EXPAND | wx.ALL, border=5)
        main_sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)
        panel.SetSizer(main_sizer)
        
        self.SetMinSize((950, 600))
        
        # 应用保存的主题
        self.apply_theme()
    
    def apply_theme(self):
        """应用当前主题到所有控件"""
        from theme import apply_theme_to_control, apply_theme_to_window
        theme = get_theme()
        
        # 应用到主窗口
        self.SetBackgroundColour(theme['bg_color'])
        self.panel.SetBackgroundColour(theme['bg_color'])
        
        # 应用到工具栏
        toolbar = self.panel.GetChildren()[0]
        toolbar.SetBackgroundColour(theme['toolbar_bg'])
        
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
        
        # 刷新所有控件
        self.Refresh()
        self.panel.Refresh()
        
        # 通知所有面板应用主题
        for panel in [self.account_panel, self.statistics_panel, self.recycle_panel, self.import_export_panel]:
            if panel and hasattr(panel, 'apply_theme'):
                panel.apply_theme()
        
        # 触发主题切换回调
        from theme import notify_theme_changed
        notify_theme_changed(config.get_theme())
    
    def refresh_ui(self):
        """刷新界面文字"""
        try:
            # 更新标题
            self.SetTitle(f"{get_text('家庭记账系统')} v0.1 - {self.user['username']}")

            # 更新状态栏
            self.SetStatusText(f"{get_text('当前账户')}: {self.user['username']}")

            # 更新工具栏按钮
            self.add_btn.SetLabel(get_text('添加'))
            self.edit_btn.SetLabel(get_text('编辑'))
            self.refresh_btn.SetLabel(get_text('刷新'))
            self.delete_btn.SetLabel(get_text('删除'))

            # 更新标签页
            self.notebook.SetPageText(0, get_text('收支记录'))
            self.notebook.SetPageText(1, get_text('统计分析'))
            self.notebook.SetPageText(2, get_text('回收站'))
            self.notebook.SetPageText(3, get_text('导入导出'))

            # 安全地更新菜单栏
            if self.menubar:
                # 解绑所有菜单事件，避免在销毁时出错
                self.SetMenuBar(None)
                self.menubar.Destroy()
                self.create_menu_bar()

            # 更新所有面板的标签
            if self.account_panel and not self.account_panel.IsBeingDeleted():
                self.account_panel.refresh_labels()
            if self.recycle_panel and not self.recycle_panel.IsBeingDeleted():
                self.recycle_panel.refresh_labels()
            if self.statistics_panel and not self.statistics_panel.IsBeingDeleted():
                self.statistics_panel.refresh_labels()
            if self.import_export_panel and not self.import_export_panel.IsBeingDeleted():
                self.import_export_panel.refresh_labels()

            # 刷新布局
            self.Layout()
            self.Refresh()
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        self.menubar = wx.MenuBar()
        
        # 定义图标尺寸
        icon_size = (16, 16)
        
        # 文件菜单
        file_menu = wx.Menu()
        import_item = wx.MenuItem(file_menu, wx.ID_ANY, f"{get_text('导入数据')}\tCtrl+I")
        import_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, icon_size))
        file_menu.Append(import_item)
        self.Bind(wx.EVT_MENU, self.on_import_data, import_item)
        
        export_item = wx.MenuItem(file_menu, wx.ID_ANY, f"{get_text('导出数据')}\tCtrl+G")
        export_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU, icon_size))
        file_menu.Append(export_item)
        self.Bind(wx.EVT_MENU, self.on_export_data, export_item)
        
        file_menu.AppendSeparator()
        
        restart_item = wx.MenuItem(file_menu, wx.ID_ANY, f"{get_text('重启')}\tCtrl+R")
        restart_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU, icon_size))
        file_menu.Append(restart_item)
        self.Bind(wx.EVT_MENU, self.on_restart, restart_item)
        
        file_menu.AppendSeparator()
        
        exit_item = wx.MenuItem(file_menu, wx.ID_EXIT, f"{get_text('退出')}\tCtrl+Q")
        exit_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, icon_size))
        file_menu.Append(exit_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.menubar.Append(file_menu, get_text('文件'))
        
        # 记录菜单
        record_menu = wx.Menu()
        add_item = wx.MenuItem(record_menu, wx.ID_ADD, f"{get_text('添加记录')}\tCtrl+N")
        add_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU, icon_size))
        record_menu.Append(add_item)
        self.Bind(wx.EVT_MENU, self.on_add_record, add_item)
        
        edit_item = wx.MenuItem(record_menu, wx.ID_EDIT, f"{get_text('编辑记录')}\tCtrl+E")
        edit_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_MENU, icon_size))
        record_menu.Append(edit_item)
        self.Bind(wx.EVT_MENU, self.on_edit_record, edit_item)
        
        delete_item = wx.MenuItem(record_menu, wx.ID_DELETE, f"{get_text('删除记录')}\tCtrl+D")
        delete_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU, icon_size))
        record_menu.Append(delete_item)
        self.Bind(wx.EVT_MENU, self.on_delete_record, delete_item)
        self.menubar.Append(record_menu, get_text('记录'))
        
        # 视图菜单
        view_menu = wx.Menu()
        stats_item = wx.MenuItem(view_menu, wx.ID_ANY, f"{get_text('统计分析')}\tCtrl+S")
        stats_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, wx.ART_MENU, icon_size))
        view_menu.Append(stats_item)
        self.Bind(wx.EVT_MENU, self.on_show_statistics, stats_item)
        self.menubar.Append(view_menu, get_text('视图'))
        
        # 管理账户菜单
        account_menu = wx.Menu()
        logout_item = wx.MenuItem(account_menu, wx.ID_ANY, f"{get_text('切换账户')}\tCtrl+L")
        logout_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_MENU, icon_size))
        account_menu.Append(logout_item)
        self.Bind(wx.EVT_MENU, self.on_logout, logout_item)
        
        change_pwd_item = wx.MenuItem(account_menu, wx.ID_ANY, f"{get_text('修改密码')}\tCtrl+P")
        change_pwd_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_MENU, icon_size))
        account_menu.Append(change_pwd_item)
        self.Bind(wx.EVT_MENU, self.on_change_password, change_pwd_item)
        
        # 只有管理员显示账户管理功能
        if self.db.is_admin(self.user_id):
            account_menu.AppendSeparator()
            manage_users_item = wx.MenuItem(account_menu, wx.ID_ANY, f"{get_text('账户管理')}...\tCtrl+U")
            manage_users_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, icon_size))
            account_menu.Append(manage_users_item)
            self.Bind(wx.EVT_MENU, self.on_manage_users, manage_users_item)
        
        self.menubar.Append(account_menu, get_text('管理账户'))
        
        # 设置菜单
        settings_menu = wx.Menu()
        settings_item = wx.MenuItem(settings_menu, wx.ID_ANY, f"{get_text('设置')}...")
        settings_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_MENU, icon_size))
        settings_menu.Append(settings_item)
        self.Bind(wx.EVT_MENU, self.on_settings, settings_item)
        self.menubar.Append(settings_menu, get_text('设置'))
        
        # 帮助菜单
        help_menu = wx.Menu()
        
        helpmanual_item = wx.MenuItem(help_menu, wx.ID_ANY, f"{get_text('操作手册')}\tF1")
        helpmanual_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, icon_size))
        help_menu.Append(helpmanual_item)
        self.Bind(wx.EVT_MENU, self.on_help_manual, helpmanual_item)
        
        about_item = wx.MenuItem(help_menu, wx.ID_ABOUT, f"{get_text('关于')}\tF2")
        about_item.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, icon_size))
        help_menu.Append(about_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.menubar.Append(help_menu, get_text('帮助'))
        
        self.SetMenuBar(self.menubar)
    
    def refresh_accounts(self):
        """刷新账户数据"""
        if hasattr(self, 'account_panel'):
            self.account_panel.load_data()
        if hasattr(self, 'statistics_panel'):
            self.statistics_panel.load_data()

    def on_notebook_page_changed(self, event):
        """Notebook页面切换时"""
        event.Skip()
    
    def on_add_record(self, event):
        """添加记录"""
        self.notebook.SetSelection(0)
        self.account_panel.on_add(None)
    
    def on_show_statistics(self, event):
        """显示统计"""
        self.notebook.SetSelection(1)
    
    def on_logout(self, event):
        """切换账户"""
        # 获取所有用户列表
        users = self.get_all_users()
        
        # 弹出密码确认对话框
        dlg = PasswordConfirmDialog(self, self.user['username'], users)
        if dlg.ShowModal() == wx.ID_OK:
            username = dlg.get_username()
            password = dlg.get_password()
            # 验证密码
            if self.db.verify_user(username, password):
                # 密码正确，获取新用户信息
                new_user = self.db.get_user_by_username(username)
                if new_user:
                    # 更新当前用户和用户ID
                    self.user = new_user
                    self.user_id = new_user['id']
                    # 更新各面板的用户ID和数据库引用
                    self.account_panel.user_id = self.user_id
                    self.account_panel.db = self.db
                    self.statistics_panel.user_id = self.user_id
                    self.statistics_panel.db = self.db
                    self.recycle_panel.user_id = self.user_id
                    self.recycle_panel.db = self.db
                    self.import_export_panel.user_id = self.user_id
                    self.import_export_panel.db = self.db
                    # 刷新界面
                    self.SetTitle(f"{get_text('家庭记账系统')} v0.1 - {new_user['username']}")
                    self.SetStatusText(f"{get_text('当前账户')}: {self.user['username']}", 0)
                    self.refresh_accounts()
                    wx.MessageBox(f"{get_text('已切换到账户')}: {username}", get_text('提示'), wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(get_text('密码错误'), get_text('错误'), wx.OK | wx.ICON_ERROR)
        dlg.Destroy()
    
    def get_all_users(self):
        """获取所有用户列表"""
        try:
            self.db.cursor.execute("SELECT username FROM users ORDER BY id")
            return [row[0] for row in self.db.cursor.fetchall()]
        except:
            return []
    
    def on_import_data(self, event):
        """导入数据"""
        from import_export import ImportDialog
        dlg = ImportDialog(self, self.user_id, self.db)
        if dlg.ShowModal() == wx.ID_OK:
            self.refresh_accounts()
        dlg.Destroy()
    
    def on_export_data(self, event):
        """导出数据"""
        from import_export import ExportDialog
        dlg = ExportDialog(self, self.user_id, self.db)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_restart(self, event):
        """重启程序"""
        if wx.MessageBox(get_text('确定要重启程序吗'), get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            # 设置标志位，跳过关闭确认
            self._is_restarting = True
            # 关闭数据库
            self.db.close()
            # 关闭窗口（不触发确认对话框）
            self.Destroy()
            # 使用subprocess重启程序
            import subprocess
            import sys
            subprocess.Popen([sys.executable, 'main.py'])
            # 退出当前应用
            wx.GetApp().ExitMainLoop()
    
    def on_exit(self, event):
        """退出"""
        self.Close()
    
    def on_help_manual(self, event):
        """操作手册"""
        import os
        # 尝试打开HTML手册
        html_path = "MANUAL.html"
        if os.path.exists(html_path):
            try:
                import webbrowser
                webbrowser.open(os.path.abspath(html_path))
                return
            except:
                pass
        
        wx.MessageBox("找不到操作手册文件", get_text('提示'), wx.OK | wx.ICON_WARNING)
    
    def on_about(self, event):
        """关于"""
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_change_password(self, event):
        """修改密码"""
        dlg = ChangeOwnPasswordDialog(self, user_id=self.user_id, 
                                     username=self.user['username'], db=self.db)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_manage_users(self, event):
        """账户管理（管理员）"""
        dlg = UserManageDialog(self, user_id=self.user_id, db=self.db)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_settings(self, event):
        """打开设置窗口"""
        from settings import SettingsDialog
        dlg = SettingsDialog(self, self.user_id, self.db)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_add_record_from_toolbar(self, event):
        """工具栏添加记录"""
        self.notebook.SetSelection(0)
        self.account_panel.on_add(None)
    
    def on_edit_record_from_toolbar(self, event):
        """工具栏编辑记录"""
        self.notebook.SetSelection(0)
        self.account_panel.on_edit(None)
    
    def on_refresh_selection(self, event):
        """刷新（取消选中收支记录和回收站的记录）"""
        # 取消收支记录表格的选中
        if hasattr(self, 'account_panel'):
            self.account_panel.grid.ClearSelection()
            self.account_panel.selected_rows = set()
            self.account_panel.update_stats()
        
        # 取消回收站表格的选中
        if hasattr(self, 'recycle_panel'):
            self.recycle_panel.grid.ClearSelection()
            self.recycle_panel.update_stats()
    
    def on_delete_record_from_toolbar(self, event):
        """工具栏删除记录"""
        # 先切换到收支记录标签页
        self.notebook.SetSelection(0)
        self.account_panel.on_delete(None)
    
    def on_edit_record(self, event):
        """菜单编辑记录"""
        self.notebook.SetSelection(0)
        self.account_panel.on_edit(None)
    
    def on_delete_record(self, event):
        """菜单删除记录"""
        self.notebook.SetSelection(0)
        self.account_panel.on_delete(None)
    
    def on_close(self, event):
        """关闭"""
        # 如果正在重启，跳过确认
        if getattr(self, '_is_restarting', False):
            event.Skip()
            return
        if wx.MessageBox(get_text('确定要退出吗'), get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            self.db.close()
            event.Skip()
        else:
            event.Veto()


class MainApp(wx.App):
    """应用程序"""
    
    def OnInit(self):
        from login import LoginDialog
        
        dlg = LoginDialog()
        if dlg.ShowModal() == wx.ID_OK:
            user = dlg.get_user()
            dlg.Destroy()
            
            if user:
                frame = MainFrame(user)
                frame.Show()
                return True
            else:
                return False
        else:
            dlg.Destroy()
            return False


class AboutDialog(wx.Dialog):
    """关于对话框"""
    
    def __init__(self, parent):
        super().__init__(parent, title=get_text('关于'), size=(450, 400))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        # 禁止最大化最小化按钮
        self.SetWindowStyle(self.GetWindowStyle() & ~(wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
        
        # 添加主题切换监听
        add_theme_listener(self.on_theme_changed)
        # 应用主题
        self.apply_theme()
        
        panel = wx.Panel(self)
        self.panel = panel
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 程序图标和名称
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 程序图标（缩小尺寸）
        try:
            self.logo_bitmap = wx.Bitmap("family_accounting.png", wx.BITMAP_TYPE_PNG)
            # 缩小图标尺寸
            self.logo_bitmap = self.logo_bitmap.GetSubBitmap(wx.Rect(0, 0, min(48, self.logo_bitmap.GetWidth()), min(48, self.logo_bitmap.GetHeight())))
            self.logo = wx.StaticBitmap(panel, bitmap=self.logo_bitmap)
        except:
            self.logo = wx.StaticBitmap(panel)
        header_sizer.Add(self.logo, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=15)
        
        # 程序名称
        name_sizer = wx.BoxSizer(wx.VERTICAL)
        title_label = wx.StaticText(panel, label=get_text('家庭记账系统'))
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_label.SetFont(title_font)
        name_sizer.Add(title_label, flag=wx.LEFT, border=10)
        
        version_label = wx.StaticText(panel, label="版本 0.1")
        version_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        version_label.SetFont(version_font)
        name_sizer.Add(version_label, flag=wx.LEFT, border=10)
        
        header_sizer.Add(name_sizer, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(header_sizer, flag=wx.EXPAND | wx.ALL, border=15)
        
        # Notebook组件
        self.notebook = wx.Notebook(panel)
        
# 作者页
        author_panel = wx.Panel(self.notebook)
        author_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 作者信息
        author_label = wx.StaticText(author_panel, label="\n作者：天涯客")
        author_sizer.Add(author_label, flag=wx.LEFT | wx.TOP, border=10)
        
        # Email
        email_label = wx.StaticText(author_panel, label="Email：774667285@qq.com")
        author_sizer.Add(email_label, flag=wx.LEFT | wx.TOP, border=10)
        
        # 博客链接（可点击）
        blog_sizer = wx.BoxSizer(wx.HORIZONTAL)
        blog_label = wx.StaticText(author_panel, label="博客：")
        blog_sizer.Add(blog_label, flag=wx.ALIGN_CENTER_VERTICAL)
        
        blog_url = "https://www.chinjua.com.cn/"
        try:
            blog_link = wx.adv.HyperlinkCtrl(author_panel, wx.ID_ANY, "https://www.chinjua.com.cn/", blog_url)
        except:
            blog_link = wx.Button(author_panel, label="https://www.chinjua.com.cn/")
            blog_link.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(blog_url))
        blog_sizer.Add(blog_link, flag=wx.LEFT, border=5)
        author_sizer.Add(blog_sizer, flag=wx.LEFT | wx.TOP, border=10)
        
        # 项目地址链接（可点击）
        project_sizer = wx.BoxSizer(wx.HORIZONTAL)
        project_label = wx.StaticText(author_panel, label="项目地址：")
        project_sizer.Add(project_label, flag=wx.ALIGN_CENTER_VERTICAL)
        
        project_url = "https://github.com/chinjua/family_accounting"
        try:
            project_link = wx.adv.HyperlinkCtrl(author_panel, wx.ID_ANY, "https://github.com/chinjua/family_accounting", project_url)
        except:
            project_link = wx.Button(author_panel, label="https://github.com/chinjua/family_accounting")
            project_link.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open(project_url))
        project_sizer.Add(project_link, flag=wx.LEFT, border=5)
        author_sizer.Add(project_sizer, flag=wx.LEFT | wx.TOP, border=10)
        
        author_panel.SetSizer(author_sizer)
        self.notebook.AddPage(author_panel, get_text('作者'))
        
        # 协议页
        license_panel = wx.Panel(self.notebook)
        license_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 协议文本框（不可编辑）
        self.license_text = wx.TextCtrl(license_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP, size=(400, 250))
        license_sizer.Add(self.license_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        license_panel.SetSizer(license_sizer)
        self.notebook.AddPage(license_panel, get_text('协议'))
        
        # 加载LICENSE文件
        self.load_license_file()
        
        # 更新页
        update_panel = wx.Panel(self.notebook)
        update_sizer = wx.BoxSizer(wx.VERTICAL)
        update_text = wx.StaticText(update_panel, label="\n2026-04-10 v0.1版发布")
        update_sizer.Add(update_text, flag=wx.ALL, border=10)
        update_panel.SetSizer(update_sizer)
        self.notebook.AddPage(update_panel, get_text('更新'))
        
        # 添加i18n支持
        from i18n import add_language_listener
        add_language_listener(self.on_language_changed)
        
        main_sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=15)
        
        # 关闭按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_btn = AquaButton(panel, label=get_text('关闭'), size=(80, 30))
        close_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.Add(close_btn, flag=wx.ALIGN_CENTER)
        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
        
        panel.SetSizer(main_sizer)
        self.Centre()
    
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
        self.Refresh()
    
    def on_close(self, event):
        """关闭"""
        self.EndModal(wx.ID_OK)
    
    def load_license_file(self):
        """加载LICENSE文件"""
        try:
            with open("LICENSE.txt", "r", encoding="utf-8") as f:
                content = f.read()
            self.license_text.SetValue(content)
        except FileNotFoundError:
            self.license_text.SetValue("LICENSE.txt 文件未找到")
        except Exception as e:
            self.license_text.SetValue(f"加载 LICENSE.txt 失败: {str(e)}")
    
    def on_language_changed(self):
        """语言切换回调"""
        try:
            self.notebook.SetPageText(0, get_text('作者'))
            self.notebook.SetPageText(1, get_text('协议'))
            self.notebook.SetPageText(2, get_text('更新'))
            self.close_btn.SetLabel(get_text('关闭'))
            self.Refresh()
        except:
            pass


if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()
