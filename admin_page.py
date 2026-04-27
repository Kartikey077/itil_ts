"""
Admin Panel Application for Ticket Management System
This module provides a GUI interface for administrators to manage tickets,
assign employees, and view dashboard statistics.
"""
import os
import sys
import csv
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMenu,
    QMessageBox, QComboBox, QDialog, QLineEdit, QTextEdit, QFormLayout,
    QDateEdit, QScrollArea, QGroupBox, QGridLayout, QTabWidget,
    QSizePolicy, QDialogButtonBox, QCheckBox, QSplitter
)
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtGui import QPixmap, QIcon, QCursor, QColor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QDate, pyqtSignal
from PyQt5.QtCore import QDate
import hashlib
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AssignEmployeeDialog(QDialog):
    """Dialog to assign an employee to a ticket"""
    
    def __init__(self, ticket_id, employees, parent=None):
        super().__init__(parent)
        self.ticket_id = ticket_id
        self.employees = employees
        self.selected_employee = None
        self.selected_status = None
        self.setWindowTitle(f"Assign Employee - Ticket {ticket_id}")
        self.setModal(True)
        # BIGGER DIALOG - Increased size
        self.setFixedSize(650, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 15px;
            }
            QLabel#headerLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1e293b;
            }
            QLabel#sectionLabel {
                font-size: 18px;
                font-weight: bold;
                color: #334155;
                margin-top: 10px;
            }
            QLabel#subjectLabel {
                font-size: 14px;
                color: #4b5563;
                padding: 8px;
                background-color: #f3f4f6;
                border-radius: 6px;
            }
            /* BIGGER COMBOBOX - Fixed dropdown height */
            QComboBox {
                padding: 18px 16px;
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                font-size: 16px;
                min-width: 400px;
                min-height: 35px;
                background-color: white;
                color: #1e293b;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 50px;
                border-left: 2px solid #cbd5e1;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-top: 10px solid #475569;
                margin-right: 15px;
            }
            /* BIGGER DROPDOWN LIST - Fixed height and width */
            QComboBox QAbstractItemView {
                font-size: 16px;
                background-color: white;
                selection-background-color: #3b82f6;
                selection-color: white;
                padding: 12px;
                min-height: 40px;
                max-height: 300px;
                min-width: 400px;
            }
            QComboBox QAbstractItemView::item {
                padding: 12px;
                min-height: 35px;
            }
            /* BIGGER BUTTONS */
            QPushButton {
                padding: 18px 36px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                min-width: 180px;
                min-height: 35px;
                border: none;
            }
            QPushButton#assignBtn {
                background-color: #059669;
                color: white;
            }
            QPushButton#assignBtn:hover {
                background-color: #10b981;
            }
            QPushButton#assignBtn:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
            QPushButton#cancelBtn {
                background-color: #dc2626;
                color: white;
            }
            QPushButton#cancelBtn:hover {
                background-color: #ef4444;
            }
        """)
        
        self.initUI()
    
    def initUI(self):
        """Initialize and arrange all UI elements in the dialog."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 25, 30, 30)
        
        # ===== HEADER SECTION =====
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        icon_label = QLabel("👥")
        icon_label.setStyleSheet("font-size: 32px;")
        
        title_label = QLabel(f"Assign Ticket #{self.ticket_id}")
        title_label.setObjectName("headerLabel")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # ===== TICKET SUBJECT SECTION =====
        if self.parent():
            ticket_subject = self.parent().get_ticket_subject(self.ticket_id)
            subject_label = QLabel(f"📝 {ticket_subject}")
            subject_label.setObjectName("subjectLabel")
            subject_label.setWordWrap(True)
            main_layout.addWidget(subject_label)
        
        # ===== EMPLOYEE SELECTION SECTION =====
        employee_label = QLabel("Select Employee")
        employee_label.setObjectName("sectionLabel")
        main_layout.addWidget(employee_label)
        
        self.employee_combo = QComboBox()
        self.employee_combo.addItem("── Select Employee ──", None)
        
        for emp in self.employees:
            emp_name = emp.get('name', emp.get('username', 'Unknown'))
            emp_username = emp.get('username', '')
            emp_email = emp.get('email', '')
            emp_role = emp.get('role', 'Support Agent')
            emp_status = emp.get('status', 'Active')
            
            if emp_status == 'Active':
                status_icon = "🟢"
                status_text = "Available"
            elif emp_status == 'Busy':
                status_icon = "🔴"
                status_text = "Busy"
            elif emp_status == 'In Meeting':
                status_icon = "🟡"
                status_text = "In Meeting"
            else:
                status_icon = "⚪"
                status_text = "Unknown"
            
            display_text = f"{status_icon} {emp_name} ({emp_role}) - {status_text}"
            employee_data = {
                'name': emp_name,
                'username': emp_username,
                'email': emp_email,
                'role': emp_role,
                'status': emp_status
            }
            self.employee_combo.addItem(display_text, employee_data)
        
        self.employee_combo.currentIndexChanged.connect(self.on_employee_selected)
        main_layout.addWidget(self.employee_combo)
        
        # ===== STATUS UPDATE SECTION =====
        status_label = QLabel("Update Status")
        status_label.setObjectName("sectionLabel")
        main_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Assigned",
            "In Progress", 
            "On Hold",
            "Pending Review",
            "Resolved",
            "Closed"
        ])
        self.status_combo.setCurrentIndex(0)
        main_layout.addWidget(self.status_combo)
        
        main_layout.addStretch()
        
        # ===== BUTTONS SECTION =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.assign_btn = QPushButton("✓ Assign & Update")
        self.assign_btn.setObjectName("assignBtn")
        self.assign_btn.clicked.connect(self.assign_employee)
        self.assign_btn.setEnabled(False)
        self.assign_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        button_layout.addWidget(self.assign_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def on_employee_selected(self, index):
        self.assign_btn.setEnabled(index > 0)
    
    def assign_employee(self):
        if self.employee_combo.currentIndex() <= 0:
            return
            
        self.selected_employee = self.employee_combo.currentData()
        self.selected_status = self.status_combo.currentText()
        
        if self.parent():
            success = self.parent().update_ticket_assignment(
                self.ticket_id,
                self.selected_employee['name'],
                self.selected_status
            )
            
            if success:
                QMessageBox.information(
                    self.parent(),
                    "Success",
                    f"✅ Ticket {self.ticket_id} has been assigned to {self.selected_employee['name']}\n"
                    f"Status updated to: {self.selected_status}"
                )
                
                self.parent().refresh_current_view()
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"❌ Failed to assign ticket {self.ticket_id}. Please try again."
                )

# ==================== ADD EMPLOYEE FORM WIDGET ====================

