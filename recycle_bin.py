# -*- coding: utf-8 -*-
"""
回收站模块 - 处理已删除记录的恢复和永久删除
"""
import wx
import wx.grid as gridlib
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text, add_language_listener, remove_language_listener
from theme import get_theme, apply_theme_to_grid, get_button_colors





class RecycleBinPanel(wx.Panel):
    """回收站面板"""
    
    def __init__(self, parent, user_id, db):
        super().__init__(parent)
        self.user_id = user_id
        self.db = db
        self.deleted_accounts = []
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self.filter_type = 0  # 0=全部, 1=收入, 2=支出
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
    
    def refresh_labels(self):
        """刷新界面文字"""
        # 更新提示
        self.hint.SetLabel(f"{get_text('以下是已删除的记录')}")
        
        # 更新按钮
        self.restore_btn.SetLabel(get_text('恢复'))
        self.permanent_btn.SetLabel(get_text('永久删除'))
        self.empty_btn.SetLabel(get_text('清空回收站'))
        
        # 更新分页按钮
        self.first_btn.SetLabel(get_text('首页'))
        self.prev_btn.SetLabel(get_text('上一页'))
        self.next_btn.SetLabel(get_text('下一页'))
        self.last_btn.SetLabel(get_text('末页'))
        self.jump_btn.SetLabel(get_text('跳转'))
        
        # 更新列标题
        self.grid.SetColLabelValue(0, get_text('日期'))
        self.grid.SetColLabelValue(1, get_text('类型'))
        self.grid.SetColLabelValue(2, get_text('分类'))
        self.grid.SetColLabelValue(3, get_text('金额'))
        self.grid.SetColLabelValue(4, get_text('支付方式'))
        self.grid.SetColLabelValue(5, get_text('经手人'))
        self.grid.SetColLabelValue(6, get_text('说明'))
        self.grid.SetColLabelValue(7, get_text('删除时间'))
        self.grid.ForceRefresh()
        
        self.update_pager()
        self.Layout()
    
    def apply_filter(self, filter_type):
        """应用筛选"""
        self.filter_type = filter_type
        self.current_page = 1
        self.load_data()
    
    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 提示
        self.hint = wx.StaticText(self, label=f"{get_text('以下是已删除的记录')}")
        self.hint.SetForegroundColour(wx.Colour(128, 128, 128))
        main_sizer.Add(self.hint, flag=wx.ALL, border=10)
        
        # Grid表格
        self.grid = gridlib.Grid(self)
        self.grid.CreateGrid(0, 8)
        self.grid.SetColLabelValue(0, get_text('日期'))
        self.grid.SetColLabelValue(1, get_text('类型'))
        self.grid.SetColLabelValue(2, get_text('分类'))
        self.grid.SetColLabelValue(3, get_text('金额'))
        self.grid.SetColLabelValue(4, get_text('支付方式'))
        self.grid.SetColLabelValue(5, get_text('经手人'))
        self.grid.SetColLabelValue(6, get_text('说明'))
        self.grid.SetColLabelValue(7, get_text('删除时间'))

        self.grid.EnableDragColSize(True)

        self.grid.EnableEditing(False)
        self.grid.SetSelectionMode(gridlib.Grid.SelectRows)
        
        # 绑定窗口大小变化事件
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        # 绑定选择事件，统计选中行
        self.grid.Bind(gridlib.EVT_GRID_SELECT_CELL, self.on_grid_selection_changed)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # 点击空白处取消选中
        self.Bind(wx.EVT_LEFT_DOWN, self.on_panel_click)
        
        main_sizer.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.RIGHT | wx.BOTTOM, border=10)
        
        # 底部栏：按钮 + 分页居中
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 按钮栏（左侧）
        self.restore_btn = AquaButton(self, label=get_text('恢复'), size=(100, 30))
        self.permanent_btn = AquaButton(self, label=get_text('永久删除'), size=(100, 30))
        self.empty_btn = AquaButton(self, label=get_text('清空回收站'), size=(110, 30))

        # 设置按钮文字为黑色
        btn_fg = wx.Colour(0, 0, 0)
        for btn in [self.restore_btn, self.permanent_btn, self.empty_btn]:
            btn.SetForegroundColour(btn_fg)

        self.restore_btn.Bind(wx.EVT_BUTTON, self.on_restore)
        self.permanent_btn.Bind(wx.EVT_BUTTON, self.on_permanent_delete)
        self.empty_btn.Bind(wx.EVT_BUTTON, self.on_empty)

        bottom_sizer.Add(self.restore_btn)
        bottom_sizer.Add(self.permanent_btn, flag=wx.LEFT, border=10)
        bottom_sizer.Add(self.empty_btn, flag=wx.LEFT, border=10)

        # 伸缩器
        bottom_sizer.AddStretchSpacer()
        
        # 分页控件（居中）
        pager_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.first_btn = AquaButton(self, label=get_text('首页'), size=(50, 25))
        self.first_btn.SetForegroundColour(btn_fg)
        self.first_btn.Bind(wx.EVT_BUTTON, self.on_first_page)
        pager_sizer.Add(self.first_btn)
        
        self.prev_btn = AquaButton(self, label=get_text('上一页'), size=(60, 25))
        self.prev_btn.SetForegroundColour(btn_fg)
        self.prev_btn.Bind(wx.EVT_BUTTON, self.on_prev_page)
        pager_sizer.Add(self.prev_btn, flag=wx.LEFT, border=5)
        
        self.page_text = wx.StaticText(self, label=f"{get_text('第')} 1 / 1 {get_text('页')}")
        pager_sizer.Add(self.page_text, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=10)
        
        self.next_btn = AquaButton(self, label=get_text('下一页'), size=(60, 25))
        self.next_btn.SetForegroundColour(btn_fg)
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next_page)
        pager_sizer.Add(self.next_btn)
        
        self.last_btn = AquaButton(self, label=get_text('末页'), size=(50, 25))
        self.last_btn.SetForegroundColour(btn_fg)
        self.last_btn.Bind(wx.EVT_BUTTON, self.on_last_page)
        pager_sizer.Add(self.last_btn, flag=wx.LEFT, border=5)

        self.page_input = wx.TextCtrl(self, size=(50, 25), style=wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.page_input.Bind(wx.EVT_TEXT_ENTER, self.on_jump_page)
        pager_sizer.Add(self.page_input, flag=wx.LEFT, border=15)
        self.jump_btn = AquaButton(self, label=get_text('跳转'), size=(45, 25))
        self.jump_btn.SetForegroundColour(btn_fg)
        self.jump_btn.Bind(wx.EVT_BUTTON, self.on_jump_page)
        pager_sizer.Add(self.jump_btn, flag=wx.LEFT, border=10)
        
        bottom_sizer.Add(pager_sizer)
        
        # 伸缩器
        bottom_sizer.AddStretchSpacer()
        
        # 总记录数（右侧）
        self.total_text = wx.StaticText(self, label=f"{get_text('共')} 0 {get_text('条记录')}")
        bottom_sizer.Add(self.total_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        main_sizer.Add(bottom_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        self.SetSizer(main_sizer)
    
    def load_data(self):
        """加载数据"""
        # 根据筛选类型获取数据
        if self.filter_type == 0:  # 全部
            self.total_count = self.db.get_deleted_accounts_count(self.user_id)
            self.deleted_accounts = self.db.get_deleted_accounts(self.user_id, page=self.current_page, page_size=self.page_size)
        elif self.filter_type == 1:  # 收入
            self.total_count = self.db.get_deleted_accounts_count_by_type(self.user_id, '收入')
            self.deleted_accounts = self.db.get_deleted_accounts_by_type(self.user_id, '收入', page=self.current_page, page_size=self.page_size)
        elif self.filter_type == 2:  # 支出
            self.total_count = self.db.get_deleted_accounts_count_by_type(self.user_id, '支出')
            self.deleted_accounts = self.db.get_deleted_accounts_by_type(self.user_id, '支出', page=self.current_page, page_size=self.page_size)
        
        self.refresh_grid()
        self.update_pager()
        
        # 更新状态栏统计（显示所有记录的统计）
        self.update_stats()
    
    def update_stats(self):
        """更新状态栏统计（当前页所有记录）"""
        total_income = 0.0
        total_expense = 0.0
        
        for acc in self.deleted_accounts:
            amount = acc.get('amount', 0)
            if acc.get('type') == '收入':
                total_income += amount
            else:
                total_expense += amount
        
        total_balance = total_income - total_expense
        self.update_status_bar(total_income, total_expense, total_balance)
    
    def refresh_grid(self):
        """刷新表格"""
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())

        # 设置颜色
        green = wx.Colour(0, 128, 0)
        red = wx.Colour(220, 0, 0)

        for idx, acc in enumerate(self.deleted_accounts):
            self.grid.AppendRows(1)
            row = idx

            acc_type = acc['type']
            row_color = green if acc_type == get_text('收入') else red

            self.grid.SetCellValue(row, 0, acc.get('date', ''))
            self.grid.SetCellValue(row, 1, acc_type)
            self.grid.SetCellValue(row, 2, acc.get('category') or '')
            self.grid.SetCellValue(row, 3, f"{acc.get('amount', 0):.2f}")
            # 支付方式如果为空则显示空，经手人如果为空则显示"爸爸"
            payment = acc.get('payment_method') or ''
            handler = acc.get('handler') or '爸爸'
            self.grid.SetCellValue(row, 4, payment)
            self.grid.SetCellValue(row, 5, handler)
            self.grid.SetCellValue(row, 6, acc.get('description') or '')
            self.grid.SetCellValue(row, 7, acc.get('deleted_at', '')[:16] if acc.get('deleted_at') else '')

            for col in range(8):
                self.grid.SetCellTextColour(row, col, row_color)
            
            # 设置对齐方式：金额右对齐，说明左对齐，其他居中
            align_left = wx.ALIGN_LEFT
            align_center = wx.ALIGN_CENTER
            align_right = wx.ALIGN_RIGHT
            
            for col in [0, 1, 2, 4, 5, 7]:
                self.grid.SetCellAlignment(row, col, align_center, wx.ALIGN_CENTER)
            self.grid.SetCellAlignment(row, 3, align_right, wx.ALIGN_CENTER)  # 金额右对齐
            self.grid.SetCellAlignment(row, 6, align_left, wx.ALIGN_CENTER)   # 说明
    
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
        
        # 可用宽度（减去边距，与收支记录面板保持一致）
        available_width = max(grid_width - 5, 100)
        
        if available_width <= 0:
            return
        
        # 列宽比例
        # 0:日期, 1:类型, 2:分类, 3:金额, 4:支付方式, 5:经手人, 6:说明, 7:删除时间
        col_ratios = [10, 6, 10, 12, 14, 10, 20, 18]  # 总计100份
        
        # 计算每列宽度
        total_ratio = sum(col_ratios)
        unit_width = available_width / total_ratio
        
        total_width = 0
        for i, ratio in enumerate(col_ratios):
            if i < 7:  # 前7列按比例分配
                col_width = int(unit_width * ratio)
                # 设置最小宽度确保可读性
                min_widths = [80, 50, 60, 80, 80, 60, 100, 70]
                col_width = max(col_width, min_widths[i])
                self.grid.SetColSize(i, col_width)
                total_width += col_width
            else:  # 最后一列使用剩余空间
                last_col_width = max(available_width - total_width, 70)
                self.grid.SetColSize(i, last_col_width)
        
        # 强制刷新
        self.grid.ForceRefresh()

    def update_pager(self):
        """更新分页控件"""
        total_pages = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.page_text.SetLabel(f"{get_text('第')} {self.current_page} / {total_pages} {get_text('页')}")
        self.total_text.SetLabel(f"{get_text('共')} {self.total_count} {get_text('条记录')}")
        self.page_input.SetValue(str(self.current_page))
        
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
            wx.MessageBox(get_text('请输入有效的页码'), get_text('提示'), wx.OK | wx.ICON_WARNING)
    
    def on_restore(self, event):
        """恢复记录"""
        selected_rows = self.grid.GetSelectedRows()
        if not selected_rows:
            wx.MessageBox(get_text('请选择要恢复的记录'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        count = len(selected_rows)
        confirm_msg = f"{get_text('确定要恢复选中的')} {count} {get_text('条记录吗')}?"
        
        if wx.MessageBox(confirm_msg, get_text('确认'), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            restored_count = 0
            for row in selected_rows:
                if row < len(self.deleted_accounts):
                    account_id = self.deleted_accounts[row]['id']
                    success, msg = self.db.restore_account(account_id, self.user_id)
                    if success:
                        restored_count += 1
            
            if restored_count > 0:
                self.load_data()
                wx.MessageBox(f"{get_text('成功恢复')} {restored_count} {get_text('条记录')}", get_text('成功'), wx.OK | wx.ICON_INFORMATION)
                # 通知主窗口刷新收支记录
                parent = self.GetParent()
                while parent and not hasattr(parent, 'refresh_accounts'):
                    parent = parent.GetParent()
                if parent and hasattr(parent, 'refresh_accounts'):
                    parent.refresh_accounts()
    
    def on_permanent_delete(self, event):
        """永久删除"""
        selected_rows = self.grid.GetSelectedRows()
        if not selected_rows:
            wx.MessageBox(get_text('请选择要永久删除的记录'), get_text('提示'), wx.OK | wx.ICON_WARNING)
            return
        
        if wx.MessageBox(f"{get_text('确定要永久删除')}\n{get_text('此操作不可恢复')}", get_text('危险操作'),
                        wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            row = selected_rows[0]
            if row < len(self.deleted_accounts):
                account_id = self.deleted_accounts[row]['id']
                success, msg = self.db.permanent_delete_account(account_id)
                
                if success:
                    self.load_data()
                    wx.MessageBox(msg, get_text('成功'), wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox(msg, get_text('错误'), wx.OK | wx.ICON_ERROR)
    
    def on_empty(self, event):
        """清空回收站"""
        if not self.deleted_accounts:
            wx.MessageBox(get_text('回收站已是空的'), get_text('提示'), wx.OK | wx.ICON_INFORMATION)
            return
        
        if wx.MessageBox(f"{get_text('确定要清空回收站吗')}\n{get_text('将永久删除')} {len(self.deleted_accounts)} {get_text('条记录')}",
                        get_text('危险操作'), wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            success, msg = self.db.empty_recycle_bin(self.user_id)
            
            if success:
                self.load_data()
                wx.MessageBox(msg, get_text('成功'), wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox(msg, get_text('错误'), wx.OK | wx.ICON_ERROR)
    
    def on_refresh(self, event):
        """刷新"""
        self.load_data()
    
    def on_grid_selection_changed(self, event):
        """网格选择变化时更新选中行统计"""
        wx.CallAfter(self.update_selected_rows_stats)
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
        if self.deleted_accounts:
            # 清除当前选择
            self.grid.ClearSelection()
            # 选中所有行
            for row in range(len(self.deleted_accounts)):
                self.grid.SelectRow(row, True)
            # 更新统计
            wx.CallAfter(self.update_selected_rows_stats)
    
    def update_selected_rows_stats(self):
        """更新选中行的统计"""
        selected_rows = self.grid.GetSelectedRows()
        
        if not selected_rows:
            # 无选中行，显示当前页所有记录统计
            self.update_stats()
            return
        
        # 统计选中行的金额
        selected_income = 0.0
        selected_expense = 0.0
        
        for row in selected_rows:
            if row < len(self.deleted_accounts):
                acc = self.deleted_accounts[row]
                amount = acc.get('amount', 0)
                if acc.get('type') == '收入':
                    selected_income += amount
                else:
                    selected_expense += amount
        
        selected_balance = selected_income - selected_expense
        
        # 更新状态栏
        self.update_status_bar(selected_income, selected_expense, selected_balance)
    
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


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    db = Database()
    panel = RecycleBinPanel(frame, user_id=1, db=db)
    frame.Show()
    app.MainLoop()
