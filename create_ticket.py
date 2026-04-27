# create_ticket.py - PROFESSIONAL FULL-PAGE DESIGN
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QComboBox, QLineEdit, QTextEdit, QFormLayout, QGroupBox,
    QScrollArea, QMessageBox, QDateEdit, QTimeEdit, QCheckBox, QDesktopWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
import json
import os
import mysql.connector
from datetime import datetime

class CreateTicketWidget(QWidget):
    ticket_created = pyqtSignal(dict)
    
    def __init__(self, controller=None, user_data=None):
        super().__init__()
        self.controller = controller
        self.user_data = user_data or {}
        
        # Comprehensive mapping of user data from various possible key names
        self.user_info = {
            'name': (
                self.user_data.get('name') or 
                self.user_data.get('full_name') or
                f"{self.user_data.get('first_name', '')} {self.user_data.get('last_name', '')}".strip() or
                self.user_data.get('user_name', '') or
                ""
            ),
            'email': (
                self.user_data.get('email') or 
                self.user_data.get('user_email') or
                ""
            ),
            'department': (
                self.user_data.get('department') or 
                self.user_data.get('company') or
                self.user_data.get('user_department') or
                ""
            ),
            'phone': (
                self.user_data.get('phone') or 
                self.user_data.get('contact_phone') or
                ""
            )
        }
        
        # Debug output to verify data is being received
        print(f"[CreateTicketWidget] ========== INITIALIZATION ==========")
        print(f"[CreateTicketWidget] Raw user_data received: {self.user_data}")
        print(f"[CreateTicketWidget] Mapped user_info: {self.user_info}")
        print(f"[CreateTicketWidget] =====================================")
        
        self.setWindowTitle("Create New Ticket - ITIL Compliant")
        self.showMaximized()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #D6EAF8;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #2C3E50;
            }
        """)
        self.initUI()
        self.load_configuration_data()
        
    def initUI(self):
        # Main layout with scroll area that takes full page
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for entire page
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #D6EAF8;
            }
            QScrollBar:vertical {
                background: #A9CCE3;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498DB;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980B9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main content widget that takes full width
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #D6EAF8;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(100, 20, 100, 40)  # Reduced top margin
        
        # Header with compact design
        header_label = QLabel("Create New Ticket")
        header_label.setFont(QFont("Segoe UI", 28, QFont.Bold))  # Slightly smaller font
        header_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                padding: 10px 0px 5px 0px;  # Reduced padding
                background-color: transparent;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setMinimumHeight(60)  # Reduced minimum height
        
        subheader_label = QLabel("ITIL 4 Compliant Ticketing System")
        subheader_label.setFont(QFont("Segoe UI", 14))  # Smaller font
        subheader_label.setStyleSheet("""
            QLabel {
                color: #34495E;
                padding: 8px 0px 20px 0px;  # Reduced padding
                background-color: transparent;
                font-weight: 500;
            }
        """)
        subheader_label.setAlignment(Qt.AlignCenter)
        
        self.content_layout.addWidget(header_label)
        self.content_layout.addWidget(subheader_label)
        
        # Create form sections
        self.create_user_section()
        self.create_classification_section()
        self.create_details_section()
        self.create_additional_section()
        
        # Action buttons
        self.create_action_buttons()
        
        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)
        
        self.update_priority()
        
    def create_user_section(self):
        section_header = QLabel("User Information")
        section_header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        section_header.setStyleSheet("color: #2C3E50; padding: 20px 0px 15px 0px;")
        self.content_layout.addWidget(section_header)
        
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #EBF5FB;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setVerticalSpacing(18)
        form_layout.setHorizontalSpacing(35)
        form_layout.setContentsMargins(35, 35, 35, 35)
        
        # Use mapped user_info instead of direct user_data access
        self.user_name = self.create_styled_input(
            self.user_info.get('name', ''), 
            "Auto-populated from login", 
            True
        )
        self.user_email = self.create_styled_input(
            self.user_info.get('email', ''), 
            "Auto-populated from login", 
            True
        )
        self.user_department = self.create_styled_input(
            self.user_info.get('department', ''), 
            "Auto-populated from login", 
            True
        )
        self.contact_phone = self.create_styled_input(
            self.user_info.get('phone', ''), 
            "Optional contact number", 
            False
        )
        
        form_layout.addRow(self.create_form_label("Name:"), self.user_name)
        form_layout.addRow(self.create_form_label("Email:"), self.user_email)
        form_layout.addRow(self.create_form_label("Department:"), self.user_department)
        form_layout.addRow(self.create_form_label("Contact Phone:"), self.contact_phone)
        
        self.content_layout.addWidget(form_container)
        
    def create_classification_section(self):
        section_header = QLabel("Classification & Prioritization")
        section_header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        section_header.setStyleSheet("color: #2C3E50; padding: 30px 0px 15px 0px;")  # Reduced padding
        self.content_layout.addWidget(section_header)
        
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #EBF5FB;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setVerticalSpacing(18)
        form_layout.setHorizontalSpacing(35)
        form_layout.setContentsMargins(35, 35, 35, 35)
        
        self.ticket_type = self.create_styled_combo_box(["", "Incident", "Service Request", "Change Request"])
        self.ticket_type.currentTextChanged.connect(self.on_ticket_type_changed)
        
        self.service = self.create_styled_combo_box([""])
        self.service.currentTextChanged.connect(self.on_service_changed)
        
        self.category = self.create_styled_combo_box([""])
        self.category.currentTextChanged.connect(self.on_category_changed)
        
        self.subcategory = self.create_styled_combo_box([""])
        
        self.impact = self.create_styled_combo_box(["", "Individual", "Department", "Entire Organization"])
        self.impact.currentTextChanged.connect(self.update_priority)
        
        self.urgency = self.create_styled_combo_box(["", "Low", "Medium", "High", "Critical"])
        self.urgency.currentTextChanged.connect(self.update_priority)
        
        self.priority = QLabel("Not calculated")
        self.priority.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 15px;
                color: #2C3E50;
                background-color: #D1F2EB;
                padding: 14px 18px;
                border-radius: 8px;
                border: 1px solid #A3E4D7;
            }
        """)
        
        self.assignment_group = self.create_styled_combo_box([""])
        
        form_layout.addRow(self.create_form_label("Ticket Type *:"), self.ticket_type)
        form_layout.addRow(self.create_form_label("Service *:"), self.service)
        form_layout.addRow(self.create_form_label("Category *:"), self.category)
        form_layout.addRow(self.create_form_label("Subcategory:"), self.subcategory)
        form_layout.addRow(self.create_form_label("Impact *:"), self.impact)
        form_layout.addRow(self.create_form_label("Urgency *:"), self.urgency)
        form_layout.addRow(self.create_form_label("Calculated Priority:"), self.priority)
        form_layout.addRow(self.create_form_label("Assignment Group:"), self.assignment_group)
        
        self.content_layout.addWidget(form_container)
    
    def create_details_section(self):
        section_header = QLabel("Ticket Details")
        section_header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        section_header.setStyleSheet("color: #2C3E50; padding: 30px 0px 15px 0px;")  # Reduced padding
        self.content_layout.addWidget(section_header)
        
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #EBF5FB;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(18)
        form_layout.setContentsMargins(35, 35, 35, 35)
        
        # Subject row
        subject_layout = QHBoxLayout()
        subject_label = self.create_form_label("Subject *:")
        self.subject = self.create_styled_input("", "Brief summary of the issue or request...", False)
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject)
        form_layout.addLayout(subject_layout)
        
        # Description
        desc_label = self.create_form_label("Description *:")
        form_layout.addWidget(desc_label)
        
        self.description = QTextEdit()
        self.description.setPlaceholderText(
            "Please provide detailed information:\n"
            "• What were you doing when the problem occurred?\n"
            "• What error messages did you see?\n"
            "• When did the issue start?\n"
            "• Steps to reproduce the issue..."
        )
        self.description.setMinimumHeight(160)
        self.description.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #AED6F1;
                border-radius: 8px;
                padding: 18px;
                font-size: 15px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #3498DB;
                background-color: #F8F9F9;
            }
            QTextEdit:hover {
                border-color: #3498DB;
            }
        """)
        form_layout.addWidget(self.description)
        
        # Attachment
        attach_layout = QHBoxLayout()
        self.attach_btn = QPushButton("📎 Attach Files")
        self.attach_btn.setFixedHeight(45)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #85C1E9;
                color: #2C3E50;
                font-weight: bold;
                font-size: 15px;
                border: none;
                border-radius: 8px;
                padding: 0 25px;
            }
            QPushButton:hover {
                background-color: #5DADE2;
                color: white;
            }
        """)
        self.attach_btn.clicked.connect(self.attach_files)
        
        self.attachment_label = QLabel("No files attached")
        self.attachment_label.setStyleSheet("color: #566573; font-style: italic; font-size: 14px; padding: 5px;")
        
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addWidget(self.attachment_label)
        attach_layout.addStretch()
        form_layout.addLayout(attach_layout)
        
        self.content_layout.addWidget(form_container)
    
    def create_additional_section(self):
        section_header = QLabel("Additional Information")
        section_header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        section_header.setStyleSheet("color: #2C3E50; padding: 30px 0px 15px 0px;")  # Reduced padding
        self.content_layout.addWidget(section_header)
        
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #EBF5FB;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        form_layout = QFormLayout(form_container)
        form_layout.setVerticalSpacing(18)
        form_layout.setHorizontalSpacing(35)
        form_layout.setContentsMargins(35, 35, 35, 35)
        
        # Date input
        self.occurrence_date = QDateEdit()
        self.occurrence_date.setDate(QDateTime.currentDateTime().date())
        self.occurrence_date.setCalendarPopup(True)
        self.occurrence_date.setDisplayFormat("MMMM d, yyyy")
        self.occurrence_date.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 2px solid #D6DBDF;
                border-radius: 8px;
                padding: 14px 18px;
                font-size: 15px;
                color: #2C3E50;
                min-height: 25px;
            }
            QDateEdit:focus {
                border-color: #3498DB;
            }
            QDateEdit:hover {
                border-color: #85C1E9;
            }
        """)
        
        # Time input
        self.occurrence_time = QTimeEdit()
        self.occurrence_time.setTime(QDateTime.currentDateTime().time())
        self.occurrence_time.setDisplayFormat("h:mm AP")
        self.occurrence_time.setStyleSheet("""
            QTimeEdit {
                background-color: white;
                border: 2px solid #D6DBDF;
                border-radius: 8px;
                padding: 14px 18px;
                font-size: 15px;
                color: #2C3E50;
                min-height: 25px;
            }
            QTimeEdit:focus {
                border-color: #3498DB;
            }
            QTimeEdit:hover {
                border-color: #85C1E9;
            }
        """)
        
        # Checkbox
        self.business_hours = QCheckBox("Issue occurred during business hours")
        self.business_hours.setChecked(True)
        self.business_hours.setStyleSheet("""
            QCheckBox {
                spacing: 12px;
                font-weight: 500;
                color: #2C3E50;
                font-size: 15px;
                padding: 10px 0px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #85C1E9;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #3498DB;
                border-color: #3498DB;
            }
        """)
        
        # Related tickets input
        self.related_tickets = self.create_styled_input("", "e.g., INC-001, SRQ-005", False)
        self.related_tickets.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #D6DBDF;
                border-radius: 8px;
                padding: 14px 18px;
                font-size: 15px;
                color: #2C3E50;
                min-height: 25px;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
            QLineEdit:hover {
                border-color: #85C1E9;
            }
            QLineEdit::placeholder {
                color: #7B8D93;
                font-style: italic;
            }
        """)
        
        form_layout.addRow(self.create_form_label("Occurrence Date:"), self.occurrence_date)
        form_layout.addRow(self.create_form_label("Occurrence Time:"), self.occurrence_time)
        form_layout.addRow("", self.business_hours)
        form_layout.addRow(self.create_form_label("Related Tickets:"), self.related_tickets)
        
        self.content_layout.addWidget(form_container)
    
    def create_action_buttons(self):
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 40, 0, 30)  # Reduced top margin
        
        draft_btn = QPushButton("Save Draft")
        draft_btn.setFixedHeight(55)
        draft_btn.setStyleSheet("""
            QPushButton {
                background-color: #7FB3D5;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 0 40px;
            }
            QPushButton:hover {
                background-color: #5499C7;
            }
        """)
        
        submit_btn = QPushButton("Submit Ticket")
        submit_btn.setFixedHeight(55)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #58D68D;
                color: white;
                font-size: 17px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 0 50px;
            }
            QPushButton:hover {
                background-color: #28B463;
            }
        """)
        submit_btn.clicked.connect(self.submit_ticket)
        
        button_layout.addWidget(draft_btn)
        button_layout.addStretch()
        button_layout.addWidget(submit_btn)
        
        self.content_layout.addWidget(button_container)
    
    def create_styled_input(self, text, placeholder, readonly=False):
        input_field = QLineEdit()
        input_field.setText(text)
        input_field.setPlaceholderText(placeholder)
        input_field.setReadOnly(readonly)
        input_field.setStyleSheet(self.get_input_style(readonly))
        return input_field
    
    def create_styled_combo_box(self, items):
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(self.get_combo_style())
        combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return combo
    
    def create_form_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #2C3E50;
                font-size: 16px;
                padding: 8px;
            }
        """)
        return label
    
    def get_input_style(self, readonly=False):
        if readonly:
            return """
                QLineEdit {
                    background-color: #F4F6F6;
                    border: 2px solid #D6DBDF;
                    border-radius: 8px;
                    padding: 14px 18px;
                    font-size: 15px;
                    color: #566573;
                }
            """
        else:
            return """
                QLineEdit {
                    background-color: white;
                    border: 2px solid #D6DBDF;
                    border-radius: 8px;
                    padding: 14px 18px;
                    font-size: 15px;
                    color: #2C3E50;
                }
                QLineEdit:focus {
                    border-color: #3498DB;
                    background-color: #F8F9F9;
                }
                QLineEdit:hover {
                    border-color: #85C1E9;
                }
            """
    
    def get_combo_style(self):
        return """
            QComboBox {
                background-color: white;
                border: 2px solid #D6DBDF;
                border-radius: 8px;
                padding: 14px 18px;
                font-size: 15px;
                color: #2C3E50;
                min-width: 220px;
            }
            QComboBox:focus {
                border-color: #3498DB;
                background-color: #F8F9F9;
            }
            QComboBox:hover {
                border-color: #85C1E9;
                background-color: #F8F9F9;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 35px;
                border-left: 1px solid #D6DBDF;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: #EBF5FB;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2C3E50;
                width: 0px;
                height: 0px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #3498DB;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #D6DBDF;
                border-radius: 8px;
                background-color: white;
                outline: none;
                font-size: 14px;
                padding: 8px;
                margin-top: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 12px 15px;
                border-radius: 6px;
                color: #2C3E50;
                margin: 2px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498DB;
                color: white;
                border: 1px solid #2980B9;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #D4E6F1;
                color: #2C3E50;
                border: 1px solid #85C1E9;
            }
            QComboBox QAbstractItemView::item:selected:hover {
                background-color: #2980B9;
                color: white;
            }
        """

    def load_configuration_data(self):
        """Load service catalog data"""
        try:
            self.service_catalog = {
                "Email Services": {
                    "categories": {
                        "Access Issues": ["Cannot Login", "Password Reset", "Account Locked"],
                        "Configuration": ["Outlook Setup", "Mobile Device", "Signature Setup"],
                        "Performance": ["Slow Performance", "Connection Issues", "Sync Problems"]
                    },
                    "assignment_group": "Email Support Team"
                },
                "Network Services": {
                    "categories": {
                        "Connectivity": ["No Internet", "Slow Connection", "VPN Issues"],
                        "WiFi": ["WiFi Not Working", "Weak Signal", "Authentication Failed"]
                    },
                    "assignment_group": "Network Team"
                },
                "Software Applications": {
                    "categories": {
                        "Office Suite": ["Word Issues", "Excel Problems", "PowerPoint Error"],
                        "CRM": ["Login Issues", "Data Not Loading", "Report Generation"]
                    },
                    "assignment_group": "Application Support"
                }
            }
            
            for service in self.service_catalog.keys():
                self.service.addItem(service)
                
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def on_ticket_type_changed(self, ticket_type):
        pass
    
    def on_service_changed(self, service):
        self.category.clear()
        self.category.addItem("")
        self.subcategory.clear()
        self.subcategory.addItem("")
        
        if service and service in self.service_catalog:
            categories = list(self.service_catalog[service]["categories"].keys())
            for category in categories:
                self.category.addItem(category)
            
            assignment_group = self.service_catalog[service]["assignment_group"]
            self.assignment_group.clear()
            self.assignment_group.addItem("")
            self.assignment_group.addItem(assignment_group)
    
    def on_category_changed(self, category):
        self.subcategory.clear()
        self.subcategory.addItem("")
        
        service = self.service.currentText()
        if service and category and service in self.service_catalog:
            categories = self.service_catalog[service]["categories"]
            if category in categories:
                subcategories = categories[category]
                for subcategory in subcategories:
                    self.subcategory.addItem(subcategory)

    def update_priority(self):
        impact = self.impact.currentText()
        urgency = self.urgency.currentText()
        
        if not impact or not urgency:
            self.priority.setText("Not calculated")
            self.priority.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 15px;
                    color: #566573;
                    background-color: #EAEDED;
                    padding: 14px 18px;
                    border-radius: 8px;
                    border: 1px solid #BDC3C7;
                }
            """)
            return
        
        priority_matrix = {
            ("Individual", "Low"): "P4 - Low",
            ("Individual", "Medium"): "P4 - Low", 
            ("Individual", "High"): "P3 - Medium",
            ("Individual", "Critical"): "P2 - High",
            ("Department", "Low"): "P4 - Low",
            ("Department", "Medium"): "P3 - Medium",
            ("Department", "High"): "P2 - High", 
            ("Department", "Critical"): "P1 - Critical",
            ("Entire Organization", "Low"): "P3 - Medium",
            ("Entire Organization", "Medium"): "P2 - High",
            ("Entire Organization", "High"): "P1 - Critical",
            ("Entire Organization", "Critical"): "P1 - Critical"
        }
        
        priority = priority_matrix.get((impact, urgency), "P4 - Low")
        self.priority.setText(priority)
        
        if "P1" in priority:
            self.priority.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 15px;
                    color: #E74C3C;
                    background-color: #FDEDEC;
                    padding: 14px 18px;
                    border-radius: 8px;
                    border: 1px solid #F5B7B1;
                }
            """)
        elif "P2" in priority:
            self.priority.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 15px;
                    color: #E67E22;
                    background-color: #FEF5E7;
                    padding: 14px 18px;
                    border-radius: 8px;
                    border: 1px solid #F8C471;
                }
            """)
        elif "P3" in priority:
            self.priority.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 15px;
                    color: #F39C12;
                    background-color: #FEF9E7;
                    padding: 14px 18px;
                    border-radius: 8px;
                    border: 1px solid #F7DC6F;
                }
            """)
        else:
            self.priority.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 15px;
                    color: #27AE60;
                    background-color: #EAFAF1;
                    padding: 14px 18px;
                    border-radius: 8px;
                    border: 1px solid #A9DFBF;
                }
            """)

    def attach_files(self):
        QMessageBox.information(self, "Attachment", 
                              "File attachment feature would be implemented here.")
        self.attachment_label.setText("Files ready to attach")
    
    def validate_form(self):
        required_fields = [
            (self.ticket_type.currentText(), "Ticket Type"),
            (self.service.currentText(), "Service"),
            (self.category.currentText(), "Category"),
            (self.impact.currentText(), "Impact"),
            (self.urgency.currentText(), "Urgency"),
            (self.subject.text().strip(), "Subject"),
            (self.description.toPlainText().strip(), "Description")
        ]
        
        missing_fields = []
        for field_value, field_name in required_fields:
            if not field_value:
                missing_fields.append(field_name)
        
        if missing_fields:
            QMessageBox.warning(self, "Missing Information", 
                              f"Please fill in the following required fields:\n• " + 
                              "\n• ".join(missing_fields))
            return False
        
        if len(self.subject.text().strip()) < 10:
            QMessageBox.warning(self, "Invalid Subject", 
                              "Subject should be at least 10 characters long.")
            return False
            
        if len(self.description.toPlainText().strip()) < 20:
            QMessageBox.warning(self, "Insufficient Description", 
                              "Please provide a more detailed description (at least 20 characters).")
            return False
        
        return True
    
    def generate_ticket_number(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        type_prefix = {
            "Incident": "INC",
            "Service Request": "SRQ", 
            "Change Request": "CHG"
        }.get(self.ticket_type.currentText(), "TKT")
        return f"{type_prefix}-{timestamp}"
    
    def submit_ticket(self):
        if not self.validate_form():
            return
        
        try:
            ticket_data = {
                "ticket_number": self.generate_ticket_number(),
                "created_at": QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"),
                "user_name": self.user_name.text(),
                "user_email": self.user_email.text(),
                "user_department": self.user_department.text(),
                "contact_phone": self.contact_phone.text(),
                "ticket_type": self.ticket_type.currentText(),
                "service": self.service.currentText(),
                "category": self.category.currentText(),
                "subcategory": self.subcategory.currentText(),
                "impact": self.impact.currentText(),
                "urgency": self.urgency.currentText(),
                "priority": self.priority.text(),
                "subject": self.subject.text().strip(),
                "description": self.description.toPlainText().strip(),
                "attachments": self.attachment_label.text(),
                "occurrence_date": self.occurrence_date.date().toString("yyyy-MM-dd"),
                "occurrence_time": self.occurrence_time.time().toString("hh:mm"),
                "business_hours": self.business_hours.isChecked(),
                "related_tickets": self.related_tickets.text(),
                "assignment_group": self.assignment_group.currentText(),
                "status": "New"
            }
            
            self.save_ticket_to_storage(ticket_data)
            self.save_ticket_to_mysql(ticket_data)

            
            QMessageBox.information(self, "Ticket Created Successfully!",
                                  f"🎉 Your ticket has been created!\n\n"
                                  f"Ticket Number: {ticket_data['ticket_number']}\n"
                                  f"Priority: {ticket_data['priority']}\n"
                                  f"Assignment Group: {ticket_data['assignment_group']}\n\n"
                                  f"You will receive email updates on your ticket status.")
            
            self.ticket_created.emit(ticket_data)
            self.reset_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to create ticket:\n{str(e)}")
    
    def save_ticket_to_storage(self, ticket_data):
        try:
            os.makedirs("tickets", exist_ok=True)
            filename = f"tickets/{ticket_data['ticket_number']}.json"
            with open(filename, 'w') as f:
                json.dump(ticket_data, f, indent=2)
            print(f"Ticket saved to: {filename}")
        except Exception as e:
            print(f"Error saving ticket: {e}")
    def save_ticket_to_mysql(self, ticket_data):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Kai*123",
                database="kaiticket"
            )
            cur = conn.cursor()

            query = """
                INSERT INTO tickets (
                    ticket_number, created_at, user_name, user_email, user_department,
                    contact_phone, ticket_type, service, category, subcategory,
                    impact, urgency, priority, subject, description,
                    attachments, occurrence_date, occurrence_time, business_hours,
                    related_tickets, assignment_group, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                ticket_data["ticket_number"],
                ticket_data["created_at"],
                ticket_data["user_name"],
                ticket_data["user_email"],
                ticket_data["user_department"],
                ticket_data["contact_phone"],
                ticket_data["ticket_type"],
                ticket_data["service"],
                ticket_data["category"],
                ticket_data["subcategory"],
                ticket_data["impact"],
                ticket_data["urgency"],
                ticket_data["priority"],
                ticket_data["subject"],
                ticket_data["description"],
                ticket_data["attachments"],
                ticket_data["occurrence_date"],
                ticket_data["occurrence_time"],
                ticket_data["business_hours"],
                ticket_data["related_tickets"],
                ticket_data["assignment_group"],
                ticket_data["status"]
            )

            cur.execute(query, values)
            conn.commit()
            cur.close()
            conn.close()
            print("Ticket saved to MySQL database.")
        except Exception as e:
            print("Error saving ticket to MySQL:", e)
    
    def reset_form(self):
        self.ticket_type.setCurrentIndex(0)
        self.service.setCurrentIndex(0)
        self.category.clear()
        self.category.addItem("")
        self.subcategory.clear()
        self.subcategory.addItem("")
        self.impact.setCurrentIndex(0)
        self.urgency.setCurrentIndex(0)
        self.assignment_group.clear()
        self.assignment_group.addItem("")
        self.subject.clear()
        self.description.clear()
        self.contact_phone.clear()
        self.attachment_label.setText("No files attached")
        self.occurrence_date.setDate(QDateTime.currentDateTime().date())
        self.occurrence_time.setTime(QDateTime.currentDateTime().time())
        self.business_hours.setChecked(True)
        self.related_tickets.clear()
        self.update_priority()


class TicketManagementSystem(QWidget):
    def __init__(self, controller=None, user_data=None):
        super().__init__()
        self.controller = controller
        self.user_data = user_data or {}
        print(f"[TicketManagementSystem] Received user_data: {self.user_data}")
        self.showMaximized()
        self.setStyleSheet("QWidget { background-color: #D6EAF8; }")
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # Pass controller and user_data to CreateTicketWidget
        self.create_ticket_widget = CreateTicketWidget(
            controller=self.controller, 
            user_data=self.user_data
        )
        self.create_ticket_widget.ticket_created.connect(self.on_ticket_created)
        layout.addWidget(self.create_ticket_widget)
    
    def on_ticket_created(self, ticket_data):
        print(f"New ticket created: {ticket_data['ticket_number']}")