class AddEmployeeForm(QWidget):
    """Inline form to add a new employee"""
    
    employee_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_admin = parent
        self.setVisible(False)
        self.setStyleSheet(self.get_form_style())
        self.initUI()
    
    def get_form_style(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
                border-radius: 15px;
                margin: 10px 0;
            }
            QLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px 10px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 12px;
                background-color: white;
                color: #1e293b;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3b82f6;
            }
            QPushButton {
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
                border-radius: 8px;
                cursor: pointer;
            }
            QPushButton#submitBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                min-width: 120px;
            }
            QPushButton#submitBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
            }
            QPushButton#cancelBtn {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                min-width: 120px;
            }
            QPushButton#cancelBtn:hover {
                background-color: #e2e8f0;
            }
            QPushButton#generateBtn {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 11px;
                border-radius: 6px;
            }
            QPushButton#generateBtn:hover {
                background-color: #7c3aed;
            }
            QCheckBox {
                color: #475569;
                font-size: 11px;
            }
        """
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("➕")
        icon_label.setStyleSheet("font-size: 20px;")
        title_label = QLabel("Add New Employee")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Form layout using Grid
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 5, 0, 5)
        
        # Row 0: First Name, Last Name
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        form_layout.addWidget(QLabel("First Name *"), 0, 0)
        form_layout.addWidget(self.first_name_input, 0, 1)
        form_layout.addWidget(QLabel("Last Name *"), 0, 2)
        form_layout.addWidget(self.last_name_input, 0, 3)
        
        # Row 1: Email, Phone
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("employee@company.com")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("10-digit number")
        form_layout.addWidget(QLabel("Email *"), 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)
        form_layout.addWidget(QLabel("Phone *"), 1, 2)
        form_layout.addWidget(self.phone_input, 1, 3)
        
        # Row 2: Employee ID, Username
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("EMP001")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("john.doe")
        form_layout.addWidget(QLabel("Employee ID *"), 2, 0)
        form_layout.addWidget(self.employee_id_input, 2, 1)
        form_layout.addWidget(QLabel("Username *"), 2, 2)
        form_layout.addWidget(self.username_input, 2, 3)
        
        # Row 3: Department, Role
        self.department_combo = QComboBox()
        self.department_combo.addItems([
            "IT Support", "Network Team", "Application Support", 
            "Security Team", "Hardware Team", "Database Team", 
            "Cloud Services", "QA Team"
        ])
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Support Agent", "Senior Support Agent", "Network Engineer",
            "Application Analyst", "Security Analyst", "Database Administrator",
            "QA Tester", "Team Lead", "Manager"
        ])
        form_layout.addWidget(QLabel("Department *"), 3, 0)
        form_layout.addWidget(self.department_combo, 3, 1)
        form_layout.addWidget(QLabel("Role *"), 3, 2)
        form_layout.addWidget(self.role_combo, 3, 3)
        
        # Row 4: Join Date, Status
        self.join_date_input = QDateEdit()
        self.join_date_input.setDate(QDate.currentDate())
        self.join_date_input.setCalendarPopup(True)
        self.join_date_input.setDisplayFormat("yyyy-MM-dd")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive", "On Leave", "Training"])
        form_layout.addWidget(QLabel("Join Date *"), 4, 0)
        form_layout.addWidget(self.join_date_input, 4, 1)
        form_layout.addWidget(QLabel("Status"), 4, 2)
        form_layout.addWidget(self.status_combo, 4, 3)
        
        # Row 5: Password
        password_widget = QWidget()
        password_layout = QHBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password or generate")
        self.generate_password_btn = QPushButton("Generate")
        self.generate_password_btn.setObjectName("generateBtn")
        self.generate_password_btn.clicked.connect(self.generate_password)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.generate_password_btn)
        
        form_layout.addWidget(QLabel("Password *"), 5, 0)
        form_layout.addWidget(password_widget, 5, 1, 1, 3)
        
        # Row 6: Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.show_password_cb = QCheckBox("Show Password")
        self.show_password_cb.stateChanged.connect(self.toggle_password)
        
        form_layout.addWidget(QLabel("Confirm Password *"), 6, 0)
        form_layout.addWidget(self.confirm_password_input, 6, 1)
        form_layout.addWidget(self.show_password_cb, 6, 2, 1, 2)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.submit_btn = QPushButton("✓ Add Employee")
        self.submit_btn.setObjectName("submitBtn")
        self.submit_btn.clicked.connect(self.add_employee)
        
        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.hide_form)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.submit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def generate_password(self):
        import random
        import string
        chars = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(random.choice(chars) for _ in range(12))
        self.password_input.setText(password)
        self.confirm_password_input.setText(password)
    
    def toggle_password(self):
        if self.show_password_cb.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_form(self):
        errors = []
        if not self.first_name_input.text().strip():
            errors.append("First Name is required")
        if not self.last_name_input.text().strip():
            errors.append("Last Name is required")
        
        email = self.email_input.text().strip()
        if not email:
            errors.append("Email is required")
        elif "@" not in email or "." not in email:
            errors.append("Valid email is required")
        
        phone = self.phone_input.text().strip()
        if not phone:
            errors.append("Phone is required")
        elif not phone.isdigit() or len(phone) < 10:
            errors.append("Valid 10-digit phone number is required")
        
        if not self.employee_id_input.text().strip():
            errors.append("Employee ID is required")
        if not self.username_input.text().strip():
            errors.append("Username is required")
        
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters")
        elif password != confirm:
            errors.append("Passwords do not match")
        
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
        return True
    
    def check_duplicate(self):
        username = self.username_input.text().strip()
        employee_id = self.employee_id_input.text().strip()
        
        query1 = "SELECT username FROM employees WHERE username = %s"
        result1 = self.parent_admin.execute_query(query1, (username,)) if self.parent_admin else []
        
        if result1:
            QMessageBox.warning(self, "Duplicate", f"Username '{username}' already exists!")
            return False
        
        query2 = "SELECT employee_id FROM employee_details WHERE employee_id = %s"
        result2 = self.parent_admin.execute_query(query2, (employee_id,)) if self.parent_admin else []
        
        if result2:
            QMessageBox.warning(self, "Duplicate", f"Employee ID '{employee_id}' already exists!")
            return False
        
        return True
    
    def add_employee(self):
        if not self.validate_form():
            return
        if not self.check_duplicate():
            return
        
        try:
            employee_data = {
                'username': self.username_input.text().strip(),
                'password': self.password_input.text(),
                'first_name': self.first_name_input.text().strip(),
                'last_name': self.last_name_input.text().strip(),
                'email': self.email_input.text().strip(),
                'phone': self.phone_input.text().strip(),
                'department': self.department_combo.currentText(),
                'role': self.role_combo.currentText(),
                'employee_id': self.employee_id_input.text().strip(),
                'join_date': self.join_date_input.date().toString("yyyy-MM-dd"),
                'status': self.status_combo.currentText(),
                'company': ''
            }
            
            # Insert into employees table
            query1 = """
                INSERT INTO employees (username, password, first, last, email, phone, company)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params1 = (
                employee_data['username'],
                self.hash_password(employee_data['password']),
                employee_data['first_name'],
                employee_data['last_name'],
                employee_data['email'],
                employee_data['phone'],
                employee_data['company']
            )
            
            # Insert into employee_details table
            query2 = """
                INSERT INTO employee_details 
                (employee_id, username, name, email, phone, department, role, join_date, status, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            full_name = f"{employee_data['first_name']} {employee_data['last_name']}"
            params2 = (
                employee_data['employee_id'],
                employee_data['username'],
                full_name,
                employee_data['email'],
                employee_data['phone'],
                employee_data['department'],
                employee_data['role'],
                employee_data['join_date'],
                employee_data['status'],
                datetime.now()
            )
            
            if self.parent_admin:
                success1 = self.parent_admin.execute_query(query1, params1, fetch=False)
                success2 = self.parent_admin.execute_query(query2, params2, fetch=False)
                
                if success1 and success2:
                    QMessageBox.information(self, "Success", f"✅ Employee {employee_data['username']} added successfully!")
                    self.hide_form()
                    self.clear_form()
                    self.employee_added.emit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add employee!")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
    
    def clear_form(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.employee_id_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.department_combo.setCurrentIndex(0)
        self.role_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.join_date_input.setDate(QDate.currentDate())
        self.show_password_cb.setChecked(False)
    
    def hide_form(self):
        self.setVisible(False)
        self.clear_form()


# ==================== EMPLOYEE MANAGEMENT PAGE ====================

class EmployeeManagementPage(QWidget):
    """Employee management page with filter, table, and add form"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_admin = parent
        self.current_role_filter = "All Roles"
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter Bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        filter_label = QLabel("Filter by Role:")
        filter_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
        
        self.role_filter_combo = QComboBox()
        self.role_filter_combo.setMinimumWidth(200)
        self.role_filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
        """)
        self.role_filter_combo.currentTextChanged.connect(self.filter_by_role)
        
        self.add_employee_btn = QPushButton("➕ Add New Employee")
        self.add_employee_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        self.add_employee_btn.clicked.connect(self.toggle_add_form)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_employee_table)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.role_filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(self.add_employee_btn)
        filter_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Add Employee Form
        self.add_form = AddEmployeeForm(self.parent_admin)
        self.add_form.employee_added.connect(self.on_employee_added)
        main_layout.addWidget(self.add_form)
        
        # Employee Table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(7)
        self.employee_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Email", "Department", "Role", "Status", "Actions"])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        
        main_layout.addWidget(self.employee_table)
        
        # Count label
        self.count_label = QLabel("Total Employees: 0")
        self.count_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px 5px;")
        main_layout.addWidget(self.count_label)
        
        self.setLayout(main_layout)
        
        # Load data
        self.load_roles()
        self.load_employee_table()
    
    def load_roles(self):
        """Load distinct roles for filter dropdown"""
        query = "SELECT DISTINCT role FROM employee_details WHERE role IS NOT NULL ORDER BY role"
        roles_result = self.parent_admin.execute_query(query) if self.parent_admin else []
        
        self.role_filter_combo.clear()
        self.role_filter_combo.addItem("All Roles")
        
        for role in roles_result:
            if role['role']:
                self.role_filter_combo.addItem(role['role'])
    
    def filter_by_role(self, role):
        """Filter employees by role"""
        self.current_role_filter = role
        self.load_employee_table()
    
    def load_employee_table(self):
        """Load employee data into table"""
        if self.current_role_filter == "All Roles":
            query = """
                SELECT ed.employee_id, ed.name, ed.email, ed.department, ed.role, ed.status, ed.username
                FROM employee_details ed
                ORDER BY ed.name
            """
            employees = self.parent_admin.execute_query(query) if self.parent_admin else []
        else:
            query = """
                SELECT ed.employee_id, ed.name, ed.email, ed.department, ed.role, ed.status, ed.username
                FROM employee_details ed
                WHERE ed.role = %s
                ORDER BY ed.name
            """
            employees = self.parent_admin.execute_query(query, (self.current_role_filter,)) if self.parent_admin else []
        
        self.employee_table.setRowCount(len(employees))
        
        status_colors = {
            'Active': QColor('#27ae60'),
            'Inactive': QColor('#95a5a6'),
            'On Leave': QColor('#f39c12'),
            'Training': QColor('#3498db')
        }
        
        for row, emp in enumerate(employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(str(emp.get('employee_id', ''))))
            self.employee_table.setItem(row, 1, QTableWidgetItem(emp.get('name', '')))
            self.employee_table.setItem(row, 2, QTableWidgetItem(emp.get('email', '')))
            self.employee_table.setItem(row, 3, QTableWidgetItem(emp.get('department', '')))
            self.employee_table.setItem(row, 4, QTableWidgetItem(emp.get('role', '')))
            
            status = emp.get('status', 'Active')
            status_item = QTableWidgetItem(status)
            if status in status_colors:
                status_item.setForeground(status_colors[status])
            self.employee_table.setItem(row, 5, status_item)
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)
            
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedSize(80, 28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda checked, e=emp: self.delete_employee(e))
            
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            self.employee_table.setCellWidget(row, 6, action_widget)
        
        self.count_label.setText(f"Total Employees: {len(employees)}")
    
    def toggle_add_form(self):
        """Toggle the add employee form visibility"""
        if self.add_form.isVisible():
            self.add_form.hide_form()
            self.add_employee_btn.setText("➕ Add New Employee")
        else:
            self.add_form.setVisible(True)
            self.add_employee_btn.setText("✖ Cancel")
    
    def on_employee_added(self):
        """Handle employee added signal"""
        self.toggle_add_form()
        self.load_roles()
        self.load_employee_table()
        if hasattr(self.parent_admin, 'teams_section') and self.parent_admin.teams_section:
            self.parent_admin.teams_section.load_teams_data()
    
    def refresh_employee_table(self):
        """Refresh the employee table"""
        self.load_employee_table()
        QMessageBox.information(self, "Refreshed", "Employee list has been updated!")
    
    def delete_employee(self, employee):
        """Delete employee from database"""
        username = employee.get('username')
        name = employee.get('name')
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query1 = "DELETE FROM employee_details WHERE username = %s"
                query2 = "DELETE FROM employees WHERE username = %s"
                
                self.parent_admin.execute_query(query1, (username,), fetch=False)
                self.parent_admin.execute_query(query2, (username,), fetch=False)
                
                QMessageBox.information(self, "Success", f"✅ Employee '{name}' deleted successfully!")
                self.load_employee_table()
                self.load_roles()
                
                if hasattr(self.parent_admin, 'teams_section') and self.parent_admin.teams_section:
                    self.parent_admin.teams_section.load_teams_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete employee:\n{str(e)}")


# ==================== TEAMS SECTION WIDGET ====================

class TeamsSection(QWidget):
    """Teams section showing department-wise team details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_admin = parent
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("👥 Team Management")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1c2833;")
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_teams_data)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Department tabs
        self.department_tabs = QTabWidget()
        self.department_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1abc9c;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e2e8f0;
            }
        """)
        
        layout.addWidget(self.department_tabs)
        
        # Summary section
        summary_group = QGroupBox("📊 Department Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }
        """)
        
        self.summary_layout = QGridLayout(summary_group)
        self.summary_layout.setSpacing(15)
        
        layout.addWidget(summary_group)
        
        self.setLayout(layout)
        self.load_teams_data()
    
    def load_teams_data(self):
        """Load all teams data from database"""
        self.department_tabs.clear()
        
        # Clear summary layout
        for i in reversed(range(self.summary_layout.count())):
            widget = self.summary_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get all departments
        query = """
            SELECT DISTINCT department, COUNT(*) as count
            FROM employee_details
            WHERE department IS NOT NULL AND department != ''
            GROUP BY department
            ORDER BY department
        """
        
        departments = self.parent_admin.execute_query(query) if self.parent_admin else []
        
        if not departments:
            no_data_label = QLabel("No departments found. Please add employees first.")
            no_data_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 50px;")
            no_data_label.setAlignment(Qt.AlignCenter)
            self.department_tabs.addTab(no_data_label, "No Data")
            return
        
        row = 0
        col = 0
        
        for dept in departments:
            department_name = dept['department']
            employee_count = dept['count']
            
            # Create summary card
            card = self.create_summary_card(department_name, employee_count)
            self.summary_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
            
            # Create department tab
            tab_widget = self.create_department_tab(department_name)
            self.department_tabs.addTab(tab_widget, f"🏢 {department_name}")
    
    def create_summary_card(self, department_name, employee_count):
        """Create a summary card for a department"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #1abc9c;
                background-color: #f0fdf4;
            }
        """)
        card.setFixedWidth(200)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        icon_map = {
            'IT Support': '💻', 'Network Team': '🌐', 'Application Support': '📱',
            'Security Team': '🔒', 'Hardware Team': '🖥️', 'Database Team': '🗄️',
            'Cloud Services': '☁️', 'QA Team': '✅'
        }
        
        icon = icon_map.get(department_name, '👥')
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        dept_label = QLabel(department_name)
        dept_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        dept_label.setAlignment(Qt.AlignCenter)
        
        count_label = QLabel(str(employee_count))
        count_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #1abc9c;")
        count_label.setAlignment(Qt.AlignCenter)
        
        members_label = QLabel("Members")
        members_label.setStyleSheet("font-size: 11px; color: #64748b;")
        members_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(dept_label)
        layout.addWidget(count_label)
        layout.addWidget(members_label)
        
        return card
    
    def create_department_tab(self, department_name):
        """Create a tab widget for a specific department"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Department header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1abc9c, stop:1 #16a085);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        info_layout = QVBoxLayout()
        dept_title = QLabel(f"📋 {department_name} Department")
        dept_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        
        stats = self.get_department_stats(department_name)
        stats_label = QLabel(f"👥 {stats['total']} Members | 👨‍💼 Manager: {stats['manager']}")
        stats_label.setStyleSheet("font-size: 12px; color: #e0f2fe;")
        
        info_layout.addWidget(dept_title)
        info_layout.addWidget(stats_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Team members table
        members_label = QLabel("Team Members")
        members_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; margin-top: 10px;")
        layout.addWidget(members_label)
        
        members_table = QTableWidget()
        members_table.setColumnCount(6)
        members_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Role", "Email", "Phone", "Status"])
        members_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        members_table.setAlternatingRowColors(True)
        members_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        query = """
            SELECT ed.employee_id, ed.name, ed.role, ed.email, ed.phone, ed.status
            FROM employee_details ed
            WHERE ed.department = %s
            ORDER BY 
                CASE WHEN ed.role LIKE '%Manager%' THEN 1
                     WHEN ed.role LIKE '%Lead%' THEN 2
                     ELSE 3 END,
                ed.name
        """
        
        members = self.parent_admin.execute_query(query, (department_name,)) if self.parent_admin else []
        
        members_table.setRowCount(len(members))
        
        status_colors = {
            'Active': QColor('#27ae60'),
            'Inactive': QColor('#95a5a6'),
            'On Leave': QColor('#f39c12'),
            'Training': QColor('#3498db')
        }
        
        for row, member in enumerate(members):
            members_table.setItem(row, 0, QTableWidgetItem(str(member.get('employee_id', ''))))
            members_table.setItem(row, 1, QTableWidgetItem(member.get('name', '')))
            members_table.setItem(row, 2, QTableWidgetItem(member.get('role', '')))
            members_table.setItem(row, 3, QTableWidgetItem(member.get('email', '')))
            members_table.setItem(row, 4, QTableWidgetItem(member.get('phone', '')))
            
            status = member.get('status', 'Active')
            status_item = QTableWidgetItem(status)
            if status in status_colors:
                status_item.setForeground(status_colors[status])
            members_table.setItem(row, 5, status_item)
        
        layout.addWidget(members_table)
        
        return widget
    
    def get_department_stats(self, department_name):
        """Get statistics for a department"""
        query_total = "SELECT COUNT(*) as total FROM employee_details WHERE department = %s"
        query_manager = """
            SELECT name FROM employee_details 
            WHERE department = %s AND (role LIKE '%Manager%' OR role LIKE '%Lead%')
            LIMIT 1
        """
        
        total_result = self.parent_admin.execute_query(query_total, (department_name,)) if self.parent_admin else []
        manager_result = self.parent_admin.execute_query(query_manager, (department_name,)) if self.parent_admin else []
        
        total = total_result[0]['total'] if total_result else 0
        manager = manager_result[0]['name'] if manager_result else "Not Assigned"
        
        return {'total': total, 'manager': manager}

class AdminPanel(QWidget):
    def get_all_employees(self):
        """Fetch only valid employees from database"""
        query = """
            SELECT 
                e.username,
                CONCAT(e.first, ' ', e.last) AS name,
                e.email,
                ed.employee_id,
                ed.department,
                ed.role,
                ed.status
            FROM employees e
            INNER JOIN employee_details ed 
            ON e.username = ed.username
            WHERE ed.status = 'Active'
        """
        return self.execute_query(query)
    
    def __init__(self, admin_data, controller):
        """
        Initialize the admin panel.
        
        Args:
            admin_data (dict): Dictionary containing admin information
                              (name, email, role)
        """
        super().__init__()
        self.controller = controller
        self.admin_data = admin_data
        self.admin_data = admin_data
        self.setWindowTitle("Admin Dashboard")
        self.setStyleSheet("background-color: #ecf0f1;")
        self.active_button = None
        self.current_ticket_filter = "All"  # Track current filter for refresh
        self.current_view = "Dashboard"     # Track current view for refresh
        self.employee_page = None
        self.teams_section = None
        self.initUI()
        # Ensure database has required columns
        self.ensure_assigned_column()

    def initUI(self):
        """Initialize the main user interface."""
        # ===== NAVBAR SECTION =====
        # Top navigation bar with buttons and profile
        navbar = QWidget()
        navbar.setStyleSheet("""
            background-color: #6f8da8;
            color: white;
            padding: 16px 30px;
        """)
        navbar_layout = QHBoxLayout()
        navbar_layout.setContentsMargins(25, 10, 25, 10)
        navbar_layout.setSpacing(25)

        # Application title
        title_label = QLabel("Admin Dashboard")
        title_label.setStyleSheet("""
            font-size: 22px;
            color: white;
            font-weight: bold;
            padding-bottom: 6px;
        """)
        navbar_layout.addWidget(title_label, alignment=Qt.AlignVCenter)

        # Navigation buttons
        nav_buttons = ["Dashboard", "Tickets", "Employees", "Teams", "Reports"]
        self.nav_buttons = {}
        for btn_text in nav_buttons:
            btn = QPushButton(btn_text)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet(self.default_button_style())
            btn.clicked.connect(lambda checked, b=btn_text: self.handle_nav_click(b))
            navbar_layout.addWidget(btn, alignment=Qt.AlignVCenter)
            self.nav_buttons[btn_text] = btn

        navbar_layout.addStretch(1)

        # Profile button with user image
        self.user_logo_btn = QPushButton()
        self.user_logo_btn.setCursor(QCursor(Qt.PointingHandCursor))
        ICON_SIZE = 50

        # Try to load image, if not found use emoji
        if os.path.exists("user-circle.png"):
            pixmap = QPixmap("user-circle.png")
            if not pixmap.isNull():
                self.user_logo_btn.setIcon(QIcon(pixmap))
                self.user_logo_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
                self.user_logo_btn.setText("")
            else:
                self.user_logo_btn.setText("👤")
                self.user_logo_btn.setFont(QFont("Segoe UI", 20))
        else:
            # Use emoji as fallback
            self.user_logo_btn.setText("👤")
            self.user_logo_btn.setFont(QFont("Segoe UI", 20))

        self.user_logo_btn.setFixedSize(ICON_SIZE + 10, ICON_SIZE + 10)
        self.user_logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #06b6d4;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0891b2;
            }
        """)
        self.user_logo_btn.clicked.connect(self.show_user_tooltip)
        navbar_layout.addWidget(self.user_logo_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)

        navbar.setLayout(navbar_layout)
        navbar.setFixedHeight(90)

        # ===== CONTENT AREA =====
        # Dynamic area that changes based on navigation
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)

        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        # Main layout combining navbar and content
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(navbar)
        main_layout.addWidget(self.scroll_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.setLayout(main_layout)

        # Start with dashboard
        self.highlight_button("Dashboard")
        self.load_dashboard()
        self.showMaximized()  # Start in fullscreen

    # ===== DATABASE CONNECTION METHODS =====
    def get_db_connection(self):
        """
        Establish and return MySQL database connection.
        
        Returns:
            MySQLConnection object or None if connection fails
        """
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
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to connect to database: {err}")
            return None

    def execute_query(self, query, params=None, fetch=True):
        """
        Execute database query and return results.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Parameters for parameterized query
            fetch (bool): True for SELECT queries, False for INSERT/UPDATE/DELETE
        
        Returns:
            List of dictionaries for fetch=True, boolean for fetch=False
        """
        conn = self.get_db_connection()
        if not conn:
            return [] if fetch else False
        
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount > 0  # True if at least one row affected
            
            cursor.close()
            conn.close()
            return result
        except mysql.connector.Error as err:
            print(f"[Query Error] {err}")
            return [] if fetch else False

    def ensure_assigned_column(self):
        """
        Check if assigned_to column exists in tickets table.
        Add it if it doesn't exist to prevent errors.
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Check if column exists in database schema
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'kaiticket' 
                AND TABLE_NAME = 'tickets' 
                AND COLUMN_NAME = 'assigned_to'
            """)
            
            result = cursor.fetchone()
            
            if result[0] == 0:
                # Add the column if it doesn't exist
                cursor.execute("""
                    ALTER TABLE tickets 
                    ADD COLUMN assigned_to VARCHAR(255) DEFAULT NULL
                """)
                conn.commit()
                print("[Database] Added 'assigned_to' column to tickets table")
            
            cursor.close()
            conn.close()
            return True
            
        except mysql.connector.Error as err:
            print(f"[Error] Failed to check/add assigned_to column: {err}")
            return False
        
    def load_employee_management(self):
        """Load the employee management page with add/delete functionality"""
        if not self.employee_page:
            self.employee_page = EmployeeManagementPage(self)
        self.content_layout.addWidget(self.employee_page)

    def load_teams_section(self):
        """Load the teams section showing department-wise details"""
        if not self.teams_section:
            self.teams_section = TeamsSection(self)
        self.content_layout.addWidget(self.teams_section)


    # ===== STYLE METHODS =====
    def default_button_style(self):
        """Return stylesheet for inactive navigation buttons."""
        return """
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                color: #d5f5e3;
                text-decoration: underline;
            }
        """

    def active_button_style(self):
        """Return stylesheet for active navigation button."""
        return """
            QPushButton {
                color: white;
                background-color: #1abc9c;
                border-radius: 6px;
                font-size: 16px;
                padding: 6px 14px;
            }
        """

    def dropdown_menu_style(self):
        """Return stylesheet for dropdown menus."""
        return """
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
                min-width: 160px;
                font-size: 15px;
                color: #2c3e50;
            }
            QMenu::item {
                padding: 8px 12px;
            }
            QMenu::item:selected {
                background-color: #1abc9c;
                color: white;
                border-radius: 5px;
            }
        """

    def table_style(self):
        """Return stylesheet for tables."""
        return """
            QTableWidget {
                background-color: white;
                font-size: 15px;
                gridline-color: #dcdcdc;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #1a237e;
                color: white;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background-color: #1abc9c;
                color: white;
            }
        """

    # ===== NAVIGATION METHODS =====
    def highlight_button(self, name):
        """
        Highlight the active navigation button.
        
        Args:
            name (str): Name of the button to highlight
        """
        for btn_text, btn in self.nav_buttons.items():
            if btn_text == name:
                btn.setStyleSheet(self.active_button_style())
            else:
                btn.setStyleSheet(self.default_button_style())

    def clear_content(self):
        """Remove all widgets from content area."""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def handle_nav_click(self, section):
        self.highlight_button(section)
        self.current_view = section
        self.clear_content()

        if section == "Dashboard":
            self.load_dashboard()

        elif section == "Employees":
            self.load_employee_management()

        elif section == "Teams":
            self.load_teams_section()

        elif section == "Tickets":
            self.show_ticket_menu()

        elif section == "Reports":
            self.show_reports()

        else:
            self.clear_content()
            label = QLabel(f"{section} Section Coming Soon...")
            label.setStyleSheet("font-size: 22px; color: #2c3e50;")
            self.content_layout.addWidget(label)

    # ===== USER PROFILE METHODS =====
    def show_user_tooltip(self):
            menu = QMenu()
            menu.setStyleSheet(self.dropdown_menu_style())

            menu.addAction(f"👤 {self.admin_data.get('name', '')}")
            menu.addAction(f"📧 {self.admin_data.get('email', '')}")
            menu.addAction(f"🧩 Role: {self.admin_data.get('role', 'Admin')}")
            menu.addSeparator()
    
            logout_action = menu.addAction("🚪 Logout")
            logout_action.triggered.connect(self.logout)

            menu.exec_(self.user_logo_btn.mapToGlobal(self.user_logo_btn.rect().bottomRight()))

    def logout(self):
            reply = QMessageBox.question(
                self,
                'Logout',
                'Are you sure you want to logout?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.controller:
                    self.controller.show_login()

    # ===== TICKET ASSIGNMENT METHODS =====
    def get_real_employees(self):
        """
        Fetch real employees from the database.
        
        Returns:
            list: List of employee dictionaries with name, username, email, role, status
        """
        # First try to get from employee_details table
        query = """
            SELECT ed.employee_id, ed.name, ed.username, ed.email, 
                   ed.phone, ed.department, ed.role, ed.status,
                   e.password
            FROM employee_details ed
            JOIN employees e ON ed.username = e.username
            WHERE ed.status = 'Active'
            ORDER BY ed.name
        """
        
        employees = self.execute_query(query)
        
        if not employees:
            # Fallback: Get from employees table if employee_details is empty
            fallback_query = """
                SELECT username as name, username, email, first, last, phone, company
                FROM employees
                ORDER BY username
            """
            employees = self.execute_query(fallback_query)
            
            # Format the data to match expected structure
            if employees:
                formatted_employees = []
                for emp in employees:
                    formatted_employees.append({
                        'name': emp.get('first', '') + ' ' + emp.get('last', '') or emp.get('name', ''),
                        'username': emp.get('username', ''),
                        'email': emp.get('email', ''),
                        'role': 'Support Agent',
                        'status': 'Active'
                    })
                return formatted_employees
        
        return employees if employees else []

    def get_ticket_subject(self, ticket_id):
        """
        Get ticket subject by ID for display in assignment dialog.
        
        Args:
            ticket_id (str): Ticket number to look up
        
        Returns:
            str: Ticket subject or default message if not found
        """
        query = "SELECT subject FROM tickets WHERE ticket_number = %s"
        result = self.execute_query(query, (ticket_id,))
        if result:
            return result[0]['subject']
        return "Subject not found"

    def refresh_current_view(self):
        """Refresh the current view without closing dialog."""
        if self.current_view == "Dashboard":
            self.load_dashboard()
        elif self.current_view == "Tickets":
            self.load_ticket_table(self.current_ticket_filter)

    def assign_employee_to_ticket(self, ticket_id):
        """
        Open dialog to assign employee to ticket.
        
        Args:
            ticket_id (str): ID of ticket to assign
        """
        # Get real employees from database
        real_employees = self.get_real_employees()
        
        if not real_employees:
            QMessageBox.warning(self, "No Employees", 
                              "No employees found in the database. Please add employees first.")
            return
        
        # Create and show assignment dialog
        employees = self.get_all_employees()
        dialog = AssignEmployeeDialog(ticket_id, real_employees, self)
        
        # Show dialog - it will handle the assignment and refresh
        dialog.exec_()

    def update_ticket_assignment(self, ticket_id, employee_name, status):
        """
        Update ticket assignment in database.
        This function now handles Resolve and Close status changes as well.
        
        Args:
            ticket_id (str): Ticket number
            employee_name (str): Name of assigned employee
            status (str): New status for the ticket (can be Assigned, In Progress, 
                         On Hold, Pending Review, Resolved, or Closed)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get employee_id from name
            emp_query = "SELECT employee_id FROM employee_details WHERE name = %s"
            emp_result = self.execute_query(emp_query, (employee_name,))
            if not emp_result:
                return False
            employee_id = emp_result[0]['employee_id']
            
            # Check if assignment already exists
            check_query = "SELECT COUNT(*) as count FROM ticket_assignments WHERE ticket_number = %s"
            exists = self.execute_query(check_query, (ticket_id,))
            
            if exists and exists[0]['count'] > 0:
                # Update existing assignment
                update_query = """
                    UPDATE ticket_assignments 
                    SET employee_id = %s, 
                        status = %s, 
                        last_updated = NOW()
                    WHERE ticket_number = %s
                """
                success = self.execute_query(update_query, (employee_id, status, ticket_id), fetch=False)
            else:
                # Insert new assignment
                insert_query = """
                    INSERT INTO ticket_assignments (ticket_number, employee_id, assigned_date, status, last_updated)
                    VALUES (%s, %s, NOW(), %s, NOW())
                """
                success = self.execute_query(insert_query, (ticket_id, employee_id, status), fetch=False)
            
            # Update the main tickets table with new status and assigned employee
            update_query = """
                UPDATE tickets 
                SET assigned_to = %s, status = %s 
                WHERE ticket_number = %s
            """
            self.execute_query(update_query, (employee_name, status, ticket_id), fetch=False)
            
            return success
            
        except Exception as e:
            print(f"Error updating ticket assignment: {e}")
            return False

    def tickets_per_day(self):
            query = """
                SELECT DATE(created_at) as d, COUNT(*) as c
                FROM tickets
                GROUP BY d
                ORDER BY d
            """
            data = self.execute_query(query)

            dates = [str(row['d']) for row in data] if data else []
            counts = [row['c'] for row in data] if data else []

            fig = Figure()
            canvas = FigureCanvas(fig)
            canvas.setFixedHeight(300) 
            ax = fig.add_subplot(111)

            ax.plot(dates, counts)
            ax.set_title("Tickets Per Day")
            fig.tight_layout() 
            return canvas

    # ===== DASHBOARD METHODS =====
    def load_dashboard(self):
        """Load and display dashboard with statistics and recent tickets."""
        self.current_view = "Dashboard"
        self.clear_content()
        
        # Header
        heading = QLabel("📊 System Overview")
        heading.setStyleSheet("font-size: 22px; font-weight: bold; color: #1c2833;")
        self.content_layout.addWidget(heading)

        # Get real statistics from database
        stats = self.get_dashboard_stats()

        # Create statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_cards = [
            ("Total Tickets", stats['total'], "#3498db"),
            ("Open", stats['open'], "#e74c3c"),
            ("Closed", stats['closed'], "#2ecc71"),
            ("Pending", stats['pending'], "#f39c12"),
            ("Today", stats['today'], "#9b59b6"),
            ("High Priority", stats['high'], "#c0392b"),
        ]
        # 1. CARDS FIRST
        for title, number, color in stats_cards:
            card = self.create_stat_card(title, number, color)
            stats_layout.addWidget(card)

        stats_container = QWidget()
        stats_container.setLayout(stats_layout)
        self.content_layout.addWidget(stats_container)

        # 2. THEN GRAPHS (SIDE BY SIDE)
        graph_layout = QHBoxLayout()
        graph_layout.setSpacing(20)

        chart = self.create_status_chart(stats)
        trend_chart = self.tickets_per_day()

        graph_layout.addWidget(chart)
        graph_layout.addWidget(trend_chart)

        graph_container = QWidget()
        graph_container.setLayout(graph_layout)

        self.content_layout.addWidget(graph_container)
        
        # Add recent tickets section
        self.add_recent_tickets()

    def create_status_chart(self, stats):
            fig = Figure()
            canvas = FigureCanvas(fig)

            canvas.setFixedHeight(300)

            ax = fig.add_subplot(111)

            labels = ['Open', 'Closed', 'Pending']
            values = [stats['open'], stats['closed'], stats['pending']]

            ax.bar(labels, values)
            ax.set_title("Ticket Status Overview")
            fig.tight_layout()
            return canvas
    
    def create_stat_card(self, title, number, color):
        """
        Create a statistics card widget.
        
        Args:
            title (str): Card title
            number (str): Statistic value
            color (str): Color code for accent
        
        Returns:
            QFrame: Styled card widget
        """
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: white; border-radius: 12px; border: 1px solid #d0d3d4; }}")
        
        vbox = QVBoxLayout()
        label_title = QLabel(title)
        label_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #34495e;")
        label_number = QLabel(str(number))
        label_number.setStyleSheet(f"font-size: 42px; font-weight: bold; color: {color};")
        
        # Progress bar style accent
        progress = QFrame()
        progress.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        progress.setFixedHeight(8)
        
        vbox.addWidget(label_title)
        vbox.addWidget(label_number)
        vbox.addWidget(progress)
        vbox.addStretch(1)
        
        card.setLayout(vbox)
        card.setMinimumSize(200, 150)
        
        return card

    def get_dashboard_stats(self):
        stats = {}

        # Total tickets
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets")
        stats['total'] = result[0]['count'] if result else 0

        # Open tickets (includes New, Open, Pending, Assigned, In Progress, On Hold)
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status IN ('New','Open','Pending','Assigned','In Progress','On Hold')")
        stats['open'] = result[0]['count'] if result else 0

        # Closed/Resolved
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status IN ('Resolved','Closed')")
        stats['closed'] = result[0]['count'] if result else 0

        # Pending
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets WHERE status='Pending'")
        stats['pending'] = result[0]['count'] if result else 0

        # Tickets today
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets WHERE DATE(created_at)=CURDATE()")
        stats['today'] = result[0]['count'] if result else 0

        # High priority
        result = self.execute_query("SELECT COUNT(*) as count FROM tickets WHERE priority='High' AND status!='Closed'")
        stats['high'] = result[0]['count'] if result else 0

        return stats

    def add_recent_tickets(self):
        """Add recent tickets section to dashboard with assignment feature."""
        recent_label = QLabel("📋 Recent Tickets")
        recent_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1c2833; margin-top: 20px;")
        self.content_layout.addWidget(recent_label)
        
        # Get recent tickets from database including assigned_to
        query = """
            SELECT ticket_number, subject, user_email, 
                   COALESCE(assigned_to, 'Unassigned') as assigned_to, 
                   status, priority, created_at 
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 10
        """
        recent_tickets = self.execute_query(query)
        
        if recent_tickets:
            # Create table with 7 columns (no separate action buttons for resolve/close since it's in dialog)
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "Ticket ID", "Subject", "Raised By", "Assigned To", 
                "Status", "Priority", "Actions"
            ])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setRowCount(len(recent_tickets))
            table.setMinimumHeight(400)
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Priority color mapping
            priority_colors = {
                'High': QColor('#e74c3c'),
                'Medium': QColor('#e67e22'),
                'Low': QColor('#27ae60'),
                'P1': QColor('#e74c3c'),
                'P2': QColor('#e67e22'),
                'P3': QColor('#27ae60'),
                'P4': QColor('#3498db')
            }
            
            for row, ticket in enumerate(recent_tickets):
                self.populate_ticket_row_simple(table, row, ticket, priority_colors)
            
            table.setStyleSheet(self.table_style())
            self.content_layout.addWidget(table)
        else:
            no_data = QLabel("No recent tickets found")
            no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 20px;")
            self.content_layout.addWidget(no_data)

    # ===== EMPLOYEE MANAGEMENT METHODS =====
    def show_employee_menu(self):
        """Show dropdown menu for employee role filtering."""
        menu = QMenu()
        menu.setStyleSheet(self.dropdown_menu_style())
        
        # Get real roles from database
        query = "SELECT DISTINCT role FROM employee_details WHERE role IS NOT NULL"
        roles_result = self.execute_query(query)
        
        roles = ["All"]
        if roles_result:
            roles.extend([r['role'] for r in roles_result if r['role']])
        else:
            # Fallback to default roles if no data
            roles.extend(["Support Agent", "Network Engineer", "Hardware Specialist", "QA Tester", "Project Manager"])
        
        for role in roles:
            action = menu.addAction(role)
            action.triggered.connect(lambda checked, r=role: self.load_employee_table(r))
        
        btn = self.nav_buttons["Employees"]
        menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))

    def load_employee_table(self, role_filter):
        """
        Load and display employee table with role filter.
        
        Args:
            role_filter (str): Role to filter employees by
        """
        self.clear_content()
        
        heading = QLabel(f"👥 Employees - {role_filter}")
        heading.setStyleSheet("font-size: 22px; font-weight: bold; color: #1c2833;")
        self.content_layout.addWidget(heading)

        # Get real employees from database
        if role_filter == "All":
            query = """
                SELECT ed.employee_id, ed.name, ed.username, ed.email, 
                       ed.phone, ed.department, ed.role, ed.status,
                       e.password
                FROM employee_details ed
                JOIN employees e ON ed.username = e.username
                ORDER BY ed.name
            """
        else:
            query = """
                SELECT ed.employee_id, ed.name, ed.username, ed.email, 
                       ed.phone, ed.department, ed.role, ed.status,
                       e.password
                FROM employee_details ed
                JOIN employees e ON ed.username = e.username
                WHERE ed.role = %s
                ORDER BY ed.name
            """
            employees = self.execute_query(query, (role_filter,))
        
        if role_filter == "All":
            employees = self.execute_query(query)
        else:
            employees = self.execute_query(query, (role_filter,))
        
        if not employees:
            # Fallback: Get from employees table if employee_details is empty
            fallback_query = """
                SELECT username, first, last, email, phone, company
                FROM employees
                ORDER BY username
            """
            employees = self.execute_query(fallback_query)
            
            if employees:
                # Format as employee_details structure
                formatted_employees = []
                for emp in employees:
                    formatted_employees.append({
                        'employee_id': emp.get('username', ''),
                        'name': f"{emp.get('first', '')} {emp.get('last', '')}".strip() or emp.get('username', ''),
                        'username': emp.get('username', ''),
                        'email': emp.get('email', ''),
                        'phone': emp.get('phone', ''),
                        'department': emp.get('company', 'IT Support'),
                        'role': 'Support Agent',
                        'status': 'Active'
                    })
                employees = formatted_employees

        if employees:
            # Create table with 6 columns
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Employee ID", "Name", "Email", "Department", "Role", "Status"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setRowCount(len(employees))
            
            # Status color mapping
            status_colors = {
                'Active': QColor('#27ae60'),
                'Busy': QColor('#e74c3c'),
                'In Meeting': QColor('#f39c12'),
                'On Leave': QColor('#7f8c8d')
            }
            
            for row, emp in enumerate(employees):
                table.setItem(row, 0, QTableWidgetItem(str(emp.get('employee_id', emp.get('username', '')))))
                table.setItem(row, 1, QTableWidgetItem(emp.get('name', '')))
                table.setItem(row, 2, QTableWidgetItem(emp.get('email', '')))
                table.setItem(row, 3, QTableWidgetItem(emp.get('department', 'IT Support')))
                table.setItem(row, 4, QTableWidgetItem(emp.get('role', 'Support Agent')))
                
                status = emp.get('status', 'Active')
                status_item = QTableWidgetItem(status)
                if status in status_colors:
                    status_item.setForeground(status_colors[status])
                table.setItem(row, 5, status_item)
            
            table.setStyleSheet(self.table_style())
            self.content_layout.addWidget(table)
            
            # Add employee count
            count_label = QLabel(f"Total Employees: {len(employees)}")
            count_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 10px 0;")
            self.content_layout.addWidget(count_label)
        else:
            no_data = QLabel("No employees found in the database")
            no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 20px;")
            self.content_layout.addWidget(no_data)

    # ===== TICKET MANAGEMENT METHODS =====
    def show_ticket_menu(self):
        """Show dropdown menu for ticket status filtering."""
        menu = QMenu()
        menu.setStyleSheet(self.dropdown_menu_style())
        
        # Get distinct statuses from database
        query = "SELECT DISTINCT status FROM tickets ORDER BY status"
        statuses_result = self.execute_query(query)
        
        statuses = ["All"]
        if statuses_result:
            # Filter out None values and add to list
            statuses.extend([s['status'] for s in statuses_result if s['status']])
        else:
            # Fallback to default statuses if query fails
            statuses.extend(["New", "Open", "Pending", "Resolved", "Closed", "Assigned", "In Progress", "On Hold"])
        
        for status in statuses:
            action = menu.addAction(status)
            action.triggered.connect(lambda checked, s=status: self.load_ticket_table(s))
        
        btn = self.nav_buttons["Tickets"]
        menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))

    def load_ticket_table(self, status_filter):
        """
        Load and display ticket table with status filter.
        
        Args:
            status_filter (str): Status to filter tickets by
        """
        self.clear_content()
        self.current_view = "Tickets"
        self.current_ticket_filter = status_filter
        
        heading = QLabel(f"🎟️ Tickets - {status_filter}")
        heading.setStyleSheet("font-size: 22px; font-weight: bold; color: #1c2833;")
        self.content_layout.addWidget(heading)

        # Get tickets from database with optional status filter
        if status_filter == "All":
            query = """
                SELECT ticket_number, subject, user_email, 
                       COALESCE(assigned_to, 'Unassigned') as assigned_to, 
                       status, priority, created_at 
                FROM tickets 
                ORDER BY created_at DESC
            """
            tickets = self.execute_query(query)
        else:
            query = """
                SELECT ticket_number, subject, user_email, 
                       COALESCE(assigned_to, 'Unassigned') as assigned_to, 
                       status, priority, created_at 
                FROM tickets 
                WHERE status = %s 
                ORDER BY created_at DESC
            """
            tickets = self.execute_query(query, (status_filter,))

        if tickets:
            # Create table with 7 columns (Actions column only has Assign button)
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "Ticket ID", "Subject", "Raised By", "Assigned To", 
                "Status", "Priority", "Actions"
            ])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setRowCount(len(tickets))
            
            # Priority color mapping
            priority_colors = {
                'High': QColor('#e74c3c'),
                'Medium': QColor('#e67e22'),
                'Low': QColor('#27ae60'),
                'P1': QColor('#e74c3c'),
                'P2': QColor('#e67e22'),
                'P3': QColor('#27ae60'),
                'P4': QColor('#3498db')
            }
            
            for row, ticket in enumerate(tickets):
                self.populate_ticket_row_simple(table, row, ticket, priority_colors)
            
            table.setStyleSheet(self.table_style())
            self.content_layout.addWidget(table)
            
            # Add ticket count
            count_label = QLabel(f"Total Tickets: {len(tickets)}")
            count_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 10px 0;")
            self.content_layout.addWidget(count_label)
            
        else:
            no_data = QLabel("No tickets found")
            no_data.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 20px;")
            self.content_layout.addWidget(no_data)

    def show_reports(self):
            self.clear_content()

            layout = QVBoxLayout()
            layout.setSpacing(20)

            # ---------- FILTER ----------
            filter_layout = QHBoxLayout()

            self.from_date = QDateEdit()
            self.from_date.setCalendarPopup(True)
            self.from_date.setDate(QDate.currentDate().addYears(-1))

            self.to_date = QDateEdit()
            self.to_date.setCalendarPopup(True)
            self.to_date.setDate(QDate.currentDate())

            btn_generate = QPushButton("Generate Report")
            btn_generate.clicked.connect(self.load_report_data)
        
            filter_layout.addWidget(QLabel("From:"))
            filter_layout.addWidget(self.from_date)
            filter_layout.addWidget(QLabel("To:"))
            filter_layout.addWidget(self.to_date)
            filter_layout.addWidget(btn_generate)

            layout.addLayout(filter_layout)

            # ---------- TABLE ----------
            self.report_table = QTableWidget()
            from PyQt5.QtWidgets import QHeaderView

            self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.report_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels(
                ["ID", "User", "Status", "Priority", "Date"]
            )
            self.report_table.setMinimumHeight(400)
            self.report_table.setStyleSheet(self.table_style())
            layout.addWidget(self.report_table)

            # ---------- EXPORT ----------
            btn_export = QPushButton("Export CSV")
            btn_export.clicked.connect(self.export_report_csv)

            layout.addWidget(btn_export)

            container = QWidget()
            container.setLayout(layout)
            self.content_layout.addWidget(container)
            self.load_report_data()

    def load_report_data(self):
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd") + " 23:59:59"

            print("FROM:", from_date, "TO:", to_date)

            query = """
                SELECT ticket_number, user_email, status, priority, created_at
                FROM tickets
                WHERE created_at BETWEEN %s AND %s
                ORDER BY created_at DESC
            """

            data = self.execute_query(query, (from_date, to_date))

            print("DATA:", data)

            # CLEAR TABLE FIRST
            self.report_table.setRowCount(0)

            if not data:
                QMessageBox.warning(self, "No Data", "No tickets found in selected date range")
                return

            self.report_table.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                self.report_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['ticket_number'])))
                self.report_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['user_email'])))
                self.report_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['status'])))
                self.report_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data['priority'])))
                self.report_table.setItem(row_idx, 4, QTableWidgetItem(str(row_data['created_at'])))

    def export_report_csv(self):
            rows = self.report_table.rowCount()
            cols = self.report_table.columnCount()

            with open("report.csv", "w", newline="") as file:
                writer = csv.writer(file)

                headers = []
                for col in range(cols):
                    headers.append(self.report_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                for row in range(rows):
                    row_data = []
                    for col in range(cols):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Success", "Report exported as report.csv")

    # ==================== TICKET ROW POPULATION WITH ASSIGN BUTTON ONLY ====================
    # Resolve and Close functionality is now handled inside the Assign Dialog
    def populate_ticket_row_simple(self, table, row, ticket, priority_colors=None):
        """
        Populate a single row in the ticket table.
        Actions column only has Assign button - Resolve/Close are in the Assign Dialog.
        
        Args:
            table (QTableWidget): Table to populate
            row (int): Row index
            ticket (dict): Ticket data
            priority_colors (dict): Optional color mapping for priorities
        """
        # Ticket ID
        table.setItem(row, 0, QTableWidgetItem(ticket['ticket_number']))
        
        # Subject (truncate if too long)
        subject = ticket['subject']
        if len(subject) > 50:
            subject = subject[:47] + "..."
        table.setItem(row, 1, QTableWidgetItem(subject))
        
        # Raised By
        table.setItem(row, 2, QTableWidgetItem(ticket['user_email']))
        
        # Assigned To with color coding
        assigned_employee = ticket['assigned_to']
        assigned_item = QTableWidgetItem(assigned_employee)
        if assigned_employee == "Unassigned":
            assigned_item.setForeground(QColor('#e74c3c'))  # Red
            assigned_item.setBackground(QColor('#fdedec'))  # Light red
        else:
            assigned_item.setForeground(QColor('#27ae60'))  # Green
            assigned_item.setBackground(QColor('#e8f8f5'))  # Light green
        table.setItem(row, 3, assigned_item)
        
        # Status with color coding
        status_item = QTableWidgetItem(ticket['status'])
        status = ticket['status']
        if status in ['New', 'Open']:
            status_item.setForeground(QColor('#e74c3c'))  # Red
        elif status == 'Resolved':
            status_item.setForeground(QColor('#27ae60'))  # Green
        elif status == 'Pending':
            status_item.setForeground(QColor('#f39c12'))  # Orange
        elif status == 'Closed':
            status_item.setForeground(QColor('#7f8c8d'))  # Gray
        elif status == 'Assigned':
            status_item.setForeground(QColor('#3498db'))  # Blue
        table.setItem(row, 4, status_item)
        
        # Priority with color coding
        priority_item = QTableWidgetItem(ticket['priority'])
        priority = ticket['priority']
        
        if priority_colors:
            for key, color in priority_colors.items():
                if key in str(priority):
                    priority_item.setForeground(color)
                    break
        else:
            # Simple priority coloring if no mapping provided
            if priority == 'High' or 'P1' in str(priority):
                priority_item.setForeground(QColor('#e74c3c'))
            elif priority == 'Medium' or 'P2' in str(priority):
                priority_item.setForeground(QColor('#e67e22'))
        table.setItem(row, 5, priority_item)
        
                # Actions column - Assign button using 90% of column width
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(2, 4, 2, 4)
        actions_layout.setSpacing(0)
        
        # Assign button - Takes 90% width of action column
        assign_btn = QPushButton("👥 Assign")
        assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 0px;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        assign_btn.setCursor(QCursor(Qt.PointingHandCursor))
        assign_btn.setMinimumWidth(0)  # Allow button to shrink
        assign_btn.setMaximumWidth(16777215)  # Allow button to expand
        assign_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        assign_btn.clicked.connect(lambda checked, t=ticket['ticket_number']: 
                                 self.assign_employee_to_ticket(t))
        
        actions_layout.addWidget(assign_btn, 9)  # 9 = 90% stretch factor
        actions_layout.addStretch(1)  # 1 = 10% stretch for empty space
        table.setCellWidget(row, 6, actions_widget)


if __name__ == "__main__":
    """
    Main entry point for the application.
    Creates and runs the admin panel.
    """
    app = QApplication(sys.argv)
    
    # Admin user information
    admin_info = {
        "name": "Divye Chaudhary", 
        "email": "divyechaudhary04@gmail.com", 
        "role": "Administrator"
    }
    
    # Create and show main window
    window = AdminPanel(admin_info, None)
    
    # Start the application event loop
    sys.exit(app.exec_())