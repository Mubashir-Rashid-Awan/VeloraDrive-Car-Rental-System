# 🚗 VeloraDrive – Car Rental System

VeloraDrive is a full-stack web-based car rental application built using Flask. It allows users to browse available cars, view details, and make bookings online. The system includes secure authentication, a user dashboard, and an admin panel for managing vehicles, bookings, and users.

---

## 🛠️ Technologies Used

### 🔹 Backend
- Python
- Flask (Web Framework)

### 🔹 Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### 🔹 Database
- Microsoft SQL Server
- SQL (Joins, Constraints, Queries)

### 🔹 Other Tools
- Jinja2 (Template Engine)
- Werkzeug Security (Password Hashing)
- Git & GitHub (Version Control)

---

## ✨ Features

- ✅ User Signup & Login (Secure Authentication)
- ✅ Browse and Search Cars
- ✅ View Detailed Car Information
- ✅ Book Cars with Pickup & Return Dates
- ✅ Payment Module (Simulated)
- ✅ User Dashboard (Bookings & Profile)
- ✅ Admin Dashboard (Manage Cars, Users, Bookings)
- ✅ Reviews and Ratings System
- ✅ Invoice Generation
- ✅ Responsive Design for All Devices

---

## ⚙️ Project Setup

### 🔹 1. Clone the Repository

git clone https://github.com/your-username/veloradrive.git
cd veloradrive


### 🔹 2. Install Dependencies

pip install -r requirements.txt


### 🔹 3. Setup Database

Open SQL Server Management Studio (SSMS)
Run the file:
database/schema.sql

### 🔹 4. Configure Database (if needed)

Update values in config.py
DB_SERVER = '.\\SQLEXPRESS'
DB_NAME   = 'RentACarDB'

### 🔹 5. Run the Application

python app.py

### 6. Open in Browser

http://127.0.0.1:5000



