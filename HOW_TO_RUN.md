# 🚀 How to Run - Healthcare Predictive Analytics System (MySQL)

Follow these steps to set up and run the system on your local machine using **MySQL**.

## 📋 Prerequisites
1. **MySQL Server** installed and running (via SQL Workbench).
2. **Python 3.8+** installed.
3. **Virtual Environment** (already exists as `.venv`).

---

## 🛠️ Step-by-Step Setup

### 1️⃣ Configure Environment
Open the [`.env`](file:///Users/rajdevverma/Desktop/Healthcare_Predictive_Analytics/.env) file and update your MySQL password:
```env
MYSQL_PASSWORD=rajdev58@@
```

### 2️⃣ Initialize Database
Run the initialization script to create the `healthcare_db` and tables:
```bash
python3 database/init_db.py
```
*This will also seed default accounts: `admin@healthcare.com` and `doctor@healthcare.com`.*

### 3️⃣ Start the Application
Run the Flask server:
```bash
python3 backend/app.py
```

### 4️⃣ Access the App
Open your browser and go to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## � Default Login Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Doctor** | `doctor@healthcare.com` | `doctor123` |
| **Admin** | `admin@healthcare.com` | `admin123` |

---

## 🧪 Verification
To ensure everything is connected correctly (MySQL + ML Models), run:
```bash
python3 tests/verify_system.py
```

## 📂 Project Structure
- `backend/app.py`: Main entry point.
- `database/healthcare.sql`: MySQL Table definitions.
- `backend/ml_models/`: Trained Random Forest models.


cd ~/Desktop/Healthcare_Predictive_Analytics
source venv/bin/activate
python backend/app.py
