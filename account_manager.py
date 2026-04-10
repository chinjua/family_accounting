# -*- coding: utf-8 -*-
"""
账户管理模块 - 处理收支记录的增删改查
"""
import wx
import wx.grid as gridlib
import wx.adv as wxadv
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text, add_language_listener, remove_language_listener, get_current_language
from i18n_support import LanguageSupportMixin
from theme import get_theme, apply_theme_to_grid, get_button_colors, add_theme_listener





class AccountDialog(wx.Dialog, LanguageSupportMixin):
    """账户记录对话框（添加/编辑）"""

    def __init__(self, parent=None, user_id=None, account=None, db=None):
        self.user_id = user_id
        self.account = account
        self.db = db or Database()

        # 从数据库加载分类、支付方式、经手人
        self.income_cats = self.db.get_income_categories(self.user_id) if self.user_id else []
        self.expense_cats = self.db.get_expense_categories(self.user_id) if self.user_id else []
        self.payment_methods = self.db.get_payment_method_names(self.user_id) if self.user_id else ['现金', '其他']
        self.handler_names = self.db.get_handler_names(self.user_id) if self.user_id else ['其他']

        # 如果数据库为空，使用默认值
        if not self.income_cats:
            self.income_cats = ['工资', '奖金', '投资收益', '兼职', '其他收入']
        if not self.expense_cats:
            self.expense_cats = ['餐饮', '交通', '购物', '医疗', '教育', '娱乐', '住房', '通讯', '其他支出']
        if not self.payment_methods:
            self.payment_methods = ['现金', '微信', '支付宝', '银行卡', '信用卡', '花呗', '白条', '转账', '其他']
        if not self.handler_names:
            self.handler_names = ['爸爸', '妈妈', '爷爷', '奶奶', '孩子', '其他']

        # 根据语言设置窗口宽度
        current_lang = get_current_language()
        if current_lang == 'en_US':
            self.dialog_width = 400
        else:
            self.dialog_width = 360
        self.control_width = 220

        title = get_text('添加') if account else get_text('编辑')
        super().__init__(parent, title=title, size=(self.dialog_width, 380))
        
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

        if account:
            self.load_data()
    
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
        # 更新标题
        title = get_text('编辑') if self.account else get_text('添加')
        self.SetTitle(title)

        # 根据语言更新窗口宽度
        current_lang = get_current_language()
        new_width = 400 if current_lang == 'en_US' else 360

        if new_width != self.dialog_width:
            self.dialog_width = new_width
            self.SetSize((self.dialog_width, 380))

        # 更新标签
        self.date_label.SetLabel(f"{get_text('日期')}:")
        self.type_label.SetLabel(f"{get_text('类型')}:")
        self.type_radio_income.SetLabel(get_text('收入'))
        self.type_radio_expense.SetLabel(get_text('支出'))
        self.amount_label.SetLabel(f"{get_text('金额')}:")
        self.cat_label.SetLabel(f"{get_text('分类')}:")
        self.payment_label.SetLabel(f"{get_text('支付方式')}:")
        self.handler_label.SetLabel(f"{get_text('经手人')}:")
        self.desc_label.SetLabel(f"{get_text('说明')}:")

        # 更新按钮
        self.ok_btn.SetLabel(get_text('确定'))
        self.cancel_btn.SetLabel(get_text('取消'))

        # 刷新布局
        self.Layout()
    
    def init_ui(self):
        """初始化界面"""
        panel = wx.Panel(self)
        self.panel = panel

        # 使用FlexGridSizer实现网格布局
        grid_sizer = wx.FlexGridSizer(rows=7, cols=2, hgap=10, vgap=10)
        
        # 第1行：类型
        self.type_label = wx.StaticText(panel, label=f"{get_text('类型')}:")
        type_panel = wx.Panel(panel)
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.type_radio_income = wx.RadioButton(type_panel, label=get_text('收入'), style=wx.RB_GROUP)
        self.type_radio_expense = wx.RadioButton(type_panel, label=get_text('支出'))
        self.type_radio_income.SetValue(True)
        self.type_radio_income.Bind(wx.EVT_RADIOBUTTON, self.on_type_changed)
        self.type_radio_expense.Bind(wx.EVT_RADIOBUTTON, self.on_type_changed)
        type_sizer.Add(self.type_radio_income)
        type_sizer.Add(self.type_radio_expense, flag=wx.LEFT, border=50)
        type_panel.SetSizer(type_sizer)
        grid_sizer.Add(self.type_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(type_panel, flag=wx.EXPAND)
        
        # 第2行：日期
        self.date_label = wx.StaticText(panel, label=f"{get_text('日期')}:")
        self.date_picker = wxadv.DatePickerCtrl(panel, style=wxadv.DP_DEFAULT)
        grid_sizer.Add(self.date_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.date_picker, flag=wx.EXPAND)

        # 第3行：分类
        self.cat_label = wx.StaticText(panel, label=f"{get_text('分类')}:")
        self.cat_choice = wx.Choice(panel, size=(self.control_width, -1))
        self.update_categories()
        grid_sizer.Add(self.cat_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.cat_choice)

        # 第4行：金额
        self.amount_label = wx.StaticText(panel, label=f"{get_text('金额')}:")
        self.amount_text = wx.TextCtrl(panel, size=(self.control_width, -1))
        grid_sizer.Add(self.amount_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.amount_text)

        # 第5行：支付方式
        self.payment_label = wx.StaticText(panel, label=f"{get_text('支付方式')}:")
        self.payment_choice = wx.Choice(panel, choices=self.payment_methods, size=(self.control_width, -1))
        self.payment_choice.SetSelection(0)  # 默认选择第一个
        grid_sizer.Add(self.payment_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.payment_choice)

        # 第6行：经手人
        self.handler_label = wx.StaticText(panel, label=f"{get_text('经手人')}:")
        self.handler_choice = wx.Choice(panel, size=(self.control_width, -1))
        # 设置经手人列表，默认选择"爸爸"
        self.handler_choice.Set(self.handler_names)
        # 默认选择"爸爸"，如果不在列表中则选择第一个
        if "爸爸" in self.handler_names:
            self.handler_choice.SetStringSelection("爸爸")
        else:
            self.handler_choice.SetSelection(0)
        grid_sizer.Add(self.handler_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.handler_choice)

        # 第7行：说明
        self.desc_label = wx.StaticText(panel, label=f"{get_text('说明')}:")
        self.desc_text = wx.TextCtrl(panel, size=(self.control_width, 60), style=wx.TE_MULTILINE)
        grid_sizer.Add(self.desc_label, flag=wx.ALIGN_TOP)
        grid_sizer.Add(self.desc_text, flag=wx.EXPAND)

        # 按钮
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = AquaButton(btn_panel, label=get_text('确定'), size=(100, 30))
        self.cancel_btn = AquaButton(btn_panel, label=get_text('取消'), size=(100, 30))
        
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
        self.amount_text.SetFocus()
    
    def update_categories(self):
        """更新分类列表"""
        if self.type_radio_income.GetValue():
            self.cat_choice.Set(self.income_cats)
        else:
            self.cat_choice.Set(self.expense_cats)
        self.cat_choice.SetSelection(0)
    
    def on_type_changed(self, event):
        """类型改变时更新分类"""
        self.update_categories()
        event.Skip()
    
    def load_data(self):
        """加载编辑数据"""
        # 设置日期
        date_str = self.account.get('date', '')
        if date_str:
            try:
                date_parts = date_str.split('-')
                if len(date_parts) == 3:
                    year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                    self.date_picker.SetValue(wx.DateTime(day, month - 1, year))
            except:
                pass
        
        if self.account['type'] == '收入':
            self.type_radio_income.SetValue(True)
        else:
            self.type_radio_expense.SetValue(True)
        self.update_categories()
        # 金额格式化为2位小数
        amount = self.account['amount']
        self.amount_text.SetValue(f"{amount:.2f}")
        self.cat_choice.SetStringSelection(self.account.get('category', ''))
        self.desc_text.SetValue(self.account.get('description', ''))
        
        # 设置支付方式
        payment_method = self.account.get('payment_method', '')
        if payment_method:
            # 查找支付方式在列表中的位置
            try:
                idx = self.payment_methods.index(payment_method)
                self.payment_choice.SetSelection(idx)
            except ValueError:
                # 如果不在列表中，默认选择第一个
                self.payment_choice.SetSelection(0)
        else:
            self.payment_choice.SetSelection(0)
        
        # 设置经手人
        handler = self.account.get('handler', '')
        if handler:
            # 查找经手人在列表中的位置
            handler_list = self.handler_choice.GetItems()
            if handler in handler_list:
                self.handler_choice.SetStringSelection(handler)
            else:
                # 如果不在列表中，添加到列表并选中
                self.handler_choice.Append(handler)
                self.handler_choice.SetStringSelection(handler)
        else:
            # 默认选择"爸爸"
            if "爸爸" in self.handler_names:
                self.handler_choice.SetStringSelection("爸爸")
            else:
                self.handler_choice.SetSelection(0)
    
    def on_ok(self, event):
        """确定按钮"""
        try:
            amount = float(self.amount_text.GetValue())
            if amount <= 0:
                wx.MessageBox(get_text('请输入正确的金额'), get_text('提示'), wx.OK | wx.ICON_WARNING)
                return
        except ValueError:
            wx.MessageBox(get_text('金额必须是数字'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        type_ = "收入" if self.type_radio_income.GetValue() else "支出"
        category = self.cat_choice.GetStringSelection()
        desc = self.desc_text.GetValue().strip()
        payment_method = self.payment_choice.GetStringSelection()
        handler = self.handler_choice.GetStringSelection()

        # 使用选择的日期
        date_str = self.date_picker.GetValue().Format('%Y-%m-%d')

        self.result = {
            'type': type_,
            'amount': amount,
            'category': category,
            'description': desc,
            'payment_method': payment_method,
            'handler': handler,
            'date': date_str
        }
        self.EndModal(wx.ID_OK)
    
    def on_cancel(self, event):
        """取消按钮"""
        self.EndModal(wx.ID_CANCEL)
    
    def get_result(self):
        """获取结果"""
        return getattr(self, 'result', None)


class AccountManagePanel(wx.Panel):
    """账户管理面板"""

    def __init__(self, parent, user_id, db):
        super().__init__(parent)
        self.user_id = user_id
        self.db = db
        self.accounts = []
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self.filter_type = 0  # 0=全部, 1=收入, 2=支出
        self.selected_rows = set()  # 记录选中行
        self.date_filter_enabled = False  # 日期筛选是否启用
        self.init_ui()
        self.load_data()
        
        # 添加语言切换监听
        add_language_listener(self.on_language_changed)
    
    def on_language_changed(self):
        """语言切换回调"""
        try:
            if self and not self.IsBeingDeleted():
                wx.CallAfter(self.refresh_labels)
        except:
            pass
    
    def on_panel_click(self, event):
        """点击面板空白处取消选中"""
        # 检查点击位置是否在grid内
        pos = event.GetPosition()
        grid_pos = self.grid.ScreenToClient(self.ScreenToClient(pos))
        
        # 如果点击不在grid内，则取消选中
        if not self.grid.GetRect().Contains(grid_pos):
            self.grid.ClearSelection()
            self.selected_rows = set()
            self.update_stats()
        
        event.Skip()
    
    def apply_theme(self):
        """应用当前主题"""
        theme = get_theme()
        
        # 设置面板背景
        self.SetBackgroundColour(theme['bg_color'])
        
        # 应用到网格
        apply_theme_to_grid(self.grid, theme)
        
        # 刷新
        self.Refresh()
    
    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 顶部筛选栏
        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 类型筛选下拉列表
        self.type_label = wx.StaticText(self, label=get_text('类型') + ':')
        filter_sizer.Add(self.type_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.filter_choice = wx.Choice(self, choices=[get_text('全部'), get_text('收入'), get_text('支出')], size=(80, -1))
        self.filter_choice.SetSelection(0)
        self.filter_choice.Bind(wx.EVT_CHOICE, self.on_filter_type_changed)
        filter_sizer.Add(self.filter_choice, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=15)
        
        # 分隔线
        filter_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), flag=wx.EXPAND | wx.RIGHT, border=15)
        
        # 日期筛选复选框（默认选中）
        self.date_filter_checkbox = wx.CheckBox(self, label=get_text('显示全部'))
        self.date_filter_checkbox.SetValue(True)
        self.date_filter_checkbox.Bind(wx.EVT_CHECKBOX, self.on_date_filter_toggle)
        filter_sizer.Add(self.date_filter_checkbox, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        
        # 开始日期
        self.start_date_label = wx.StaticText(self, label=get_text('开始日期') + ':')
        filter_sizer.Add(self.start_date_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.start_date_picker = wxadv.DatePickerCtrl(self, style=wxadv.DP_DEFAULT)
        self.start_date_picker.Disable()  # 默认禁用
        filter_sizer.Add(self.start_date_picker, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        
        # 结束日期
        self.end_date_label = wx.StaticText(self, label=get_text('结束日期') + ':')
        filter_sizer.Add(self.end_date_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        self.end_date_picker = wxadv.DatePickerCtrl(self, style=wxadv.DP_DEFAULT)
        self.end_date_picker.SetValue(wx.DateTime.Now())  # 默认为今天
        self.end_date_picker.Disable()  # 默认禁用
        filter_sizer.Add(self.end_date_picker, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        
        # 筛选按钮
        self.filter_btn = AquaButton(self, label=get_text('筛选'), size=(60, 25))
        self.filter_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.filter_btn.Bind(wx.EVT_BUTTON, self.on_filter_by_date)
        self.filter_btn.Disable()  # 默认禁用
        filter_sizer.Add(self.filter_btn, flag=wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(filter_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Grid表格
        self.grid = gridlib.Grid(self)
        self.grid.CreateGrid(0, 7)
        self.grid.SetColLabelValue(0, get_text('日期'))
        self.grid.SetColLabelValue(1, get_text('类型'))
        self.grid.SetColLabelValue(2, get_text('分类'))
        self.grid.SetColLabelValue(3, get_text('金额'))
        self.grid.SetColLabelValue(4, get_text('支付方式'))
        self.grid.SetColLabelValue(5, get_text('经手人'))
        self.grid.SetColLabelValue(6, get_text('说明'))

        # 启用列自动调整
        self.grid.EnableDragColSize(True)

        # 只读模式
        self.grid.EnableEditing(False)
        self.grid.SetSelectionMode(gridlib.Grid.SelectRows)

        # 绑定窗口大小变化事件，自动调整列宽
        self.Bind(wx.EVT_SIZE, self.on_size)

        # 绑定单元格双击事件，打开编辑窗口
        self.grid.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.on_grid_double_click)

        # 绑定选择事件，统计选中行
        self.grid.Bind(gridlib.EVT_GRID_SELECT_CELL, self.on_grid_selection_changed)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # 点击空白处取消选中
        self.Bind(wx.EVT_LEFT_DOWN, self.on_panel_click)

        main_sizer.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.RIGHT | wx.TOP, border=10)
        
        # 底部栏：分页居中
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 总记录数（左侧）
        self.total_text = wx.StaticText(self, label="共 0 条记录")
        bottom_sizer.Add(self.total_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        # 伸缩器
        bottom_sizer.AddStretchSpacer()
        
        # 分页控件（居中）
        pager_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 首页按钮
        self.first_btn = AquaButton(self, label=get_text('首页'), size=(50, 25))
        self.first_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.first_btn.Bind(wx.EVT_BUTTON, self.on_first_page)
        pager_sizer.Add(self.first_btn, flag=wx.ALIGN_CENTER_VERTICAL)
        
        # 上一页按钮
        self.prev_btn = AquaButton(self, label=get_text('上一页'), size=(60, 25))
        self.prev_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_page)
        pager_sizer.Add(self.prev_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=5)
        
        # 页码信息
        self.page_text = wx.StaticText(self, label=f"{get_text('第')} 1 / 1 {get_text('页')}")
        pager_sizer.Add(self.page_text, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=10)
        
        # 下一页按钮
        self.next_btn = AquaButton(self, label=get_text('下一页'), size=(60, 25))
        self.next_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next_page)
        pager_sizer.Add(self.next_btn, flag=wx.ALIGN_CENTER_VERTICAL)
        
        # 末页按钮
        self.last_btn = AquaButton(self, label=get_text('末页'), size=(50, 25))
        self.last_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.last_btn.Bind(wx.EVT_BUTTON, self.on_last_page)
        pager_sizer.Add(self.last_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=5)

        # 跳转控件
        self.page_input = wx.TextCtrl(self, size=(50, 25), style=wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.page_input.Bind(wx.EVT_TEXT_ENTER, self.on_jump_page)
        pager_sizer.Add(self.page_input, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=15)
        self.jump_btn = AquaButton(self, label="跳转", size=(45, 25))
        self.jump_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.jump_btn.Bind(wx.EVT_BUTTON, self.on_jump_page)
        pager_sizer.Add(self.jump_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        
        bottom_sizer.Add(pager_sizer)
        
        # 伸缩器
        bottom_sizer.AddStretchSpacer()
        
        main_sizer.Add(bottom_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        self.SetSizer(main_sizer)
    
    def on_filter_type_changed(self, event):
        """类型筛选变化"""
        self.filter_type = self.filter_choice.GetSelection()
        self.current_page = 1
        self.load_data()
    
    def on_date_filter_toggle(self, event):
        """切换日期筛选状态"""
        checked = self.date_filter_checkbox.GetValue()
        self.date_filter_enabled = not checked  # 复选框选中时禁用日期筛选
        
        # 更新日期选择器和筛选按钮的启用状态
        self.start_date_picker.Enable(not checked)
        self.end_date_picker.Enable(not checked)
        self.filter_btn.Enable(not checked)
        self.start_date_label.Enable(not checked)
        self.end_date_label.Enable(not checked)
        
        # 重新加载数据
        self.current_page = 1
        self.load_data()
    
    def on_filter_by_date(self, event):
        """按日期筛选"""
        self.current_page = 1
        self.load_data()
    
    def apply_filter(self, filter_type):
        """应用筛选"""
        self.filter_type = filter_type
        self.current_page = 1
        self.load_data()

    def load_data(self):
        """加载数据"""
        # 如果启用了日期筛选
        if self.date_filter_enabled and not self.date_filter_checkbox.GetValue():
            start_date = self.start_date_picker.GetValue().Format('%Y-%m-%d')
            end_date = self.end_date_picker.GetValue().Format('%Y-%m-%d')
            
            # 根据筛选类型获取数据
            if self.filter_type == 0:  # 全部
                self.total_count = self.db.get_accounts_count_by_date_range(self.user_id, start_date, end_date)
                self.accounts = self.db.get_accounts_by_date_range(self.user_id, start_date, end_date, page=self.current_page, page_size=self.page_size)
            elif self.filter_type == 1:  # 收入
                self.total_count = self.db.get_accounts_count_by_date_range_and_type(self.user_id, start_date, end_date, '收入')
                self.accounts = self.db.get_accounts_by_date_range_and_type(self.user_id, start_date, end_date, '收入', page=self.current_page, page_size=self.page_size)
            elif self.filter_type == 2:  # 支出
                self.total_count = self.db.get_accounts_count_by_date_range_and_type(self.user_id, start_date, end_date, '支出')
                self.accounts = self.db.get_accounts_by_date_range_and_type(self.user_id, start_date, end_date, '支出', page=self.current_page, page_size=self.page_size)
        else:
            # 根据筛选类型获取数据
            if self.filter_type == 0:  # 全部
                self.total_count = self.db.get_accounts_count(self.user_id)
                self.accounts = self.db.get_accounts(self.user_id, page=self.current_page, page_size=self.page_size)
            elif self.filter_type == 1:  # 收入
                self.total_count = self.db.get_accounts_count_by_type(self.user_id, '收入')
                self.accounts = self.db.get_accounts_by_type(self.user_id, '收入', page=self.current_page, page_size=self.page_size)
            elif self.filter_type == 2:  # 支出
                self.total_count = self.db.get_accounts_count_by_type(self.user_id, '支出')
                self.accounts = self.db.get_accounts_by_type(self.user_id, '支出', page=self.current_page, page_size=self.page_size)

        self.refresh_grid()
        self.update_stats()
        self.update_pager()
    
    def refresh_grid(self):
        """刷新表格"""
        # 清空选中行状态
        self.selected_rows = set()
        self.grid.ClearSelection()
        
        # 清空数据
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        
        # 强制设置表头颜色为黑色文字白色背景
        # 先设置背景为白色，再设置文字为黑色
        self.grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
        self.grid.SetLabelTextColour(wx.Colour(0, 0, 0))

        # 设置颜色
        green = wx.Colour(0, 128, 0) # 绿色-收入
        red = wx.Colour(220, 0, 0) # 红色-支出

        # 添加数据
        for idx, acc in enumerate(self.accounts):
            self.grid.AppendRows(1)
            row = idx

            acc_type = acc['type']
            row_color = green if acc_type == '收入' else red

            self.grid.SetCellValue(row, 0, acc['date'])
            self.grid.SetCellValue(row, 1, acc_type)
            self.grid.SetCellValue(row, 2, acc.get('category') or '')
            self.grid.SetCellValue(row, 3, f"{acc['amount']:.2f}")
            # 支付方式如果为空则显示空，经手人如果为空则显示"爸爸"
            payment = acc.get('payment_method') or ''
            handler = acc.get('handler') or '爸爸'
            self.grid.SetCellValue(row, 4, payment)
            self.grid.SetCellValue(row, 5, handler)
            self.grid.SetCellValue(row, 6, acc.get('description') or '')

            # 设置整行颜色
            for col in range(7):
                self.grid.SetCellTextColour(row, col, row_color)
            
            # 设置对齐方式：金额右对齐，说明左对齐，其他居中
            align_left = wx.ALIGN_LEFT
            align_center = wx.ALIGN_CENTER
            align_right = wx.ALIGN_RIGHT
            
            for col in [0, 1, 2, 4, 5]:
                self.grid.SetCellAlignment(row, col, align_center, wx.ALIGN_CENTER)
            self.grid.SetCellAlignment(row, 3, align_right, wx.ALIGN_CENTER)  # 金额右对齐
            self.grid.SetCellAlignment(row, 6, align_left, wx.ALIGN_CENTER)   # 说明
        
        # 强制刷新表格以恢复表头颜色
        self.grid.ForceRefresh()
    
    def update_stats(self):
        """更新统计（根据当前筛选条件）"""
        # 检查数据库是否已关闭
        try:
            if not hasattr(self.db, 'conn') or self.db.conn is None:
                return
            # 尝试执行一个简单的查询来检查连接是否有效
            self.db.cursor.execute("SELECT 1")
        except:
            return
        
        # 根据筛选类型和日期范围获取统计
        if self.date_filter_enabled and not self.date_filter_checkbox.GetValue():
            # 日期筛选 + 类型筛选
            start_date = self.start_date_picker.GetValue().Format('%Y-%m-%d')
            end_date = self.end_date_picker.GetValue().Format('%Y-%m-%d')
            
            if self.filter_type == 0:  # 全部
                stats = self.db.get_statistics_by_date_range(self.user_id, start_date, end_date)
            elif self.filter_type == 1:  # 收入
                income = self.db.get_statistics_by_date_range_and_type(self.user_id, start_date, end_date, '收入')
                stats = {'income': income, 'expense': 0, 'balance': income}
            elif self.filter_type == 2:  # 支出
                expense = self.db.get_statistics_by_date_range_and_type(self.user_id, start_date, end_date, '支出')
                stats = {'income': 0, 'expense': expense, 'balance': -expense}
        else:
            # 仅类型筛选（全部/收入/支出）
            if self.filter_type == 0:  # 全部
                stats = self.db.get_statistics(self.user_id)
            elif self.filter_type == 1:  # 收入
                income = self.db.get_statistics_by_type(self.user_id, '收入')
                stats = {'income': income, 'expense': 0, 'balance': income}
            elif self.filter_type == 2:  # 支出
                expense = self.db.get_statistics_by_type(self.user_id, '支出')
                stats = {'income': 0, 'expense': expense, 'balance': -expense}
        
        # 更新状态栏
        self.update_status_bar(stats['income'], stats['expense'], stats['balance'])
    
    def update_status_bar(self, income, expense, balance):
        """更新主窗口状态栏的统计信息"""
        # 获取主窗口
        parent = self.GetParent()
        while parent and not isinstance(parent, wx.Frame):
            parent = parent.GetParent()
        
        if parent and isinstance(parent, wx.Frame):
            parent.SetStatusText(f"{get_text('收入')}: ¥{income:.2f}", 1)
            parent.SetStatusText(f"{get_text('支出')}: ¥{expense:.2f}", 2)
            parent.SetStatusText(f"{get_text('结余')}: ¥{balance:.2f}", 3)
    
    def refresh_labels(self):
        """刷新标签文字"""
        try:
            # 更新 grid 列标题
            self.grid.SetColLabelValue(0, get_text('日期'))
            self.grid.SetColLabelValue(1, get_text('类型'))
            self.grid.SetColLabelValue(2, get_text('分类'))
            self.grid.SetColLabelValue(3, get_text('金额'))
            self.grid.SetColLabelValue(4, get_text('支付方式'))
            self.grid.SetColLabelValue(5, get_text('经手人'))
            self.grid.SetColLabelValue(6, get_text('说明'))

            # 强制刷新grid以显示新的列标题
            self.grid.ForceRefresh()
            
            # 更新筛选栏标签
            self.type_label.SetLabel(get_text('类型') + ':')
            self.date_filter_checkbox.SetLabel(get_text('显示全部'))
            self.start_date_label.SetLabel(get_text('开始日期') + ':')
            self.end_date_label.SetLabel(get_text('结束日期') + ':')
            self.filter_btn.SetLabel(get_text('筛选'))
            self.filter_choice.SetItems([get_text('全部'), get_text('收入'), get_text('支出')])
            self.filter_choice.SetSelection(self.filter_type)

            # 更新统计和分页
            self.update_stats()
            self.update_pager()

            # 更新分页按钮
            self.first_btn.SetLabel(get_text('首页'))
            self.prev_btn.SetLabel(get_text('上一页'))
            self.next_btn.SetLabel(get_text('下一页'))
            self.last_btn.SetLabel(get_text('末页'))
            self.jump_btn.SetLabel("跳转")

            # 刷新整个面板
            self.Refresh()
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def on_size(self, event):
        """窗口大小变化时自动调整列宽"""
        event.Skip()
        wx.CallAfter(self.auto_size_columns)
    
    def auto_size_columns(self):
        """自动调整列宽以填满整个grid，不使用水平滚动条"""
        if not self.grid:
            return
        
        # 获取grid的可见宽度
        grid_width = self.grid.GetClientSize().width
        
        # 可用宽度（减去边距）
        available_width = max(grid_width - 5, 100)
        
        if available_width <= 0:
            return
        
        # 列宽比例（基于内容重要性和典型长度）
        # 0:日期, 1:类型, 2:分类, 3:金额, 4:支付方式, 5:经手人, 6:说明
        col_ratios = [10, 6, 12, 14, 16, 12, 30]  # 总计100份
        
        # 计算每列宽度
        total_ratio = sum(col_ratios)
        unit_width = available_width / total_ratio
        
        for i, ratio in enumerate(col_ratios):
            col_width = int(unit_width * ratio)
            # 设置最小宽度确保可读性
            min_widths = [80, 50, 60, 80, 80, 60, 100]
            col_width = max(col_width, min_widths[i])
            self.grid.SetColSize(i, col_width)
        
        # 禁用水平滚动条
        self.grid.SetScrollLineX(0)
        
        # 强制刷新
        self.grid.ForceRefresh()

    def update_pager(self):
        """更新分页控件"""
        total_pages = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.page_text.SetLabel(f"{get_text('第')} {self.current_page} / {total_pages} {get_text('页')}")
        self.total_text.SetLabel(f"{get_text('共')} {self.total_count} {get_text('条记录')}")
        self.page_input.SetValue(str(self.current_page))
        
        # 更新按钮状态
        self.first_btn.Enable(self.current_page > 1)
        self.prev_btn.Enable(self.current_page > 1)
        self.next_btn.Enable(self.current_page < total_pages)
        self.last_btn.Enable(self.current_page < total_pages)
    
    def on_first_page(self, event):
        """首页"""
        self.current_page = 1
        self.load_data()
    
    def on_prev_page(self, event):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()
    
    def on_next_page(self, event):
        """下一页"""
        total_pages = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_data()
    
    def on_last_page(self, event):
        """末页"""
        self.current_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.load_data()
    
    def on_jump_page(self, event):
        """跳转页面"""
        try:
            page = int(self.page_input.GetValue())
            total_pages = max(1, (self.total_count + self.page_size - 1) // self.page_size)
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages
            self.current_page = page
            self.load_data()
        except ValueError:
            wx.MessageBox("请输入有效的页码", "提示", wx.OK | wx.ICON_WARNING)
    
    def on_add(self, event):
        """添加记录"""
        dlg = AccountDialog(self, self.user_id, db=self.db)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_result()
            success, msg = self.db.add_account(
                user_id=self.user_id,
                name=data['category'],
                type_=data['type'],
                amount=data['amount'],
                category=data['category'],
                description=data['description'],
                date=data['date'],
                payment_method=data.get('payment_method', ''),
                handler=data.get('handler', '')
            )
            if success:
                self.load_data()
            else:
                wx.MessageBox(msg, "错误", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_edit(self, event):
        """编辑记录"""
        selected_rows = self.grid.GetSelectedRows()
        if not selected_rows:
            wx.MessageBox("请选择要编辑的记录", "提示", wx.OK | wx.ICON_WARNING)
            return

        row = selected_rows[0]
        if row >= len(self.accounts):
            return

        account = self.accounts[row]
        dlg = AccountDialog(self, self.user_id, account, self.db)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.get_result()
            success, msg = self.db.update_account(
                account_id=account['id'],
                user_id=self.user_id,
                name=data['category'],
                type_=data['type'],
                amount=data['amount'],
                category=data['category'],
                description=data['description'],
                date=data['date'],
                payment_method=data.get('payment_method', ''),
                handler=data.get('handler', '')
            )
            if success:
                self.load_data()
            else:
                wx.MessageBox(msg, "错误", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()
    
    def on_delete(self, event):
        """删除记录"""
        selected_rows = self.grid.GetSelectedRows()
        if not selected_rows:
            wx.MessageBox(get_text('请选择要删除的记录'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return

        count = len(selected_rows)
        confirm_msg = f"{get_text('确定要删除选中的')} {count} {get_text('条记录吗')}?\n{get_text('删除后可在回收站中恢复')}."
        
        if wx.MessageBox(confirm_msg, get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            deleted_count = 0
            for row in selected_rows:
                if row < len(self.accounts):
                    account_id = self.accounts[row]['id']
                    success, msg = self.db.soft_delete_account(account_id, self.user_id)
                    if success:
                        deleted_count += 1
            
            if deleted_count > 0:
                self.load_data()
                # 自动刷新回收站
                self.refresh_recycle_bin()
                wx.MessageBox(f"{get_text('成功删除')} {deleted_count} {get_text('条记录')}", get_text('提示'), wx.OK | wx.ICON_INFORMATION)

    def refresh_recycle_bin(self):
        """刷新回收站（通知主窗口）"""
        # 获取主窗口
        parent = self.GetParent()
        while parent and not hasattr(parent, 'recycle_panel'):
            parent = parent.GetParent()
        
        # 如果找到主窗口，刷新回收站
        if parent and hasattr(parent, 'recycle_panel'):
            parent.recycle_panel.load_data()
    
    def on_refresh(self, event):
        """刷新"""
        self.load_data()
    
    def on_grid_selection_changed(self, event):
        """网格选择变化时更新选中行统计"""
        self.update_selected_rows_stats()
        event.Skip()
    
    def on_key_down(self, event):
        """键盘按键处理"""
        # Ctrl+A 全选所有行
        if event.ControlDown() and event.GetKeyCode() == 65:  # 65 is 'A'
            self.select_all_rows()
        else:
            # 延迟更新，等待选择完成
            wx.CallAfter(self.update_selected_rows_stats)
        event.Skip()
    
    def select_all_rows(self):
        """选中所有行"""
        if self.accounts:
            # 清除当前选择
            self.grid.ClearSelection()
            # 选中所有行
            for row in range(len(self.accounts)):
                self.grid.SelectRow(row, True)
            # 更新统计
            wx.CallAfter(self.update_selected_rows_stats)
    
    def update_selected_rows_stats(self):
        """更新选中行的统计"""
        selected_rows = self.grid.GetSelectedRows()
        
        if not selected_rows:
            # 无选中行，显示总体统计
            self.update_stats()
            return
        
        # 统计选中行的金额
        selected_income = 0.0
        selected_expense = 0.0
        
        for row in selected_rows:
            if row < len(self.accounts):
                acc = self.accounts[row]
                amount = acc.get('amount', 0)
                if acc.get('type') == '收入':
                    selected_income += amount
                else:
                    selected_expense += amount
        
        selected_balance = selected_income - selected_expense
        selected_count = len(selected_rows)
        
        # 更新状态栏
        self.update_status_bar(selected_income, selected_expense, selected_balance)
    
    def on_grid_double_click(self, event):
        """双击表格行打开编辑窗口"""
        row = event.GetRow()
        if row >= 0 and row < len(self.accounts):
            self.on_edit(event)
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    db = Database()
    panel = AccountManagePanel(frame, user_id=1, db=db)
    frame.Show()
    app.MainLoop()
