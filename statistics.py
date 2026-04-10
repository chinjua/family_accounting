# -*- coding: utf-8 -*-
"""
统计可视化模块 - 图表和数据可视化
"""
import wx
import wx.adv as wxadv
from wx.lib.agw.aquabutton import AquaButton
from database import Database
from i18n import get_text, get_current_language, LANGUAGES, add_language_listener, remove_language_listener
from theme import get_theme, get_button_colors, get_card_colors


# 饼图颜色
PIE_COLORS = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#FF6384', '#C9CBCF', '#7CB342', '#D81B60',
    '#1E88E5', '#43A047', '#FDD835', '#FB8C00', '#8E24AA'
]

# 柱状图颜色
BAR_INCOME_COLOR = '#4CAF50'
BAR_EXPENSE_COLOR = '#F44336'


class PieChartPanel(wx.Panel):
    """饼图面板"""
    
    def __init__(self, parent, data, title=""):
        super().__init__(parent)
        self.data = data
        self.title = title
        self.SetBackgroundColour(wx.WHITE)
        self.Bind(wx.EVT_PAINT, self.on_paint)
    
    def on_paint(self, event):
        """绘制饼图"""
        dc = wx.PaintDC(self)
        dc.Clear()
        
        if not self.data:
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.DrawLabel("暂无数据", wx.Rect(0, 0, self.GetSize()[0], self.GetSize()[1]),
                        wx.ALIGN_CENTER | wx.ALIGN_CENTER)
            return
        
        # 计算饼图参数
        width, height = self.GetSize()
        center_x = width // 2
        center_y = height // 2 - 20
        radius = min(width, height) // 2 - 60
        
        if radius <= 0:
            return
        
        # 计算总数
        total = sum(item['amount'] for item in self.data)
        if total == 0:
            return
        
        # 绘制饼图
        start_angle = 0
        rect = wx.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        for i, item in enumerate(self.data):
            if item['amount'] <= 0:
                continue
            
            sweep_angle = (item['amount'] / total) * 360
            color = wx.Colour(int(PIE_COLORS[i % len(PIE_COLORS)][1:3], 16),
                            int(PIE_COLORS[i % len(PIE_COLORS)][3:5], 16),
                            int(PIE_COLORS[i % len(PIE_COLORS)][5:7], 16))
            
            # 绘制扇形（饼图的一个切片）
            import math
            
            # 生成扇形轮廓点
            points = []
            # 起点连接到圆心
            points.append((center_x, center_y))
            
            # 沿圆弧的点
            steps = max(1, int(sweep_angle / 5))
            for step in range(steps + 1):
                angle = start_angle + (sweep_angle * step / steps)
                rad = math.radians(angle)
                px = center_x + radius * math.cos(rad)
                py = center_y - radius * math.sin(rad)
                points.append((px, py))
            
            # 绘制多边形扇形
            if len(points) >= 3:
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(wx.WHITE, 2))
                dc.DrawPolygon(points)
            
            start_angle += sweep_angle
        
        # 绘制图例
        legend_x = 20
        legend_y = height - 20 - len(self.data) * 18
        legend_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        
        for i, item in enumerate(self.data):
            if item['amount'] <= 0:
                continue
            
            color = wx.Colour(int(PIE_COLORS[i % len(PIE_COLORS)][1:3], 16),
                            int(PIE_COLORS[i % len(PIE_COLORS)][3:5], 16),
                            int(PIE_COLORS[i % len(PIE_COLORS)][5:7], 16))
            
            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            dc.DrawRectangle(legend_x, legend_y + i * 18, 14, 14)
            
            dc.SetFont(legend_font)
            label = f"{item['category']}: ¥{item['amount']:.2f} ({item['percentage']:.1f}%)"
            dc.DrawText(label, legend_x + 20, legend_y + i * 18)
        
        # 绘制标题
        if self.title:
            title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            dc.SetFont(title_font)
            dc.DrawLabel(self.title, wx.Rect(0, 5, width, 25), wx.ALIGN_CENTER)


