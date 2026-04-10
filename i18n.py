# -*- coding: utf-8 -*-
"""
国际化模块 - 支持多语言
支持：简体中文、繁体中文、English
"""
import wx
import json
import os

# 支持的语言列表
LANGUAGES = {
    'zh_CN': {'name': '简体中文', 'native': '简体中文'},
    'zh_TW': {'name': '繁體中文', 'native': '繁體中文'},
    'en_US': {'name': 'English', 'native': 'English'},
}

# 默认语言
DEFAULT_LANGUAGE = 'zh_CN'

# 当前语言（初始为默认，将由配置管理器覆盖）
current_language = DEFAULT_LANGUAGE

# 语言切换监听器列表
_language_listeners = []


def init_language():
    """初始化语言设置，从配置文件加载"""
    global current_language
    try:
        from config_manager import config
        saved_lang = config.get_language(DEFAULT_LANGUAGE)
        if saved_lang in LANGUAGES:
            current_language = saved_lang
    except Exception as e:
        pass  # 如果配置文件不存在，使用默认语言
    return current_language


def add_language_listener(callback):
    """添加语言切换监听器
    
    Args:
        callback: 回调函数，会在语言切换时被调用
    """
    if callback not in _language_listeners:
        _language_listeners.append(callback)


def remove_language_listener(callback):
    """移除语言切换监听器"""
    if callback in _language_listeners:
        _language_listeners.remove(callback)


def notify_language_changed():
    """通知所有监听器语言已切换"""
    for callback in _language_listeners:
        try:
            callback()
        except Exception as e:
            pass

