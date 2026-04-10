# 家庭记账系统 (Family Accounting)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![wxPython](https://img.shields.io/badge/wxPython-4.2+-green.svg)

一款功能完善的家庭财务管理软件，支持收支记录管理、统计分析、数据导入导出和多语言界面。

## 功能特性

### 核心功能
- **收支记录管理**：添加、编辑、删除收支记录
- **分类管理**：收入和支出分类，支持自定义排序
- **支付方式**：现金、微信、支付宝、银行卡等，支持自定义排序
- **经手人记录**：记录家庭成员支出，默认选择"爸爸"
- **日期筛选**：按日期范围筛选记录
- **Ctrl+A全选**：快速选中所有记录
- **刷新功能**：工具栏刷新按钮，取消表格选中状态

### 数据分析
- **统计分析**：收入支出趋势、分类占比
- **月度报告**：月度收支明细
- **图表展示**：直观的数据可视化

### 主题支持
- **6种主题**：浅色、灰色、蓝色、绿色、紫色、银白色
- **主题保存在配置中**：下次启动自动应用

### 多语言
- 简体中文
- 繁体中文
- English

### 实用功能
- **回收站**：误删恢复，永久删除
- **数据导入导出**：CSV/Excel格式支持
- **重启功能**：无需关闭程序即可重启
- **设置窗口**：管理分类、支付方式、经手人

## 系统要求

- Python 3.8+
- wxPython Phoenix 4.2+
- SQLite3

## 安装依赖

```bash
pip install wxPython>=4.2.0
pip install openpyxl  # Excel支持（可选）
```

## 运行程序

```bash
python main.py
```

## 默认账户

- 用户名：admin
- 密码：123456

## 项目结构

```
family_accounting/
├── main.py                 # 程序入口
├── main_frame.py           # 主窗口
├── login.py                # 登录窗口
├── register.py             # 注册窗口
├── account_manager.py       # 收支记录管理
├── statistics.py           # 统计分析
├── recycle_bin.py          # 回收站
├── import_export.py         # 数据导入导出
├── user_manager.py          # 用户管理
├── settings.py             # 设置窗口
├── database.py             # 数据库操作
├── theme.py                # 主题管理
├── i18n.py                 # 多语言支持
├── config_manager.py        # 配置管理
├── i18n_support.py         # 语言切换支持
└── requirements.txt        # 依赖列表
```

## 主要功能

### 登录窗口
- 输入账户和密码登录
- 支持新用户注册
- 主题和语言切换

### 主窗口
- 工具栏：添加、编辑、刷新、删除按钮
- 收支记录、统计分析、回收站、导入导出四个选项卡
- 设置菜单：管理分类、支付方式、经手人

### 收支记录
- 表格展示所有记录
- 支持日期范围筛选
- 收入/支出类型筛选
- 分页显示（每页50条）
- 状态栏实时统计选中记录
- 点击空白处或刷新按钮取消选中

### 统计分析
- 按月份统计收支
- 分类占比饼图
- 收入支出趋势图

### 回收站
- 查看已删除记录
- 恢复记录
- 永久删除
- 点击空白处或刷新按钮取消选中

### 设置窗口
- 收入分类管理（添加、修改、删除、上移、下移）
- 支出分类管理（添加、修改、删除、上移、下移）
- 支付方式管理（添加、修改、删除、上移、下移）
- 经手人管理（添加、修改、删除、上移、下移）

## 数据导入导出

### 导入支持格式
- CSV 文件
- Excel (.xls, .xlsx)

### 导出支持格式
- CSV 文件
- Excel (.xlsx)

## 更新日志

### v0.1 (2026-04-10)
- 初始版本
- 基础收支管理功能

## 技术栈

- **GUI框架**：wxPython Phoenix
- **数据库**：SQLite3
- **图表**：matplotlib
- **Excel支持**：openpyxl

## 许可证

MIT License

## 作者

- 作者：天涯客
- Email：774667285@qq.com
- 博客：https://www.chinjua.com.cn/
- 项目地址：https://github.com/chinjua/family_accounting

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 致谢

感谢 wxPython 社区和所有开源贡献者。
