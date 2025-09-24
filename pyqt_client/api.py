import requests

API_BASE = "http://127.0.0.1:8000/api"
session = requests.Session()  # Keeps cookies after login

# ---------------- Login ----------------
def login(username, password):
    resp = session.post(f"{API_BASE}/login/", json={"username": username, "password": password})
    return resp

# ---------------- Logout ----------------
def logout():
    resp = session.post(f"{API_BASE}/logout/")
    return resp

# ---------------- Submit Incident ----------------
def submit_incident(title, description):
    resp = session.post(f"{API_BASE}/incidents/", json={"title": title, "description": description})
    return resp

# ---------------- Get My Incidents ----------------
def get_incidents():
    resp = session.get(f"{API_BASE}/incidents/")
    return resp
