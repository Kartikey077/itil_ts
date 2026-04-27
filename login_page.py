import sys
import os
import json
import re
import random
import hashlib
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer

# ---------------- MYSQL CONFIG ----------------
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Kai*123"
MYSQL_DB = "kaiticket"

try:
    import mysql.connector
    from mysql.connector import errorcode
except Exception as e:
    raise RuntimeError(
        "mysql-connector-python is required but not installed or importable. "
        "Install it (pip install mysql-connector-python) and ensure MySQL server is reachable."
    )

DB_FILE = "accounts.json"

# ---------------- HELPERS: PASSWORD, STRENGTH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def password_strength(password):
    length = len(password) >= 8
    upper = re.search(r"[A-Z]", password)
    lower = re.search(r"[a-z]", password)
    digit = re.search(r"\d", password)
    score = sum([length, bool(upper), bool(lower), bool(digit)])
    if score <= 1:
        return "Weak", "#ef4444"
    elif score == 2:
        return "Medium", "#f59e0b"
    else:
        return "Strong", "#10b981"

def is_valid_password(password):
    return password_strength(password)[0] == "Strong"

def generate_password():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&"
    return "".join(random.choice(chars) for _ in range(10))

# ---------------- MYSQL DATABASE LAYER ----------------
def get_mysql_conn(create_if_missing=True):
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=False
        )
        return conn
    except mysql.connector.Error as err:
        if create_if_missing and getattr(errorcode, "ER_BAD_DB_ERROR", None) and err.errno == errorcode.ER_BAD_DB_ERROR:
            tmp = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
            cur = tmp.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET 'utf8mb4'")
            tmp.commit()
            cur.close()
            tmp.close()
            conn = mysql.connector.connect(
                host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=False
            )
            return conn
        else:
            raise