class BarChartPanel(wx.Panel):
    """柱状图面板"""
    
    def __init__(self, parent, data, title="", bar_width=30):
        super().__init__(parent)
        self.data = data
        self.title = title
        self.bar_width = bar_width
        self.SetBackgroundColour(wx.WHITE)
        self.Bind(wx.EVT_PAINT, self.on_paint)
    
    def on_paint(self, event):
        """绘制柱状图"""
        dc = wx.PaintDC(self)
        dc.Clear()
        
        if not self.data:
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.DrawLabel("暂无数据", wx.Rect(0, 0, self.GetSize()[0], self.GetSize()[1]),
                        wx.ALIGN_CENTER | wx.ALIGN_CENTER)
            return
        
        width, height = self.GetSize()
        padding_left = 60
        padding_right = 20
        padding_top = 40
        padding_bottom = 40
        
        chart_width = width - padding_left - padding_right
        chart_height = height - padding_top - padding_bottom
        
        if chart_width <= 0 or chart_height <= 0:
            return
        
        # 计算最大值
        max_value = max(max(item.get('income', 0), item.get('expense', 0)) for item in self.data)
        if max_value == 0:
            max_value = 100
        
        # 绘制坐标轴
        dc.SetPen(wx.Pen(wx.BLACK, 2))
        dc.DrawLine(padding_left, padding_top, padding_left, height - padding_bottom)
        dc.DrawLine(padding_left, height - padding_bottom, width - padding_right, height - padding_bottom)
        
        # 绘制网格线
        dc.SetPen(wx.Pen(wx.Colour(200, 200, 200), 1))
        grid_count = 5
        for i in range(1, grid_count + 1):
            y = height - padding_bottom - (chart_height * i / grid_count)
            value = max_value * i / grid_count
            dc.DrawLine(padding_left, y, width - padding_right, y)
            
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.DrawText(f"¥{int(value)}", 5, y - 5)
        
        # 绘制柱状图
        bar_spacing = chart_width / len(self.data)
        
        for i, item in enumerate(self.data):
            x = padding_left + i * bar_spacing + bar_spacing / 4
            
            # 收入柱
            income = item.get('income', 0)
            if income > 0:
                income_height = (income / max_value) * chart_height
                dc.SetBrush(wx.Brush(wx.Colour(76, 175, 80)))
                dc.SetPen(wx.Pen(wx.WHITE, 1))
                dc.DrawRectangle(int(x), int(height - padding_bottom - income_height),
                               int(self.bar_width), int(income_height))
            
            # 支出柱
            expense = item.get('expense', 0)
            if expense > 0:
                expense_height = (expense / max_value) * chart_height
                dc.SetBrush(wx.Brush(wx.Colour(244, 67, 54)))
                dc.SetPen(wx.Pen(wx.WHITE, 1))
                dc.DrawRectangle(int(x + self.bar_width + 2), int(height - padding_bottom - expense_height),
                               int(self.bar_width), int(expense_height))
            
            # X轴标签
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            label = item.get('label', '')[:7]
            dc.DrawText(label, int(x), height - padding_bottom + 5)
        
        # 绘制标题
        if self.title:
            title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            dc.SetFont(title_font)
            dc.DrawLabel(self.title, wx.Rect(0, 5, width, 25), wx.ALIGN_CENTER)
        
        # 绘制图例
        legend_y = 10
        dc.SetBrush(wx.Brush(wx.Colour(76, 175, 80)))
        dc.DrawRectangle(width - 150, legend_y, 12, 12)
        dc.DrawText("收入", width - 135, legend_y)
        dc.SetBrush(wx.Brush(wx.Colour(244, 67, 54)))
        dc.DrawRectangle(width - 80, legend_y, 12, 12)
        dc.DrawText("支出", width - 65, legend_y)


