"""
Employee Management Script
Run this script to add, update, or delete employees
"""

import mysql.connector
import hashlib
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Kai*123',  # Update with your MySQL password
    'database': 'kaiticket'
}

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def add_employee(employee_data):
    """
    Add a new employee to both employees and employee_details tables
    
    employee_data = {
        'username': 'emp_username',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@company.com',
        'phone': '1234567890',
        'department': 'IT Support',
        'role': 'Support Agent',
        'employee_id': 'EMP001',
        'join_date': '2024-01-15'
    }
    """
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Insert into employees table (for login)
        query1 = """
            INSERT INTO employees (username, password, first, last, email, phone, company)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            password = VALUES(password),
            first = VALUES(first),
            last = VALUES(last),
            email = VALUES(email),
            phone = VALUES(phone)
        """
        
        cursor.execute(query1, (
            employee_data['username'],
            hash_password(employee_data['password']),
            employee_data['first_name'],
            employee_data['last_name'],
            employee_data['email'],
            employee_data['phone'],
            employee_data.get('company', '')
        ))
        
        # Insert into employee_details table (for profile)
        query2 = """
            INSERT INTO employee_details 
            (employee_id, username, name, email, phone, department, role, join_date, status, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            email = VALUES(email),
            phone = VALUES(phone),
            department = VALUES(department),
            role = VALUES(role),
            status = VALUES(status)
        """
        
        full_name = f"{employee_data['first_name']} {employee_data['last_name']}"
        
        cursor.execute(query2, (
            employee_data['employee_id'],
            employee_data['username'],
            full_name,
            employee_data['email'],
            employee_data['phone'],
            employee_data['department'],
            employee_data['role'],
            employee_data['join_date'],
            'Active',
            datetime.now()
        ))
        
        conn.commit()
        print(f"✅ Employee {employee_data['username']} added successfully!")
        return True
        
    except mysql.connector.Error as err:
        print(f"Error adding employee: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def list_all_employees():
    """List all employees in the system"""
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT e.username, e.first, e.last, e.email, e.phone,
               ed.employee_id, ed.department, ed.role, ed.status
        FROM employees e
        LEFT JOIN employee_details ed ON e.username = ed.username
        WHERE e.username IN (SELECT username FROM employees)
    """
    
    cursor.execute(query)
    employees = cursor.fetchall()
    
    print("\n" + "="*80)
    print("EMPLOYEES LIST")
    print("="*80)
    
    for emp in employees:
        print(f"\nUsername: {emp['username']}")
        print(f"Name: {emp['first']} {emp['last']}")
        print(f"Email: {emp['email']}")
        print(f"Phone: {emp['phone']}")
        print(f"Department: {emp.get('department', 'N/A')}")
        print(f"Role: {emp.get('role', 'N/A')}")
        print(f"Status: {emp.get('status', 'N/A')}")
        print("-"*40)
    
    cursor.close()
    conn.close()
    
    return employees

def update_employee_status(username, status):
    """Update employee status (Active/Inactive)"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    query = "UPDATE employee_details SET status = %s WHERE username = %s"
    cursor.execute(query, (status, username))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    print(f"✅ Employee {username} status updated to {status}")
    return True

def delete_employee(username):
    """Delete an employee from the system"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Delete from employee_details first (due to foreign key)
        cursor.execute("DELETE FROM employee_details WHERE username = %s", (username,))
        cursor.execute("DELETE FROM employees WHERE username = %s", (username,))
        conn.commit()
        
        print(f"✅ Employee {username} deleted successfully!")
        return True
    except mysql.connector.Error as err:
        print(f"Error deleting employee: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Sample employees to add
SAMPLE_EMPLOYEES = [
    {
        'username': 'emp1',
        'password': 'emp123',
        'first_name': 'Kartikey',
        'last_name': 'Rai',
        'email': 'kai@company.com',
        'phone': '9876543210',
        'department': 'IT Support',
        'role': 'Senior Support Agent',
        'employee_id': 'EMP001',
        'join_date': '2024-01-15'
    },
    {
        'username': 'emp2',
        'password': 'emp456',
        'first_name': 'Ankur',
        'last_name': 'Rai',
        'email': 'ankur@company.com',
        'phone': '9876543211',
        'department': 'IT Support',
        'role': 'Support Agent',
        'employee_id': 'EMP002',
        'join_date': '2024-02-01'
    },
    {
        'username': 'emp3',
        'password': 'emp789',
        'first_name': 'Divye',
        'last_name': 'Chaudhary',
        'email': 'divye@company.com',
        'phone': '9876543212',
        'department': 'Network Team',
        'role': 'Network Engineer',
        'employee_id': 'EMP003',
        'join_date': '2024-01-20'
    },
    {
        'username': 'emp4',
        'password': 'empabc',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'email': 'priya@company.com',
        'phone': '9876543213',
        'department': 'Application Support',
        'role': 'Application Analyst',
        'employee_id': 'EMP004',
        'join_date': '2024-03-10'
    },
    {
        'username': 'emp5',
        'password': 'empxyz',
        'first_name': 'Rahul',
        'last_name': 'Verma',
        'email': 'rahul@company.com',
        'phone': '9876543214',
        'department': 'Security Team',
        'role': 'Security Analyst',
        'employee_id': 'EMP005',
        'join_date': '2024-02-15'
    }
]

def add_sample_employees():
    """Add sample employees to the system"""
    print("\n" + "="*80)
    print("ADDING SAMPLE EMPLOYEES")
    print("="*80)
    
    for emp in SAMPLE_EMPLOYEES:
        add_employee(emp)
        print()

def main():
    """Main menu for employee management"""
    while True:
        print("\n" + "="*60)
        print("EMPLOYEE MANAGEMENT SYSTEM")
        print("="*60)
        print("1. List all employees")
        print("2. Add new employee")
        print("3. Update employee status")
        print("4. Delete employee")
        print("5. Add sample employees")
        print("6. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            list_all_employees()
            
        elif choice == '2':
            print("\n--- Add New Employee ---")
            emp_data = {}
            emp_data['username'] = input("Username: ")
            emp_data['password'] = input("Password: ")
            emp_data['first_name'] = input("First Name: ")
            emp_data['last_name'] = input("Last Name: ")
            emp_data['email'] = input("Email: ")
            emp_data['phone'] = input("Phone: ")
            emp_data['department'] = input("Department: ")
            emp_data['role'] = input("Role: ")
            emp_data['employee_id'] = input("Employee ID: ")
            emp_data['join_date'] = input("Join Date (YYYY-MM-DD): ")
            add_employee(emp_data)
            
        elif choice == '3':
            username = input("Enter username: ")
            status = input("Enter status (Active/Inactive): ")
            update_employee_status(username, status)
            
        elif choice == '4':
            username = input("Enter username to delete: ")
            confirm = input(f"Are you sure you want to delete {username}? (y/n): ")
            if confirm.lower() == 'y':
                delete_employee(username)
                
        elif choice == '5':
            add_sample_employees()
            
        elif choice == '6':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
