import sys
import mysql.connector
from datetime import datetime, date
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QBrush, QColor, QIcon


class EmployeeDashboard(QWidget):
    def __init__(self, employee_data, main_app):
        super().__init__()
        self.main_app = main_app
        # Employee data from database
        if employee_data:
            self.employee_data = employee_data
            self.user_email = employee_data.get('email', '')
            self.user_name = employee_data.get('name', 'Employee')
            self.employee_id = employee_data.get('employee_id', '')
            self.department = employee_data.get('department', '')
            self.role = employee_data.get('role', 'Support Agent')
            self.phone = employee_data.get('phone', '')
            self.join_date = employee_data.get('join_date', '')
        else:
            self.employee_data = {}
            self.user_email = "kai@company.com"
            self.user_name = "Kartikey Rai"
            self.employee_id = "EMP001"
            self.department = "IT Support"
            self.role = "Support Agent"
            self.phone = "+91 98765 43210"
            self.join_date = "2024-01-15"
        
        self.tasks = {}
        self.current_month = QDate.currentDate().month()
        self.current_year = QDate.currentDate().year()
        self.assigned_tickets = []
        self.total_assigned = 0
        self.in_progress = 0
        self.resolved_week = 0
        self.completion_rate = 0
        self.kb_articles = []
        
        self.setWindowTitle("Smart Ticketing System - Employee Portal")
        
        # Apply dark unique theme
        self.apply_dark_unique_theme()
        
        # Initialize database
        self.init_database()
        
        # Load real data from database
        self.load_employee_real_data()
        self.load_assigned_tickets()
        self.load_dashboard_stats()
        self.load_tasks_from_db()
        self.load_knowledge_base()
        
        self.initUI()

    def init_database(self):
        """Initialize database connection and ensure required tables exist"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            cursor.execute("""
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
            
            cursor.execute("""
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
            
            cursor.execute("""
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
            
            cursor.execute("""
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id VARCHAR(50),
                    activity_type VARCHAR(100),
                    activity_description TEXT,
                    activity_date DATETIME,
                    INDEX idx_employee_date (employee_id, activity_date)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("[Database] Tables initialized successfully")
            
            self.insert_sample_knowledge_base()
            
        except Exception as e:
            print(f"[Database] Initialization error: {e}")

    def get_db_connection(self):
        """Establish and return MySQL database connection"""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Kai*123",
                database="kaiticket"
            )
            return conn
        except mysql.connector.Error as err:
            print(f"[Database Error] Connection failed: {err}")
            return None

    def insert_sample_knowledge_base(self):
        """Insert sample knowledge base articles if table is empty"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_base")
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_articles = [
                    ("How to reset user password", "Security", 
                     "Step-by-step guide to reset user passwords:\n1. Login to admin portal\n2. Navigate to Users section\n3. Search for the user\n4. Click 'Reset Password'\n5. Set new temporary password\n6. Notify user of new password", 
                     datetime.now()),
                    ("VPN connection troubleshooting", "Network",
                     "Common VPN issues and solutions:\n- Restart VPN client\n- Check internet connection\n- Verify credentials\n- Clear DNS cache\n- Update VPN software",
                     datetime.now()),
                    ("Email configuration for Outlook", "Email",
                     "Outlook setup instructions:\n1. Open Outlook\n2. Go to File > Add Account\n3. Enter email address\n4. Select manual setup\n5. Configure IMAP/POP3 settings\n6. Test connection",
                     datetime.now()),
                    ("Software installation errors", "Software",
                     "Common software installation fixes:\n- Run as administrator\n- Disable antivirus temporarily\n- Check disk space\n- Install required dependencies\n- Update Windows",
                     datetime.now()),
                    ("Network printer setup", "Hardware",
                     "Printer setup steps:\n1. Connect printer to network\n2. Install drivers\n3. Add printer in Windows\n4. Set as default if needed\n5. Print test page",
                     datetime.now()),
                ]
                
                insert_query = """
                    INSERT INTO knowledge_base (title, category, content, created_at, views, helpful_count, not_helpful_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                for article in sample_articles:
                    cursor.execute(insert_query, (article[0], article[1], article[2], article[3], 0, 0, 0))
                
                conn.commit()
                print("[Database] Sample knowledge base articles inserted")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error inserting sample data: {e}")

    def load_employee_real_data(self):
        """Load real employee data from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            username = self.user_email.split('@')[0]
            
            query = """
                SELECT ed.*, e.password 
                FROM employee_details ed
                JOIN employees e ON ed.username = e.username
                WHERE ed.email = %s OR ed.username = %s
            """
            cursor.execute(query, (self.user_email, username))
            result = cursor.fetchone()
            
            if result:
                self.employee_id = result.get('employee_id', self.employee_id)
                self.user_name = result.get('name', self.user_name)
                self.user_email = result.get('email', self.user_email)
                self.phone = result.get('phone', self.phone)
                self.department = result.get('department', self.department)
                self.role = result.get('role', self.role)
                self.join_date = str(result.get('join_date', self.join_date)) if result.get('join_date') else self.join_date
                
                self.employee_data = {
                    'employee_id': self.employee_id,
                    'name': self.user_name,
                    'email': self.user_email,
                    'phone': self.phone,
                    'department': self.department,
                    'role': self.role,
                    'join_date': self.join_date
                }
                
                update_query = "UPDATE employee_details SET last_login = %s WHERE employee_id = %s"
                cursor.execute(update_query, (datetime.now(), self.employee_id))
                conn.commit()
                
            else:
                insert_query = """
                    INSERT INTO employee_details 
                    (employee_id, username, name, email, phone, department, role, join_date, status, last_login)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name = VALUES(name), email = VALUES(email), phone = VALUES(phone),
                    department = VALUES(department), role = VALUES(role), last_login = VALUES(last_login)
                """
                cursor.execute(insert_query, (
                    self.employee_id, username, self.user_name, self.user_email, 
                    self.phone, self.department, self.role, self.join_date, 'Active', datetime.now()
                ))
                conn.commit()
            
            cursor.close()
            conn.close()
            self.log_employee_activity("Login", "Employee logged into the system")
            
        except Exception as e:
            print(f"[Database] Error loading employee data: {e}")

    def log_employee_activity(self, activity_type, description):
        """Log employee activity to database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            query = """
                INSERT INTO employee_activity_log (employee_id, activity_type, activity_description, activity_date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (self.employee_id, activity_type, description, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error logging activity: {e}")

    def load_assigned_tickets(self):
        """Load tickets assigned to this employee from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT t.ticket_number, t.subject, t.priority, t.status, 
                       t.user_email as requested_by, t.created_at, t.description,
                       ta.assigned_date, ta.comments
                FROM tickets t
                LEFT JOIN ticket_assignments ta ON t.ticket_number = ta.ticket_number
                WHERE ta.employee_id = %s
                ORDER BY ta.assigned_date DESC
            """
            cursor.execute(query, (self.employee_id,))
            self.assigned_tickets = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error loading assigned tickets: {e}")
            self.assigned_tickets = []

    def load_dashboard_stats(self):
        """Load real dashboard statistics from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            query1 = "SELECT COUNT(*) as count FROM ticket_assignments WHERE employee_id = %s"
            cursor.execute(query1, (self.employee_id,))
            self.total_assigned = cursor.fetchone()['count'] or 0
            
            query2 = """
                SELECT COUNT(*) as count 
                FROM ticket_assignments ta
                JOIN tickets t ON ta.ticket_number = t.ticket_number
                WHERE ta.employee_id = %s AND t.status IN ('In Progress', 'Open')
            """
            cursor.execute(query2, (self.employee_id,))
            self.in_progress = cursor.fetchone()['count'] or 0
            
            query3 = """
                SELECT COUNT(*) as count 
                FROM ticket_assignments ta
                JOIN tickets t ON ta.ticket_number = t.ticket_number
                WHERE ta.employee_id = %s 
                AND t.status = 'Resolved'
                AND WEEK(t.created_at) = WEEK(CURDATE())
            """
            cursor.execute(query3, (self.employee_id,))
            self.resolved_week = cursor.fetchone()['count'] or 0
            
            query4 = """
                SELECT 
                    COUNT(CASE WHEN t.status = 'Resolved' THEN 1 END) as resolved,
                    COUNT(*) as total
                FROM ticket_assignments ta
                JOIN tickets t ON ta.ticket_number = t.ticket_number
                WHERE ta.employee_id = %s
            """
            cursor.execute(query4, (self.employee_id,))
            result = cursor.fetchone()
            total = result['total'] if result['total'] > 0 else 1
            self.completion_rate = round((result['resolved'] / total) * 100) if result['resolved'] else 0
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error loading dashboard stats: {e}")
            self.total_assigned = 12
            self.in_progress = 5
            self.resolved_week = 8
            self.completion_rate = 85

    def load_tasks_from_db(self):
        """Load tasks from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT task_date, task_title, task_description, task_status
                FROM employee_tasks
                WHERE employee_id = %s
                ORDER BY task_date DESC
            """
            cursor.execute(query, (self.employee_id,))
            tasks = cursor.fetchall()
            
            self.tasks = {}
            for task in tasks:
                task_date = str(task['task_date'])
                if task_date not in self.tasks:
                    self.tasks[task_date] = []
                self.tasks[task_date].append((
                    task['task_title'],
                    task['task_description'],
                    task['task_status']
                ))
            
            cursor.close()
            conn.close()
            print(f"[Database] Loaded {len(tasks)} tasks")
            
        except Exception as e:
            print(f"[Database] Error loading tasks: {e}")
            self.tasks = {}

    def save_task_to_db(self, task_date, task_title, task_description, task_status='Pending'):
        """Save task to database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            query = """
                INSERT INTO employee_tasks (employee_id, task_date, task_title, task_description, task_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                self.employee_id, task_date, task_title, task_description, 
                task_status, datetime.now(), datetime.now()
            ))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Database] Error saving task: {e}")
            return False

    def update_task_status_in_db(self, task_date, task_title, new_status):
        """Update task status in database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            query = """
                UPDATE employee_tasks 
                SET task_status = %s, updated_at = %s
                WHERE employee_id = %s AND task_date = %s AND task_title = %s
            """
            cursor.execute(query, (new_status, datetime.now(), self.employee_id, task_date, task_title))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Database] Error updating task: {e}")
            return False

    def delete_task_from_db(self, task_date, task_title):
        """Delete task from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            query = """
                DELETE FROM employee_tasks 
                WHERE employee_id = %s AND task_date = %s AND task_title = %s
            """
            cursor.execute(query, (self.employee_id, task_date, task_title))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Database] Error deleting task: {e}")
            return False

    def update_ticket_status_in_db(self, ticket_number, new_status, comments):
        """Update ticket status in database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            query1 = "UPDATE tickets SET status = %s WHERE ticket_number = %s"
            cursor.execute(query1, (new_status, ticket_number))
            
            query2 = """
                UPDATE ticket_assignments 
                SET status = %s, last_updated = %s, comments = CONCAT(IFNULL(comments, ''), %s)
                WHERE ticket_number = %s AND employee_id = %s
            """
            cursor.execute(query2, (new_status, datetime.now(), f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {comments}", ticket_number, self.employee_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            self.log_employee_activity("Ticket Update", f"Updated ticket {ticket_number} to {new_status}")
            return True
            
        except Exception as e:
            print(f"[Database] Error updating ticket: {e}")
            return False

    def update_kb_feedback(self, article_id, is_helpful):
        """Update knowledge base feedback"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            if is_helpful:
                query = "UPDATE knowledge_base SET helpful_count = helpful_count + 1 WHERE id = %s"
            else:
                query = "UPDATE knowledge_base SET not_helpful_count = not_helpful_count + 1 WHERE id = %s"
            
            cursor.execute(query, (article_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[Database] Error updating KB feedback: {e}")
            return False

    def increment_kb_view(self, article_id):
        """Increment knowledge base article view count"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            query = "UPDATE knowledge_base SET views = views + 1 WHERE id = %s"
            cursor.execute(query, (article_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error incrementing view: {e}")

    def load_knowledge_base(self):
        """Load knowledge base articles from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id, title, category, content, views, helpful_count, not_helpful_count FROM knowledge_base ORDER BY views DESC"
            cursor.execute(query)
            self.kb_articles = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Database] Error loading knowledge base: {e}")
            self.kb_articles = []

    def calculate_avg_response_time(self):
        """Calculate average response time from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return "2.4h"
            
            cursor = conn.cursor()
            query = """
                SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, last_updated)) as avg_time
                FROM tickets t
                JOIN ticket_assignments ta ON t.ticket_number = ta.ticket_number
                WHERE ta.employee_id = %s AND last_updated IS NOT NULL
            """
            cursor.execute(query, (self.employee_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0]:
                avg_hours = round(result[0], 1)
                return f"{avg_hours}h"
            return "2.4h"
            
        except Exception as e:
            print(f"[Database] Error calculating response time: {e}")
            return "2.4h"

    def apply_dark_unique_theme(self):
        """Apply dark unique theme with excellent contrast"""
        self.setStyleSheet("""
            /* Main Window - Dark Midnight Blue */
            QWidget {
                background-color: #0a0e27;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                color: #e0e0e0;
            }
            
            /* Header - Deep Indigo */
            QFrame#headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:1 #1e1b4b);
                border-bottom: 3px solid #8b5cf6;
            }
            
            QLabel#headerTitle {
                color: #c4b5fd;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            
            QLabel#headerGreeting {
                color: #a5b4fc;
                font-size: 15px;
                font-weight: 500;
            }
            
            QFrame#verticalSeparator {
                background-color: #8b5cf6;
                max-width: 2px;
                min-width: 2px;
            }
            
            /* Sidebar - Dark Violet */
            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e1b4b);
                border-right: 1px solid #2d2a5e;
            }
            
            /* Navigation Buttons */
            QPushButton {
                color: #94a3b8;
                padding: 12px 16px;
                text-align: left;
                border: none;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                margin: 4px 10px;
                background-color: transparent;
            }
            
            QPushButton:hover {
                background-color: rgba(139, 92, 246, 0.2);
                color: #c4b5fd;
            }
            
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: #ffffff;
                font-weight: bold;
            }
            
            QPushButton#settingsBtn {
                background-color: #1e1b4b;
                border-top: 1px solid #2d2a5e;
                border-radius: 8px;
                margin-top: 20px;
            }
            
            QPushButton#settingsBtn:hover {
                background-color: #8b5cf6;
                color: white;
            }
            
            /* Content Area */
            QWidget#contentArea {
                background-color: #0a0e27;
            }
            
            /* Stat Cards - Dark with border */
            QFrame#statCard {
                background-color: #111827;
                border-radius: 12px;
                border: 1px solid #374151;
            }
            
            QFrame#statCard:hover {
                border-color: #8b5cf6;
            }
            
            QLabel#statValue {
                font-size: 28px;
                font-weight: bold;
            }
            
            QLabel#statLabel {
                font-size: 13px;
                color: #9ca3af;
                font-weight: 500;
            }
            
            /* Tables - Dark theme */
            QTableWidget {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 10px;
                font-size: 13px;
                alternate-background-color: #1f2937;
                gridline-color: #374151;
                color: #e5e7eb;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #374151;
            }
            
            QTableWidget::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #1f2937;
                color: #c4b5fd;
                font-weight: bold;
                font-size: 12px;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #8b5cf6;
            }
            
            /* Calendar - Dark theme */
            QCalendarWidget {
                background-color: #111827;
                border-radius: 10px;
                border: 1px solid #374151;
            }
            
            QCalendarWidget QTableView {
                selection-background-color: #8b5cf6;
                selection-color: white;
                color: #e5e7eb;
            }
            
            QCalendarWidget QHeaderView::section {
                background-color: #1f2937;
                color: #c4b5fd;
                font-weight: bold;
            }
            
            QCalendarWidget QToolButton {
                color: #e5e7eb;
                font-size: 14px;
                font-weight: bold;
            }
            
            QCalendarWidget QMenu {
                background-color: #111827;
                color: #e5e7eb;
            }
            
            /* Input Fields */
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e5e7eb;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #8b5cf6;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #8b5cf6;
                margin-right: 8px;
            }
            
            /* Action Buttons */
            QPushButton#actionBtn {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#actionBtn:hover {
                background-color: #6d28d9;
            }
            
            QPushButton#secondaryBtn {
                background-color: #4c1d95;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton#secondaryBtn:hover {
                background-color: #3b0764;
            }
            
            /* Dialog */
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            
            /* List Widget */
            QListWidget {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 5px;
                color: #e5e7eb;
            }
            
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #374151;
            }
            
            QListWidget::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
            
            /* Group Box */
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #374151;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #111827;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #c4b5fd;
            }
            
            /* Labels */
            QLabel {
                color: #e5e7eb;
            }
            
            /* Menu */
            QMenu {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 5px;
                color: #e5e7eb;
            }
            
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
            
            QMenu::separator {
                background-color: #374151;
                height: 1px;
                margin: 5px 0;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #1f2937;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4c1d95;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #8b5cf6;
            }
            
            QScrollBar:horizontal {
                background-color: #1f2937;
                height: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #4c1d95;
                border-radius: 4px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #8b5cf6;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #374151;
                border-radius: 8px;
                background-color: #111827;
            }
            
            QTabBar::tab {
                background-color: #1f2937;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                color: #9ca3af;
            }
            
            QTabBar::tab:selected {
                background-color: #8b5cf6;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #4c1d95;
                color: white;
            }
        """)

    def initUI(self):
        """Initialize the user interface components"""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        logo_label = QLabel("🎫 Smart Ticketing")
        logo_label.setStyleSheet("""
            color: #a78bfa;
            font-size: 18px;
            font-weight: bold;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-bottom: 2px solid #8b5cf6;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        self.buttons = []
        nav_items = [
            ("🏠 Dashboard", "dashboard"),
            ("👤 My Profile", "profile"),
            ("🎟️ My Tickets", "tickets"),
            ("✅ Tasks", "tasks"),
            ("📅 Calendar", "calendar"),
            ("📚 Knowledge Base", "knowledge")
        ]

        for text, page_id in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, x=page_id, b=btn: self.switch_page(x, b))
            sidebar_layout.addWidget(btn)
            self.buttons.append(btn)
            setattr(self, f"{page_id}_btn", btn)

        sidebar_layout.addStretch()

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(settings_btn)

        # Main Content Area
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentArea")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        title_label = QLabel("Employee Portal")
        title_label.setObjectName("headerTitle")
        
        separator = QFrame()
        separator.setObjectName("verticalSeparator")
        separator.setFrameShape(QFrame.VLine)
        
        greeting_label = QLabel(f"Welcome back, {self.user_name}!")
        greeting_label.setObjectName("headerGreeting")

        header_layout.addWidget(title_label)
        header_layout.addWidget(separator)
        header_layout.addWidget(greeting_label)
        header_layout.addStretch()

        profile_widget = QWidget()
        profile_layout = QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(12)

        employee_info = QLabel(f"{self.role} | {self.department}")
        employee_info.setStyleSheet("color: #a5b4fc; font-size: 12px; background-color: #1e1b4b; padding: 5px 12px; border-radius: 15px;")
        
        email_label = QLabel(self.user_email)
        email_label.setStyleSheet("color: #94a3b8; font-size: 12px;")

        avatar_btn = QPushButton("👤")
        avatar_btn.setFixedSize(40, 40)
        avatar_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 20px;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        avatar_btn.clicked.connect(self.show_profile_menu)

        profile_layout.addWidget(employee_info)
        profile_layout.addWidget(email_label)
        profile_layout.addWidget(avatar_btn)
        header_layout.addWidget(profile_widget)
        
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setFixedHeight(32)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        logout_btn.clicked.connect(self.logout)

        profile_layout.addWidget(logout_btn)

        self.content_layout.addWidget(header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #0a0e27;")
        
        self.stack.addWidget(self.dashboard_page())
        self.stack.addWidget(self.profile_page())
        self.stack.addWidget(self.tickets_page())
        self.stack.addWidget(self.todo_page())
        self.stack.addWidget(self.calendar_page())
        self.stack.addWidget(self.knowledge_base_page())

        self.content_layout.addWidget(self.stack)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_widget)
        self.setLayout(main_layout)
        
        self.dashboard_btn.setChecked(True)

    def dashboard_page(self):
        """Create professional dashboard page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        welcome_header = QLabel(f"Dashboard Overview - {datetime.now().strftime('%B %Y')}")
        welcome_header.setStyleSheet("font-size: 22px; font-weight: bold; color: #c4b5fd;")
        layout.addWidget(welcome_header)

        stats_layout1 = QHBoxLayout()
        stats_layout1.setSpacing(15)

        stats_data = [
            ("🎟️", "Assigned Tickets", str(self.total_assigned), "#8b5cf6"),
            ("⏳", "In Progress", str(self.in_progress), "#f59e0b"),
            ("✅", "Resolved This Week", str(self.resolved_week), "#10b981"),
            ("📊", "Completion Rate", f"{self.completion_rate}%", "#ec4899")
        ]

        for icon, label, value, color in stats_data:
            card = self.create_stat_card(icon, label, value, color)
            stats_layout1.addWidget(card)

        layout.addLayout(stats_layout1)

        recent_label = QLabel("Recent Activity")
        recent_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #c4b5fd; margin-top: 10px;")
        layout.addWidget(recent_label)

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["Ticket ID", "Subject", "Priority", "Status", "Updated"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setMinimumHeight(280)
        
        for row, ticket in enumerate(self.assigned_tickets[:5]):
            self.recent_table.insertRow(row)
            self.recent_table.setItem(row, 0, QTableWidgetItem(ticket['ticket_number']))
            subject = ticket['subject'][:50] + "..." if len(ticket['subject']) > 50 else ticket['subject']
            self.recent_table.setItem(row, 1, QTableWidgetItem(subject))
            
            priority_item = QTableWidgetItem(ticket['priority'])
            if "High" in str(ticket['priority']):
                priority_item.setForeground(QColor("#ef4444"))
            elif "Medium" in str(ticket['priority']):
                priority_item.setForeground(QColor("#f59e0b"))
            else:
                priority_item.setForeground(QColor("#10b981"))
            self.recent_table.setItem(row, 2, priority_item)
            
            status_item = QTableWidgetItem(ticket['status'])
            if "Resolved" in str(ticket['status']):
                status_item.setForeground(QColor("#10b981"))
            elif "Progress" in str(ticket['status']):
                status_item.setForeground(QColor("#8b5cf6"))
            self.recent_table.setItem(row, 3, status_item)
            
            self.recent_table.setItem(row, 4, QTableWidgetItem(str(ticket['assigned_date'])[:10] if ticket['assigned_date'] else "N/A"))
        
        layout.addWidget(self.recent_table)
        layout.addStretch()
        return page

    def create_stat_card(self, icon, label, value, color):
        """Create a professional statistics card"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(110)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        
        label_label = QLabel(label)
        label_label.setObjectName("statLabel")
        
        layout.addWidget(icon_label)
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return card

    def profile_page(self):
        """Create employee profile page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        title = QLabel("My Profile")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #c4b5fd;")
        layout.addWidget(title)

        # Avatar and Basic Info
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setSpacing(30)

        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet("""
            font-size: 80px;
            background-color: #8b5cf6;
            color: white;
            border-radius: 50px;
            padding: 15px;
            min-width: 110px;
            min-height: 110px;
        """)
        avatar_label.setAlignment(Qt.AlignCenter)
        
        basic_info = QWidget()
        basic_layout = QVBoxLayout(basic_info)
        
        name_label = QLabel(self.user_name)
        name_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e5e7eb;")
        
        role_label = QLabel(f"{self.role} • {self.department}")
        role_label.setStyleSheet("font-size: 14px; color: #9ca3af;")
        
        email_label = QLabel(self.user_email)
        email_label.setStyleSheet("font-size: 13px; color: #6b7280;")
        
        status_label = QLabel("● Active")
        status_label.setStyleSheet("font-size: 13px; color: #10b981; font-weight: 500;")
        
        basic_layout.addWidget(name_label)
        basic_layout.addWidget(role_label)
        basic_layout.addWidget(email_label)
        basic_layout.addWidget(status_label)
        
        top_layout.addWidget(avatar_label)
        top_layout.addWidget(basic_info)
        top_layout.addStretch()
        
        layout.addWidget(top_section)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #374151; max-height: 1px; margin: 10px 0;")
        layout.addWidget(divider)

        # Personal Information
        section_title = QLabel("Personal Information")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c4b5fd; margin-top: 10px;")
        layout.addWidget(section_title)

        info_widget = QWidget()
        info_layout = QGridLayout(info_widget)
        info_layout.setSpacing(20)
        info_layout.setVerticalSpacing(15)

        details = [
            ("Full Name:", self.user_name),
            ("Email:", self.user_email),
            ("Employee ID:", self.employee_id),
            ("Role:", self.role),
            ("Department:", self.department),
            ("Phone:", self.phone),
            ("Join Date:", self.join_date),
            ("Location:", "India")
        ]

        for i, (label, value) in enumerate(details):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-size: 13px; font-weight: 600; color: #9ca3af; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("font-size: 13px; color: #e5e7eb; padding: 6px; background-color: #1f2937; border-radius: 6px;")
            info_layout.addWidget(label_widget, i, 0)
            info_layout.addWidget(value_widget, i, 1)

        layout.addWidget(info_widget)

        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setStyleSheet("background-color: #374151; max-height: 1px; margin: 10px 0;")
        layout.addWidget(divider2)

        # Performance Metrics Section
        perf_title = QLabel("Performance Metrics")
        perf_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #c4b5fd; margin-top: 10px;")
        layout.addWidget(perf_title)

        metrics_widget = QWidget()
        metrics_widget.setStyleSheet("""
            QWidget {
                background-color: #1f2937;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        metrics_layout = QHBoxLayout(metrics_widget)
        metrics_layout.setSpacing(20)

        avg_response = self.calculate_avg_response_time()
        
        metrics_data = [
            ("Tickets Resolved", str(self.resolved_week), "#10b981", "✅"),
            ("In Progress", str(self.in_progress), "#f59e0b", "🔄"),
            ("Avg Response Time", avg_response, "#8b5cf6", "⏱️"),
            ("Completion Rate", f"{self.completion_rate}%", "#ec4899", "📈")
        ]

        for metric, value, color, icon in metrics_data:
            metric_card = QFrame()
            metric_card.setStyleSheet(f"""
                QFrame {{
                    background-color: #111827;
                    border-radius: 10px;
                    padding: 12px;
                    border: 1px solid #374151;
                }}
            """)
            metric_layout = QVBoxLayout(metric_card)
            metric_layout.setSpacing(8)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px;")
            
            metric_value = QLabel(value)
            metric_value.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
            
            metric_label = QLabel(metric)
            metric_label.setStyleSheet("font-size: 11px; color: #9ca3af;")
            
            metric_layout.addWidget(icon_label)
            metric_layout.addWidget(metric_value)
            metric_layout.addWidget(metric_label)
            metrics_layout.addWidget(metric_card)

        metrics_layout.addStretch()
        layout.addWidget(metrics_widget)

        edit_btn = QPushButton("✏️ Edit Profile")
        edit_btn.setObjectName("actionBtn")
        edit_btn.setFixedWidth(160)
        edit_btn.setFixedHeight(38)
        edit_btn.clicked.connect(self.edit_profile)
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addStretch()
        layout.addWidget(btn_container)

        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(scroll)

        return container

    def tickets_page(self):
        """Create tickets management page with simple text buttons"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("My Assigned Tickets")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c4b5fd;")
        layout.addWidget(title)

        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        
        filter_label = QLabel("Filter by Status:")
        filter_label.setStyleSheet("font-weight: bold; color: #9ca3af;")
        
        self.ticket_filter = QComboBox()
        self.ticket_filter.addItems(["All Tickets", "Assigned", "In Progress", "On Hold", "Resolved", "Closed"])
        self.ticket_filter.setMinimumWidth(150)
        self.ticket_filter.currentTextChanged.connect(self.filter_tickets)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.clicked.connect(self.refresh_tickets)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.ticket_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_btn)

        layout.addWidget(filter_widget)

        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(8)
        self.tickets_table.setHorizontalHeaderLabels([
            "Ticket ID", "Subject", "Priority", "Status", "Requested By", "Created", "Description", "Actions"
        ])
        self.tickets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setMinimumHeight(400)
        self.tickets_table.verticalHeader().setDefaultSectionSize(45)
        
        self.refresh_tickets_table()
        
        layout.addWidget(self.tickets_table)
        layout.addStretch()
        return page

    def refresh_tickets_table(self):
        """Refresh the tickets table with proper button heights"""
        self.tickets_table.setRowCount(0)
        filter_text = self.ticket_filter.currentText() if hasattr(self, 'ticket_filter') else "All Tickets"
        
        row = 0
        for ticket in self.assigned_tickets:
            if filter_text != "All Tickets" and ticket['status'] != filter_text:
                continue
                
            self.tickets_table.insertRow(row)
            self.tickets_table.setItem(row, 0, QTableWidgetItem(ticket['ticket_number']))
            subject = ticket['subject'][:50] + "..." if len(ticket['subject']) > 50 else ticket['subject']
            self.tickets_table.setItem(row, 1, QTableWidgetItem(subject))
            
            priority_item = QTableWidgetItem(ticket['priority'])
            if "High" in str(ticket['priority']) or "P1" in str(ticket['priority']):
                priority_item.setForeground(QColor("#ef4444"))
            elif "Medium" in str(ticket['priority']) or "P2" in str(ticket['priority']):
                priority_item.setForeground(QColor("#f59e0b"))
            else:
                priority_item.setForeground(QColor("#10b981"))
            self.tickets_table.setItem(row, 2, priority_item)
            
            status_item = QTableWidgetItem(ticket['status'])
            if ticket['status'] == 'Resolved':
                status_item.setForeground(QColor("#10b981"))
            elif ticket['status'] in ['In Progress', 'Open']:
                status_item.setForeground(QColor("#8b5cf6"))
            elif ticket['status'] == 'On Hold':
                status_item.setForeground(QColor("#f59e0b"))
            elif ticket['status'] == 'Closed':
                status_item.setForeground(QColor("#6b7280"))
            else:
                status_item.setForeground(QColor("#ef4444"))
            self.tickets_table.setItem(row, 3, status_item)
            
            self.tickets_table.setItem(row, 4, QTableWidgetItem(ticket['requested_by']))
            self.tickets_table.setItem(row, 5, QTableWidgetItem(str(ticket['created_at'])[:10] if ticket['created_at'] else "N/A"))
            
            # View Description Button - FIXED HEIGHT
            desc_btn = QPushButton("📄 View Description")
            desc_btn.setFlat(True)
            desc_btn.setCursor(Qt.PointingHandCursor)
            desc_btn.setFixedHeight(30)
            desc_btn.setMinimumWidth(120)
            desc_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #a78bfa;
                    border: none;
                    padding: 5px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    color: #c4b5fd;
                    text-decoration: underline;
                }
            """)
            desc_btn.clicked.connect(lambda checked, t=ticket['ticket_number'], d=ticket.get('description', 'No description provided'): self.view_ticket_description(t, d))
            self.tickets_table.setCellWidget(row, 6, desc_btn)
            
            # Update Status Button - FIXED HEIGHT
            update_btn = QPushButton("🔄 Update Status")
            update_btn.setFlat(True)
            update_btn.setCursor(Qt.PointingHandCursor)
            update_btn.setFixedHeight(30)
            update_btn.setMinimumWidth(120)
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #60a5fa;
                    border: none;
                    padding: 5px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    color: #93c5fd;
                    text-decoration: underline;
                }
            """)
            update_btn.clicked.connect(lambda checked, t=ticket['ticket_number']: self.update_ticket_status(t))
            self.tickets_table.setCellWidget(row, 7, update_btn)
            row += 1
    def view_ticket_description(self, ticket_id, description):
        """Open dialog to view full ticket description"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ticket Description - {ticket_id}")
        dialog.setFixedSize(700, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            QLabel {
                color: #e5e7eb;
            }
            QTextEdit {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 12px;
                color: #e5e7eb;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(f"Ticket #{ticket_id} - Description")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #c4b5fd;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        desc_label = QLabel("Full Description:")
        desc_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #9ca3af; margin-top: 10px;")
        layout.addWidget(desc_label)
        
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setPlainText(description if description else "No description provided for this ticket.")
        desc_text.setMinimumHeight(300)
        layout.addWidget(desc_text)
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("actionBtn")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def filter_tickets(self, filter_text):
        self.refresh_tickets_table()

    def refresh_tickets(self):
        self.load_assigned_tickets()
        self.refresh_tickets_table()
        QMessageBox.information(self, "Refresh", "Tickets refreshed successfully!")

    def update_ticket_status(self, ticket_id):
        """Open dialog to update ticket status"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Update Ticket Status - {ticket_id}")
        dialog.setFixedSize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            QLabel {
                color: #e5e7eb;
            }
            QComboBox, QTextEdit {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
                color: #e5e7eb;
                font-size: 13px;
            }
            QComboBox:focus, QTextEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel("🔄")
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(f"Update Status - Ticket #{ticket_id}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #c4b5fd;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        current_status = None
        for ticket in self.assigned_tickets:
            if ticket['ticket_number'] == ticket_id:
                current_status = ticket['status']
                break
        
        if current_status:
            current_status_label = QLabel(f"Current Status: {current_status}")
            current_status_label.setStyleSheet("""
                background-color: #1f2937;
                padding: 8px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                color: #e5e7eb;
            """)
            layout.addWidget(current_status_label)
        
        status_label = QLabel("Select New Status:")
        status_label.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(status_label)
        
        status_combo = QComboBox()
        status_combo.addItems(["In Progress", "On Hold", "Resolved", "Closed"])
        status_combo.setMinimumHeight(35)
        layout.addWidget(status_combo)
        
        comment_label = QLabel("Add Comments (Optional):")
        comment_label.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(comment_label)
        
        comment_text = QTextEdit()
        comment_text.setPlaceholderText("Add your comments, resolution notes, or updates here...")
        comment_text.setMinimumHeight(120)
        layout.addWidget(comment_text)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        update_btn = QPushButton("✓ Update Status")
        update_btn.setObjectName("actionBtn")
        update_btn.setFixedHeight(38)
        
        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c1d95;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3b0764;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        def update():
            new_status = status_combo.currentText()
            comment = comment_text.toPlainText()
            
            confirm = QMessageBox.question(
                dialog,
                "Confirm Update",
                f"Are you sure you want to update ticket {ticket_id}\n"
                f"Status: {current_status} → {new_status}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                if self.update_ticket_status_in_db(ticket_id, new_status, comment):
                    QMessageBox.information(self, "Success", 
                                          f"✅ Ticket {ticket_id} status updated to: {new_status}")
                    self.load_assigned_tickets()
                    self.refresh_tickets_table()
                    self.load_dashboard_stats()
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update ticket status!")
        
        update_btn.clicked.connect(update)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(update_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def todo_page(self):
        """To-Do List page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("My Tasks")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c4b5fd;")
        layout.addWidget(title)

        add_task_btn = QPushButton("➕ Add New Task")
        add_task_btn.setObjectName("actionBtn")
        add_task_btn.setFixedWidth(140)
        add_task_btn.clicked.connect(self.add_new_task)
        layout.addWidget(add_task_btn)

        self.todo_table = QTableWidget()
        self.todo_table.setColumnCount(5)
        self.todo_table.setHorizontalHeaderLabels(["Date", "Task", "Description", "Status", "Actions"])
        self.todo_table.horizontalHeader().setStretchLastSection(True)
        self.todo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.todo_table.setAlternatingRowColors(True)
        self.todo_table.setMinimumHeight(400)
        self.todo_table.verticalHeader().setDefaultSectionSize(50)
        
        layout.addWidget(self.todo_table)
        self.load_tasks_into_table()
        return page

    def load_tasks_into_table(self):
        """Load tasks into table"""
        self.todo_table.setRowCount(0)
        row = 0
        for task_date, items in self.tasks.items():
            for task_data in items:
                task_title = task_data[0]
                task_desc = task_data[1]
                task_status = task_data[2] if len(task_data) > 2 else "Pending"
                    
                self.todo_table.insertRow(row)
                self.todo_table.setItem(row, 0, QTableWidgetItem(task_date))
                self.todo_table.setItem(row, 1, QTableWidgetItem(task_title))
                self.todo_table.setItem(row, 2, QTableWidgetItem(task_desc))
                
                status_combo = QComboBox()
                status_combo.addItems(["Pending", "In Progress", "Completed"])
                status_combo.setCurrentText(task_status)
                status_combo.setMinimumHeight(30)
                status_combo.setStyleSheet("""
                    QComboBox {
                        padding: 5px;
                        border: 1px solid #374151;
                        border-radius: 5px;
                        background-color: #1f2937;
                        color: #e5e7eb;
                    }
                """)
                status_combo.currentTextChanged.connect(
                    lambda checked, d=task_date, t=task_title: self.update_task_status_from_table(d, t)
                )
                self.todo_table.setCellWidget(row, 3, status_combo)
                
                delete_btn = QPushButton("🗑️ Delete")
                delete_btn.setFixedHeight(32)
                delete_btn.setMinimumWidth(80)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 10px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #b91c1c;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, d=task_date, t=task_title: self.delete_task(d, t))
                self.todo_table.setCellWidget(row, 4, delete_btn)
                row += 1

    def update_task_status_from_table(self, date, task):
        """Update task status"""
        for row in range(self.todo_table.rowCount()):
            if self.todo_table.item(row, 0).text() == date and self.todo_table.item(row, 1).text() == task:
                status_combo = self.todo_table.cellWidget(row, 3)
                new_status = status_combo.currentText()
                if self.update_task_status_in_db(date, task, new_status):
                    for i, task_data in enumerate(self.tasks.get(date, [])):
                        if task_data[0] == task:
                            self.tasks[date][i] = (task_data[0], task_data[1], new_status)
                            break
                    self.show_tasks_for_date()
                break

    def delete_task(self, date, task):
        reply = QMessageBox.question(self, 'Delete Task', f'Delete "{task}"?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.delete_task_from_db(date, task):
                if date in self.tasks:
                    self.tasks[date] = [t for t in self.tasks[date] if t[0] != task]
                    if not self.tasks[date]:
                        del self.tasks[date]
                self.load_tasks_into_table()
                self.show_tasks_for_date()

    def calendar_page(self):
        """Calendar page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        calendar_header = QWidget()
        calendar_header_layout = QHBoxLayout(calendar_header)
        
        title = QLabel("Task Calendar")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c4b5fd;")
        
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        
        prev_month_btn = QPushButton("◀")
        prev_month_btn.setFixedSize(35, 35)
        prev_month_btn.setObjectName("secondaryBtn")
        prev_month_btn.clicked.connect(self.prev_month)
        
        self.month_year_label = QLabel(f"{QDate.currentDate().toString('MMMM yyyy')}")
        self.month_year_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #a78bfa; min-width: 150px;")
        self.month_year_label.setAlignment(Qt.AlignCenter)
        
        next_month_btn = QPushButton("▶")
        next_month_btn.setFixedSize(35, 35)
        next_month_btn.setObjectName("secondaryBtn")
        next_month_btn.clicked.connect(self.next_month)
        
        nav_layout.addWidget(prev_month_btn)
        nav_layout.addWidget(self.month_year_label)
        nav_layout.addWidget(next_month_btn)
        
        calendar_header_layout.addWidget(title)
        calendar_header_layout.addStretch()
        calendar_header_layout.addWidget(nav_widget)
        
        layout.addWidget(calendar_header)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #111827;
                border-radius: 10px;
                border: 1px solid #374151;
            }
            QCalendarWidget QTableView {
                qproperty-gridVisible: true;
                selection-background-color: #8b5cf6;
                selection-color: white;
                color: #e5e7eb;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1f2937;
            }
            QCalendarWidget QToolButton {
                color: #e5e7eb;
                background-color: transparent;
                font-size: 13px;
                font-weight: bold;
            }
            QCalendarWidget QSpinBox {
                color: #e5e7eb;
                background-color: #1f2937;
                selection-background-color: #8b5cf6;
            }
        """)
        self.calendar.clicked.connect(self.open_task_dialog)
        self.calendar.selectionChanged.connect(self.show_tasks_for_date)
        layout.addWidget(self.calendar)

        task_label = QLabel("Tasks for Selected Date:")
        task_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #c4b5fd; margin-top: 15px;")
        layout.addWidget(task_label)

        self.task_display = QTextEdit()
        self.task_display.setReadOnly(True)
        self.task_display.setMinimumHeight(120)
        self.task_display.setStyleSheet("background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 10px; color: #e5e7eb;")
        layout.addWidget(self.task_display)

        return page

    def prev_month(self):
        current_date = self.calendar.selectedDate()
        new_date = current_date.addMonths(-1)
        self.calendar.setSelectedDate(new_date)
        self.month_year_label.setText(new_date.toString("MMMM yyyy"))

    def next_month(self):
        current_date = self.calendar.selectedDate()
        new_date = current_date.addMonths(1)
        self.calendar.setSelectedDate(new_date)
        self.month_year_label.setText(new_date.toString("MMMM yyyy"))

    def show_tasks_for_date(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.task_display.clear()
        
        if date in self.tasks:
            self.task_display.append(f"<b style='color:#a78bfa'>Tasks for {date}:</b><br><br>")
            for task_data in self.tasks[date]:
                task_title = task_data[0]
                task_desc = task_data[1]
                task_status = task_data[2] if len(task_data) > 2 else "Pending"
                status_icon = "⏳" if task_status == "Pending" else "🔄" if task_status == "In Progress" else "✅"
                self.task_display.append(f"{status_icon} <b>{task_title}</b><br>   {task_desc}<br><i style='color:#9ca3af'>({task_status})</i><br><br>")
        else:
            self.task_display.append("No tasks scheduled for this date.")

    def open_task_dialog(self, date):
        dialog = QDialog(self)
        dialog.setWindowTitle("Schedule Task")
        dialog.setFixedSize(500, 450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            QLabel { color: #e5e7eb; }
            QLineEdit, QTextEdit {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
                color: #e5e7eb;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        date_str = date.toString("yyyy-MM-dd")
        
        title_label = QLabel(f"Schedule Task for {date_str}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #a78bfa;")
        
        task_input = QLineEdit()
        task_input.setPlaceholderText("Task Title")
        
        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Task Description")
        desc_input.setMinimumHeight(100)
        
        save_btn = QPushButton("Save Task")
        save_btn.setObjectName("actionBtn")
        
        layout.addWidget(title_label)
        layout.addWidget(task_input)
        layout.addWidget(desc_input)
        layout.addWidget(save_btn)

        def save():
            task = task_input.text()
            desc = desc_input.toPlainText()
            
            if task:
                if self.save_task_to_db(date_str, task, desc):
                    if date_str not in self.tasks:
                        self.tasks[date_str] = []
                    self.tasks[date_str].append((task, desc, "Pending"))
                    QMessageBox.information(self, "Success", "Task Added Successfully!")
                    dialog.close()
                    self.load_tasks_into_table()
                    self.show_tasks_for_date()
                else:
                    QMessageBox.warning(self, "Error", "Failed to save task!")

        save_btn.clicked.connect(save)
        dialog.exec_()

    def add_new_task(self):
        current_date = QDate.currentDate()
        self.open_task_dialog(current_date)

    def knowledge_base_page(self):
        """Knowledge base page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("Knowledge Base")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #c4b5fd;")
        layout.addWidget(title)

        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        
        self.kb_search = QLineEdit()
        self.kb_search.setPlaceholderText("Search knowledge base...")
        self.kb_search.setStyleSheet("padding: 10px; border: 1px solid #374151; border-radius: 6px; background-color: #1f2937; color: #e5e7eb;")
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setObjectName("actionBtn")
        search_btn.setFixedWidth(100)
        search_btn.clicked.connect(self.search_kb)
        
        search_layout.addWidget(self.kb_search)
        search_layout.addWidget(search_btn)
        layout.addWidget(search_widget)

        categories = ["All", "Network", "Email", "Software", "Hardware", "Security"]
        category_buttons = QWidget()
        cat_layout = QHBoxLayout(category_buttons)
        
        for cat in categories:
            btn = QPushButton(cat)
            btn.setObjectName("secondaryBtn")
            btn.clicked.connect(lambda checked, c=cat: self.filter_kb_category(c))
            cat_layout.addWidget(btn)
        
        cat_layout.addStretch()
        layout.addWidget(category_buttons)

        self.kb_list = QListWidget()
        for article in self.kb_articles:
            item_text = f"📄 {article['title']} - {article['category']} (Views: {article['views']})"
            self.kb_list.addItem(item_text)
            self.kb_list.item(self.kb_list.count() - 1).setData(Qt.UserRole, article['id'])
        
        self.kb_list.itemDoubleClicked.connect(self.view_kb_article)
        layout.addWidget(self.kb_list)

        return page

    def search_kb(self):
        query = self.kb_search.text().strip().lower()
        if query:
            self.kb_list.clear()
            matches = 0
            for article in self.kb_articles:
                if query in article['title'].lower() or query in article['category'].lower():
                    item_text = f"📄 {article['title']} - {article['category']} (Views: {article['views']})"
                    self.kb_list.addItem(item_text)
                    self.kb_list.item(self.kb_list.count() - 1).setData(Qt.UserRole, article['id'])
                    matches += 1
            if matches == 0:
                self.kb_list.addItem("No matching articles found")
        else:
            self.kb_list.clear()
            for article in self.kb_articles:
                item_text = f"📄 {article['title']} - {article['category']} (Views: {article['views']})"
                self.kb_list.addItem(item_text)
                self.kb_list.item(self.kb_list.count() - 1).setData(Qt.UserRole, article['id'])

    def filter_kb_category(self, category):
        self.kb_list.clear()
        for article in self.kb_articles:
            if category == "All" or article['category'] == category:
                item_text = f"📄 {article['title']} - {article['category']} (Views: {article['views']})"
                self.kb_list.addItem(item_text)
                self.kb_list.item(self.kb_list.count() - 1).setData(Qt.UserRole, article['id'])

    def view_kb_article(self, item):
        article_id = item.data(Qt.UserRole)
        article = None
        for art in self.kb_articles:
            if art['id'] == article_id:
                article = art
                break
        if not article:
            return
        
        self.increment_kb_view(article_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Knowledge Base Article")
        dialog.setFixedSize(700, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            QTextEdit {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 12px;
                color: #e5e7eb;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel(article['title'])
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #c4b5fd;")
        
        category_badge = QLabel(f"Category: {article['category']}")
        category_badge.setStyleSheet("""
            background-color: #8b5cf6;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 11px;
        """)
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(f"<div style='color: #e5e7eb; line-height: 1.5;'>{article['content'].replace(chr(10), '<br>')}</div>")
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("actionBtn")
        close_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(category_badge)
        layout.addWidget(content)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        self.load_knowledge_base()
        self.filter_kb_category("All")

    def switch_page(self, page_id, btn):
        page_map = {
            "dashboard": 0,
            "profile": 1,
            "tickets": 2,
            "tasks": 3,
            "calendar": 4,
            "knowledge": 5
        }
        if page_id in page_map:
            self.stack.setCurrentIndex(page_map[page_id])
        for button in self.buttons:
            button.setChecked(False)
        btn.setChecked(True)

    def edit_profile(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Profile")
        dialog.setFixedSize(500, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #111827;
                border-radius: 12px;
            }
            QLabel { color: #e5e7eb; }
            QLineEdit {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
                color: #e5e7eb;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Edit Profile Information")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #a78bfa;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        name_input = QLineEdit(self.user_name)
        phone_input = QLineEdit(self.phone)
        department_input = QLineEdit(self.department)
        
        form_layout.addRow("Full Name:", name_input)
        form_layout.addRow("Phone:", phone_input)
        form_layout.addRow("Department:", department_input)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("actionBtn")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #4c1d95; color: white; border: none; border-radius: 6px; padding: 8px 20px;")
        
        def save_changes():
            self.user_name = name_input.text()
            self.phone = phone_input.text()
            self.department = department_input.text()
            
            try:
                conn = self.get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    query = "UPDATE employee_details SET name = %s, phone = %s, department = %s WHERE employee_id = %s"
                    cursor.execute(query, (self.user_name, self.phone, self.department, self.employee_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    QMessageBox.information(self, "Success", "Profile updated successfully!")
                    dialog.close()
                    self.update_greeting()
                    self.stack.widget(1).deleteLater()
                    self.stack.insertWidget(1, self.profile_page())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update profile: {e}")
        
        save_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        dialog.exec_()
    
    def update_greeting(self):
        for widget in self.findChildren(QLabel):
            if widget.objectName() == "headerGreeting":
                widget.setText(f"Welcome back, {self.user_name}!")
                break

    def open_settings(self):
        QMessageBox.information(self, "Settings", "Settings feature coming soon!")

    def show_profile_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 5px;
                color: #e5e7eb;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #8b5cf6;
                color: white;
            }
        """)
        
        profile_action = menu.addAction("👤 My Profile")
        profile_action.triggered.connect(lambda: self.switch_page("profile", self.profile_btn))
        menu.addSeparator()
        logout_action = menu.addAction("🚪 Logout")
        logout_action.triggered.connect(self.logout)
        menu.exec_(QCursor.pos())
    
    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.log_employee_activity("Logout", "Employee logged out of the system")
            self.main_app.show_login()
            self.main_app.resize(1280, 800)
            self.main_app.showNormal()