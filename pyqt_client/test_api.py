import api

# Step 1: Log in
username = "Kai"  # replace with your username
password = "Kai12345"  # replace with your password

login_resp = api.login(username, password)
if login_resp.status_code != 200:
    print("Login failed:", login_resp.text)
    exit()

print("Login successful!")

# Step 2: Get incidents
resp = api.get_incidents()
print("Status code:", resp.status_code)
print(resp.json())
