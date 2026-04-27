from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSpacerItem, QSizePolicy, QDialog, QTextEdit,
    QLineEdit, QFormLayout, QDialogButtonBox, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette, QPainter, QBrush, QLinearGradient, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
import sys
import os
import webbrowser

# Import MainWindow from login_page
from login_page import MainWindow


class TicketingHome(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Smart Ticketing System - Home")
        self.setGeometry(100, 50, 1200, 800)
        self.setMinimumSize(1000, 700)
        self.showMaximized()
        
        # Set application icon
        if os.path.exists("ticket_icon.ico"):
            self.setWindowIcon(QIcon("ticket_icon.ico"))
        
        self.set_background()
        self.initUI()
        
        # Animation for hero section
        self.animate_hero()

    def set_background(self):
        """Set professional gradient background"""
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0f172a"))
        gradient.setColorAt(0.5, QColor("#1e1b4b"))
        gradient.setColorAt(1.0, QColor("#0a0e27"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def animate_hero(self):
        """Animate hero section elements"""
        self.animation = QPropertyAnimation(self.hero_title, b"geometry")
        self.animation.setDuration(800)
        self.animation.setStartValue(self.hero_title.geometry())
        self.animation.setEndValue(self.hero_title.geometry())
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        self.animation.start()

    def initUI(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create navigation bar
        navbar = self.create_navbar()
        main_layout.addWidget(navbar)

        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: #1f2937;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #8b5cf6;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a78bfa;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Hero Section
        content_layout.addWidget(self.create_hero_section())
        
        # Features Section
        content_layout.addWidget(self.create_features_section())
        
        # Statistics Section
        content_layout.addWidget(self.create_statistics_section())
        
        # About Us Section
        content_layout.addWidget(self.create_about_section())
        
        # How It Works Section
        content_layout.addWidget(self.create_how_it_works_section())
        
        # Testimonials Section
        content_layout.addWidget(self.create_testimonials_section())
        
        # CTA Section
        content_layout.addWidget(self.create_cta_section())
        
        # Footer
        content_layout.addWidget(self.create_footer())

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)

    def create_navbar(self):
        """Create professional navigation bar"""
        navbar = QFrame()
        navbar.setFixedHeight(70)
        navbar.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.95);
                border-bottom: 1px solid #334155;
            }
        """)
        
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(40, 0, 40, 0)
        
        # Logo
        logo_label = QLabel("🎫 SmartTicketing")
        logo_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        logo_label.setStyleSheet("color: #8b5cf6;")
        navbar_layout.addWidget(logo_label)
        
        navbar_layout.addStretch()
        
        # Navigation links
        nav_links = ["Home", "Features", "About", "Contact"]
        for link in nav_links:
            btn = QPushButton(link)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: #cbd5e1;
                    font-size: 14px;
                    padding: 8px 16px;
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #a78bfa;
                }
            """)
            navbar_layout.addWidget(btn)
        
        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setFixedSize(100, 38)
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #5b21b6);
            }
        """)
        login_btn.clicked.connect(self.controller.show_login)
        navbar_layout.addWidget(login_btn)
        
        return navbar

    def create_hero_section(self):
        """Create hero section with animation"""
        hero_widget = QFrame()
        hero_widget.setStyleSheet("background: transparent;")
        hero_layout = QVBoxLayout(hero_widget)
        hero_layout.setContentsMargins(40, 60, 40, 80)
        hero_layout.setSpacing(20)
        
        # Main title
        self.hero_title = QLabel("Smart IT Service Management")
        self.hero_title.setFont(QFont("Segoe UI", 42, QFont.Bold))
        self.hero_title.setAlignment(Qt.AlignCenter)
        self.hero_title.setStyleSheet("color: #ffffff;")
        hero_layout.addWidget(self.hero_title)
        
        # Subtitle
        subtitle = QLabel("Streamline Your IT Support with Intelligent Ticketing System")
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8;")
        hero_layout.addWidget(subtitle)
        
        # Description
        description = QLabel(
            "Empower your team with our AI-powered ticketing solution. "
            "Track, manage, and resolve IT issues faster than ever before."
        )
        description.setFont(QFont("Segoe UI", 13))
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("color: #64748b; max-width: 700px;")
        hero_layout.addWidget(description, alignment=Qt.AlignCenter)
        
        hero_layout.addSpacing(20)
        
        # CTA Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.addStretch()
        
        get_started_btn = QPushButton("Get Started")
        get_started_btn.setFixedSize(180, 50)
        get_started_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                color: white;
                font-weight: bold;
                font-size: 15px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #5b21b6);
            }
        """)
        get_started_btn.clicked.connect(self.controller.show_login)
        
        learn_more_btn = QPushButton("Learn More")
        learn_more_btn.setFixedSize(180, 50)
        learn_more_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px solid #8b5cf6;
                color: #c4b5fd;
                font-weight: bold;
                font-size: 15px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.1);
                border-color: #a78bfa;
                color: #a78bfa;
            }
        """)
        
        buttons_layout.addWidget(get_started_btn)
        buttons_layout.addWidget(learn_more_btn)
        buttons_layout.addStretch()
        
        hero_layout.addLayout(buttons_layout)
        
        return hero_widget

    def create_features_section(self):
        """Create features section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("background: rgba(30, 41, 59, 0.5); margin: 20px; border-radius: 20px;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(50, 50, 50, 50)
        section_layout.setSpacing(30)
        
        # Section Title
        title = QLabel("Why Choose SmartTicketing?")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #f1f5f9;")
        section_layout.addWidget(title)
        
        subtitle = QLabel("Powerful features to streamline your IT support operations")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 20px;")
        section_layout.addWidget(subtitle)
        
        # Features Grid
        features_grid = QGridLayout()
        features_grid.setSpacing(25)
        
        features = [
            ("🎟️", "Smart Ticketing", "AI-powered ticket categorization and prioritization for faster resolution"),
            ("📊", "Real-time Analytics", "Comprehensive dashboards and reports for performance tracking"),
            ("👥", "Team Collaboration", "Seamless communication and assignment between team members"),
            ("🔒", "Enterprise Security", "Bank-grade encryption and secure data handling"),
            ("📱", "Multi-Platform", "Access from anywhere with responsive web interface"),
            ("🤖", "AI Chatbot", "24/7 intelligent assistant for instant issue resolution")
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            card = self.create_feature_card(icon, title, desc)
            row = i // 3
            col = i % 3
            features_grid.addWidget(card, row, col)
        
        section_layout.addLayout(features_grid)
        
        return section_widget

    def create_feature_card(self, icon, title, description):
        """Create individual feature card"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 16px;
                padding: 20px;
            }
            QFrame:hover {
                background-color: #334155;
                border: 1px solid #8b5cf6;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 36))
        icon_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e2e8f0;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #94a3b8;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        return card

    def create_statistics_section(self):
        """Create statistics counter section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:1 #0f172a);
                margin: 20px;
                border-radius: 25px;
            }
        """)
        section_layout = QHBoxLayout(section_widget)
        section_layout.setContentsMargins(60, 50, 60, 50)
        section_layout.setSpacing(40)
        
        stats = [
            ("10K+", "Tickets Resolved"),
            ("99.9%", "Satisfaction Rate"),
            ("< 2hr", "Avg Response Time"),
            ("24/7", "Support Available")
        ]
        
        for value, label in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setSpacing(8)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("color: #a78bfa;")
            
            label_label = QLabel(label)
            label_label.setFont(QFont("Segoe UI", 14))
            label_label.setAlignment(Qt.AlignCenter)
            label_label.setStyleSheet("color: #cbd5e1;")
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            
            section_layout.addWidget(stat_widget)
        
        return section_widget

    def create_about_section(self):
        """Create About Us section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("background: transparent; margin: 20px;")
        section_layout = QHBoxLayout(section_widget)
        section_layout.setContentsMargins(50, 60, 50, 60)
        section_layout.setSpacing(50)
        
        # Left side - Content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        about_title = QLabel("About Us")
        about_title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        about_title.setStyleSheet("color: #c4b5fd;")
        content_layout.addWidget(about_title)
        
        about_text = QLabel(
            "SmartTicketing is a next-generation IT service management platform "
            "designed to revolutionize how organizations handle technical support. "
            "Our mission is to empower IT teams with intelligent tools that automate "
            "routine tasks, prioritize critical issues, and deliver exceptional user experiences.\n\n"
            "With our AI-driven approach, we're helping businesses reduce resolution times "
            "by up to 60% while improving customer satisfaction scores significantly."
        )
        about_text.setFont(QFont("Segoe UI", 13))
        about_text.setWordWrap(True)
        about_text.setStyleSheet("color: #cbd5e1; line-height: 1.6;")
        content_layout.addWidget(about_text)
        
        content_layout.addSpacing(20)
        
        # Key points
        points = [
            "✓ Enterprise-grade security and compliance",
            "✓ Seamless integration with existing tools",
            "✓ Dedicated customer success team",
            "✓ Regular updates and feature enhancements"
        ]
        
        for point in points:
            point_label = QLabel(point)
            point_label.setFont(QFont("Segoe UI", 12))
            point_label.setStyleSheet("color: #94a3b8; padding: 5px;")
            content_layout.addWidget(point_label)
        
        # Right side - Stats or Image
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Placeholder for illustration
        illustration = QFrame()
        illustration.setFixedSize(350, 350)
        illustration.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e293b, stop:1 #334155);
                border-radius: 20px;
                border: 2px solid #8b5cf6;
            }
        """)
        
        ill_layout = QVBoxLayout(illustration)
        ill_label = QLabel("🎫")
        ill_label.setFont(QFont("Segoe UI", 80))
        ill_label.setAlignment(Qt.AlignCenter)
        ill_label.setStyleSheet("color: #a78bfa;")
        ill_layout.addWidget(ill_label)
        
        ill_text = QLabel("Smart Ticketing System")
        ill_text.setFont(QFont("Segoe UI", 16, QFont.Bold))
        ill_text.setAlignment(Qt.AlignCenter)
        ill_text.setStyleSheet("color: #e2e8f0;")
        ill_layout.addWidget(ill_text)
        
        stats_layout.addWidget(illustration)
        stats_layout.addStretch()
        
        section_layout.addWidget(content_widget, 2)
        section_layout.addWidget(stats_widget, 1)
        
        return section_widget

    def create_how_it_works_section(self):
        """Create How It Works section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("background: rgba(30, 41, 59, 0.5); margin: 20px; border-radius: 20px;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(50, 50, 50, 50)
        section_layout.setSpacing(30)
        
        title = QLabel("How It Works")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #f1f5f9;")
        section_layout.addWidget(title)
        
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(30)
        
        steps = [
            ("1", "Create Ticket", "Submit your issue with detailed description"),
            ("2", "Smart Assignment", "AI assigns to right team automatically"),
            ("3", "Track Progress", "Monitor status in real-time dashboard"),
            ("4", "Get Resolution", "Receive solution and provide feedback")
        ]
        
        for num, step, desc in steps:
            step_widget = QFrame()
            step_widget.setStyleSheet("""
                QFrame {
                    background-color: #1e293b;
                    border-radius: 16px;
                    padding: 20px;
                }
            """)
            
            step_layout = QVBoxLayout(step_widget)
            step_layout.setSpacing(12)
            
            num_label = QLabel(num)
            num_label.setFont(QFont("Segoe UI", 40, QFont.Bold))
            num_label.setAlignment(Qt.AlignCenter)
            num_label.setStyleSheet("color: #a78bfa;")
            
            step_label = QLabel(step)
            step_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
            step_label.setAlignment(Qt.AlignCenter)
            step_label.setStyleSheet("color: #e2e8f0;")
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Segoe UI", 12))
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #94a3b8;")
            
            step_layout.addWidget(num_label)
            step_layout.addWidget(step_label)
            step_layout.addWidget(desc_label)
            
            steps_layout.addWidget(step_widget)
        
        section_layout.addLayout(steps_layout)
        
        return section_widget

    def create_testimonials_section(self):
        """Create testimonials section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("background: transparent; margin: 20px;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(50, 60, 50, 60)
        section_layout.setSpacing(30)
        
        title = QLabel("What Our Clients Say")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #f1f5f9;")
        section_layout.addWidget(title)
        
        testimonials_layout = QHBoxLayout()
        testimonials_layout.setSpacing(25)
        
        testimonials = [
            ("⭐" * 5, "This platform has transformed our IT support operations. Resolution times have decreased by 60%!", "Sarah Johnson", "IT Director, TechCorp"),
            ("⭐" * 5, "The AI chatbot is incredible! It resolves most issues before they even reach our team.", "Michael Chen", "Support Manager, InnovateInc"),
            ("⭐" * 5, "Seamless integration and beautiful interface. Our team loves using this system daily.", "Emily Rodriguez", "CTO, StartupHub")
        ]
        
        for rating, comment, author, title_text in testimonials:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e293b;
                    border-radius: 20px;
                    padding: 25px;
                }
            """)
            
            card_layout = QVBoxLayout(card)
            
            rating_label = QLabel(rating)
            rating_label.setFont(QFont("Segoe UI", 14))
            
            comment_label = QLabel(f'"{comment}"')
            comment_label.setFont(QFont("Segoe UI", 12))
            comment_label.setWordWrap(True)
            comment_label.setStyleSheet("color: #cbd5e1; font-style: italic;")
            
            author_label = QLabel(f"- {author}")
            author_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            author_label.setStyleSheet("color: #a78bfa; margin-top: 10px;")
            
            title_label = QLabel(title_text)
            title_label.setFont(QFont("Segoe UI", 11))
            title_label.setStyleSheet("color: #94a3b8;")
            
            card_layout.addWidget(rating_label)
            card_layout.addWidget(comment_label)
            card_layout.addWidget(author_label)
            card_layout.addWidget(title_label)
            
            testimonials_layout.addWidget(card)
        
        section_layout.addLayout(testimonials_layout)
        
        return section_widget

    def create_cta_section(self):
        """Create Call to Action section"""
        section_widget = QFrame()
        section_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:1 #6d28d9);
                margin: 30px;
                border-radius: 25px;
            }
        """)
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(60, 50, 60, 50)
        section_layout.setSpacing(20)
        
        title = QLabel("Ready to Transform Your IT Support?")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        section_layout.addWidget(title)
        
        subtitle = QLabel("Join thousands of satisfied customers using SmartTicketing")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #e0e7ff;")
        section_layout.addWidget(subtitle)
        
        section_layout.addSpacing(20)
        
        cta_btn = QPushButton("Get Started Now →")
        cta_btn.setFixedSize(220, 55)
        cta_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #6d28d9;
                font-weight: bold;
                font-size: 15px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #f3e8ff;
                transform: scale(1.05);
            }
        """)
        cta_btn.clicked.connect(self.controller.show_login)
        
        section_layout.addWidget(cta_btn, alignment=Qt.AlignCenter)
        
        return section_widget

    def create_footer(self):
        """Create footer section"""
        footer = QFrame()
        footer.setFixedHeight(200)
        footer.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-top: 1px solid #334155;
            }
        """)
        
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(50, 30, 50, 30)
        
        # Footer content
        content_layout = QHBoxLayout()
        
        # Company info
        company_widget = QWidget()
        company_layout = QVBoxLayout(company_widget)
        
        logo_label = QLabel("🎫 SmartTicketing")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #a78bfa;")
        company_layout.addWidget(logo_label)
        
        tagline = QLabel("Intelligent IT Service Management")
        tagline.setStyleSheet("color: #64748b; font-size: 12px;")
        company_layout.addWidget(tagline)
        
        copyright_label = QLabel("© 2024 SmartTicketing. All rights reserved.")
        copyright_label.setStyleSheet("color: #475569; font-size: 11px; margin-top: 10px;")
        company_layout.addWidget(copyright_label)
        
        content_layout.addWidget(company_widget)
        content_layout.addStretch()
        
        # Quick links
        links_widget = QWidget()
        links_layout = QVBoxLayout(links_widget)
        
        links_title = QLabel("Quick Links")
        links_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        links_title.setStyleSheet("color: #cbd5e1;")
        links_layout.addWidget(links_title)
        
        for link in ["About Us", "Features", "Pricing", "Contact"]:
            link_btn = QPushButton(link)
            link_btn.setFlat(True)
            link_btn.setStyleSheet("""
                QPushButton {
                    color: #64748b;
                    font-size: 11px;
                    text-align: left;
                    padding: 2px 0;
                }
                QPushButton:hover {
                    color: #a78bfa;
                }
            """)
            links_layout.addWidget(link_btn)
        
        content_layout.addWidget(links_widget)
        content_layout.addStretch()
        
        # Contact info
        contact_widget = QWidget()
        contact_layout = QVBoxLayout(contact_widget)
        
        contact_title = QLabel("Contact Us")
        contact_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        contact_title.setStyleSheet("color: #cbd5e1;")
        contact_layout.addWidget(contact_title)
        
        email_label = QLabel("📧 support@smartticketing.com")
        email_label.setStyleSheet("color: #64748b; font-size: 11px;")
        contact_layout.addWidget(email_label)
        
        phone_label = QLabel("📞 +1 (555) 123-4567")
        phone_label.setStyleSheet("color: #64748b; font-size: 11px;")
        contact_layout.addWidget(phone_label)
        
        content_layout.addWidget(contact_widget)
        
        footer_layout.addLayout(content_layout)
        
        return footer

    def open_login(self):
        """Open login page"""
        self.controller.show_login()

    def open_signup(self):
        """Open signup page"""
        self.controller.show_login()
        if hasattr(self.controller, 'login'):
            self.controller.login.show_register()


# Dialog classes remain the same
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About SmartTicketing")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
                border-radius: 15px;
            }
            QLabel {
                color: #e2e8f0;
            }
            QTextEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
                color: #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
            <h2 style='color: #a78bfa;'>Smart Ticketing System</h2>
            <p><b>Version:</b> 2.0.0</p>
            <p><b>Developer:</b> SmartTicketing Team</p>
            <p><b>Description:</b><br>
            Smart Ticketing System is an enterprise-grade IT service management platform 
            that leverages artificial intelligence to automate ticket routing, prioritize 
            critical issues, and provide instant resolutions through intelligent chatbots.</p>
            <p><b>Key Features:</b><br>
            • AI-Powered Ticket Classification<br>
            • Real-time Analytics Dashboard<br>
            • Multi-role Support (Admin, Employee, User)<br>
            • Knowledge Base Management<br>
            • Automated Escalation Rules<br>
            • SLA Management</p>
            <p><b>License:</b> Commercial License<br>
            <b>Website:</b> <a href='https://smartticketing.com' style='color: #a78bfa;'>www.smartticketing.com</a></p>
        """)
        layout.addWidget(about_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.setStyleSheet("QPushButton { background-color: #8b5cf6; color: white; border-radius: 6px; padding: 8px 20px; }")
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help & Support")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
                border-radius: 15px;
            }
            QLabel {
                color: #e2e8f0;
            }
            QTextEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
                color: #cbd5e1;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        faq = QTextEdit()
        faq.setReadOnly(True)
        faq.setHtml("""
            <h3 style='color: #a78bfa;'>📚 Frequently Asked Questions</h3>
            
            <p><b>1. How do I create a ticket?</b><br>
            Login to your account → Click 'Create Ticket' → Fill in the details → Submit</p>
            
            <p><b>2. How can I track my ticket status?</b><br>
            Go to 'My Tickets' section in your dashboard to view real-time status updates.</p>
            
            <p><b>3. What are the different priority levels?</b><br>
            • P1 - Critical (System down)<br>
            • P2 - High (Major functionality affected)<br>
            • P3 - Medium (Minor issues)<br>
            • P4 - Low (General inquiries)</p>
            
            <p><b>4. How do I reset my password?</b><br>
            Click 'Forgot Password' on login page → Enter your email → Follow instructions</p>
            
            <p><b>5. What is the SLA response time?</b><br>
            • P1: 15 minutes<br>
            • P2: 1 hour<br>
            • P3: 4 hours<br>
            • P4: 24 hours</p>
            
            <h4 style='color: #a78bfa; margin-top: 20px;'>📞 Need More Help?</h4>
            <p>Contact our support team:<br>
            Email: support@smartticketing.com<br>
            Phone: +1 (555) 123-4567<br>
            Hours: 24/7</p>
        """)
        layout.addWidget(faq)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.setStyleSheet("QPushButton { background-color: #8b5cf6; color: white; border-radius: 6px; padding: 8px 20px; }")
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ContactDialog(QDialog):
    def __init__(self, parent=None, support_email="support@smartticketing.com"):
        super().__init__(parent)
        self.support_email = support_email
        self.setWindowTitle("Contact Support")
        self.setMinimumSize(500, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
                border-radius: 15px;
            }
            QLabel {
                color: #e2e8f0;
            }
            QLineEdit, QTextEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: #cbd5e1;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Contact Support Team")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #a78bfa; margin-bottom: 10px;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com")
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Brief description of your issue")
        
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Please provide detailed information about your query...")
        self.msg_input.setFixedHeight(150)
        
        form.addRow("Name:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Subject:", self.subject_input)
        form.addRow("Message:", self.msg_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        buttons.accepted.connect(self.on_send)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_send(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        subject = self.subject_input.text().strip()
        msg = self.msg_input.toPlainText().strip()
        
        if not (name and email and msg):
            from PyQt5 import QtWidgets
            QtWidgets.QMessageBox.warning(self, "Incomplete", "Please fill all required fields.")
            return
        
        mail_body = f"Name: {name}%0AEmail: {email}%0ASubject: {subject}%0A%0AMessage:%0A{msg}"
        mailto = f"mailto:{self.support_email}?subject={webbrowser.quote(subject)}&body={webbrowser.quote(mail_body)}"
        webbrowser.open(mailto)
        
        from PyQt5 import QtWidgets
        QtWidgets.QMessageBox.information(self, "Email Opened", "Your email client will open. Please send the email to complete your request.")
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    class TempController:
        def show_login(self):
            print("Go login")
        def show_register(self):
            print("Go register")
    
    window = TicketingHome(TempController())
    window.show()
    sys.exit(app.exec_())