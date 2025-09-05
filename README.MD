# ITIL Ticketing System

A lightweight **desktop-based ticketing system** following ITIL practices.  
Built with **Django (backend)** and **PyQt6 (GUI)**, packaged into an `.exe` for easy use.

---

## Features (Planned)
- User login & authentication  
- Ticket creation and tracking  
- Multi-user support with PostgreSQL  
- Desktop `.exe` build using PyInstaller  

---

## Tech Stack
- Python 3.12  
- Django 4.2 LTS  
- PyQt6  
- PostgreSQL  
- PyInstaller  

---

## Setup
```bash
# Clone repo
git clone https://github.com/<your-username>/itil_ts.git
cd itil_ts

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install --no-index --find-links=Packages -r requirements.txt

# Run server
python manage.py runserver
