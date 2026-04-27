"""
Database Update Script for Employee Dashboard
Run this script once to set up all required tables and data
"""

import mysql.connector
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kai*123',  # Update with your MySQL password
    'database': 'kaiticket'
}

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_employee_details_table():
    """Create employee_details table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = """
        CREATE TABLE IF NOT EXISTS employee_details (
            employee_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            department VARCHAR(100),
            role VARCHAR(100),
            join_date DATE,
            status VARCHAR(50) DEFAULT 'Active',
            avatar VARCHAR(255),
            last_login DATETIME,
            INDEX idx_email (email),
            INDEX idx_username (username)
        )
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print("✅ employee_details table created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating employee_details table: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_ticket_assignments_table():
    """Create ticket_assignments table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = """
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
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print("✅ ticket_assignments table created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating ticket_assignments table: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_employee_tasks_table():
    """Create employee_tasks table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = """
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
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print("✅ employee_tasks table created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating employee_tasks table: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_knowledge_base_table():
    """Create knowledge_base table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = """
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
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print("✅ knowledge_base table created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating knowledge_base table: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_employee_activity_log_table():
    """Create employee_activity_log table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = """
        CREATE TABLE IF NOT EXISTS employee_activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(50),
            activity_type VARCHAR(100),
            activity_description TEXT,
            activity_date DATETIME,
            INDEX idx_employee_date (employee_id, activity_date)
        )
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print("✅ employee_activity_log table created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating employee_activity_log table: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def insert_sample_knowledge_base():
    """Insert sample knowledge base articles"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_articles = [
            ("How to reset user password", "Security", 
             """Step-by-step guide to reset user passwords:

1. Login to the admin portal using your credentials
2. Navigate to Users → Manage Users section
3. Search for the user account using username or email
4. Click on the user profile and select 'Reset Password'
5. Enter a new temporary password (follow password policy)
6. Confirm the new password
7. Click 'Save Changes'
8. Notify the user of their new password via email

Important: Always instruct users to change their temporary password on first login.""", 
             datetime.now()),
            
            ("VPN connection troubleshooting", "Network",
             """Common VPN issues and solutions:

Issue 1: VPN connection timeout
Solution: 
- Restart the VPN client application
- Check your internet connection
- Verify your VPN credentials
- Clear DNS cache using 'ipconfig /flushdns'

Issue 2: Authentication failed
Solution:
- Ensure you're using the correct username/password
- Check if your account is active in the system
- Contact IT support if issue persists

Issue 3: Slow VPN connection
Solution:
- Connect to a closer VPN server
- Check your local internet speed
- Close bandwidth-heavy applications
- Update VPN client to latest version""",
             datetime.now()),
            
            ("Email configuration for Outlook", "Email",
             """Outlook setup instructions for company email:

Step 1: Open Microsoft Outlook
Step 2: Go to File → Add Account
Step 3: Enter your email address
Step 4: Select 'Manual setup or additional server types'
Step 5: Choose 'POP or IMAP'
Step 6: Enter the following settings:
   - Incoming mail server: mail.company.com (IMAP)
   - Outgoing mail server: mail.company.com (SMTP)
   - Port (IMAP): 993 (SSL)
   - Port (SMTP): 465 (SSL/TLS)

Step 7: Enter your full email address and password
Step 8: Click 'Test Account Settings' to verify
Step 9: Click 'Next' and then 'Finish'

Troubleshooting:
- Ensure you have a stable internet connection
- Check if your account has IMAP enabled
- Contact IT if authentication fails""",
             datetime.now()),
            
            ("Software installation errors", "Software",
             """Common software installation fixes:

Error 1: 'Access Denied' or 'Permission Required'
Solution:
- Right-click installer and select 'Run as Administrator'
- Temporarily disable User Account Control (UAC)
- Ensure you have local admin rights

Error 2: 'Another installation is in progress'
Solution:
- Restart your computer
- Check Task Manager for running installers
- Delete temp files: %temp% folder

Error 3: 'Insufficient disk space'
Solution:
- Run Disk Cleanup utility
- Uninstall unnecessary programs
- Move files to external storage
- Clear browser cache and downloads

Error 4: 'Missing DLL files'
Solution:
- Run System File Checker: sfc /scannow
- Reinstall Microsoft Visual C++ Redistributables
- Update Windows to latest version

Always restart your computer after installation for changes to take effect.""",
             datetime.now()),
            
            ("Network printer setup", "Hardware",
             """Network printer setup guide:

For Windows:
1. Connect printer to the network (Ethernet or Wi-Fi)
2. Note the printer's IP address (print configuration page)
3. Go to Settings → Devices → Printers & Scanners
4. Click 'Add a printer or scanner'
5. Select 'The printer that I want isn't listed'
6. Choose 'Add a printer using TCP/IP address'
7. Enter the printer's IP address
8. Install printer driver when prompted
9. Print a test page to verify

For Mac:
1. Go to System Preferences → Printers & Scanners
2. Click '+' to add a printer
3. Select 'IP' tab
4. Enter printer IP address
5. Select protocol (usually HP Jetdirect or AirPrint)
6. Choose printer driver
7. Click 'Add'

Troubleshooting:
- Ensure printer is powered on and connected
- Check network connectivity (ping printer IP)
- Restart print spooler service
- Update printer drivers from manufacturer's website""",
             datetime.now()),
        ]
        
        insert_query = """
            INSERT INTO knowledge_base (title, category, content, created_at, views, helpful_count, not_helpful_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for article in sample_articles:
            cursor.execute(insert_query, (article[0], article[1], article[2], article[3], 0, 0, 0))
        
        conn.commit()
        print("✅ Sample knowledge base articles inserted")
    else:
        print("ℹ️ Knowledge base already has data, skipping sample insertion")
    
    cursor.close()
    conn.close()
    return True

def add_foreign_key_constraints():
    """Add foreign key constraints if they don't exist"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if foreign key exists for ticket_assignments
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'kaiticket' 
            AND TABLE_NAME = 'ticket_assignments' 
            AND CONSTRAINT_NAME = 'fk_ticket_assignments_employee'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE ticket_assignments 
                ADD CONSTRAINT fk_ticket_assignments_employee 
                FOREIGN KEY (employee_id) REFERENCES employee_details(employee_id) ON DELETE CASCADE
            """)
            print("✅ Foreign key constraint added for ticket_assignments")
        
        # Check for employee_tasks foreign key
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'kaiticket' 
            AND TABLE_NAME = 'employee_tasks' 
            AND CONSTRAINT_NAME = 'fk_employee_tasks_employee'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE employee_tasks 
                ADD CONSTRAINT fk_employee_tasks_employee 
                FOREIGN KEY (employee_id) REFERENCES employee_details(employee_id) ON DELETE CASCADE
            """)
            print("✅ Foreign key constraint added for employee_tasks")
        
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Note: Foreign key constraint may already exist or can't be added: {err}")
    
    cursor.close()
    conn.close()
    return True

def update_tickets_table():
    """Update tickets table to ensure it has required columns"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check if assigned_to column exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'kaiticket' 
        AND TABLE_NAME = 'tickets' 
        AND COLUMN_NAME = 'assigned_to'
    """)
    
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE tickets ADD COLUMN assigned_to VARCHAR(255) DEFAULT NULL")
        print("✅ Added assigned_to column to tickets table")
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def insert_sample_employee_data():
    """Insert sample employee data if not exists"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check if employee exists in employees table
    cursor.execute("SELECT COUNT(*) FROM employees WHERE username = 'kai'")
    emp_count = cursor.fetchone()[0]
    
    if emp_count == 0:
        # Insert into employees table
        cursor.execute("""
            INSERT INTO employees (username, password, first, last, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('kai', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 
              'Kartikey', 'Rai', 'kai@company.com', '9876543210'))
        print("✅ Sample employee inserted into employees table")
    
    # Check if employee exists in employee_details table
    cursor.execute("SELECT COUNT(*) FROM employee_details WHERE username = 'kai'")
    details_count = cursor.fetchone()[0]
    
    if details_count == 0:
        cursor.execute("""
            INSERT INTO employee_details (employee_id, username, name, email, phone, department, role, join_date, status, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('EMP001', 'kai', 'Kartikey Rai', 'kai@company.com', '9876543210', 
              'IT Support', 'Support Agent', '2024-01-15', 'Active', datetime.now()))
        print("✅ Sample employee inserted into employee_details table")
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def main():
    """Main function to run all database updates"""
    print("=" * 60)
    print("Employee Dashboard Database Update Script")
    print("=" * 60)
    print()
    
    # Create all tables
    print("Creating tables...")
    print("-" * 40)
    create_employee_details_table()
    create_ticket_assignments_table()
    create_employee_tasks_table()
    create_knowledge_base_table()
    create_employee_activity_log_table()
    print()
    
    # Update existing tables
    print("Updating existing tables...")
    print("-" * 40)
    update_tickets_table()
    print()
    
    # Insert sample data
    print("Inserting sample data...")
    print("-" * 40)
    insert_sample_knowledge_base()
    insert_sample_employee_data()
    print()
    
    # Add foreign key constraints
    print("Adding foreign key constraints...")
    print("-" * 40)
    add_foreign_key_constraints()
    print()
    
    print("=" * 60)
    print("✅ Database update completed successfully!")
    print("=" * 60)
    
    # Test connection
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n📊 Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