# 翻译字典
TRANSLATIONS = {
    # 简体中文
    'zh_CN': {
        # 登录窗口
        '家庭记账系统': '家庭记账系统',
        '账户': '账户',
        '密码': '密码',
        '登录': '登录',
        '注册': '注册',
        '取消': '取消',
        '默认账户': '默认账户',
        '退出': '退出',
        
        # 主窗口
        '收支记录': '收支记录',
        '统计分析': '统计分析',
        '回收站': '回收站',
        '导入导出': '导入导出',
        '文件': '文件',
        '记录': '记录',
        '视图': '视图',
        '帮助': '帮助',
        '刷新': '刷新',
        '切换账户': '切换账户',
        '添加记录': '添加记录',
        '编辑': '编辑',
        '删除': '删除',
        '关于': '关于',
        '管理账户': '管理账户',
        '修改密码': '修改密码',
        '账户管理': '账户管理',
        '语言': '语言',
        '重启': '重启',
        '设置': '设置',
        '创建时间': '创建时间',
        '分类管理': '分类管理',
        '支付方式': '支付方式',
        '经手人': '经手人',
        '收入分类': '收入分类',
        '支出分类': '支出分类',
        '添加': '添加',
        '修改': '修改',
        '删除': '删除',
        '请输入名称': '请输入名称',
        '名称不能为空': '名称不能为空',
        '已存在': '已存在',
        '操作': '操作',
        '管理员账户': '管理员账户',
        '删除账户': '删除账户',
        '管理员可修改所有账户的密码，删除非管理员账户': '管理员可修改所有账户的密码，删除非管理员账户',
        '确认': '确认',
        '确定要重启程序吗': '确定要重启程序吗',
        '是': '是',
        '否': '否',
        
        # 收支记录
        '添加': '添加',
        '日期': '日期',
        '类型': '类型',
        '分类': '分类',
        '货币': '货币',
        '金额': '金额',
        '说明': '说明',
        '收入': '收入',
        '支出': '支出',
        '全部': '全部',
        '确定': '确定',
        '取消': '取消',
        '关于': '关于',
        '作者': '作者',
        '协议': '协议',
        '更新': '更新',
        '关闭': '关闭',
        '操作手册': '操作手册',
        '帮助手册': '操作手册',
        '确定要退出吗': '确定要退出吗',
        '请选择要编辑的记录': '请选择要编辑的记录',
        '请选择要删除的记录': '请选择要删除的记录',
        '确定要删除选中的记录吗': '确定要删除选中的记录吗？',
        '删除后可在回收站中恢复': '删除后可在回收站中恢复',
        
        # 分页
        '首页': '首页',
        '上一页': '上一页',
        '下一页': '下一页',
        '末页': '末页',
        '第': '第',
        '/': '/',
        '页': '页',
        '共': '共',
    '条记录': '条记录',
    
    # 筛选
    '显示全部': '显示全部',
    '筛选': '筛选',

    # 统计
    '开始日期': '开始日期',
    '结束日期': '结束日期',
        '查询': '查询',
        '总收入': '总收入',
        '总支出': '总支出',
        '结余': '结余',
        '支出分类': '支出分类',
        '收入分类': '收入分类',
        '支出分布': '支出分布',
        '收入分布': '收入分布',
        '月度趋势': '月度趋势',
        
        # 回收站
        '以下是已删除的记录': '以下是已删除的记录',
        '可以恢复或永久删除': '可以恢复或永久删除',
        '恢复': '恢复',
        '永久删除': '永久删除',
        '清空回收站': '清空回收站',
        '请选择要恢复的记录': '请选择要恢复的记录',
        '请选择要永久删除的记录': '请选择要永久删除的记录',
        '确定要永久删除': '确定要永久删除这条记录吗？',
        '此操作不可恢复': '此操作不可恢复！',
        '回收站已是空的': '回收站已是空的',
        '删除时间': '删除时间',
        '请输入有效的页码': '请输入有效的页码',
        '确定要清空回收站吗': '确定要清空回收站吗？',
        '将永久删除': '将永久删除',
        
        # 导入导出
        '数据导入导出': '数据导入导出',
        '导入数据': '导入数据',
        '导出数据': '导出数据',
        '从CSV/Excel文件导入收支记录': '从CSV/Excel文件导入收支记录',
        '将收支记录导出为CSV/Excel文件': '将收支记录导出为CSV/Excel文件',
        '选择文件导入': '选择文件导入',
        '导出': '导出',
        '请选择文件': '请先选择文件',
        '导入完成': '导入完成',
        '导出完成': '导出完成',
        
        # 账户管理
        '修改密码 - ': '修改密码 - ',
        '新密码': '新密码',
        '确认密码': '确认密码',
        '原密码': '原密码',
        '密码至少6个字符': '密码至少6个字符',
        '两次输入的密码不一致': '两次输入的密码不一致',
        '原密码错误': '原密码错误',
        '密码修改成功': '密码修改成功',
        '请先选择要修改密码的账户': '请先选择要修改密码的账户',
        '请先选择要删除的账户': '请先选择要删除的账户',
        '不能删除管理员账户': '不能删除管理员账户',
        '确定要删除账户': '确定要删除账户',
        '此操作将同时删除该账户的所有收支记录': '此操作将同时删除该账户的所有收支记录',
        '且不可恢复': '且不可恢复！',
        '(管理员账户)': '(管理员账户)',
        '关闭': '关闭',
        
        # 错误提示
        '错误': '错误',
        '提示': '提示',
        '成功': '成功',
        '危险操作': '危险操作',
        '请输入正确的金额': '请输入正确的金额',
        '金额必须是数字': '金额必须是数字',
        '记录不存在或已删除': '记录不存在或已删除',
        '账户已存在': '账户已存在',
        '账户和密码不能为空': '账户和密码不能为空',
        '账户至少3个字符': '账户至少3个字符',
        
        # 注册
        '注册新账户': '注册新账户',
        '确认密码': '确认密码',
        '密码至少6个字符': '密码至少6个字符',
        '两次输入的密码不一致': '两次输入的密码不一致',
        '注册成功': '注册成功',
        '注册失败': '注册失败',
        '当前账户': '当前账户',
        '语言切换成功，请重启程序以完全应用': '语言切换成功，请重启程序以完全应用',
        '登录失败': '登录失败',
        '账户或密码错误': '账户或密码错误',
        '语言切换成功': '语言切换成功',
        '日期筛选': '日期筛选',
        '收支概览': '收支概览',
        '数据可视化': '数据可视化',
        '查看分类': '查看分类',
        '暂无数据': '暂无数据',
        '支付方式': '支付方式',
        '经手人': '经手人',
        '导入': '导入',
        '至少3个字符': '至少3个字符',
        '至少6个字符': '至少6个字符',
        '所有支持格式': '所有支持格式',
        '支持格式': '支持格式',
        '保存至': '保存至',
        '跳过': '跳过',
        '从CSV文件导入收支记录': '从CSV文件导入收支记录',
        '导入成功': '导入成功',
        '导出成功': '导出成功',
        '编辑记录': '编辑记录',
        '删除记录': '删除记录',

        # 密码确认对话框
        '确认身份': '确认身份',
        '请输入账户': '请输入账户',
        '的密码': '的密码',
        '密码错误': '密码错误',
    },
    
    # 繁体中文
    'zh_TW': {
        '家庭记账系统': '家庭記帳系統',
        '账户': '帳戶',
        '密码': '密碼',
        '登录': '登錄',
        '注册': '註冊',
        '取消': '取消',
        '默认账户': '默認帳戶',
        '退出': '退出',
        '收支记录': '收支記錄',
        '统计分析': '統計分析',
        '回收站': '回收筒',
        '导入导出': '匯入匯出',
        '文件': '檔案',
        '记录': '記錄',
        '视图': '檢視',
        '帮助': '說明',
        '刷新': '重新整理',
        '切换账户': '切換帳戶',
        '添加记录': '新增記錄',
        '编辑': '編輯',
        '删除': '刪除',
        '关于': '關於',
        '管理账户': '管理帳戶',
        '修改密码': '修改密碼',
        '账户管理': '帳戶管理',
        '语言': '語言',
        '重启': '重啟',
        '设置': '設置',
        '创建时间': '創建時間',
        '分类管理': '分類管理',
        '支付方式': '支付方式',
        '经手人': '經手人',
        '收入分类': '收入分類',
        '支出分类': '支出分類',
        '添加': '新增',
        '修改': '修改',
        '删除': '刪除',
        '请输入名称': '請輸入名稱',
        '名称不能为空': '名稱不能為空',
        '已存在': '已存在',
        '操作': '操作',
        '管理员账户': '管理員帳戶',
        '删除账户': '刪除帳戶',
        '管理员可修改所有账户的密码，删除非管理员账户': '管理員可修改所有帳戶的密碼，刪除非管理員帳戶',
        '确认': '確認',
        '确定要重启程序吗': '確定要重啟程式嗎',
        '是': '是',
        '否': '否',
        '添加': '新增',
        '日期': '日期',
        '类型': '類型',
        '分类': '分類',
        '货币': '幣種',
        '金额': '金額',
        '说明': '說明',
        '收入': '收入',
        '支出': '支出',
        '确定': '確定',
        '关于': '關於',
        '作者': '作者',
        '协议': '協議',
        '更新': '更新',
        '关闭': '關閉',
        '操作手册': '操作手冊',
        '帮助手册': '操作手冊',
        '确定要退出嗎': '確定要退出嗎',
        '请选择要编辑的记录': '請選擇要編輯的記錄',
        '请选择要删除的记录': '請選擇要刪除的記錄',
        '确定要删除选中的记录吗': '確定要刪除選中的記錄嗎？',
        '删除后可在回收站中恢复': '刪除後可在回收筒中恢復',
        '首页': '首頁',
        '上一页': '上一頁',
        '下一页': '下一頁',
        '末页': '末頁',
        '第': '第',
        '页': '頁',
        '共': '共',
    '条记录': '條記錄',
    '显示全部': '顯示全部',
    '筛选': '篩選',
    '开始日期': '開始日期',
    '结束日期': '結束日期',
        '查询': '查詢',
        '总收入': '總收入',
        '总支出': '總支出',
        '结余': '結餘',
        '支出分类': '支出分類',
        '收入分类': '收入分類',
        '支出分布': '支出分布',
        '收入分布': '收入分布',
        '月度趋势': '月度趨勢',
        '以下是已删除的记录': '以下為已刪除的記錄',
        '可以恢复或永久删除': '可以恢復或永久刪除',
        '恢复': '恢復',
        '永久删除': '永久刪除',
        '清空回收站': '清空回收筒',
        '请选择要恢复的记录': '請選擇要恢復的記錄',
        '请选择要永久删除的记录': '請選擇要永久刪除的記錄',
        '确定要永久删除': '確定要永久刪除這條記錄嗎？',
        '此操作不可恢复': '此操作不可恢復！',
        '回收站已是空的': '回收筒已經是空的',
        '删除时间': '刪除時間',
        '请输入有效的页码': '請輸入有效的頁碼',
        '确定要清空回收站吗': '確定要清空回收筒嗎？',
        '将永久删除': '將永久刪除',
        '数据导入导出': '資料匯入匯出',
        '导入数据': '匯入資料',
        '导出数据': '匯出資料',
        '从CSV/Excel文件导入收支记录': '從CSV/Excel檔案匯入收支記錄',
        '将收支记录导出为CSV/Excel文件': '將收支記錄匯出為CSV/Excel檔案',
        '选择文件导入': '選擇檔案匯入',
        '导出': '匯出',
        '请选择文件': '請先選擇檔案',
        '导入完成': '匯入完成',
        '导出完成': '匯出完成',
        '修改密码 - ': '修改密碼 - ',
        '新密码': '新密碼',
        '确认密码': '確認密碼',
        '原密码': '原密碼',
        '密码至少6个字符': '密碼至少6個字元',
        '两次输入的密码不一致': '兩次輸入的密碼不一致',
        '原密码错误': '原密碼錯誤',
        '密码修改成功': '密碼修改成功',
        '请先选择要修改密码的账户': '請先選擇要修改密碼的帳戶',
        '请先选择要删除的账户': '請先選擇要刪除的帳戶',
        '不能删除管理员账户': '不能刪除管理員帳戶',
        '确定要删除账户': '確定要刪除帳戶',
        '此操作将同时删除该账户的所有收支记录': '此操作將同時刪除該帳戶的所有收支記錄',
        '且不可恢复': '且不可恢復！',
        '(管理员账户)': '(管理員帳戶)',
        '关闭': '關閉',
        '错误': '錯誤',
        '提示': '提示',
        '成功': '成功',
        '危险操作': '危險操作',
        '请输入正确的金额': '請輸入正確的金額',
        '金额必须是数字': '金額必須是數字',
        '记录不存在或已删除': '記錄不存在或已刪除',
        '账户已存在': '帳戶已存在',
        '账户和密码不能为空': '帳戶和密碼不能為空',
        '账户至少3个字符': '帳戶至少3個字元',
        '注册新账户': '註冊新帳戶',
        '注册成功': '註冊成功',
        '注册失败': '註冊失敗',
        '当前账户': '目前帳戶',
        '语言切换成功，请重启程序以完全应用': '語言切換成功，請重啟程式以完全應用',
        '登录失败': '登錄失敗',
        '账户或密码错误': '帳戶或密碼錯誤',
        '语言切换成功': '語言切換成功',
        '日期筛选': '日期篩選',
        '收支概览': '收支概覽',
        '数据可视化': '資料視覺化',
        '查看分类': '查看分類',
        '暂无数据': '暫無資料',
        '支付方式': '支付方式',
        '经手人': '經手人',
        '导入': '匯入',
        '至少3个字符': '至少3個字元',
        '至少6个字符': '至少6個字元',
        '所有支持格式': '所有支援格式',
        '支持格式': '支援格式',
        '保存至': '儲存至',
        '跳过': '跳過',
        '从CSV文件导入收支记录': '從CSV檔案匯入收支記錄',
        '导入成功': '匯入成功',
        '导出成功': '匯出成功',
        '编辑记录': '編輯記錄',
        '删除记录': '刪除記錄',

        # 密碼確認對話框
        '确认身份': '確認身份',
        '请输入账户': '請輸入帳戶',
        '的密码': '的密碼',
        '密码错误': '密碼錯誤',
    },
    
    # 英语
    'en_US': {
        '家庭记账系统': 'Family Accounting',
        '账户': 'Account',
        '密码': 'Password',
        '登录': 'Login',
        '注册': 'Register',
        '取消': 'Cancel',
        '默认账户': 'Default Account',
        '退出': 'Exit',
        '收支记录': 'Records',
        '统计分析': 'Statistics',
        '回收站': 'Recycle Bin',
        '导入导出': 'Import/Export',
        '文件': 'File',
        '记录': 'Record',
        '视图': 'View',
        '帮助': 'Help',
        '刷新': 'Refresh',
        '切换账户': 'Switch Account',
        '添加记录': 'Add Record',
        '编辑': 'Edit',
        '删除': 'Delete',
        '关于': 'About',
        '管理账户': 'Account',
        '修改密码': 'Change Password',
        '账户管理': 'Manage Accounts',
        '语言': 'Language',
        '重启': 'Restart',
        '设置': 'Settings',
        '创建时间': 'Created At',
        '分类管理': 'Categories',
        '支付方式': 'Payment Methods',
        '经手人': 'Handlers',
        '收入分类': 'Income Categories',
        '支出分类': 'Expense Categories',
        '添加': 'Add',
        '修改': 'Edit',
        '删除': 'Delete',
        '请输入名称': 'Please enter name',
        '名称不能为空': 'Name cannot be empty',
        '已存在': 'Already exists',
        '操作': 'Action',
        '管理员账户': 'Administrator Account',
        '删除账户': 'Delete Account',
        '管理员可修改所有账户的密码，删除非管理员账户': 'Administrators can modify all account passwords and delete non-admin accounts',
        '确认': 'Confirm',
        '确定要重启程序吗': 'Are you sure you want to restart?',
        '是': 'Yes',
        '否': 'No',
        '添加': 'Add',
        '日期': 'Date',
        '类型': 'Type',
        '分类': 'Category',
        '货币': 'Currency',
        '金额': 'Amount',
        '说明': 'Description',
        '收入': 'Income',
        '支出': 'Expense',
        '全部': 'All',
        '确定': 'OK',
        '关于': 'About',
        '作者': 'Author',
        '协议': 'License',
        '更新': 'Update',
        '关闭': 'Close',
        '操作手册': 'User Manual',
        '帮助手册': 'Help Manual',
        '确定要退出吗': 'Are you sure you want to exit?',
        '请选择要编辑的记录': 'Please select a record to edit',
        '请选择要删除的记录': 'Please select a record to delete',
        '确定要删除选中的记录吗': 'Are you sure you want to delete the selected record?',
        '删除后可在回收站中恢复': 'Deleted records can be restored from Recycle Bin',
        '首页': 'First',
        '上一页': 'Prev',
        '下一页': 'Next',
        '末页': 'Last',
        '第': '',
        '页': 'Page',
        '共': 'Total',
    '条记录': 'Records',
    '显示全部': 'Show All',
    '筛选': 'Filter',
    '开始日期': 'Start Date',
    '结束日期': 'End Date',
        '查询': 'Query',
        '总收入': 'Total Income',
        '总支出': 'Total Expense',
        '结余': 'Balance',
        '支出分类': 'Expense Categories',
        '收入分类': 'Income Categories',
        '支出分布': 'Expense Distribution',
        '收入分布': 'Income Distribution',
        '月度趋势': 'Monthly Trend',
        '以下是已删除的记录': 'Deleted records are shown below',
        '可以恢复或永久删除': 'You can restore or permanently delete them',
        '恢复': 'Restore',
        '永久删除': 'Delete',
        '清空回收站': 'Empty Recycle Bin',
        '请选择要恢复的记录': 'Please select a record to restore',
        '请选择要永久删除的记录': 'Please select a record to permanently delete',
        '确定要永久删除': 'Are you sure you want to permanently delete this record?',
        '此操作不可恢复': 'This action cannot be undone!',
        '回收站已是空的': 'Recycle Bin is empty',
        '删除时间': 'Deleted At',
        '请输入有效的页码': 'Please enter a valid page number',
        '确定要清空回收站吗': 'Are you sure you want to empty the Recycle Bin?',
        '将永久删除': 'This will permanently delete',
        '数据导入导出': 'Data Import/Export',
        '导入数据': 'Import Data',
        '导出数据': 'Export Data',
        '从CSV/Excel文件导入收支记录': 'Import records from CSV/Excel file',
        '将收支记录导出为CSV/Excel文件': 'Export records to CSV/Excel file',
        '选择文件导入': 'Select File to Import',
        '导出': 'Export',
        '请选择文件': 'Please select a file first',
        '导入完成': 'Import Complete',
        '导出完成': 'Export Complete',
        '修改密码 - ': 'Change Password - ',
        '新密码': 'New Password',
        '确认密码': 'Confirm Password',
        '原密码': 'Current Password',
        '密码至少6个字符': 'Password must be at least 6 characters',
        '两次输入的密码不一致': 'Passwords do not match',
        '原密码错误': 'Current password is incorrect',
        '密码修改成功': 'Password changed successfully',
        '请先选择要修改密码的账户': 'Please select an account first',
        '请先选择要删除的账户': 'Please select an account to delete',
        '不能删除管理员账户': 'Cannot delete admin account',
        '确定要删除账户': 'Are you sure you want to delete account',
        '此操作将同时删除该账户的所有收支记录': 'This will delete all records for this account',
        '且不可恢复': 'and cannot be undone!',
        '(管理员账户)': '(Admin)',
        '关闭': 'Close',
        '错误': 'Error',
        '提示': 'Warning',
        '成功': 'Success',
        '危险操作': 'Danger',
        '请输入正确的金额': 'Please enter a valid amount',
        '金额必须是数字': 'Amount must be a number',
        '记录不存在或已删除': 'Record not found or already deleted',
        '账户已存在': 'Account already exists',
        '账户和密码不能为空': 'Account and password cannot be empty',
        '账户至少3个字符': 'Account must be at least 3 characters',
        '注册新账户': 'Register New Account',
        '注册成功': 'Registration successful',
        '注册失败': 'Registration failed',
        '当前账户': 'Current Account',
        '语言切换成功，请重启程序以完全应用': 'Language changed. Please restart to apply.',
        '登录失败': 'Login Failed',
        '账户或密码错误': 'Invalid account or password',
        '语言切换成功': 'Language Changed',
        '日期筛选': 'Date Filter',
        '收支概览': 'Overview',
        '数据可视化': 'Data Visualization',
        '查看分类': 'View Category',
        '暂无数据': 'No Data',
        '支付方式': 'Payment Method',
        '经手人': 'Handler',
        '导入': 'Import',
        '至少3个字符': 'At least 3 characters',
        '至少6个字符': 'At least 6 characters',
        '所有支持格式': 'All supported formats',
        '支持格式': 'Supported formats',
        '保存至': 'Save to',
        '跳过': 'Skip',
        '从CSV文件导入收支记录': 'Import records from CSV file',
        '导入成功': 'Import successful',
        '导出成功': 'Export successful',
        '编辑记录': 'Edit Record',
        '删除记录': 'Delete Record',

        # Password confirmation dialog
        '确认身份': 'Confirm Identity',
        '请输入账户': 'Please enter password for',
        '的密码': '\'s account',
        '密码错误': 'Incorrect password',
    },
}


def get_text(key, lang=None):
    """获取翻译文本"""
    global current_language
    if lang is None:
        lang = current_language
    
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANGUAGE
    
    return TRANSLATIONS.get(lang, {}).get(key, key)


def set_language(lang):
    """设置当前语言"""
    global current_language
    if lang in LANGUAGES:
        current_language = lang
        notify_language_changed()
        return True
    return False


def get_current_language():
    """获取当前语言"""
    return current_language


def get_language_name(lang_code):
    """获取语言名称"""
    return LANGUAGES.get(lang_code, {}).get('native', lang_code)


# 快捷函数
_ = get_text