def init_mysql_schema_and_seed():
    conn = get_mysql_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                username VARCHAR(150) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                first VARCHAR(100),
                last VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                company VARCHAR(255)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                username VARCHAR(150) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                first VARCHAR(100),
                last VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                company VARCHAR(255)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(150) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                first VARCHAR(100),
                last VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                company VARCHAR(255)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_number VARCHAR(50),
                created_at VARCHAR(50),
                user_name VARCHAR(255),
                user_email VARCHAR(255),
                user_department VARCHAR(255),
                contact_phone VARCHAR(50),
                ticket_type VARCHAR(50),
                service VARCHAR(255),
                category VARCHAR(255),
                subcategory VARCHAR(255),
                impact VARCHAR(50),
                urgency VARCHAR(50),
                priority VARCHAR(50),
                subject TEXT,
                description TEXT,
                attachments TEXT,
                occurrence_date VARCHAR(50),
                occurrence_time VARCHAR(50),
                business_hours BOOLEAN,
                related_tickets TEXT,
                assignment_group VARCHAR(255),
                status VARCHAR(50)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_details (
                employee_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                department VARCHAR(100),
                role VARCHAR(100),
                join_date DATE,
                status VARCHAR(50),
                avatar VARCHAR(255),
                last_login DATETIME,
                INDEX idx_email (email),
                INDEX idx_username (username)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ticket_assignments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_number VARCHAR(50),
                employee_id VARCHAR(50),
                assigned_date DATETIME,
                status VARCHAR(50),
                last_updated DATETIME,
                comments TEXT,
                INDEX idx_ticket (ticket_number),
                INDEX idx_employee (employee_id)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(50),
                task_date DATE,
                task_title VARCHAR(255),
                task_description TEXT,
                task_status VARCHAR(50) DEFAULT 'Pending',
                created_at DATETIME,
                updated_at DATETIME,
                INDEX idx_employee_date (employee_id, task_date)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                category VARCHAR(100),
                content TEXT,
                views INT DEFAULT 0,
                helpful_count INT DEFAULT 0,
                not_helpful_count INT DEFAULT 0,
                created_at DATETIME,
                INDEX idx_category (category)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_activity_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(50),
                activity_type VARCHAR(100),
                activity_description TEXT,
                activity_date DATETIME,
                INDEX idx_employee_date (employee_id, activity_date)
            )
        """)

        seeds = {
            "admins": {
                "admin": {
                    "password": hash_password("admin123"),
                    "first": "System",
                    "last": "Admin",
                    "email": "admin@kaiticket.com",
                    "phone": "9999999999",
                    "company": "Kaiticket"
                }
            },
            "employees": {
                "emp1": {
                    "password": hash_password("emp123"),
                    "first": "Kartikey",
                    "last": "Rai",
                    "email": "kai@company.com",
                    "phone": "1234567890",
                    "company": ""
                },
                "emp2": {
                    "password": hash_password("emp456"),
                    "first": "Ankur",
                    "last": "Rai",
                    "email": "Anur@company.com",
                    "phone": "9876543210",
                    "company": ""
                },
                "emp3": {
                    "password": hash_password("emp789"),
                    "first": "Divye",
                    "last": "Chaudhary",
                    "email": "rr.brown@company.com",
                    "phone": "5556667777",
                    "company": ""
                }
            },
            "users": {
                "user1": {
                    "password": hash_password("Pass1word"),
                    "first": "Dev",
                    "last": "Rajput",
                    "email": "singhal@example.com",
                    "phone": "1112223333",
                    "company": "singhal builders"
                }
            }
        }

        for table, accounts in seeds.items():
            for username, info in accounts.items():
                cur.execute(
                    f"""INSERT INTO {table}
                        (username,password,first,last,email,phone,company)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            password=VALUES(password),
                            first=VALUES(first),
                            last=VALUES(last),
                            email=VALUES(email),
                            phone=VALUES(phone),
                            company=VALUES(company)
                    """,
                    (username, info["password"], info.get("first", ""), info.get("last", ""),
                     info.get("email", ""), info.get("phone", ""), info.get("company", ""))
                )
        
        employee_details_seeds = [
            ("EMP001", "emp1", "Kartikey Rai", "kai@company.com", "1234567890", "IT Support", "Support Agent", "2024-01-15", "Active"),
            ("EMP002", "emp2", "Ankur Rai", "Anur@company.com", "9876543210", "Network Support", "Network Engineer", "2024-02-01", "Active"),
            ("EMP003", "emp3", "Divye Chaudhary", "rr.brown@company.com", "5556667777", "Hardware Support", "Hardware Specialist", "2024-03-10", "Active"),
        ]
        
        for emp in employee_details_seeds:
            cur.execute("""
                INSERT INTO employee_details (employee_id, username, name, email, phone, department, role, join_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name), email = VALUES(email), phone = VALUES(phone),
                    department = VALUES(department), role = VALUES(role), status = VALUES(status)
            """, emp)
        
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def load_db():
    init_mysql_schema_and_seed()
    conn = get_mysql_conn()
    cur = conn.cursor(dictionary=True)
    data = {"admins": {}, "employees": {}, "users": {}}
    try:
        cur.execute("SELECT username,password,first,last,email,phone,company FROM admins")
        for row in cur.fetchall():
            data["admins"][row["username"]] = {
                "password": row["password"],
                "first": row.get("first", "") or "",
                "last": row.get("last", "") or "",
                "email": row.get("email", "") or "",
                "phone": row.get("phone", "") or "",
                "company": row.get("company", "") or ""
            }
        cur.execute("SELECT username,password,first,last,email,phone,company FROM employees")
        for row in cur.fetchall():
            data["employees"][row["username"]] = {
                "password": row["password"],
                "first": row.get("first", "") or "",
                "last": row.get("last", "") or "",
                "email": row.get("email", "") or "",
                "phone": row.get("phone", "") or "",
                "company": row.get("company", "") or ""
            }
        cur.execute("SELECT username,password,first,last,email,phone,company FROM users")
        for row in cur.fetchall():
            data["users"][row["username"]] = {
                "password": row["password"],
                "first": row.get("first", "") or "",
                "last": row.get("last", "") or "",
                "email": row.get("email", "") or "",
                "phone": row.get("phone", "") or "",
                "company": row.get("company", "") or ""
            }
    finally:
        cur.close()
        conn.close()
    return data

def save_db(data):
    conn = get_mysql_conn()
    cur = conn.cursor()
    try:
        for table in ("admins", "employees", "users"):
            accounts = data.get(table, {})
            for username, info in accounts.items():
                if isinstance(info, dict):
                    password = info.get("password") or ""
                    first = info.get("first", "")
                    last = info.get("last", "")
                    email = info.get("email", "")
                    phone = info.get("phone", "")
                    company = info.get("company", "")
                    cur.execute(
                        f"""INSERT INTO {table}
                            (username,password,first,last,email,phone,company)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            ON DUPLICATE KEY UPDATE
                                password=VALUES(password),
                                first=VALUES(first),
                                last=VALUES(last),
                                email=VALUES(email),
                                phone=VALUES(phone),
                                company=VALUES(company)
                        """,
                        (username, password, first, last, email, phone, company)
                    )
                else:
                    password = str(info)
                    cur.execute(
                        f"""INSERT INTO {table}
                            (username,password,first,last,email,phone,company)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                            ON DUPLICATE KEY UPDATE password=VALUES(password)
                        """,
                        (username, password, "", "", "", "", "")
                    )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

db = load_db()

# ---------------- ADMIN DASHBOARD ----------------
class AdminDashboard(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard - Users & Employees")
        self.resize(1000, 600)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #1e1b4b);
                border-radius: 20px;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 18px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                color: #e2e8f0;
                alternate-background-color: #0f172a;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #8b5cf6;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QtWidgets.QLabel("📊 Registered Users and Employees")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; color: #a78bfa;")
        layout.addWidget(title)

        cols = ["Role", "Username", "First Name", "Last Name", "Email", "Phone", "Company"]
        self.table = QtWidgets.QTableWidget(0, len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        self.refresh()
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setFixedSize(100, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignCenter)

    def refresh(self):
        global db
        db = load_db()
        self.table.setRowCount(0)
        for user, info in db.get('employees', {}).items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            vals = ["Employee", user,
                    info.get('first', ''), info.get('last', ''),
                    info.get('email', ''), info.get('phone', ''),
                    info.get('company', '')]
            for col, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, col, item)
        for user, info in db.get('users', {}).items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            vals = ["User", user,
                    info.get('first', ''), info.get('last', ''),
                    info.get('email', ''), info.get('phone', ''),
                    info.get('company', '')]
            for col, v in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(v)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(row, col, item)


# ---------------- MAIN LOGIN WINDOW ----------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Smart Ticketing System - Login')
        self.setMinimumSize(1200, 750)
        self.showMaximized()
        self.setStyleSheet(self.get_main_style())
        
        self.setup_ui()
        self.setup_animations()

    def get_main_style(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0e27, stop:0.5 #1a1a3e, stop:1 #0f172a);
            }
            QWidget {
                background: transparent;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 14px;
                color: #f1f5f9;
                selection-background-color: #8b5cf6;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
            }
            QLineEdit:hover {
                border-color: #a78bfa;
            }
            QLineEdit::placeholder {
                color: #64748b;
                font-size: 13px;
            }
            QComboBox {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 14px;
                color: #f1f5f9;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #8b5cf6;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #8b5cf6;
                margin-right: 12px;
            }
            QPushButton {
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 15px;
                padding: 14px 28px;
                cursor: pointer;
            }
            QPushButton#signinBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: white;
            }
            QPushButton#signinBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #5b21b6);
            }
            QPushButton#signupBtn {
                background: transparent;
                color: #c4b5fd;
                border: 2px solid #8b5cf6;
            }
            QPushButton#signupBtn:hover {
                background: rgba(139, 92, 246, 0.15);
                color: #a78bfa;
            }
            QPushButton#backBtn {
                background: rgba(51, 65, 85, 0.9);
                color: #e2e8f0;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton#backBtn:hover {
                background: #475569;
                color: white;
            }
            QRadioButton {
                color: #cbd5e1;
                font-size: 14px;
                spacing: 10px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #8b5cf6;
                background: transparent;
            }
            QRadioButton::indicator:checked {
                background: #8b5cf6;
                border-color: #a78bfa;
            }
            QCheckBox {
                color: #94a3b8;
                font-size: 13px;
                spacing: 10px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid #8b5cf6;
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #8b5cf6;
            }
            QLabel {
                color: #e2e8f0;
            }
            QLabel#errorLabel {
                color: #ef4444;
                font-size: 12px;
                padding: 5px;
            }
            QLabel#successLabel {
                color: #10b981;
                font-size: 12px;
                padding: 5px;
            }
            QFrame#cardFrame {
                background: rgba(30, 41, 59, 0.85);
                border-radius: 28px;
                border: 1px solid #334155;
            }
            QFrame#leftCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:1 #0f172a);
                border-radius: 28px;
                border: 1px solid #8b5cf6;
            }
        """

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(35)

        # Left Section - Branding
        left_section = self.create_left_section()
        
        # Right Section - Forms
        right_section = self.create_right_section()
        
        main_layout.addWidget(left_section, 1)
        main_layout.addWidget(right_section, 1)

    def create_left_section(self):
        left_widget = QtWidgets.QFrame()
        left_widget.setObjectName("leftCard")
        layout = QtWidgets.QVBoxLayout(left_widget)
        layout.setContentsMargins(35, 45, 35, 45)
        layout.setSpacing(25)
        
        # Logo
        logo_label = QtWidgets.QLabel("🎫")
        logo_label.setFont(QtGui.QFont("Segoe UI", 52))
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Title
        title = QtWidgets.QLabel("Smart Ticketing")
        title.setFont(QtGui.QFont("Segoe UI", 26, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #a78bfa;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QtWidgets.QLabel("Enterprise IT Service Management")
        subtitle.setFont(QtGui.QFont("Segoe UI", 13))
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Divider
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet("background-color: #334155; max-height: 1px;")
        layout.addWidget(divider)
        
        layout.addSpacing(15)
        
        # Features
        features = [
            ("🚀", "AI-Powered Ticket Routing"),
            ("📊", "Real-time Analytics Dashboard"),
            ("🔒", "Bank-Grade Security"),
            ("🤖", "24/7 Smart Chatbot Support"),
            ("⚡", "Automated Workflows"),
            ("📱", "Multi-Platform Access")
        ]
        
        for icon, text in features:
            feature_widget = QtWidgets.QWidget()
            feature_layout = QtWidgets.QHBoxLayout(feature_widget)
            feature_layout.setContentsMargins(0, 10, 0, 10)
            
            icon_label = QtWidgets.QLabel(icon)
            icon_label.setFont(QtGui.QFont("Segoe UI", 20))
            icon_label.setFixedWidth(40)
            
            text_label = QtWidgets.QLabel(text)
            text_label.setFont(QtGui.QFont("Segoe UI", 12))
            text_label.setStyleSheet("color: #cbd5e1;")
            
            feature_layout.addWidget(icon_label)
            feature_layout.addWidget(text_label)
            feature_layout.addStretch()
            
            layout.addWidget(feature_widget)
        
        layout.addStretch()
        
        # Version info
        version_label = QtWidgets.QLabel("Version 2.0.0")
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(version_label)
        
        return left_widget

    def create_right_section(self):
        right_widget = QtWidgets.QFrame()
        right_widget.setObjectName("cardFrame")
        layout = QtWidgets.QVBoxLayout(right_widget)
        layout.setContentsMargins(40, 35, 40, 40)
        layout.setSpacing(20)

        # Back button - FIXED: Made larger and more visible
        back_btn = QtWidgets.QPushButton("← Back to Home")
        back_btn.setObjectName("backBtn")
        back_btn.setFixedSize(150, 42)
        back_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_btn.clicked.connect(self.go_home)
        layout.addWidget(back_btn, alignment=QtCore.Qt.AlignLeft)

        # Stacked widget for Login/Register
        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack)
        
        # Create pages
        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()
        
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        
        layout.addStretch()
        
        return right_widget

    def create_login_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(22)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Title
        title = QtWidgets.QLabel("Welcome Back!")
        title.setFont(QtGui.QFont("Segoe UI", 26, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #a78bfa;")
        layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Sign in to access your account")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(15)
        
        # Role Selection
        role_label = QtWidgets.QLabel("Login as:")
        role_label.setFont(QtGui.QFont("Segoe UI", 14, QtGui.QFont.Bold))
        role_label.setStyleSheet("color: #e2e8f0; margin-bottom: 5px;")
        layout.addWidget(role_label)
        
        role_widget = QtWidgets.QWidget()
        role_layout = QtWidgets.QHBoxLayout(role_widget)
        role_layout.setSpacing(25)
        
        self.role_group = QtWidgets.QButtonGroup()
        roles = ['Admin', 'Employee', 'User']
        for r in roles:
            btn = QtWidgets.QRadioButton(r)
            btn.setStyleSheet("color: #cbd5e1; font-size: 14px; padding: 5px;")
            self.role_group.addButton(btn)
            role_layout.addWidget(btn)
            if r == 'User':
                btn.setChecked(True)
        
        role_layout.addStretch()
        layout.addWidget(role_widget)
        
        layout.addSpacing(10)
        
        # Username
        username_label = QtWidgets.QLabel("Username")
        username_label.setStyleSheet("color: #cbd5e1; font-size: 13px; margin-bottom: 5px;")
        layout.addWidget(username_label)
        
        self.entry_user = QtWidgets.QLineEdit()
        self.entry_user.setPlaceholderText("Enter your username")
        self.entry_user.setMinimumHeight(48)
        layout.addWidget(self.entry_user)
        
        # Password
        password_label = QtWidgets.QLabel("Password")
        password_label.setStyleSheet("color: #cbd5e1; font-size: 13px; margin-bottom: 5px;")
        layout.addWidget(password_label)
        
        self.entry_pass = QtWidgets.QLineEdit()
        self.entry_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.entry_pass.setPlaceholderText("Enter your password")
        self.entry_pass.setMinimumHeight(48)
        layout.addWidget(self.entry_pass)
        
        # Show password
        self.show_pass_cb = QtWidgets.QCheckBox("Show Password")
        self.show_pass_cb.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.show_pass_cb.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.show_pass_cb)
        
        layout.addSpacing(10)
        
        # Sign In Button
        self.signin_btn = QtWidgets.QPushButton("SIGN IN")
        self.signin_btn.setObjectName("signinBtn")
        self.signin_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.signin_btn.setMinimumHeight(50)
        self.signin_btn.clicked.connect(self.login_action)
        layout.addWidget(self.signin_btn)
        
        layout.addSpacing(10)
        
        # Sign Up link
        signup_text = QtWidgets.QLabel("Don't have an account?")
        signup_text.setAlignment(QtCore.Qt.AlignCenter)
        signup_text.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout.addWidget(signup_text)
        
        self.signup_link = QtWidgets.QLabel("Create an Account")
        self.signup_link.setAlignment(QtCore.Qt.AlignCenter)
        self.signup_link.setStyleSheet("color: #a78bfa; text-decoration: underline; font-size: 14px; font-weight: bold;")
        self.signup_link.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.signup_link.mousePressEvent = lambda e: self.show_register()
        layout.addWidget(self.signup_link)
        
        layout.addStretch()
        
        return page

    def create_register_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(18)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Title
        title = QtWidgets.QLabel("Create Account")
        title.setFont(QtGui.QFont("Segoe UI", 26, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color: #a78bfa;")
        layout.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Join the Smart Ticketing System")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Scroll area for register form
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QtWidgets.QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QtWidgets.QVBoxLayout(scroll_content)
        form_layout.setSpacing(18)
        
        # 2-column layout for better organization
        row1 = QtWidgets.QWidget()
        row1_layout = QtWidgets.QHBoxLayout(row1)
        row1_layout.setSpacing(20)
        
        # First Name
        first_widget = QtWidgets.QWidget()
        first_layout = QtWidgets.QVBoxLayout(first_widget)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(8)
        first_label = QtWidgets.QLabel("First Name *")
        first_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_first = QtWidgets.QLineEdit()
        self.reg_first.setPlaceholderText("Enter first name")
        self.reg_first.setMinimumHeight(44)
        first_layout.addWidget(first_label)
        first_layout.addWidget(self.reg_first)
        
        # Last Name
        last_widget = QtWidgets.QWidget()
        last_layout = QtWidgets.QVBoxLayout(last_widget)
        last_layout.setContentsMargins(0, 0, 0, 0)
        last_layout.setSpacing(8)
        last_label = QtWidgets.QLabel("Last Name *")
        last_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_last = QtWidgets.QLineEdit()
        self.reg_last.setPlaceholderText("Enter last name")
        self.reg_last.setMinimumHeight(44)
        last_layout.addWidget(last_label)
        last_layout.addWidget(self.reg_last)
        
        row1_layout.addWidget(first_widget)
        row1_layout.addWidget(last_widget)
        form_layout.addWidget(row1)
        
        # Email
        email_label = QtWidgets.QLabel("Email Address *")
        email_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_email = QtWidgets.QLineEdit()
        self.reg_email.setPlaceholderText("your@email.com")
        self.reg_email.setMinimumHeight(44)
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.reg_email)
        
        # Phone & Company row
        row2 = QtWidgets.QWidget()
        row2_layout = QtWidgets.QHBoxLayout(row2)
        row2_layout.setSpacing(20)
        
        phone_widget = QtWidgets.QWidget()
        phone_layout = QtWidgets.QVBoxLayout(phone_widget)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(8)
        phone_label = QtWidgets.QLabel("Phone Number *")
        phone_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_phone = QtWidgets.QLineEdit()
        self.reg_phone.setPlaceholderText("9876543210")
        self.reg_phone.setMinimumHeight(44)
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.reg_phone)
        
        company_widget = QtWidgets.QWidget()
        company_layout = QtWidgets.QVBoxLayout(company_widget)
        company_layout.setContentsMargins(0, 0, 0, 0)
        company_layout.setSpacing(8)
        company_label = QtWidgets.QLabel("Company Name *")
        company_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_company = QtWidgets.QLineEdit()
        self.reg_company.setPlaceholderText("Your company")
        self.reg_company.setMinimumHeight(44)
        company_layout.addWidget(company_label)
        company_layout.addWidget(self.reg_company)
        
        row2_layout.addWidget(phone_widget)
        row2_layout.addWidget(company_widget)
        form_layout.addWidget(row2)
        
        # Username
        username_label = QtWidgets.QLabel("Username *")
        username_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        self.reg_user = QtWidgets.QLineEdit()
        self.reg_user.setPlaceholderText("Choose a username")
        self.reg_user.setMinimumHeight(44)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.reg_user)
        
        # Password
        pass_label = QtWidgets.QLabel("Password *")
        pass_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        form_layout.addWidget(pass_label)
        
        password_widget = QtWidgets.QWidget()
        password_layout = QtWidgets.QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(10)
        
        self.reg_pass = QtWidgets.QLineEdit()
        self.reg_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.reg_pass.setPlaceholderText("Enter password")
        self.reg_pass.setMinimumHeight(44)
        
        self.eye_pass_btn = QtWidgets.QPushButton("👁️")
        self.eye_pass_btn.setFixedSize(50, 44)
        self.eye_pass_btn.setStyleSheet("background: #1e293b; border: 2px solid #334155; border-radius: 10px; font-size: 18px;")
        self.eye_pass_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.eye_pass_btn.clicked.connect(self.toggle_reg_pass)
        
        password_layout.addWidget(self.reg_pass)
        password_layout.addWidget(self.eye_pass_btn)
        form_layout.addWidget(password_widget)
        
        # Confirm Password
        confirm_label = QtWidgets.QLabel("Confirm Password *")
        confirm_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        form_layout.addWidget(confirm_label)
        
        confirm_widget = QtWidgets.QWidget()
        confirm_layout = QtWidgets.QHBoxLayout(confirm_widget)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(10)
        
        self.reg_confirm = QtWidgets.QLineEdit()
        self.reg_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        self.reg_confirm.setPlaceholderText("Confirm your password")
        self.reg_confirm.setMinimumHeight(44)
        
        self.eye_confirm_btn = QtWidgets.QPushButton("👁️")
        self.eye_confirm_btn.setFixedSize(50, 44)
        self.eye_confirm_btn.setStyleSheet("background: #1e293b; border: 2px solid #334155; border-radius: 10px; font-size: 18px;")
        self.eye_confirm_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.eye_confirm_btn.clicked.connect(self.toggle_reg_confirm)
        
        confirm_layout.addWidget(self.reg_confirm)
        confirm_layout.addWidget(self.eye_confirm_btn)
        form_layout.addWidget(confirm_widget)
        
        # Password Strength
        self.strength_lbl = QtWidgets.QLabel("Password Strength: ")
        self.strength_lbl.setStyleSheet("font-size: 12px; margin-top: 5px;")
        form_layout.addWidget(self.strength_lbl)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Register Button
        self.register_btn = QtWidgets.QPushButton("REGISTER")
        self.register_btn.setObjectName("signinBtn")
        self.register_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.register_btn.setMinimumHeight(50)
        self.register_btn.clicked.connect(self.save_user)
        layout.addWidget(self.register_btn)
        
        # Back to Login
        back_to_login = QtWidgets.QLabel("← Back to Login")
        back_to_login.setAlignment(QtCore.Qt.AlignCenter)
        back_to_login.setStyleSheet("color: #a78bfa; text-decoration: underline; font-size: 13px; cursor: pointer; padding: 10px;")
        back_to_login.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        back_to_login.mousePressEvent = lambda e: self.show_login()
        layout.addWidget(back_to_login)
        
        # Connect validation signals
        self.reg_pass.textChanged.connect(self.check_strength)
        self.reg_email.textChanged.connect(self.check_email)
        self.reg_confirm.textChanged.connect(self.check_confirm)
        
        return page

    def setup_animations(self):
        """Setup animations for smooth transitions"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(600)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    # ---------------- UI Helpers ----------------
    def toggle_password(self):
        if self.show_pass_cb.isChecked():
            self.entry_pass.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.entry_pass.setEchoMode(QtWidgets.QLineEdit.Password)

    def toggle_reg_pass(self):
        mode = self.reg_pass.echoMode()
        self.reg_pass.setEchoMode(QtWidgets.QLineEdit.Normal if mode == QtWidgets.QLineEdit.Password else QtWidgets.QLineEdit.Password)

    def toggle_reg_confirm(self):
        mode = self.reg_confirm.echoMode()
        self.reg_confirm.setEchoMode(QtWidgets.QLineEdit.Normal if mode == QtWidgets.QLineEdit.Password else QtWidgets.QLineEdit.Password)

    def show_admin_dashboard(self):
        dlg = AdminDashboard(self)
        dlg.exec_()

    def msgbox(self, kind, title, text):
        msg = QtWidgets.QMessageBox(self)
        if kind in ('warning',):
            msg.setIcon(QtWidgets.QMessageBox.Warning)
        elif kind in ('critical', 'error'):
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        elif kind in ('information', 'info', 'success'):
            msg.setIcon(QtWidgets.QMessageBox.Information)
        else:
            msg.setIcon(QtWidgets.QMessageBox.NoIcon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e293b;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 90px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        msg.exec_()

    # ---------------- VALIDATION ----------------
    def check_strength(self):
        pwd = self.reg_pass.text()
        s, color = password_strength(pwd)
        self.strength_lbl.setText(f'Password Strength: {s}')
        self.strength_lbl.setStyleSheet(f'color:{color}; font-size: 12px; font-weight: bold; margin-top: 5px;')
        self.reg_pass.setStyleSheet(f'background:#1e293b; color:white; border:2px solid {color}; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;')

    def check_email(self):
        email = self.reg_email.text().strip()
        if re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            self.reg_email.setStyleSheet('background:#1e293b; color:white; border:2px solid #10b981; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;')
        else:
            self.reg_email.setStyleSheet('background:#1e293b; color:white; border:2px solid #ef4444; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;')

    def check_confirm(self):
        if self.reg_confirm.text() == self.reg_pass.text() and self.reg_pass.text():
            self.reg_confirm.setStyleSheet('background:#1e293b; color:white; border:2px solid #10b981; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;')
        else:
            self.reg_confirm.setStyleSheet('background:#1e293b; color:white; border:2px solid #ef4444; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;')

    def reset_register_form(self):
        default = 'background:#1e293b; color:white; border:2px solid #334155; border-radius:12px; padding: 12px 16px; font-size: 14px; min-height: 20px;'
        self.reg_email.setStyleSheet(default)
        self.reg_pass.setStyleSheet(default)
        self.reg_confirm.setStyleSheet(default)
        self.strength_lbl.setText('Password Strength: ')
        self.strength_lbl.setStyleSheet('color:#94a3b8; font-size:12px;')

    # ---------------- NAVIGATION ----------------
    def show_register(self):
        role_btn = self.role_group.checkedButton()
        if role_btn and role_btn.text() != 'User':
            self.msgbox('critical', 'Error', 'Only Users can register! Admins and Employees cannot sign up.')
            return
        self.reset_register_form()
        self.stack.setCurrentIndex(1)

    def show_login(self):
        self.stack.setCurrentIndex(0)
        
    def go_home(self):
        self.controller.show_home()

    # ---------------- LOGIN ACTION ----------------
    def login_action(self):
        global db
        db = load_db()
        role_btn = self.role_group.checkedButton()
        if role_btn is None:
            self.msgbox('warning', 'Missing Role', 'Please select a role.')
            return
        role_text = role_btn.text().lower()
        if role_text == 'admin':
            role = 'admins'
        elif role_text == 'employee':
            role = 'employees'
        else:
            role = 'users'

        username = self.entry_user.text().strip()
        password = self.entry_pass.text()
        if not username:
            self.msgbox('warning', 'Missing Field', 'Username must be filled out.')
            return
        if not password:
            self.msgbox('warning', 'Missing Field', 'Password must be filled out.')
            return
        hashed = hash_password(password)
        stored = db.get(role, {}).get(username)
        match = False
        if isinstance(stored, dict):
            match = stored.get('password') == hashed
        elif isinstance(stored, str):
            match = stored == hashed

        if match:
            if isinstance(stored, dict):
                first = stored.get('first') or "N/A"
                last = stored.get('last') or "N/A"
                email = stored.get('email') or "N/A"
                phone = stored.get('phone') or "N/A"
                company = stored.get('company') or "N/A"
            else:
                first = last = email = phone = company = "N/A"

            self.msgbox('information', 'Login Success', f"Welcome {role_btn.text()} {username}!")
            
            if role_btn.text() == 'Admin':
                admin_data = {
                    "name": f"{first} {last}",
                    "email": email,
                    "username": username,
                    "phone": phone,
                    "company": company,
                    "role": "Admin"
                }
                self.controller.show_admin_dashboard(admin_data)
                
            elif role_btn.text() == 'Employee':
                try:
                    from employee_dashboard import EmployeeDashboard
                    employee_data = {
                        "name": f"{first} {last}",
                        "email": email,
                        "username": username,
                        "phone": phone,
                        "company": company,
                        "first_name": first,
                        "last_name": last,
                        "department": company if company != "N/A" else "IT Support",
                        "role": "Support Agent",
                        "employee_id": f"EMP{username}" if username != "N/A" else "EMP001",
                        "join_date": "2024-01-01"
                    }
                    self.controller.show_employee_dashboard(employee_data)
                except ImportError as e:
                    self.msgbox('critical', 'Error', f'Could not load Employee Dashboard: {str(e)}')
                except Exception as e:
                    self.msgbox('critical', 'Error', f'Error launching Employee Dashboard: {str(e)}')
                    
            elif role_btn.text() == 'User':
                try:
                    from user_dashboard import UserDashboard
                    user_data = {
                        "name": f"{first} {last}",
                        "email": email,
                        "department": company,
                        "phone": phone
                    }
                    self.controller.show_dashboard(user_data)
                except ImportError as e:
                    self.msgbox('critical', 'Error', f'Could not load User Dashboard: {str(e)}')
                except Exception as e:
                    self.msgbox('critical', 'Error', f'Error launching User Dashboard: {str(e)}')
        else:
            self.msgbox('critical', 'Error', 'Invalid Username or password')

    # ---------------- REGISTER ACTION ----------------
    def save_user(self):
        global db
        first = self.reg_first.text().strip()
        last = self.reg_last.text().strip()
        email = self.reg_email.text().strip()
        phone = self.reg_phone.text().strip()
        company = self.reg_company.text().strip()
        u = self.reg_user.text().strip()
        p = self.reg_pass.text()
        cp = self.reg_confirm.text()

        if not first:
            self.msgbox('critical', 'Error', "Enter First Name.")
            return
        if not last:
            self.msgbox('critical', 'Error', 'Enter Last Name.')
            return
        if not first.isalpha() or not last.isalpha():
            self.msgbox('critical', 'Error', 'Name must contain only letters.')
            return
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            self.msgbox('critical', 'Error', 'Enter a valid email address.')
            return
        if not phone.isdigit() or len(phone) < 10:
            self.msgbox('critical', 'Error', 'Enter a valid phone number (at least 10 digits).')
            return
        if not company:
            self.msgbox('critical', 'Error', 'Company name is required.')
            return
        if not u:
            self.msgbox('critical', 'Error', 'Enter username.')
            return

        db = load_db()
        if u in db.get('users', {}):
            self.msgbox('critical', 'Error', 'User already exists!')
            return
        if not is_valid_password(p):
            self.msgbox('critical', 'Error', 'Weak password! Please follow rules.\nPassword must be at least 8 characters with uppercase, lowercase and number.')
            return
        if p != cp:
            self.msgbox('critical', 'Error', 'Passwords do not match!')
            return

        db.setdefault('users', {})[u] = {
            'password': hash_password(p),
            'first': first,
            'last': last,
            'email': email,
            'phone': phone,
            'company': company
        }
        save_db(db)

        self.msgbox('information', 'Success', f'User {u} registered successfully!\n\nYou can now login with your credentials.')

        # Clear fields
        self.reg_first.clear()
        self.reg_last.clear()
        self.reg_email.clear()
        self.reg_phone.clear()
        self.reg_company.clear()
        self.reg_user.clear()
        self.reg_pass.clear()
        self.reg_confirm.clear()

        self.show_login()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    class TempController:
        def show_home(self):
            print("Back pressed")
        def show_admin_dashboard(self, data):
            print("Admin dashboard")
        def show_employee_dashboard(self, data):
            print("Employee dashboard")
        def show_dashboard(self, data):
            print("User dashboard")
    
    win = MainWindow(TempController())
    win.show()
    sys.exit(app.exec_())