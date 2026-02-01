# 🎓 Student Progress Tracker (Teacher Tool)

A web-based Student Progress Tracking System built using Flask, designed specifically for school teachers to manage student records, generate report cards, and quickly search or filter students.

This project focuses on clarity, simplicity, and real classroom usability.

---

## ✨ Key Features

### 📋 Student Management
- Add student details (Name, Roll Number, Class)
- Store academic records permanently using JSON
- View all students in a clean list

### 📄 Report Card Generation
- Automatically generate **school-style report cards**
- Subject-wise marks and grades
- Total marks, percentage, and overall grade
- Teacher remarks section
- Printable, professional layout

### 👩‍🏫 Teacher-Friendly Navigation
- **View Report Card** for any student anytime
- Persistent data (records remain after restart)

### 🏫 Class-wise Filtering
- Filter students by class (e.g., 8A, 9B)
- Helps teachers managing multiple sections

### 🔍 Search by Student Name
- Search students **only by name**
- Simple and intuitive (no need to remember class or roll)
- Designed to reduce teacher cognitive load

---

## 🧠 Design Philosophy

- Built to **mirror real school workflows**
- No unnecessary complexity
- Backend-driven architecture (Flask + Jinja)
- Minimal JavaScript (server-side logic preferred)
- Focused on **teachability and maintainability**

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS (Responsive, clean UI)
- **Backend:** Python, Flask
- **Templating:** Jinja2
- **Data Storage:** JSON file (`students.json`)
- **Environment:** Python Virtual Environment

---

## 📂 Project Structure
```bash
student_progress/
│
├── app.py # Flask backend
├── students.json # Persistent student data
│
├── templates/
│ ├── index.html # Dashboard
│ ├── add_students.html # Add student form
│ ├── students.html # All students list (search & filter)
│ └── report.html # Detailed report card
│
├── static/
│ └── styles/
│ └── style.css # Application styling
│
└── README.md
```

## ▶️ How to Run the Project

### 1️⃣ Create Virtual Environment
python -m venv venv
Activate it:

Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate

2️⃣ Install Dependencies
- pip install flask

3️⃣ Run the Application
- python app.py

Open in browser:
http://127.0.0.1:5000/


🧪 How It Works (Flow)
Teacher adds student details

Backend calculates marks, grade, and remarks

Data is stored in students.json

Teacher can:

- View all students

- Filter by class

- Search by name

- Open any student’s report card

🎯 Use Cases
- School teachers

- Academic record demonstration

- CS teaching aid (Flask, CRUD, file handling)

- Beginner-friendly school management system

🚀 Future Enhancements
- Edit / Delete student records

- Attendance management

- PDF export of report cards

- Teacher login system

- Class-wise analytics dashboard
