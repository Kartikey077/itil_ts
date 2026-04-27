# user_dashboard.py - USER DASHBOARD WITH TICKET MANAGEMENT
import sys
from openai import OpenAI
client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QTextEdit, QLineEdit, QComboBox,
    QScrollArea, QGroupBox, QGridLayout, QMessageBox, QSizePolicy,
    QMenu, QAction, QListWidget, QListWidgetItem, QInputDialog, QDialog
)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient, QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer, QDateTime, QSize
import mysql.connector
import json
import os

# Import create_ticket module for ticket creation functionality
from create_ticket import TicketManagementSystem

class UserDashboard(QMainWindow):
    """Main dashboard for users to view and manage their tickets"""
    
    # Signal for new ticket notification
    new_ticket_notification = pyqtSignal(dict)
    
    def __init__(self, user_data, controller):
        super().__init__()
        self.controller = controller
        self.user_data = user_data
        self.user_email = user_data.get('email', '')
        # Store notifications
        self.notifications = []
        self.unread_count = 0
        print(f"[Dashboard] User logged in: {self.user_data.get('name')} ({self.user_email})")
        
        self.setWindowTitle(f"User Dashboard - {user_data.get('name', 'User')}")
        self.showMaximized()
        
        # Store stat labels for real-time updates
        self.stat_labels = {}
        
        # Timer for checking new tickets/notifications
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_new_tickets)
        self.notification_timer.start(30000)
        
        # Store last check timestamp
        self.last_check_time = QDateTime.currentDateTime()
        
        # Predefined knowledge base articles
        self.knowledge_base = [
            {"title": "How to Reset Your Password", 
             "content": "1. Go to login page\n2. Click 'Forgot Password'\n3. Enter your email\n4. Check your inbox for reset link\n5. Create new password",
             "icon": "🔑"},
            {"title": "VPN Connection Issues", 
             "content": "1. Restart VPN client\n2. Clear DNS cache: ipconfig /flushdns\n3. Check internet connection\n4. Update VPN software\n5. Contact IT if persists",
             "icon": "🌐"},
            {"title": "Email Not Syncing", 
             "content": "1. Check internet connection\n2. Restart Outlook/Email client\n3. Clear cache\n4. Re-add account if needed\n5. Check server settings",
             "icon": "📧"},
            {"title": "Software Installation Failed", 
             "content": "1. Run as Administrator\n2. Disable antivirus temporarily\n3. Check disk space\n4. Install required dependencies\n5. Use compatibility mode",
             "icon": "💻"},
            {"title": "Printer Not Working", 
             "content": "1. Check printer power and connection\n2. Clear print queue\n3. Restart print spooler\n4. Reinstall printer drivers\n5. Set as default printer",
             "icon": "🖨️"}
        ]
        
        self.initUI()
        self.load_user_data()
        self.load_recent_tickets()
        self.load_notifications_from_db()
        
        # Connect notification signal
        self.new_ticket_notification.connect(self.add_notification)
        
        # Create chat button after UI is ready
        QTimer.singleShot(500, self.create_chat_button)
        
    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.controller:
                self.controller.show_login()
    
    def initUI(self):
        """Initialize the user interface components"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #f0f2f5; border: none; }")
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # ==================== HEADER ====================
        header_widget = QWidget()
        header_widget.setFixedHeight(130)
        header_widget.setStyleSheet("""
            background-color: #2c3e50;
            border-radius: 15px;
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(35, 20, 35, 20)
        
        # Welcome section
        welcome_container = QWidget()
        welcome_layout = QVBoxLayout(welcome_container)
        welcome_layout.setSpacing(8)
        welcome_layout.setContentsMargins(0, 5, 0, 5)
        
        welcome_label = QLabel(f"👋 Welcome, {self.user_data.get('name', 'User')}")
        welcome_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        welcome_label.setStyleSheet("color: white;")
        
        date_label = QLabel(QDate.currentDate().toString("dddd, MMMM d, yyyy"))
        date_label.setFont(QFont("Segoe UI", 13))
        date_label.setStyleSheet("color: #bdc3c7;")
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(date_label)
        
        header_layout.addWidget(welcome_container)
        header_layout.addStretch()
        
        # Right side buttons
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Notification button
        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFixedSize(60, 60)
        self.notif_btn.setFont(QFont("Segoe UI", 24))
        self.notif_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.15);
                color: white;
                border-radius: 30px;
                font-size: 26px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.25);
            }
        """)
        self.notif_btn.clicked.connect(self.show_notification_menu)
        
        # Profile button
        self.user_logo_btn = QPushButton()
        self.user_logo_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.user_logo_btn.setFixedSize(65, 65)
        
        if os.path.exists("user-circle.png"):
            pixmap = QPixmap("user-circle.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.user_logo_btn.setIcon(QIcon(scaled_pixmap))
                self.user_logo_btn.setIconSize(QSize(60, 60))
                self.user_logo_btn.setText("")
        else:
            self.user_logo_btn.setText("👤")
            self.user_logo_btn.setFont(QFont("Segoe UI", 28))
        
        self.user_logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 2px solid white;
                border-radius: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.user_logo_btn.clicked.connect(self.show_user_tooltip)
        
        right_layout.addWidget(self.notif_btn)
        right_layout.addWidget(self.user_logo_btn)
        
        header_layout.addWidget(right_container)
        
        main_layout.addWidget(header_widget)
        
        # ==================== STATISTICS CARDS ====================
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        stats_data = [
            ("📋 Open Tickets", "open_tickets", "#e74c3c"),
            ("⏳ Pending", "pending_tickets", "#f39c12"),
            ("✅ Resolved/Closed", "resolved_closed", "#27ae60"),
            ("⏱️ Avg Response", "avg_response", "#3498db")
        ]
        
        self.stat_cards = {}
        for title, key, color in stats_data:
            card = self.create_stat_card(title, "0", color, key)
            stats_layout.addWidget(card)
            self.stat_cards[key] = card
        
        main_layout.addWidget(stats_widget)
        
        # ==================== QUICK ACTIONS ====================
        actions_label = QLabel("Quick Actions")
        actions_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        actions_label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")
        main_layout.addWidget(actions_label)
        
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setSpacing(20)
        
        create_btn = QPushButton("📝 Create New Ticket")
        create_btn.setMinimumHeight(70)
        create_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219a54;
            }
        """)
        create_btn.clicked.connect(self.open_create_ticket)
        
        check_btn = QPushButton("🔍 Check Ticket Status")
        check_btn.setMinimumHeight(70)
        check_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        check_btn.clicked.connect(self.check_ticket_status)
        
        actions_layout.addWidget(create_btn, 1)
        actions_layout.addWidget(check_btn, 1)
        
        main_layout.addWidget(actions_widget)
        
        # ==================== RECENT TICKETS ====================
        tickets_label = QLabel("Recent Tickets")
        tickets_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        tickets_label.setStyleSheet("color: #2c3e50; margin-top: 15px;")
        main_layout.addWidget(tickets_label)
        
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 10)
        
        filter_label = QLabel("Filter by:")
        filter_label.setFont(QFont("Segoe UI", 11))
        filter_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Open", "Pending", "In Progress", "Resolved", "Closed"])
        self.filter_combo.setFixedWidth(120)
        self.filter_combo.setFont(QFont("Segoe UI", 11))
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.filter_tickets)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setFont(QFont("Segoe UI", 11))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 5px 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all_data)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(filter_widget)
        
        # Tickets table
        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(5)
        self.tickets_table.setHorizontalHeaderLabels(["Ticket ID", "Subject", "Status", "Priority", "Created"])
        self.tickets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tickets_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #3498db;
                font-size: 13px;
            }
        """)
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tickets_table.setMinimumHeight(300)
        self.tickets_table.cellDoubleClicked.connect(self.view_ticket_details)
        
        main_layout.addWidget(self.tickets_table)
        
        # ==================== KNOWLEDGE BASE SECTION ====================
        kb_label = QLabel("📚 Knowledge Base")
        kb_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        kb_label.setStyleSheet("color: #2c3e50; margin-top: 15px;")
        main_layout.addWidget(kb_label)
        
        kb_widget = QWidget()
        kb_grid = QGridLayout(kb_widget)
        kb_grid.setSpacing(15)
        kb_grid.setContentsMargins(0, 0, 0, 0)
        
        row, col = 0, 0
        for article in self.knowledge_base:
            kb_card = self.create_kb_card(article)
            kb_grid.addWidget(kb_card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        main_layout.addWidget(kb_widget)
        main_layout.addStretch()
    
    def create_stat_card(self, title, value, color, key):
        """Create statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e8ed;
                padding: 15px;
            }}
        """)
        card.setMinimumHeight(110)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: #7f8c8d;")
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.value_label = value_label
        card.key = key
        
        return card
    
    def create_kb_card(self, article):
        """Create knowledge base card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e1e8ed;
                padding: 12px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        card.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel(article["icon"])
        icon_label.setFont(QFont("Segoe UI", 24))
        
        title_label = QLabel(article["title"])
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setWordWrap(True)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        preview = article["content"][:60] + "..." if len(article["content"]) > 60 else article["content"]
        preview_label = QLabel(preview)
        preview_label.setFont(QFont("Segoe UI", 10))
        preview_label.setStyleSheet("color: #7f8c8d;")
        preview_label.setWordWrap(True)
        
        layout.addLayout(header_layout)
        layout.addWidget(preview_label)
        
        card.article = article
        card.mousePressEvent = lambda e: self.show_kb_article(article)
        
        return card
    
    def show_kb_article(self, article):
        """Show full knowledge base article"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Knowledge Base Article")
        dialog.setFixedSize(550, 450)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel(article["icon"])
        icon_label.setFont(QFont("Segoe UI", 36))
        
        title_label = QLabel(article["title"])
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        content_text = QTextEdit()
        content_text.setPlainText(article["content"])
        content_text.setReadOnly(True)
        content_text.setMinimumHeight(250)
        content_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                background-color: #f8f9fa;
            }
        """)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        
        layout.addLayout(header_layout)
        layout.addWidget(content_text)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    # ==================== PROFILE DROPDOWN - LARGER TEXT ====================
    def show_user_tooltip(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 12px;
                padding: 8px;
                min-width: 240px;
            }
            QMenu::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 2px;
                font-size: 16px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ecf0f1;
                margin: 8px 5px;
            }
        """)

        name_action = menu.addAction(f"👤 {self.user_data.get('name', 'User')}")
        name_action.setEnabled(False)
        
        email_action = menu.addAction(f"📧 {self.user_data.get('email', '')}")
        email_action.setEnabled(False)
        
        menu.addSeparator()
        
        profile_action = menu.addAction("👤 View Profile")
        profile_action.triggered.connect(self.show_profile)
        
        menu.addSeparator()
        
        logout_action = menu.addAction("🚪 Logout")
        logout_action.triggered.connect(self.logout)

        button_pos = self.user_logo_btn.mapToGlobal(self.user_logo_btn.rect().bottomLeft())
        menu.exec_(button_pos)
    
    # ==================== NOTIFICATION DROPDOWN - LARGER TEXT ====================
    
    def load_notifications_from_db(self):
        try:
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT ticket_number, created_at
                    FROM tickets 
                    WHERE user_email = %s 
                    AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
                    ORDER BY created_at DESC LIMIT 10
                """
                cursor.execute(query, (self.user_email,))
                tickets = cursor.fetchall()
                cursor.close()
                conn.close()
                
                for ticket in tickets:
                    self.add_notification({
                        'ticket_id': ticket['ticket_number'],
                        'timestamp': ticket['created_at']
                    }, from_db=True)
        except Exception as e:
            print(f"[Notification] Error: {e}")
    
    def check_new_tickets(self):
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            last_check_str = self.last_check_time.toString("yyyy-MM-dd HH:mm:ss")
            query = """
                SELECT ticket_number, created_at
                FROM tickets 
                WHERE user_email = %s AND created_at > %s
            """
            cursor.execute(query, (self.user_email, last_check_str))
            new_tickets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            self.last_check_time = QDateTime.currentDateTime()
            
            for ticket in new_tickets:
                self.add_notification({
                    'ticket_id': ticket['ticket_number'],
                    'timestamp': ticket['created_at']
                })
        except Exception as e:
            print(f"[Notification] Error: {e}")
    
    def add_notification(self, notification, from_db=False):
        for existing in self.notifications:
            if existing.get('ticket_id') == notification.get('ticket_id'):
                return
        
        notification['read'] = False
        self.notifications.insert(0, notification)
        
        if len(self.notifications) > 15:
            self.notifications = self.notifications[:15]
        
        self.update_notification_button()
        
        if not from_db:
            self.show_notification_popup(notification)
    
    def update_notification_button(self):
        unread = sum(1 for n in self.notifications if not n.get('read', False))
        self.unread_count = unread
        
        if unread > 0:
            self.notif_btn.setText(f"🔔 {unread}")
            self.notif_btn.setFont(QFont("Segoe UI", 20, QFont.Bold))
            self.notif_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 30px;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
        else:
            self.notif_btn.setText("🔔")
            self.notif_btn.setFont(QFont("Segoe UI", 26))
            self.notif_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,0.15);
                    color: white;
                    border-radius: 30px;
                    font-size: 26px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.25);
                }
            """)
    
    def show_notification_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 12px;
                padding: 8px;
                min-width: 280px;
            }
            QMenu::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 2px;
                font-size: 16px;
            }
            QMenu::item:selected {
                background-color: #f0f8ff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ecf0f1;
                margin: 8px 5px;
            }
        """)
        
        if not self.notifications:
            no_notif = menu.addAction("📭 No new notifications")
            no_notif.setEnabled(False)
            no_notif.setStyleSheet("color: #95a5a6; padding: 12px; font-size: 14px;")
        else:
            for notif in self.notifications[:8]:
                ticket_id = notif.get('ticket_id', 'Unknown')
                display_text = f"🎫 Ticket #{ticket_id} created"
                
                action = menu.addAction(display_text)
                action.setData(notif)
                action.setFont(QFont("Segoe UI", 16))
                
                if not notif.get('read', False):
                    font = action.font()
                    font.setBold(True)
                    action.setFont(font)
                
                action.triggered.connect(lambda checked, n=notif: self.open_notification_ticket(n))
            
            if self.unread_count > 0:
                menu.addSeparator()
                mark_action = menu.addAction("✓ Mark all as read")
                mark_action.setFont(QFont("Segoe UI", 16))
                mark_action.triggered.connect(self.mark_all_notifications_read)
        
        button_pos = self.notif_btn.mapToGlobal(self.notif_btn.rect().bottomLeft())
        menu.exec_(button_pos)
    
    def show_notification_popup(self, notification):
        popup = QFrame(self)
        popup.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 12px;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
        """)
        popup.setFixedSize(230, 55)
        
        layout = QHBoxLayout(popup)
        icon_label = QLabel("🎫")
        icon_label.setStyleSheet("font-size: 20px;")
        text_label = QLabel(f"Ticket #{notification.get('ticket_id', '')} created")
        text_label.setFont(QFont("Segoe UI", 12))
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        popup.move(self.width() - popup.width() - 20, self.height() - popup.height() - 100)
        popup.show()
        QTimer.singleShot(3000, popup.deleteLater)
    
    def open_notification_ticket(self, notification):
        notification['read'] = True
        self.update_notification_button()
        self.view_ticket_details_by_id(notification.get('ticket_id'))
    
    def mark_all_notifications_read(self):
        for notif in self.notifications:
            notif['read'] = True
        self.update_notification_button()
    
    def view_ticket_details_by_id(self, ticket_id):
        self.check_ticket_status_with_id(ticket_id)
    
    # ==================== AI CHATBOT - NO BOX ON BORDER ====================
    def create_chat_button(self):
        """Create floating chat button with AI bot image"""
        self.chat_btn = QPushButton(self)
        self.chat_btn.setFixedSize(80, 80)
        self.chat_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        image_loaded = False
        if os.path.exists("ai-bot.png"):
            pixmap = QPixmap("ai-bot.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.chat_btn.setIcon(QIcon(scaled_pixmap))
                self.chat_btn.setIconSize(QSize(75, 75))
                self.chat_btn.setText("")
                image_loaded = True
        
        if not image_loaded and os.path.exists("robot.png"):
            pixmap = QPixmap("robot.png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.chat_btn.setIcon(QIcon(scaled_pixmap))
                self.chat_btn.setIconSize(QSize(75, 75))
                self.chat_btn.setText("")
                image_loaded = True
        
        if not image_loaded:
            self.chat_btn.setText("🤖")
            self.chat_btn.setFont(QFont("Segoe UI", 38))
        
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border-radius: 40px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #219a54, stop:1 #27ae60);
            }
        """)
        
        self.chat_btn.move(self.width() - 100, self.height() - 100)
        self.chat_btn.clicked.connect(self.toggle_chatbot)
        self.chat_btn.show()
        self.chat_btn.raise_()
    
    def create_chatbot(self):
        """Create chatbot window - NO BOX on border"""
        self.chat_window = QWidget(self)
        self.chat_window.setFixedSize(420, 580)
        self.chat_window.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 15px;
                border: none;
            }
        """)
        self.chat_window.move(self.width() - 450, self.height() - 640)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(90)
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #27ae60, stop:1 #2ecc71);
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # AI Avatar
        ai_avatar = QLabel()
        ai_avatar.setFixedSize(55, 55)
        
        if os.path.exists("ai-bot.png"):
            pixmap = QPixmap("ai-bot.png")
            if not pixmap.isNull():
                scaled = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                ai_avatar.setPixmap(scaled)
                ai_avatar.setStyleSheet("border-radius: 25px; background-color: white;")
        else:
            ai_avatar.setText("🤖")
            ai_avatar.setFont(QFont("Segoe UI", 28))
            ai_avatar.setStyleSheet("background-color: white; border-radius: 27px; padding: 5px;")
        
        ai_avatar.setAlignment(Qt.AlignCenter)
        
        # Title widget
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(4)
        
        title_label = QLabel("AI Support Assistant")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        
        status_label = QLabel("🟢 Online • Ready to help")
        status_label.setFont(QFont("Segoe UI", 11))
        status_label.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(status_label)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)
        close_btn.clicked.connect(self.chat_window.hide)
        
        header_layout.addWidget(ai_avatar)
        header_layout.addWidget(title_widget)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_widget)
        
        # Chat area
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none; background-color: #f8f9fa;")
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(12, 12, 12, 12)
        self.chat_container.setLayout(self.chat_layout)
        self.chat_area.setWidget(self.chat_container)
        layout.addWidget(self.chat_area)
        
        # Input area - NO BOX on border
        input_widget = QWidget()
        input_widget.setFixedHeight(70)
        input_widget.setStyleSheet("background-color: white; border-top: none;")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(12, 12, 12, 12)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything...")
        self.chat_input.setFont(QFont("Segoe UI", 12))
        self.chat_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 1px solid #dcdde1;
                border-radius: 25px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #27ae60;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(65)
        send_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 25px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219a54;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_widget)
        
        self.chat_window.setLayout(layout)
        self.chat_window.hide()
        self.add_chat_message("Hello! 👋 I'm your AI support assistant. How can I help you today?", False)
    
    def toggle_chatbot(self):
        if not hasattr(self, 'chat_window'):
            self.create_chatbot()
        
        if self.chat_window.isVisible():
            self.chat_window.hide()
        else:
            self.chat_window.show()
            self.chat_window.raise_()
    
    def send_message(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        
        self.add_chat_message(text, True)
        self.chat_input.clear()
        
        QApplication.processEvents()
        reply = self.get_ai_response(text)
        self.add_chat_message(reply, False)
    
    def add_chat_message(self, text, is_user):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setMaximumWidth(300)
        label.setFont(QFont("Segoe UI", 11))
        
        if is_user:
            label.setStyleSheet("""
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 18px;
            """)
            layout.addStretch()
            layout.addWidget(label)
        else:
            label.setStyleSheet("""
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 15px;
                border-radius: 18px;
            """)
            layout.addWidget(label)
            layout.addStretch()
        
        self.chat_layout.addWidget(container)
        
        QTimer.singleShot(100, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))
    
    def get_ai_response(self, message):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful support assistant for a ticketing system. Keep answers short and friendly."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Error: {e}")
            return "I'm having trouble connecting. Please try again later."
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'chat_btn'):
            self.chat_btn.move(self.width() - 100, self.height() - 100)
        if hasattr(self, 'chat_window') and self.chat_window.isVisible():
            self.chat_window.move(self.width() - 450, self.height() - 640)
    
    # ==================== DATABASE METHODS ====================
    
    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Kai*123",
                database="kaiticket"
            )
            return conn
        except mysql.connector.Error as err:
            print(f"[DB Error] {err}")
            return None
    
    def calculate_avg_response_time(self):
        """Calculate average response time from database - SAME as EmployeeDashboard"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return "124h"  # Default fallback
            
            cursor = conn.cursor()
            
            # Calculate average time between ticket creation and last update (response)
            # For user dashboard, we calculate based on when tickets were updated/responded to
            query = """
                SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, 
                    COALESCE(updated_at, last_updated, NOW()))) as avg_time
                FROM tickets 
                WHERE user_email = %s 
                AND (updated_at IS NOT NULL OR last_updated IS NOT NULL)
            """
            cursor.execute(query, (self.user_email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0] and result[0] > 0:
                avg_hours = round(result[0], 1)
                
                # Format the output nicely
                if avg_hours < 1:
                    # Less than 1 hour - show in minutes
                    avg_minutes = round(avg_hours * 60)
                    return f"{avg_minutes}m"
                elif avg_hours < 24:
                    # Less than 24 hours - show in hours
                    return f"{avg_hours}h"
                else:
                    # 24+ hours - show in days
                    avg_days = round(avg_hours / 24, 1)
                    return f"{avg_days}d"
            
            # If no updated tickets, try with assigned tickets
            query2 = """
                SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, assignment_date)) as avg_time
                FROM tickets t
                LEFT JOIN ticket_assignments ta ON t.ticket_number = ta.ticket_number
                WHERE t.user_email = %s AND ta.assigned_date IS NOT NULL
            """
            cursor2 = conn.cursor()
            cursor2.execute(query2, (self.user_email,))
            result2 = cursor2.fetchone()
            cursor2.close()
            
            if result2 and result2[0] and result2[0] > 0:
                avg_hours = round(result2[0], 1)
                if avg_hours < 1:
                    avg_minutes = round(avg_hours * 60)
                    return f"{avg_minutes}m"
                elif avg_hours < 24:
                    return f"{avg_hours}h"
                else:
                    avg_days = round(avg_hours / 24, 1)
                    return f"{avg_days}d"
            
            return "No data"
            
        except Exception as e:
            print(f"[Error calculating avg response] {e}")
            return "124h"
    
    def load_user_data(self):
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    COUNT(CASE WHEN status IN ('New', 'Open', 'Assigned', 'In Progress', 'On Hold') THEN 1 END) as open_tickets,
                    COUNT(CASE WHEN status IN ('Pending', 'Pending Review') THEN 1 END) as pending_tickets,
                    COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as resolved_closed
                FROM tickets WHERE user_email = %s
            """
            cursor.execute(query, (self.user_email,))
            stats = cursor.fetchone()
            cursor.close()
            conn.close()
            
            avg_response = self.calculate_avg_response_time()
            
            for key, card in self.stat_cards.items():
                if key == "open_tickets":
                    card.value_label.setText(str(stats.get('open_tickets', 0)))
                elif key == "pending_tickets":
                    card.value_label.setText(str(stats.get('pending_tickets', 0)))
                elif key == "resolved_closed":
                    card.value_label.setText(str(stats.get('resolved_closed', 0)))
                elif key == "avg_response":
                    card.value_label.setText(avg_response)
                    
        except Exception as e:
            print(f"[Error] {e}")
    
    def load_recent_tickets(self, filter_text="All"):
        try:
            conn = self.get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            if filter_text == "All":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            elif filter_text == "Open":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s AND status IN ('New', 'Open', 'Assigned', 'On Hold') ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            elif filter_text == "Pending":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s AND status IN ('Pending', 'Pending Review') ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            elif filter_text == "In Progress":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s AND status = 'In Progress' ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            elif filter_text == "Resolved":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s AND status = 'Resolved' ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            elif filter_text == "Closed":
                query = "SELECT ticket_number, subject, status, priority, created_at FROM tickets WHERE user_email = %s AND status = 'Closed' ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (self.user_email,))
            
            tickets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            self.tickets_table.setRowCount(len(tickets))
            
            for row, ticket in enumerate(tickets):
                self.tickets_table.setItem(row, 0, QTableWidgetItem(ticket['ticket_number']))
                
                subject = ticket['subject'][:50] + "..." if len(ticket['subject']) > 50 else ticket['subject']
                self.tickets_table.setItem(row, 1, QTableWidgetItem(subject))
                
                status_item = QTableWidgetItem(ticket['status'])
                if ticket['status'] in ['New', 'Open']:
                    status_item.setForeground(QColor('#e74c3c'))
                elif ticket['status'] == 'Resolved':
                    status_item.setForeground(QColor('#27ae60'))
                elif ticket['status'] in ['Pending', 'Pending Review']:
                    status_item.setForeground(QColor('#f39c12'))
                elif ticket['status'] == 'Closed':
                    status_item.setForeground(QColor('#7f8c8d'))
                elif ticket['status'] == 'In Progress':
                    status_item.setForeground(QColor('#3498db'))
                self.tickets_table.setItem(row, 2, status_item)
                
                priority_item = QTableWidgetItem(ticket['priority'])
                if 'High' in ticket['priority']:
                    priority_item.setForeground(QColor('#e74c3c'))
                elif 'Medium' in ticket['priority']:
                    priority_item.setForeground(QColor('#f39c12'))
                else:
                    priority_item.setForeground(QColor('#27ae60'))
                self.tickets_table.setItem(row, 3, priority_item)
                
                self.tickets_table.setItem(row, 4, QTableWidgetItem(str(ticket['created_at'])[:10]))
                
        except Exception as e:
            print(f"[Error] {e}")
    
    def refresh_all_data(self):
        self.load_user_data()
        self.load_recent_tickets(self.filter_combo.currentText())
        self.check_new_tickets()
        QMessageBox.information(self, "Refreshed", "Dashboard updated successfully!")
    
    def filter_tickets(self, filter_text):
        self.load_recent_tickets(filter_text)
    
    def open_create_ticket(self):
        formatted_user_data = {
            'name': self.user_data.get('name', ''),
            'email': self.user_data.get('email', ''),
            'department': self.user_data.get('department', ''),
            'phone': self.user_data.get('phone', ''),
            'username': self.user_data.get('username', '')
        }
        
        self.ticket_window = TicketManagementSystem(
            controller=self.controller, 
            user_data=formatted_user_data
        )
        
        if hasattr(self.ticket_window, 'create_ticket_widget'):
            self.ticket_window.create_ticket_widget.ticket_created.connect(self.on_ticket_created)
        
        self.ticket_window.show()
        self.ticket_window.raise_()
        self.ticket_window.activateWindow()
    
    def on_ticket_created(self, ticket_data):
        self.add_notification({
            'ticket_id': ticket_data['ticket_number'],
            'timestamp': QDateTime.currentDateTime().toString()
        })
        QTimer.singleShot(500, self.refresh_all_data)
    
    def check_ticket_status(self):
        ticket_id, ok = QInputDialog.getText(self, "Check Ticket Status", 
                                            "Enter Ticket Number:", 
                                            QLineEdit.Normal, "")
        if ok and ticket_id:
            self.check_ticket_status_with_id(ticket_id)
    
    def check_ticket_status_with_id(self, ticket_id):
        try:
            conn = self.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT ticket_number, subject, status, priority, created_at, assigned_to, description
                    FROM tickets 
                    WHERE ticket_number = %s AND user_email = %s
                """
                cursor.execute(query, (ticket_id, self.user_email))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    self.show_ticket_details_dialog(result)
                else:
                    QMessageBox.warning(self, "Not Found", f"Ticket {ticket_id} not found.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to check status: {e}")
    
    def show_ticket_details_dialog(self, ticket):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ticket #{ticket['ticket_number']} - Details")
        dialog.setFixedSize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        status_colors = {
            'New': '#e74c3c', 'Open': '#e74c3c',
            'Pending': '#f39c12', 'Pending Review': '#f39c12',
            'Assigned': '#3498db', 'In Progress': '#9b59b6',
            'On Hold': '#e67e22', 'Resolved': '#27ae60', 'Closed': '#7f8c8d'
        }
        status_color = status_colors.get(ticket['status'], '#3498db')
        
        header_label = QLabel(f"🎫 Ticket #{ticket['ticket_number']}")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_label.setStyleSheet(f"color: {status_color};")
        
        status_badge = QLabel(f"Status: {ticket['status']}")
        status_badge.setFont(QFont("Segoe UI", 13, QFont.Bold))
        status_badge.setStyleSheet(f"""
            background-color: {status_color}20;
            color: {status_color};
            padding: 8px;
            border-radius: 8px;
        """)
        status_badge.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(header_label)
        layout.addWidget(status_badge)
        
        details = [
            ("Subject:", ticket['subject']),
            ("Priority:", ticket['priority']),
            ("Created:", str(ticket['created_at'])[:16]),
            ("Assigned To:", ticket.get('assigned_to', 'Unassigned'))
        ]
        
        for label, value in details:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 8, 0, 8)
            
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 12, QFont.Bold))
            label_widget.setStyleSheet("color: #7f8c8d; min-width: 100px;")
            
            value_widget = QLabel(str(value))
            value_widget.setFont(QFont("Segoe UI", 12))
            value_widget.setWordWrap(True)
            
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            layout.addWidget(row_widget)
        
        if ticket.get('description'):
            desc_label = QLabel("Description:")
            desc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            desc_label.setStyleSheet("color: #7f8c8d; margin-top: 10px;")
            layout.addWidget(desc_label)
            
            desc_text = QTextEdit()
            desc_text.setPlainText(ticket['description'])
            desc_text.setReadOnly(True)
            desc_text.setMaximumHeight(120)
            desc_text.setStyleSheet("border: 1px solid #e1e8ed; border-radius: 8px; padding: 8px; font-size: 12px;")
            layout.addWidget(desc_text)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def show_profile(self):
        profile_text = f"""
        <h3 style='color:#2c3e50'>👤 User Profile</h3>
        <table width='100%' cellpadding='8'>
        <tr><td style='color:#7f8d8d'><b>Name:</b></td><td>{self.user_data.get('name', 'N/A')}</td></tr>
        <tr><td style='color:#7f8d8d'><b>Email:</b></td><td>{self.user_data.get('email', 'N/A')}</td></tr>
        <tr><td style='color:#7f8d8d'><b>Department:</b></td><td>{self.user_data.get('department', 'N/A')}</td></tr>
        <tr><td style='color:#7f8d8d'><b>Phone:</b></td><td>{self.user_data.get('phone', 'N/A')}</td></tr>
        <tr><td style='color:#7f8d8d'><b>Role:</b></td><td>User</td></tr>
        </table>
        """
        QMessageBox.information(self, "User Profile", profile_text)
    
    def view_ticket_details(self, row, column):
        ticket_id = self.tickets_table.item(row, 0).text()
        self.check_ticket_status_with_id(ticket_id)


# Prevent direct execution
if __name__ == "__main__":
    print("Error: user_dashboard.py is a module and should not be run directly.")