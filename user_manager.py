# -*- coding: utf-8 -*-
"""
用户管理模块 - 处理账户管理功能
管理员(admin)可修改所有账户密码、删除非管理员账户
普通用户只能修改自身密码
"""
import wx
import wx.grid as gridlib
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text
from i18n_support import LanguageSupportMixin
from theme import get_theme, add_theme_listener


class ChangePasswordDialog(wx.Dialog, LanguageSupportMixin):
    """修改密码对话框"""

    def __init__(self, parent=None, user_id=None, username=None, db=None, is_admin=False):
        self.user_id = user_id
        self.username = username
        self.db = db or Database()
        self.is_admin = is_admin

        title = f"{get_text('修改密码')} - {username}" if username else get_text('修改密码')
        super().__init__(parent, title=title, size=(350, 170))
        
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
        title = f"{get_text('修改密码')} - {self.username}" if self.username else get_text('修改密码')
        self.SetTitle(title)
        self.pwd_label.SetLabel(f"{get_text('新密码')}:")
        self.confirm_label.SetLabel(f"{get_text('确认密码')}:")
        self.ok_btn.SetLabel(get_text('确定'))
        self.cancel_btn.SetLabel(get_text('取消'))
        self.Layout()

    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)

        # 使用FlexGridSizer实现网格布局
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=10, vgap=10)

        # 新密码
        self.pwd_label = wx.StaticText(panel, label=f"{get_text('新密码')}:")
        self.pwd_text = wx.TextCtrl(panel, size=(180, -1), style=wx.TE_PASSWORD)
        grid_sizer.Add(self.pwd_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.pwd_text)

        # 确认密码
        self.confirm_label = wx.StaticText(panel, label=f"{get_text('确认密码')}:")
        self.confirm_text = wx.TextCtrl(panel, size=(180, -1), style=wx.TE_PASSWORD)
        grid_sizer.Add(self.confirm_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.confirm_text)

        # 按钮
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = AquaButton(btn_panel, label=get_text('确定'), size=(90, 30))
        self.cancel_btn = AquaButton(btn_panel, label=get_text('取消'), size=(90, 30))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.ok_btn, self.cancel_btn]:
            btn.SetForegroundColour(btn_fg)
        
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(self.ok_btn)
        btn_sizer.Add(self.cancel_btn, flag=wx.LEFT, border=20)
        btn_panel.SetSizer(btn_sizer)

        # 主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(grid_sizer, flag=wx.ALL, border=15)
        main_sizer.Add(btn_panel, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(main_sizer)
        self.pwd_text.SetFocus()

    def on_ok(self, event):
        """确定"""
        password = self.pwd_text.GetValue()
        confirm = self.confirm_text.GetValue()

        if len(password) < 6:
            wx.MessageBox(get_text('密码至少6个字符'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        if password != confirm:
            wx.MessageBox(get_text('两次输入的密码不一致'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        if self.is_admin and self.username:
            # 管理员修改其他用户密码
            success, msg = self.db.change_password_by_username(self.username, password)
        else:
            # 修改自己的密码
            success, msg = self.db.change_password(self.user_id, password)

        if success:
            wx.MessageBox(msg, get_text('成功'), wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(msg, get_text('错误'), wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event):
        """取消"""
        self.EndModal(wx.ID_CANCEL)


class UserManageDialog(wx.Dialog, LanguageSupportMixin):
    """用户管理对话框（管理员专用）"""

    def __init__(self, parent=None, user_id=None, db=None):
        self.user_id = user_id
        self.db = db or Database()
        self.users = []

        super().__init__(parent, title=get_text('账户管理'), size=(500, 350))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.init_ui()
        self.setup_language_listener()
        self.load_data()
        
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
        self.SetTitle(get_text('账户管理'))
        self.hint.SetLabel(get_text('管理员可修改所有账户的密码，删除非管理员账户'))

        # 更新列标题
        self.grid.SetColLabelValue(0, get_text('账户'))
        self.grid.SetColLabelValue(1, get_text('创建时间'))
        self.grid.SetColLabelValue(2, get_text('操作'))

        # 更新按钮标签
        self.change_pwd_btn.SetLabel(get_text('修改密码'))
        self.delete_btn.SetLabel(get_text('删除账户'))
        self.close_btn.SetLabel(get_text('关闭'))

        # 刷新表格数据
        self.refresh_grid()

        # 更新按钮
        self.change_pwd_btn.SetLabel(get_text('修改密码'))
        self.delete_btn.SetLabel(get_text('删除账户'))
        self.close_btn.SetLabel(get_text('关闭'))
        self.Layout()

    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 提示
        self.hint = wx.StaticText(panel, label=get_text('管理员可修改所有账户的密码，删除非管理员账户'))
        self.hint.SetForegroundColour(wx.Colour(128, 128, 128))
        main_sizer.Add(self.hint, flag=wx.ALL, border=10)

        # 用户列表
        self.grid = gridlib.Grid(panel)
        self.grid.CreateGrid(0, 3)
        self.grid.SetColLabelValue(0, get_text('账户'))
        self.grid.SetColLabelValue(1, get_text('创建时间'))
        self.grid.SetColLabelValue(2, get_text('操作'))

        self.grid.SetColSize(0, 100)
        self.grid.SetColSize(1, 150)
        self.grid.SetColSize(2, 200)

        self.grid.EnableEditing(False)
        self.grid.SetSelectionMode(gridlib.Grid.SelectRows)

        main_sizer.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        # 按钮栏
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.change_pwd_btn = AquaButton(panel, label=get_text('修改密码'), size=(100, 30))
        self.delete_btn = AquaButton(panel, label=get_text('删除账户'), size=(100, 30))
        self.close_btn = AquaButton(panel, label=get_text('关闭'), size=(80, 30))

        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.change_pwd_btn, self.delete_btn, self.close_btn]:
            btn.SetForegroundColour(btn_fg)

        self.change_pwd_btn.Bind(wx.EVT_BUTTON, self.on_change_password)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_user)
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)

        btn_sizer.Add(self.change_pwd_btn)
        btn_sizer.Add(self.delete_btn, flag=wx.LEFT, border=15)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.close_btn)
        main_sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(main_sizer)
    
    def load_data(self):
        """加载数据"""
        self.users = self.db.get_all_users_info()
        self.refresh_grid()
    
    def refresh_grid(self):
        """刷新表格"""
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        
        for idx, user in enumerate(self.users):
            self.grid.AppendRows(1)
            row = idx
            
            self.grid.SetCellValue(row, 0, user['username'])
            created_at = user['created_at'][:19] if user['created_at'] else ''
            self.grid.SetCellValue(row, 1, created_at)
            
            if user['username'] == 'admin':
                self.grid.SetCellValue(row, 2, "(管理员账户)")
            else:
                self.grid.SetCellValue(row, 2, "")
    
    def on_change_password(self, event):
        """修改密码"""
        selected = self.grid.GetSelectedRows()
        if not selected:
            wx.MessageBox(get_text('请先选择要修改密码的账户'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        row = selected[0]
        if row >= len(self.users):
            return

        user = self.users[row]
        dlg = ChangePasswordDialog(self, user_id=user['id'], username=user['username'],
                                   db=self.db, is_admin=True)
        if dlg.ShowModal() == wx.ID_OK:
            self.load_data()
        dlg.Destroy()

    def on_delete_user(self, event):
        """删除账户"""
        selected = self.grid.GetSelectedRows()
        if not selected:
            wx.MessageBox(get_text('请先选择要删除的账户'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        row = selected[0]
        if row >= len(self.users):
            return

        user = self.users[row]

        if user['username'] == 'admin':
            wx.MessageBox(get_text('不能删除管理员账户'), get_text('错误'), wx.OK | wx.ICON_ERROR)
            return

        msg = f"{get_text('确定要删除账户')} '{user['username']}' {get_text('吗')}?\n{get_text('此操作将同时删除该账户的所有收支记录')}\n{get_text('且不可恢复')}"
        if wx.MessageBox(msg, get_text('危险操作'), wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            success, msg = self.db.delete_user(user['id'], self.user_id)
            if success:
                wx.MessageBox(msg, get_text('成功'), wx.OK | wx.ICON_INFORMATION)
                self.load_data()
            else:
                wx.MessageBox(msg, get_text('错误'), wx.OK | wx.ICON_ERROR)

    def on_close(self, event):
        """关闭"""
        self.EndModal(wx.ID_CLOSE)


class ChangeOwnPasswordDialog(wx.Dialog, LanguageSupportMixin):
    """修改当前用户密码对话框"""

    def __init__(self, parent=None, user_id=None, username=None, db=None):
        self.user_id = user_id
        self.username = username
        self.db = db or Database()

        super().__init__(parent, title=get_text('修改密码'), size=(350, 205))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        self.init_ui()
        self.setup_language_listener()
        self.Centre()
        
        # 添加主题切换监听
        add_theme_listener(self.on_theme_changed_own)
        # 应用主题
        self.apply_theme()
    
    def on_theme_changed_own(self, theme_name):
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
        self.SetTitle(get_text('修改密码'))
        self.old_label.SetLabel(f"{get_text('原密码')}:")
        self.pwd_label.SetLabel(f"{get_text('新密码')}:")
        self.confirm_label.SetLabel(f"{get_text('确认密码')}:")
        self.ok_btn.SetLabel(get_text('确定'))
        self.cancel_btn.SetLabel(get_text('取消'))
        self.Layout()

    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)

        # 使用FlexGridSizer实现网格布局
        grid_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=10, vgap=10)

        # 原密码
        self.old_label = wx.StaticText(panel, label=f"{get_text('原密码')}:")
        self.old_text = wx.TextCtrl(panel, size=(180, -1), style=wx.TE_PASSWORD)
        grid_sizer.Add(self.old_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.old_text)

        # 新密码
        self.pwd_label = wx.StaticText(panel, label=f"{get_text('新密码')}:")
        self.pwd_text = wx.TextCtrl(panel, size=(180, -1), style=wx.TE_PASSWORD)
        grid_sizer.Add(self.pwd_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.pwd_text)

        # 确认密码
        self.confirm_label = wx.StaticText(panel, label=f"{get_text('确认密码')}:")
        self.confirm_text = wx.TextCtrl(panel, size=(180, -1), style=wx.TE_PASSWORD)
        grid_sizer.Add(self.confirm_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.confirm_text)

        # 按钮
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = AquaButton(btn_panel, label=get_text('确定'), size=(90, 30))
        self.cancel_btn = AquaButton(btn_panel, label=get_text('取消'), size=(90, 30))
        
        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.ok_btn, self.cancel_btn]:
            btn.SetForegroundColour(btn_fg)
        
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        btn_sizer.Add(self.ok_btn)
        btn_sizer.Add(self.cancel_btn, flag=wx.LEFT, border=20)
        btn_panel.SetSizer(btn_sizer)

        # 主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(grid_sizer, flag=wx.ALL, border=15)
        main_sizer.Add(btn_panel, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(main_sizer)
        self.old_text.SetFocus()

    def on_ok(self, event):
        """确定"""
        old_password = self.old_text.GetValue()
        password = self.pwd_text.GetValue()
        confirm = self.confirm_text.GetValue()

        # 验证原密码
        if not self.db.verify_user(self.username, old_password):
            wx.MessageBox(get_text('原密码错误'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        if len(password) < 6:
            wx.MessageBox(get_text('密码至少6个字符'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        if password != confirm:
            wx.MessageBox(get_text('两次输入的密码不一致'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        success, msg = self.db.change_password(self.user_id, password)

        if success:
            wx.MessageBox(msg, get_text('成功'), wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(msg, get_text('错误'), wx.OK | wx.ICON_ERROR)

    def on_cancel(self, event):
        """取消"""
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App()
    db = Database()
    
    # 测试用户管理对话框
    frame = wx.Frame(None)
    dlg = UserManageDialog(frame, user_id=1, db=db)
    dlg.ShowModal()
    dlg.Destroy()
    
    app.MainLoop()