class StatisticsPanel(wx.Panel):
    """统计面板"""
    
    def __init__(self, parent, user_id, db):
        super().__init__(parent)
        self.user_id = user_id
        self.db = db
        
        self.start_date = None
        self.end_date = None
        
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
    
    def apply_theme(self):
        """应用当前主题"""
        theme = get_theme()
        
        # 设置面板背景
        self.SetBackgroundColour(theme['bg_color'])
        
        # 刷新图表面板
        if hasattr(self, 'pie_panel'):
            self.pie_panel.Refresh()
        if hasattr(self, 'bar_panel'):
            self.bar_panel.Refresh()
        
        # 刷新
        self.Refresh()
    
    def refresh_labels(self):
        """刷新界面文字"""
        # 更新静态框标签
        self.filter_box.SetLabel(get_text('日期筛选'))
        
        # 更新按钮
        self.query_btn.SetLabel(get_text('查询'))
        
        # 更新概览卡片
        self.overview_box.SetLabel(get_text('收支概览'))
        
        # 更新概览卡片标题
        if hasattr(self, 'income_title'):
            self.income_title.SetLabel(get_text('总收入'))
        if hasattr(self, 'expense_title'):
            self.expense_title.SetLabel(get_text('总支出'))
        if hasattr(self, 'balance_title'):
            self.balance_title.SetLabel(get_text('结余'))
        
        # 更新图表类型选择
        self.type_choice.Set([get_text('收入分类'), get_text('支出分类')])
        self.type_choice.SetSelection(0)
        
        # 更新图表标题
        self.pie_panel.title = get_text('收入分布')
        self.bar_panel.title = get_text('月度趋势')
        self.pie_panel.Refresh()
        self.bar_panel.Refresh()
        
        self.Layout()
    
    def init_ui(self):
        """初始化界面"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 日期筛选
        self.filter_box = wx.StaticBox(self, label=get_text('日期筛选'))
        filter_sizer = wx.StaticBoxSizer(self.filter_box, wx.HORIZONTAL)
        
        filter_sizer.Add(wx.StaticText(self, label=get_text('开始日期') + ":"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.start_picker = wxadv.DatePickerCtrl(self, style=wxadv.DP_DEFAULT)
        filter_sizer.Add(self.start_picker, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=5)
        
        filter_sizer.Add(wx.StaticText(self, label=get_text('结束日期') + ":"), flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border=20)
        self.end_picker = wxadv.DatePickerCtrl(self, style=wxadv.DP_DEFAULT)
        self.end_picker.SetValue(wx.DateTime.Now())
        filter_sizer.Add(self.end_picker, flag=wx.LEFT, border=5)
        
        self.query_btn = AquaButton(self, label=get_text('查询'), size=(70, 25))
        self.query_btn.SetForegroundColour(wx.Colour(0, 0, 0))
        self.query_btn.Bind(wx.EVT_BUTTON, self.on_query)
        filter_sizer.Add(self.query_btn, flag=wx.LEFT, border=20)
        
        main_sizer.Add(filter_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        # 概览卡片
        self.overview_box = wx.StaticBox(self, label=get_text('收支概览'))
        overview_sizer = wx.StaticBoxSizer(self.overview_box, wx.VERTICAL)
        
        # 三列布局
        cards_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 收入卡片
        income_card = self.create_card(get_text('总收入'), "¥0.00", "#4CAF50")
        self.income_label = income_card.GetChildren()[1]
        self.income_title = income_card.GetChildren()[0]
        cards_sizer.Add(income_card, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=5)
        
        # 支出卡片
        expense_card = self.create_card(get_text('总支出'), "¥0.00", "#F44336")
        self.expense_label = expense_card.GetChildren()[1]
        self.expense_title = expense_card.GetChildren()[0]
        cards_sizer.Add(expense_card, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        
        # 余额卡片
        balance_card = self.create_card(get_text('结余'), "¥0.00", "#2196F3")
        self.balance_label = balance_card.GetChildren()[1]
        self.balance_title = balance_card.GetChildren()[0]
        cards_sizer.Add(balance_card, proportion=1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        overview_sizer.Add(cards_sizer, flag=wx.EXPAND)
        main_sizer.Add(overview_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        # 图表区域
        chart_box = wx.StaticBox(self, label=get_text('数据可视化'))
        chart_sizer = wx.StaticBoxSizer(chart_box, wx.VERTICAL)
        
        # 图表类型选择
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(wx.StaticText(self, label=get_text('查看分类') + ":"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.type_choice = wx.Choice(self, choices=[get_text('收入分类'), get_text('支出分类')])
        self.type_choice.SetSelection(0)
        self.type_choice.Bind(wx.EVT_CHOICE, self.on_type_changed)
        type_sizer.Add(self.type_choice, flag=wx.LEFT, border=10)
        chart_sizer.Add(type_sizer, flag=wx.BOTTOM, border=5)
        
        # 饼图和柱状图并排
        charts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 饼图
        self.pie_panel = PieChartPanel(self, [], get_text('支出分布'))
        charts_sizer.Add(self.pie_panel, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=5)
        
        # 柱状图
        self.bar_panel = BarChartPanel(self, [], get_text('月度趋势'))
        charts_sizer.Add(self.bar_panel, proportion=1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        chart_sizer.Add(charts_sizer, proportion=1, flag=wx.EXPAND)
        main_sizer.Add(chart_sizer, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        self.SetSizer(main_sizer)
    
    def create_card(self, title, value, color):
        """创建统计卡片"""
        card = wx.Panel(self)
        card.SetBackgroundColour(wx.Colour(245, 245, 245))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_text = wx.StaticText(card, label=title)
        title_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(title_text, flag=wx.ALIGN_CENTER | wx.TOP, border=15)
        
        value_text = wx.StaticText(card, label=value)
        value_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        value_text.SetFont(value_font)
        c = wx.Colour(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
        value_text.SetForegroundColour(c)
        sizer.Add(value_text, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        
        card.SetSizer(sizer)
        return card
    
    def load_data(self):
        """加载数据"""
        # 获取日期范围
        start_date = self.start_picker.GetValue().Format('%Y-%m-%d')
        end_date = self.end_picker.GetValue().Format('%Y-%m-%d')
        
        # 获取统计数据
        stats = self.db.get_statistics(self.user_id, start_date, end_date)
        
        # 更新概览
        self.income_label.SetLabel(f"¥{stats['income']:.2f}")
        self.expense_label.SetLabel(f"¥{stats['expense']:.2f}")
        self.balance_label.SetLabel(f"¥{stats['balance']:.2f}")
        
        # 获取分类数据
        type_ = get_text('收入') if self.type_choice.GetSelection() == 0 else get_text('支出')
        cat_stats = self.db.get_category_statistics_for_chart(self.user_id, type_, start_date, end_date)
        self.pie_panel.data = cat_stats
        self.pie_panel.title = f"{type_}{get_text('分布')}"
        self.pie_panel.Refresh()
        
        # 获取月度趋势
        monthly_data = self.db.get_monthly_trend(self.user_id, 6)
        self.bar_panel.data = monthly_data
        self.bar_panel.Refresh()
    
    def on_query(self, event):
        """查询按钮"""
        self.load_data()
    
    def on_type_changed(self, event):
        """类型改变"""
        self.load_data()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, size=(900, 600))
    db = Database()
    panel = StatisticsPanel(frame, user_id=1, db=db)
    frame.Show()
    app.MainLoop()
