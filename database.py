# -*- coding: utf-8 -*-
"""
数据库模块 - 处理所有数据库操作
"""
import sqlite3
from datetime import datetime
import hashlib


# 支持的货币列表
CURRENCIES = {
    'CNY': {'symbol': '¥', 'name': '人民币', 'code': 'CNY'},
    'USD': {'symbol': '$', 'name': '美元', 'code': 'USD'},
    'EUR': {'symbol': '€', 'name': '欧元', 'code': 'EUR'},
    'GBP': {'symbol': '£', 'name': '英镑', 'code': 'GBP'},
    'JPY': {'symbol': '¥', 'name': '日元', 'code': 'JPY'},
    'HKD': {'symbol': 'HK$', 'name': '港币', 'code': 'HKD'},
    'TWD': {'symbol': 'NT$', 'name': '新台币', 'code': 'TWD'},
    'KRW': {'symbol': '₩', 'name': '韩元', 'code': 'KRW'},
}


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path="family_accounting.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA synchronous = NORMAL")  # 提高写入性能
        self.cursor = self.conn.cursor()
        self.init_tables()
        self.create_indexes()  # 创建索引优化查询性能
    
    def init_tables(self):
        """初始化数据库表"""
        # 用户表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # 账户表（收支记录）
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('收入', '支出')),
                amount REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'CNY',
                category TEXT,
                description TEXT,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                deleted_at TEXT,
                deleted_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (deleted_by) REFERENCES users(id)
            )
        """)

        # 分类表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('收入', '支出')),
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, name, type)
            )
        """)

        # 支付方式表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, name)
            )
        """)

        # 经手人表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS handlers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, name)
            )
        """)

        self.conn.commit()
        
        # 创建索引优化查询性能
        self.create_indexes()
        
        # 数据库迁移：添加缺失的列
        self.migrate_database()
        
        self.init_default_user()
        self.init_default_categories()
        self.init_default_payment_methods()
        self.init_default_handlers()

    def migrate_database(self):
        """数据库迁移：添加缺失的列"""
        try:
            # 获取accounts表的列信息
            self.cursor.execute("PRAGMA table_info(accounts)")
            columns = [row[1] for row in self.cursor.fetchall()]
            
            # 添加 payment_method 列（如果不存在）
            if 'payment_method' not in columns:
                self.cursor.execute("ALTER TABLE accounts ADD COLUMN payment_method TEXT")
                print("数据库迁移：添加 payment_method 列")
            
            # 添加 handler 列（如果不存在）
            if 'handler' not in columns:
                self.cursor.execute("ALTER TABLE accounts ADD COLUMN handler TEXT")
                print("数据库迁移：添加 handler 列")
            
            # 获取categories表的列信息
            self.cursor.execute("PRAGMA table_info(categories)")
            cat_columns = [row[1] for row in self.cursor.fetchall()]
            if 'sort_order' not in cat_columns:
                self.cursor.execute("ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 0")
                print("数据库迁移：添加 sort_order 列到 categories")
                self.conn.commit()
                # 为现有分类分配排序顺序
                self._assign_sort_order_to_categories()
            
            # 获取payment_methods表的列信息
            self.cursor.execute("PRAGMA table_info(payment_methods)")
            pm_columns = [row[1] for row in self.cursor.fetchall()]
            if 'sort_order' not in pm_columns:
                self.cursor.execute("ALTER TABLE payment_methods ADD COLUMN sort_order INTEGER DEFAULT 0")
                print("数据库迁移：添加 sort_order 列到 payment_methods")
                self.conn.commit()
                # 为现有支付方式分配排序顺序
                self._assign_sort_order_to_payment_methods()
            
            # 获取handlers表的列信息
            self.cursor.execute("PRAGMA table_info(handlers)")
            h_columns = [row[1] for row in self.cursor.fetchall()]
            if 'sort_order' not in h_columns:
                self.cursor.execute("ALTER TABLE handlers ADD COLUMN sort_order INTEGER DEFAULT 0")
                print("数据库迁移：添加 sort_order 列到 handlers")
                self.conn.commit()
                # 为现有经手人分配排序顺序
                self._assign_sort_order_to_handlers()
            
            self.conn.commit()
        except Exception as e:
            print(f"数据库迁移失败: {e}")
    
    def create_indexes(self):
        """创建索引优化查询性能"""
        try:
            # accounts表索引
            indexes = [
                ("idx_accounts_user_id", "CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id)"),
                ("idx_accounts_date", "CREATE INDEX IF NOT EXISTS idx_accounts_date ON accounts(date)"),
                ("idx_accounts_type", "CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(type)"),
                ("idx_accounts_user_date", "CREATE INDEX IF NOT EXISTS idx_accounts_user_date ON accounts(user_id, date)"),
                ("idx_accounts_deleted", "CREATE INDEX IF NOT EXISTS idx_accounts_deleted ON accounts(deleted_at)"),
                
                # categories表索引
                ("idx_categories_user_id", "CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id)"),
                ("idx_categories_type", "CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type)"),
                
                # payment_methods表索引
                ("idx_payment_methods_user_id", "CREATE INDEX IF NOT EXISTS idx_payment_methods_user_id ON payment_methods(user_id)"),
                
                # handlers表索引
                ("idx_handlers_user_id", "CREATE INDEX IF NOT EXISTS idx_handlers_user_id ON handlers(user_id)"),
            ]
            
            for name, sql in indexes:
                try:
                    self.cursor.execute(sql)
                except Exception as e:
                    print(f"创建索引 {name} 失败: {e}")
            
            self.conn.commit()
            print("数据库索引创建完成")
        except Exception as e:
            print(f"创建索引失败: {e}")
    
    def _assign_sort_order_to_categories(self):
        """为现有分类分配排序顺序（按名称字母顺序）"""
        try:
            # 按user_id和type分组，按名称排序后分配sort_order
            self.cursor.execute("""
                SELECT id, user_id, type, name FROM categories 
                WHERE sort_order = 0 OR sort_order IS NULL
                ORDER BY user_id, type, name
            """)
            categories = self.cursor.fetchall()
            
            # 按组分配排序
            current_group = None
            order = 0
            for cat in categories:
                cat_id, user_id, type_, name = cat
                if (user_id, type_) != current_group:
                    current_group = (user_id, type_)
                    order = 0
                self.cursor.execute(
                    "UPDATE categories SET sort_order = ? WHERE id = ?",
                    (order, cat_id)
                )
                order += 1
            self.conn.commit()
        except Exception as e:
            print(f"分配分类排序失败: {e}")
    
    def _assign_sort_order_to_payment_methods(self):
        """为现有支付方式分配排序顺序"""
        try:
            self.cursor.execute("""
                SELECT id, user_id, name FROM payment_methods 
                WHERE sort_order = 0 OR sort_order IS NULL
                ORDER BY user_id, name
            """)
            methods = self.cursor.fetchall()
            
            current_user = None
            order = 0
            for method in methods:
                method_id, user_id, name = method
                if user_id != current_user:
                    current_user = user_id
                    order = 0
                self.cursor.execute(
                    "UPDATE payment_methods SET sort_order = ? WHERE id = ?",
                    (order, method_id)
                )
                order += 1
            self.conn.commit()
        except Exception as e:
            print(f"分配支付方式排序失败: {e}")
    
    def _assign_sort_order_to_handlers(self):
        """为现有经手人分配排序顺序"""
        try:
            self.cursor.execute("""
                SELECT id, user_id, name FROM handlers 
                WHERE sort_order = 0 OR sort_order IS NULL
                ORDER BY user_id, name
            """)
            handlers = self.cursor.fetchall()
            
            current_user = None
            order = 0
            for handler in handlers:
                handler_id, user_id, name = handler
                if user_id != current_user:
                    current_user = user_id
                    order = 0
                self.cursor.execute(
                    "UPDATE handlers SET sort_order = ? WHERE id = ?",
                    (order, handler_id)
                )
                order += 1
            self.conn.commit()
        except Exception as e:
            print(f"分配经手人排序失败: {e}")
    
    def init_default_user(self):
        """初始化默认管理员账户"""
        self.cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            # 创建默认管理员账户
            password_hash = self.hash_password("123456")
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                ("admin", password_hash, datetime.now().isoformat())
            )
            self.conn.commit()
    
    def init_default_categories(self):
        """初始化默认分类"""
        default_categories = {
            '收入': ['工资', '奖金', '投资收益', '兼职', '其他收入'],
            '支出': ['餐饮', '交通', '购物', '医疗', '教育', '娱乐', '住房', '通讯', '其他支出']
        }
        for type_, categories in default_categories.items():
            for idx, cat in enumerate(categories):
                try:
                    self.cursor.execute("SELECT id FROM users")
                    for row in self.cursor.fetchall():
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO categories (user_id, name, type, sort_order) VALUES (?, ?, ?, ?)",
                            (row['id'], cat, type_, idx)
                        )
                except:
                    pass
        self.conn.commit()
    
    def init_default_payment_methods(self):
        """初始化默认支付方式"""
        default_payment_methods = ['现金', '微信', '支付宝', '银行卡', '信用卡', '花呗', '白条', '转账', '其他']
        try:
            self.cursor.execute("SELECT id FROM users")
            for row in self.cursor.fetchall():
                for idx, pm in enumerate(default_payment_methods):
                    try:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO payment_methods (user_id, name, sort_order) VALUES (?, ?, ?)",
                            (row['id'], pm, idx)
                        )
                    except:
                        pass
            self.conn.commit()
        except Exception as e:
            print(f"初始化支付方式失败: {e}")
    
    def init_default_handlers(self):
        """初始化默认经手人"""
        default_handlers = ['爸爸', '妈妈', '爷爷', '奶奶', '孩子', '其他']
        try:
            self.cursor.execute("SELECT id FROM users")
            for row in self.cursor.fetchall():
                for idx, h in enumerate(default_handlers):
                    try:
                        self.cursor.execute(
                            "INSERT OR IGNORE INTO handlers (user_id, name, sort_order) VALUES (?, ?, ?)",
                            (row['id'], h, idx)
                        )
                    except:
                        pass
            self.conn.commit()
        except Exception as e:
            print(f"初始化经手人失败: {e}")
    
    # ==================== 用户相关操作 ====================
    
    @staticmethod
    def hash_password(password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        """验证用户登录"""
        password_hash = self.hash_password(password)
        self.cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户信息"""
        self.cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def register_user(self, username, password):
        """注册新用户"""
        if not username or not password:
            return False, "账户和密码不能为空"
        
        if len(username) < 3:
            return False, "账户至少3个字符"
        
        if len(password) < 6:
            return False, "密码至少6个字符"
        
        password_hash = self.hash_password(password)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, datetime.now().isoformat())
            )
            user_id = self.cursor.lastrowid
            
            # 为新用户创建默认分类
            default_categories = {
                '收入': ['工资', '奖金', '投资收益', '兼职', '其他收入'],
                '支出': ['餐饮', '交通', '购物', '医疗', '教育', '娱乐', '住房', '通讯', '其他支出']
            }
            for type_, categories in default_categories.items():
                for idx, cat in enumerate(categories):
                    self.cursor.execute(
                        "INSERT INTO categories (user_id, name, type, sort_order) VALUES (?, ?, ?, ?)",
                        (user_id, cat, type_, idx)
                    )
            
            # 为新用户创建默认支付方式
            default_payment_methods = ['现金', '微信', '支付宝', '银行卡', '信用卡', '花呗', '白条', '转账', '其他']
            for idx, pm in enumerate(default_payment_methods):
                self.cursor.execute(
                    "INSERT INTO payment_methods (user_id, name, sort_order) VALUES (?, ?, ?)",
                    (user_id, pm, idx)
                )
            
            # 为新用户创建默认经手人
            default_handlers = ['爸爸', '妈妈', '爷爷', '奶奶', '孩子', '其他']
            for idx, h in enumerate(default_handlers):
                self.cursor.execute(
                    "INSERT INTO handlers (user_id, name, sort_order) VALUES (?, ?, ?)",
                    (user_id, h, idx)
                )
            
            self.conn.commit()
            return True, "注册成功"
        except sqlite3.IntegrityError:
            return False, "账户已存在"
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def get_user(self, user_id):
        """获取用户信息"""
        self.cursor.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_users(self):
        """获取所有用户列表"""
        self.cursor.execute("SELECT username FROM users ORDER BY id")
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_all_users_info(self):
        """获取所有用户详细信息"""
        self.cursor.execute("SELECT id, username, created_at FROM users ORDER BY id")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_user_by_username(self, username):
        """根据用户名获取用户信息"""
        self.cursor.execute("SELECT id, username, created_at FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def change_password(self, user_id, new_password):
        """修改用户密码"""
        try:
            password_hash = self.hash_password(new_password)
            self.cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (password_hash, user_id)
            )
            if self.cursor.rowcount == 0:
                return False, "用户不存在"
            self.conn.commit()
            return True, "密码修改成功"
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    def change_password_by_username(self, username, new_password):
        """根据用户名修改密码（管理员功能）"""
        try:
            password_hash = self.hash_password(new_password)
            self.cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (password_hash, username)
            )
            if self.cursor.rowcount == 0:
                return False, "用户不存在"
            self.conn.commit()
            return True, f"用户 {username} 的密码修改成功"
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    def delete_user(self, user_id, admin_user_id):
        """删除用户（管理员功能）"""
        try:
            # 检查是否是管理员
            self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()
            if user and user['username'] == 'admin':
                return False, "不能删除管理员账户"
            
            # 删除用户的收支记录
            self.cursor.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
            # 删除用户的分类
            self.cursor.execute("DELETE FROM categories WHERE user_id = ?", (user_id,))
            # 删除用户
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            return True, "用户删除成功"
        except Exception as e:
            self.conn.rollback()
            return False, f"删除失败: {str(e)}"
    
    def is_admin(self, user_id):
        """检查用户是否是管理员"""
        self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result and result['username'] == 'admin'
    
    @staticmethod
    def get_currency_symbol(currency_code):
        """获取货币符号"""
        return CURRENCIES.get(currency_code, CURRENCIES['CNY'])['symbol']
    
    @staticmethod
    def get_currencies():
        """获取所有货币列表"""
        return CURRENCIES
    
    # ==================== 账户相关操作 ====================
    
    def add_account(self, user_id, name, type_, amount, category, description, date, currency='CNY', payment_method=None, handler=None):
        """添加账户记录"""
        try:
            self.cursor.execute("""
                INSERT INTO accounts (user_id, name, type, amount, currency, category, description, payment_method, handler, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, type_, amount, currency, category, description, payment_method, handler, date, datetime.now().isoformat()))
            self.conn.commit()
            return True, "添加成功"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def get_accounts(self, user_id, include_deleted=False, page=1, page_size=50):
        """获取用户的所有账户记录（分页）"""
        offset = (page - 1) * page_size
        
        if include_deleted:
            query = """
                SELECT * FROM accounts WHERE user_id = ? ORDER BY date DESC, created_at DESC
                LIMIT ? OFFSET ?
            """
        else:
            query = """
                SELECT * FROM accounts WHERE user_id = ? AND deleted_at IS NULL ORDER BY date DESC, created_at DESC
                LIMIT ? OFFSET ?
            """
        self.cursor.execute(query, (user_id, page_size, offset))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_accounts_count(self, user_id, include_deleted=False):
        """获取账户记录总数"""
        if include_deleted:
            query = "SELECT COUNT(*) as count FROM accounts WHERE user_id = ?"
        else:
            query = "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND deleted_at IS NULL"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchone()['count']
    
    def get_accounts_count_by_type(self, user_id, type_):
        """按类型获取账户记录数量"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND type = ? AND deleted_at IS NULL",
            (user_id, type_)
        )
        return self.cursor.fetchone()['count']
    
    def get_accounts_by_type(self, user_id, type_, page=1, page_size=50):
        """按类型获取账户记录（分页）"""
        offset = (page - 1) * page_size
        self.cursor.execute(
            "SELECT * FROM accounts WHERE user_id = ? AND type = ? AND deleted_at IS NULL ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?",
            (user_id, type_, page_size, offset)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_accounts_by_date_range(self, user_id, start_date, end_date, page=1, page_size=50):
        """按日期范围获取账户记录（分页）"""
        offset = (page - 1) * page_size
        self.cursor.execute(
            "SELECT * FROM accounts WHERE user_id = ? AND date >= ? AND date <= ? AND deleted_at IS NULL ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?",
            (user_id, start_date, end_date, page_size, offset)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_accounts_count_by_date_range(self, user_id, start_date, end_date):
        """按日期范围获取账户记录数量"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND date >= ? AND date <= ? AND deleted_at IS NULL",
            (user_id, start_date, end_date)
        )
        return self.cursor.fetchone()['count']
    
    def get_accounts_by_date_range_and_type(self, user_id, start_date, end_date, type_, page=1, page_size=50):
        """按日期范围和类型获取账户记录（分页）"""
        offset = (page - 1) * page_size
        self.cursor.execute(
            "SELECT * FROM accounts WHERE user_id = ? AND date >= ? AND date <= ? AND type = ? AND deleted_at IS NULL ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?",
            (user_id, start_date, end_date, type_, page_size, offset)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_accounts_count_by_date_range_and_type(self, user_id, start_date, end_date, type_):
        """按日期范围和类型获取账户记录数量"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND date >= ? AND date <= ? AND type = ? AND deleted_at IS NULL",
            (user_id, start_date, end_date, type_)
        )
        return self.cursor.fetchone()['count']
    
    def get_statistics_by_date_range_and_type(self, user_id, start_date, end_date, type_):
        """按日期范围和类型获取统计（收入或支出）"""
        query = "SELECT SUM(amount) as total FROM accounts WHERE user_id = ? AND date >= ? AND date <= ? AND type = ? AND deleted_at IS NULL"
        self.cursor.execute(query, (user_id, start_date, end_date, type_))
        result = self.cursor.fetchone()
        return result['total'] or 0 if result else 0
    
    def get_statistics_by_date_range(self, user_id, start_date, end_date):
        """按日期范围获取统计数据"""
        query = """
            SELECT 
                SUM(CASE WHEN type = '收入' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = '支出' THEN amount ELSE 0 END) as expense
            FROM accounts 
            WHERE user_id = ? AND date >= ? AND date <= ? AND deleted_at IS NULL
        """
        self.cursor.execute(query, (user_id, start_date, end_date))
        result = self.cursor.fetchone()
        if result:
            income = result['income'] or 0
            expense = result['expense'] or 0
            return {'income': income, 'expense': expense, 'balance': income - expense}
        return {'income': 0, 'expense': 0, 'balance': 0}
    
    def get_statistics_by_type(self, user_id, type_=None):
        """按类型获取统计数据"""
        if type_ is None:
            query = """
                SELECT 
                    SUM(CASE WHEN type = '收入' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type = '支出' THEN amount ELSE 0 END) as expense
                FROM accounts WHERE user_id = ? AND deleted_at IS NULL
            """
            self.cursor.execute(query, (user_id,))
        else:
            query = "SELECT SUM(amount) as total FROM accounts WHERE user_id = ? AND type = ? AND deleted_at IS NULL"
            self.cursor.execute(query, (user_id, type_))
        
        result = self.cursor.fetchone()
        if result:
            if type_ is None:
                income = result['income'] or 0
                expense = result['expense'] or 0
                return {'income': income, 'expense': expense, 'balance': income - expense}
            else:
                return result['total'] or 0
        return 0 if type_ else {'income': 0, 'expense': 0, 'balance': 0}
    
    def update_account(self, account_id, user_id, name, type_, amount, category, description, date, currency='CNY', payment_method=None, handler=None):
        """更新账户记录"""
        try:
            self.cursor.execute("""
                UPDATE accounts SET name=?, type=?, amount=?, currency=?, category=?, description=?, payment_method=?, handler=?, date=?
                WHERE id=? AND user_id=? AND deleted_at IS NULL
            """, (name, type_, amount, currency, category, description, payment_method, handler, date, account_id, user_id))
            if self.cursor.rowcount == 0:
                return False, "记录不存在或已删除"
            self.conn.commit()
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def soft_delete_account(self, account_id, user_id):
        """软删除账户记录"""
        try:
            self.cursor.execute("""
                UPDATE accounts SET deleted_at=?, deleted_by=?
                WHERE id=? AND user_id=? AND deleted_at IS NULL
            """, (datetime.now().isoformat(), user_id, account_id, user_id))
            if self.cursor.rowcount == 0:
                return False, "记录不存在或已删除"
            self.conn.commit()
            return True, "已移到回收站"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def restore_account(self, account_id, user_id):
        """恢复已删除的账户记录"""
        try:
            self.cursor.execute("""
                UPDATE accounts SET deleted_at=NULL, deleted_by=NULL
                WHERE id=? AND deleted_at IS NOT NULL
            """, (account_id,))
            if self.cursor.rowcount == 0:
                return False, "记录不存在"
            self.conn.commit()
            return True, "恢复成功"
        except Exception as e:
            return False, f"恢复失败: {str(e)}"
    
    def permanent_delete_account(self, account_id):
        """永久删除账户记录"""
        try:
            self.cursor.execute("DELETE FROM accounts WHERE id=? AND deleted_at IS NOT NULL", (account_id,))
            if self.cursor.rowcount == 0:
                return False, "记录不存在"
            self.conn.commit()
            return True, "永久删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_deleted_accounts(self, user_id, page=1, page_size=50):
        """获取回收站中的记录（分页）"""
        offset = (page - 1) * page_size
        self.cursor.execute("""
            SELECT * FROM accounts WHERE user_id = ? AND deleted_at IS NOT NULL ORDER BY deleted_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, page_size, offset))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_deleted_accounts_count(self, user_id):
        """获取回收站记录总数"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND deleted_at IS NOT NULL",
            (user_id,)
        )
        return self.cursor.fetchone()['count']
    
    def get_deleted_accounts_count_by_type(self, user_id, type_):
        """按类型获取回收站记录数量"""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM accounts WHERE user_id = ? AND type = ? AND deleted_at IS NOT NULL",
            (user_id, type_)
        )
        return self.cursor.fetchone()['count']
    
    def get_deleted_accounts_by_type(self, user_id, type_, page=1, page_size=50):
        """按类型获取回收站记录（分页）"""
        offset = (page - 1) * page_size
        self.cursor.execute("""
            SELECT * FROM accounts WHERE user_id = ? AND type = ? AND deleted_at IS NOT NULL ORDER BY deleted_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, type_, page_size, offset))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def empty_recycle_bin(self, user_id):
        """清空回收站"""
        try:
            self.cursor.execute(
                "DELETE FROM accounts WHERE user_id = ? AND deleted_at IS NOT NULL",
                (user_id,)
            )
            self.conn.commit()
            return True, f"已清空回收站，删除了{self.cursor.rowcount}条记录"
        except Exception as e:
            return False, f"清空失败: {str(e)}"
    
    # ==================== 统计相关操作 ====================
    
    def get_statistics(self, user_id, start_date=None, end_date=None):
        """获取收支统计"""
        query = """
            SELECT type, SUM(amount) as total FROM accounts 
            WHERE user_id = ? AND deleted_at IS NULL
        """
        params = [user_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY type"
        
        self.cursor.execute(query, params)
        stats = {}
        for row in self.cursor.fetchall():
            stats[row['type']] = row['total']
        
        return {
            'income': stats.get('收入', 0),
            'expense': stats.get('支出', 0),
            'balance': stats.get('收入', 0) - stats.get('支出', 0)
        }
    
    def get_category_statistics(self, user_id, type_, start_date=None, end_date=None):
        """按分类统计"""
        query = """
            SELECT category, SUM(amount) as total FROM accounts 
            WHERE user_id = ? AND type = ? AND deleted_at IS NULL
        """
        params = [user_id, type_]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY category ORDER BY total DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_monthly_statistics(self, user_id, year=None, month=None):
        """获取月度统计"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        # 获取该月的所有记录
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        query = """
            SELECT type, category, SUM(amount) as total, COUNT(*) as count
            FROM accounts 
            WHERE user_id = ? AND deleted_at IS NULL AND date >= ? AND date < ?
            GROUP BY type, category
            ORDER BY type, total DESC
        """
        self.cursor.execute(query, (user_id, start_date, end_date))
        
        results = []
        for row in self.cursor.fetchall():
            results.append({
                'type': row['type'],
                'category': row['category'],
                'total': row['total'],
                'count': row['count']
            })
        
        return results
    
    def get_monthly_trend(self, user_id, months=6):
        """获取月度趋势（最近N个月）"""
        results = []
        now = datetime.now()
        
        for i in range(months - 1, -1, -1):
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1
            
            stats = self.get_monthly_statistics(user_id, year, month)
            
            income = sum(s['total'] for s in stats if s['type'] == '收入')
            expense = sum(s['total'] for s in stats if s['type'] == '支出')
            
            results.append({
                'year': year,
                'month': month,
                'label': f"{year}-{month:02d}",
                'income': income,
                'expense': expense,
                'balance': income - expense
            })
        
        return results
    
    def get_category_statistics_for_chart(self, user_id, type_, start_date=None, end_date=None):
        """获取分类统计数据（用于图表）"""
        stats = self.get_category_statistics(user_id, type_, start_date, end_date)
        total = sum(s['total'] for s in stats) if stats else 0
        
        if total == 0:
            return []
        
        results = []
        for s in stats:
            percentage = (s['total'] / total) * 100
            results.append({
                'category': s['category'],
                'amount': s['total'],
                'percentage': percentage
            })
        
        return results
    
    def get_daily_statistics(self, user_id, start_date, end_date):
        """获取每日统计"""
        query = """
            SELECT date, type, SUM(amount) as total
            FROM accounts 
            WHERE user_id = ? AND deleted_at IS NULL AND date >= ? AND date <= ?
            GROUP BY date, type
            ORDER BY date
        """
        self.cursor.execute(query, (user_id, start_date, end_date))
        
        results = {}
        for row in self.cursor.fetchall():
            date = row['date']
            if date not in results:
                results[date] = {'date': date, 'income': 0, 'expense': 0}
            if row['type'] == '收入':
                results[date]['income'] = row['total']
            else:
                results[date]['expense'] = row['total']
        
        return list(results.values())
    
    # ==================== 分类管理 ====================
    
    def get_categories(self, user_id, type_=None):
        """获取用户的分类列表"""
        if type_:
            self.cursor.execute(
                "SELECT id, name, type, sort_order FROM categories WHERE user_id = ? AND type = ? ORDER BY sort_order, name",
                (user_id, type_)
            )
        else:
            self.cursor.execute(
                "SELECT id, name, type, sort_order FROM categories WHERE user_id = ? ORDER BY type, sort_order, name",
                (user_id,)
            )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_income_categories(self, user_id):
        """获取用户的收入分类"""
        self.cursor.execute(
            "SELECT name FROM categories WHERE user_id = ? AND type = '收入' ORDER BY sort_order, name",
            (user_id,)
        )
        return [row['name'] for row in self.cursor.fetchall()]
    
    def get_expense_categories(self, user_id):
        """获取用户的支出分类"""
        self.cursor.execute(
            "SELECT name FROM categories WHERE user_id = ? AND type = '支出' ORDER BY sort_order, name",
            (user_id,)
        )
        return [row['name'] for row in self.cursor.fetchall()]
    
    def add_category(self, user_id, name, type_):
        """添加分类（添加到末尾）"""
        try:
            # 获取当前最大sort_order
            self.cursor.execute(
                "SELECT MAX(sort_order) FROM categories WHERE user_id = ? AND type = ?",
                (user_id, type_)
            )
            max_order = self.cursor.fetchone()[0] or 0
            new_order = max_order + 1
            
            self.cursor.execute(
                "INSERT INTO categories (user_id, name, type, sort_order) VALUES (?, ?, ?, ?)",
                (user_id, name, type_, new_order)
            )
            self.conn.commit()
            return True, "添加成功"
        except sqlite3.IntegrityError:
            return False, "分类已存在"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_category(self, category_id, name):
        """修改分类"""
        try:
            self.cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (name, category_id)
            )
            if self.cursor.rowcount == 0:
                return False, "分类不存在"
            self.conn.commit()
            return True, "修改成功"
        except sqlite3.IntegrityError:
            return False, "分类已存在"
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    def delete_category(self, category_id):
        """删除分类"""
        try:
            self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            if self.cursor.rowcount == 0:
                return False, "分类不存在"
            self.conn.commit()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def move_category_up(self, user_id, category_id, type_):
        """将分类上移"""
        try:
            # 获取所有分类，按当前排序
            self.cursor.execute(
                "SELECT id FROM categories WHERE user_id = ? AND type = ? ORDER BY sort_order, name",
                (user_id, type_)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前分类的位置
            if category_id not in all_ids:
                return False, "分类不存在"
            
            current_idx = all_ids.index(category_id)
            
            if current_idx <= 0:
                return False, "已在最上端"
            
            # 交换位置
            all_ids[current_idx - 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx - 1]
            
            # 重新分配sort_order值
            for idx, cat_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE categories SET sort_order = ? WHERE id = ?",
                    (idx, cat_id)
                )
            
            self.conn.commit()
            return True, "上移成功"
        except Exception as e:
            return False, f"上移失败: {str(e)}"
    
    def move_category_down(self, user_id, category_id, type_):
        """将分类下移"""
        try:
            # 获取所有分类，按当前排序
            self.cursor.execute(
                "SELECT id FROM categories WHERE user_id = ? AND type = ? ORDER BY sort_order, name",
                (user_id, type_)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前分类的位置
            if category_id not in all_ids:
                return False, "分类不存在"
            
            current_idx = all_ids.index(category_id)
            
            if current_idx >= len(all_ids) - 1:
                return False, "已在最下端"
            
            # 交换位置
            all_ids[current_idx + 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx + 1]
            
            # 重新分配sort_order值
            for idx, cat_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE categories SET sort_order = ? WHERE id = ?",
                    (idx, cat_id)
                )
            
            self.conn.commit()
            return True, "下移成功"
        except Exception as e:
            return False, f"下移失败: {str(e)}"
    
    # ==================== 支付方式管理 ====================
    
    def get_payment_methods(self, user_id):
        """获取用户的支付方式列表"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM payment_methods WHERE user_id = ? ORDER BY sort_order, name",
            (user_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_payment_method_names(self, user_id):
        """获取用户的支付方式名称列表"""
        self.cursor.execute(
            "SELECT name FROM payment_methods WHERE user_id = ? ORDER BY sort_order, name",
            (user_id,)
        )
        return [row['name'] for row in self.cursor.fetchall()]
    
    def add_payment_method(self, user_id, name):
        """添加支付方式（添加到末尾）"""
        try:
            # 获取当前最大sort_order
            self.cursor.execute(
                "SELECT MAX(sort_order) FROM payment_methods WHERE user_id = ?",
                (user_id,)
            )
            max_order = self.cursor.fetchone()[0] or 0
            new_order = max_order + 1
            
            self.cursor.execute(
                "INSERT INTO payment_methods (user_id, name, sort_order) VALUES (?, ?, ?)",
                (user_id, name, new_order)
            )
            self.conn.commit()
            return True, "添加成功"
        except sqlite3.IntegrityError:
            return False, "支付方式已存在"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_payment_method(self, method_id, name):
        """修改支付方式"""
        try:
            self.cursor.execute(
                "UPDATE payment_methods SET name = ? WHERE id = ?",
                (name, method_id)
            )
            if self.cursor.rowcount == 0:
                return False, "支付方式不存在"
            self.conn.commit()
            return True, "修改成功"
        except sqlite3.IntegrityError:
            return False, "支付方式已存在"
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    def delete_payment_method(self, method_id):
        """删除支付方式"""
        try:
            self.cursor.execute("DELETE FROM payment_methods WHERE id = ?", (method_id,))
            if self.cursor.rowcount == 0:
                return False, "支付方式不存在"
            self.conn.commit()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def move_payment_method_up(self, user_id, method_id):
        """将支付方式上移"""
        try:
            # 获取所有支付方式，按当前排序
            self.cursor.execute(
                "SELECT id FROM payment_methods WHERE user_id = ? ORDER BY sort_order, name",
                (user_id,)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前项的位置
            if method_id not in all_ids:
                return False, "支付方式不存在"
            
            current_idx = all_ids.index(method_id)
            
            if current_idx <= 0:
                return False, "已在最上端"
            
            # 交换位置
            all_ids[current_idx - 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx - 1]
            
            # 重新分配sort_order值
            for idx, m_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE payment_methods SET sort_order = ? WHERE id = ?",
                    (idx, m_id)
                )
            
            self.conn.commit()
            return True, "上移成功"
        except Exception as e:
            return False, f"上移失败: {str(e)}"
    
    def move_payment_method_down(self, user_id, method_id):
        """将支付方式下移"""
        try:
            # 获取所有支付方式，按当前排序
            self.cursor.execute(
                "SELECT id FROM payment_methods WHERE user_id = ? ORDER BY sort_order, name",
                (user_id,)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前项的位置
            if method_id not in all_ids:
                return False, "支付方式不存在"
            
            current_idx = all_ids.index(method_id)
            
            if current_idx >= len(all_ids) - 1:
                return False, "已在最下端"
            
            # 交换位置
            all_ids[current_idx + 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx + 1]
            
            # 重新分配sort_order值
            for idx, m_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE payment_methods SET sort_order = ? WHERE id = ?",
                    (idx, m_id)
                )
            
            self.conn.commit()
            return True, "下移成功"
        except Exception as e:
            return False, f"下移失败: {str(e)}"
    
    # ==================== 经手人管理 ====================
    
    def get_handlers(self, user_id):
        """获取用户的经手人列表"""
        self.cursor.execute(
            "SELECT id, name, sort_order FROM handlers WHERE user_id = ? ORDER BY sort_order, name",
            (user_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_handler_names(self, user_id):
        """获取用户的经手人名称列表"""
        self.cursor.execute(
            "SELECT name FROM handlers WHERE user_id = ? ORDER BY sort_order, name",
            (user_id,)
        )
        return [row['name'] for row in self.cursor.fetchall()]
    
    def add_handler(self, user_id, name):
        """添加经手人（添加到末尾）"""
        try:
            # 获取当前最大sort_order
            self.cursor.execute(
                "SELECT MAX(sort_order) FROM handlers WHERE user_id = ?",
                (user_id,)
            )
            max_order = self.cursor.fetchone()[0] or 0
            new_order = max_order + 1
            
            self.cursor.execute(
                "INSERT INTO handlers (user_id, name, sort_order) VALUES (?, ?, ?)",
                (user_id, name, new_order)
            )
            self.conn.commit()
            return True, "添加成功"
        except sqlite3.IntegrityError:
            return False, "经手人已存在"
        except Exception as e:
            return False, f"添加失败: {str(e)}"
    
    def update_handler(self, handler_id, name):
        """修改经手人"""
        try:
            self.cursor.execute(
                "UPDATE handlers SET name = ? WHERE id = ?",
                (name, handler_id)
            )
            if self.cursor.rowcount == 0:
                return False, "经手人不存在"
            self.conn.commit()
            return True, "修改成功"
        except sqlite3.IntegrityError:
            return False, "经手人已存在"
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    def delete_handler(self, handler_id):
        """删除经手人"""
        try:
            self.cursor.execute("DELETE FROM handlers WHERE id = ?", (handler_id,))
            if self.cursor.rowcount == 0:
                return False, "经手人不存在"
            self.conn.commit()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def move_handler_up(self, user_id, handler_id):
        """将经手人上移"""
        try:
            # 获取所有经手人，按当前排序
            self.cursor.execute(
                "SELECT id FROM handlers WHERE user_id = ? ORDER BY sort_order, name",
                (user_id,)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前项的位置
            if handler_id not in all_ids:
                return False, "经手人不存在"
            
            current_idx = all_ids.index(handler_id)
            
            if current_idx <= 0:
                return False, "已在最上端"
            
            # 交换位置
            all_ids[current_idx - 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx - 1]
            
            # 重新分配sort_order值
            for idx, h_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE handlers SET sort_order = ? WHERE id = ?",
                    (idx, h_id)
                )
            
            self.conn.commit()
            return True, "上移成功"
        except Exception as e:
            return False, f"上移失败: {str(e)}"
    
    def move_handler_down(self, user_id, handler_id):
        """将经手人下移"""
        try:
            # 获取所有经手人，按当前排序
            self.cursor.execute(
                "SELECT id FROM handlers WHERE user_id = ? ORDER BY sort_order, name",
                (user_id,)
            )
            all_ids = [row['id'] for row in self.cursor.fetchall()]
            
            # 找到当前项的位置
            if handler_id not in all_ids:
                return False, "经手人不存在"
            
            current_idx = all_ids.index(handler_id)
            
            if current_idx >= len(all_ids) - 1:
                return False, "已在最下端"
            
            # 交换位置
            all_ids[current_idx + 1], all_ids[current_idx] = all_ids[current_idx], all_ids[current_idx + 1]
            
            # 重新分配sort_order值
            for idx, h_id in enumerate(all_ids):
                self.cursor.execute(
                    "UPDATE handlers SET sort_order = ? WHERE id = ?",
                    (idx, h_id)
                )
            
            self.conn.commit()
            return True, "下移成功"
        except Exception as e:
            return False, f"下移失败: {str(e)}"
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
