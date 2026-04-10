# -*- coding: utf-8 -*-
"""
设置模块 - 管理分类、支付方式、经手人等配置
"""
import wx
import wx.grid as gridlib
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text, add_language_listener
from theme import get_theme, add_theme_listener


class SettingsDialog(wx.Dialog):
    """设置对话框"""
    
    def __init__(self, parent=None, user_id=None, db=None):
        self.user_id = user_id
        self.db = db or Database()
        
        super().__init__(parent, title=get_text('设置'), size=(550, 400))
        
        # 设置窗口图标
        try:
            self.SetIcon(wx.Icon("family_accounting.png", wx.BITMAP_TYPE_PNG))
        except:
            pass
        
        # 禁止最大化最小化按钮
        self.SetWindowStyle(self.GetWindowStyle() & ~(wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
        
        self.init_ui()
        
        # 添加语言切换监听
        add_language_listener(self.on_language_changed)
        # 添加主题切换监听
        add_theme_listener(self.on_theme_changed)
        # 应用主题
        self.apply_theme()
    
    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建Notebook
        self.notebook = wx.Notebook(panel)
        
        # 收入分类页面
        self.income_panel = self.create_category_panel(self.notebook, '收入')
        self.notebook.AddPage(self.income_panel, get_text('收入分类'))
        
        # 支出分类页面
        self.expense_panel = self.create_category_panel(self.notebook, '支出')
        self.notebook.AddPage(self.expense_panel, get_text('支出分类'))
        
        # 支付方式页面
        self.payment_panel = self.create_list_panel(self.notebook, 'payment')
        self.notebook.AddPage(self.payment_panel, get_text('支付方式'))
        
        # 经手人页面
        self.handler_panel = self.create_list_panel(self.notebook, 'handler')
        self.notebook.AddPage(self.handler_panel, get_text('经手人'))
        
        # 绑定Notebook页面切换事件
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        
        # 创建上移下移按钮面板（放在右侧，垂直居中）
        self.move_btn_panel = wx.Panel(panel)
        move_sizer = wx.BoxSizer(wx.VERTICAL)
        self.move_up_btn = AquaButton(self.move_btn_panel, label=get_text('上移'), size=(60, 30))
        self.move_up_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.move_up_btn.Bind(wx.EVT_BUTTON, self.on_move_up)
        move_sizer.Add(self.move_up_btn, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.move_down_btn = AquaButton(self.move_btn_panel, label=get_text('下移'), size=(60, 30))
        self.move_down_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.move_down_btn.Bind(wx.EVT_BUTTON, self.on_move_down)
        move_sizer.Add(self.move_down_btn, flag=wx.EXPAND)
        self.move_btn_panel.SetSizer(move_sizer)
        
        # 使用BoxSizer实现水平布局，按钮垂直居中
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        # 将按钮面板添加到sizer，设置垂直居中对齐
        content_sizer.Add(self.move_btn_panel, flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        
        main_sizer.Add(content_sizer, proportion=1, flag=wx.EXPAND)
        
        # 关闭按钮
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.close_btn = AquaButton(panel, label=get_text('关闭'), size=(100, 30))
        self.close_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.close_btn)
        main_sizer.Add(btn_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        panel.SetSizer(main_sizer)
        self.Centre()
    
    def on_page_changed(self, event):
        """Notebook页面切换"""
        event.Skip()
    
    def get_current_panel(self):
        """获取当前选中的面板"""
        index = self.notebook.GetSelection()
        return self.notebook.GetPage(index)
    
    def on_move_up(self, event):
        """上移当前面板中的选中项"""
        panel = self.get_current_panel()
        if hasattr(panel, 'categories'):
            self.on_move_category_up(panel)
        elif hasattr(panel, 'items'):
            self.on_move_item_up(panel)
    
    def on_move_down(self, event):
        """下移当前面板中的选中项"""
        panel = self.get_current_panel()
        if hasattr(panel, 'categories'):
            self.on_move_category_down(panel)
        elif hasattr(panel, 'items'):
            self.on_move_item_down(panel)
    
    def create_category_panel(self, parent, category_type):
        """创建分类管理面板"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 在面板上存储数据和控件引用
        panel.categories = []  # 存储 (id, name) 列表
        panel.category_type = category_type  # 存储类型
        panel.list_box = wx.ListBox(panel)
        panel.text_ctrl = wx.TextCtrl(panel, size=(50, -1))
        
        # 加载数据
        self._load_categories_to_panel(panel, category_type)
        
        # 绑定事件
        panel.list_box.Bind(wx.EVT_LISTBOX, self.on_category_select)
        sizer.Add(panel.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        # 输入框和按钮
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.text_ctrl.SetSizeHints(150, -1)
        
        add_btn = AquaButton(panel, label=get_text('添加'), size=(60, 28))
        add_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        add_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_add_category(p))
        edit_btn = AquaButton(panel, label=get_text('修改'), size=(60, 28))
        edit_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        edit_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_edit_category(p))
        delete_btn = AquaButton(panel, label=get_text('删除'), size=(60, 28))
        delete_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        delete_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_delete_category(p))
        
        input_sizer.Add(panel.text_ctrl, proportion=1, flag=wx.RIGHT, border=5)
        input_sizer.Add(add_btn, flag=wx.RIGHT, border=3)
        input_sizer.Add(edit_btn, flag=wx.RIGHT, border=3)
        input_sizer.Add(delete_btn)
        sizer.Add(input_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)
        return panel
    
    def create_list_panel(self, parent, list_type):
        """创建列表管理面板（支付方式、经手人）"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 在面板上存储数据和控件引用
        panel.items = []  # 存储 (id, name) 列表
        panel.list_type = list_type  # 存储类型
        panel.list_box = wx.ListBox(panel)
        panel.text_ctrl = wx.TextCtrl(panel, size=(50, -1))
        
        # 加载数据
        self._load_list_to_panel(panel, list_type)
        
        # 绑定事件
        panel.list_box.Bind(wx.EVT_LISTBOX, self.on_list_select)
        sizer.Add(panel.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        # 输入框和按钮
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.text_ctrl.SetSizeHints(150, -1)
        
        add_btn = AquaButton(panel, label=get_text('添加'), size=(60, 28))
        add_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        add_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_add_item(p))
        edit_btn = AquaButton(panel, label=get_text('修改'), size=(60, 28))
        edit_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        edit_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_edit_item(p))
        delete_btn = AquaButton(panel, label=get_text('删除'), size=(60, 28))
        delete_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        delete_btn.Bind(wx.EVT_BUTTON, lambda e, p=panel: self.on_delete_item(p))
        
        input_sizer.Add(panel.text_ctrl, proportion=1, flag=wx.RIGHT, border=5)
        input_sizer.Add(add_btn, flag=wx.RIGHT, border=3)
        input_sizer.Add(edit_btn, flag=wx.RIGHT, border=3)
        input_sizer.Add(delete_btn)
        sizer.Add(input_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)
        return panel
    
    def _load_categories_to_panel(self, panel, category_type):
        """加载分类到面板"""
        panel.categories = self.db.get_categories(self.user_id, category_type)
        panel.list_box.Clear()
        for cat in panel.categories:
            panel.list_box.Append(cat['name'])
    
    def _load_list_to_panel(self, panel, list_type):
        """加载列表到面板"""
        if list_type == 'payment':
            panel.items = self.db.get_payment_methods(self.user_id)
        else:
            panel.items = self.db.get_handlers(self.user_id)
        panel.list_box.Clear()
        for item in panel.items:
            panel.list_box.Append(item['name'])
    
    def load_categories(self, category_type):
        """加载分类列表（兼容方法）"""
        if category_type == '收入':
            self._load_categories_to_panel(self.income_panel, category_type)
        else:
            self._load_categories_to_panel(self.expense_panel, category_type)
    
    def load_list(self, list_type):
        """加载列表（兼容方法）"""
        if list_type == 'payment':
            self._load_list_to_panel(self.payment_panel, list_type)
        else:
            self._load_list_to_panel(self.handler_panel, list_type)
    
    def on_category_select(self, event):
        """选中分类"""
        # 找到事件发生的面板
        panel = event.GetEventObject().GetParent()
        selection = panel.list_box.GetSelection()
        if selection >= 0:
            panel.text_ctrl.SetValue(panel.list_box.GetString(selection))
    
    def on_list_select(self, event):
        """选中列表项"""
        # 找到事件发生的面板
        panel = event.GetEventObject().GetParent()
        selection = panel.list_box.GetSelection()
        if selection >= 0:
            panel.text_ctrl.SetValue(panel.list_box.GetString(selection))
    
    def on_add_category(self, panel):
        """添加分类"""
        name = panel.text_ctrl.GetValue().strip()
        if not name:
            wx.MessageBox(get_text('名称不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 保存到数据库
        success, msg = self.db.add_category(self.user_id, name, panel.category_type)
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_categories_to_panel(panel, panel.category_type)
        panel.text_ctrl.SetValue('')
    
    def on_edit_category(self, panel):
        """修改分类"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        name = panel.text_ctrl.GetValue().strip()
        if not name:
            wx.MessageBox(get_text('名称不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 获取要修改的分类ID
        cat_id = panel.categories[selection]['id']
        
        # 更新数据库
        success, msg = self.db.update_category(cat_id, name)
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_categories_to_panel(panel, panel.category_type)
        panel.text_ctrl.SetValue('')
    
    def on_delete_category(self, panel):
        """删除分类"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        # 获取要删除的分类名称
        cat_name = panel.list_box.GetString(selection)
        
        # 确认删除
        confirm_msg = f"{get_text('确定要删除')} '{cat_name}' {get_text('吗')}?"
        if wx.MessageBox(confirm_msg, get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        
        # 获取要删除的分类ID
        cat_id = panel.categories[selection]['id']
        
        # 从数据库删除
        success, msg = self.db.delete_category(cat_id)
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_categories_to_panel(panel, panel.category_type)
        panel.text_ctrl.SetValue('')
    
    def on_move_category_up(self, panel):
        """将分类上移"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        if selection == 0:
            return  # 已在最上端
        
        cat_id = panel.categories[selection]['id']
        success, msg = self.db.move_category_up(self.user_id, cat_id, panel.category_type)
        if success:
            self._load_categories_to_panel(panel, panel.category_type)
            # 选中新位置
            panel.list_box.SetSelection(selection - 1)
    
    def on_move_category_down(self, panel):
        """将分类下移"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        if selection >= len(panel.categories) - 1:
            return  # 已在最下端
        
        cat_id = panel.categories[selection]['id']
        success, msg = self.db.move_category_down(self.user_id, cat_id, panel.category_type)
        if success:
            self._load_categories_to_panel(panel, panel.category_type)
            # 选中新位置
            panel.list_box.SetSelection(selection + 1)
    
    def on_add_item(self, panel):
        """添加列表项"""
        name = panel.text_ctrl.GetValue().strip()
        if not name:
            wx.MessageBox(get_text('名称不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 保存到数据库
        if panel.list_type == 'payment':
            success, msg = self.db.add_payment_method(self.user_id, name)
        else:
            success, msg = self.db.add_handler(self.user_id, name)
        
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_list_to_panel(panel, panel.list_type)
        panel.text_ctrl.SetValue('')
    
    def on_edit_item(self, panel):
        """修改列表项"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        name = panel.text_ctrl.GetValue().strip()
        if not name:
            wx.MessageBox(get_text('名称不能为空'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 获取要修改的ID
        item_id = panel.items[selection]['id']
        
        if panel.list_type == 'payment':
            success, msg = self.db.update_payment_method(item_id, name)
        else:
            success, msg = self.db.update_handler(item_id, name)
        
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_list_to_panel(panel, panel.list_type)
        panel.text_ctrl.SetValue('')
    
    def on_delete_item(self, panel):
        """删除列表项"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        # 获取要删除的项名称
        item_name = panel.list_box.GetString(selection)
        
        # 确认删除
        confirm_msg = f"{get_text('确定要删除')} '{item_name}' {get_text('吗')}?"
        if wx.MessageBox(confirm_msg, get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        
        # 获取要删除的ID
        item_id = panel.items[selection]['id']
        
        if panel.list_type == 'payment':
            success, msg = self.db.delete_payment_method(item_id)
        else:
            success, msg = self.db.delete_handler(item_id)
        
        if not success:
            wx.MessageBox(msg, get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        # 重新加载列表
        self._load_list_to_panel(panel, panel.list_type)
        panel.text_ctrl.SetValue('')
    
    def on_move_item_up(self, panel):
        """将列表项上移"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        if selection == 0:
            return  # 已在最上端
        
        item_id = panel.items[selection]['id']
        
        if panel.list_type == 'payment':
            success, msg = self.db.move_payment_method_up(self.user_id, item_id)
        else:
            success, msg = self.db.move_handler_up(self.user_id, item_id)
        
        if success:
            self._load_list_to_panel(panel, panel.list_type)
            # 选中新位置
            panel.list_box.SetSelection(selection - 1)
    
    def on_move_item_down(self, panel):
        """将列表项下移"""
        selection = panel.list_box.GetSelection()
        if selection < 0:
            return
        
        if selection >= len(panel.items) - 1:
            return  # 已在最下端
        
        item_id = panel.items[selection]['id']
        
        if panel.list_type == 'payment':
            success, msg = self.db.move_payment_method_down(self.user_id, item_id)
        else:
            success, msg = self.db.move_handler_down(self.user_id, item_id)
        
        if success:
            self._load_list_to_panel(panel, panel.list_type)
            # 选中新位置
            panel.list_box.SetSelection(selection + 1)
    
    def on_language_changed(self):
        """语言切换回调"""
        if not self or not self.IsShown():
            return
        wx.CallAfter(self.refresh_labels)
    
    def refresh_labels(self):
        """刷新界面文字"""
        self.SetTitle(get_text('设置'))
        self.notebook.SetPageText(0, get_text('收入分类'))
        self.notebook.SetPageText(1, get_text('支出分类'))
        self.notebook.SetPageText(2, get_text('支付方式'))
        self.notebook.SetPageText(3, get_text('经手人'))
        self.close_btn.SetLabel(get_text('关闭'))
    
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
        apply_theme_to_window(self, config.get_theme())
        self.Refresh()
    
    def on_close(self, event):
        """关闭"""
        self.EndModal(wx.ID_CLOSE)
