from flask import Flask, render_template, request, redirect, url_for, session
import json
from google import genai
from dotenv import load_dotenv
import os
import re
from datetime import date


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

app = Flask(__name__)
app.secret_key = "campusassist_secret_482739"  # random secret key

DATA_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"

def load_students():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_students(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)

def load_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        return {}
    with open(ATTENDANCE_FILE, "r") as f:
        return json.load(f)

def save_attendance(data):
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return render_template("index.html", show_ai_button=True)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        students = load_students()
        student_id = len(students) + 1

        maths = int(request.form["maths"])
        science = int(request.form["science"])
        computer = int(request.form["computer"])

        total = maths + science + computer
        percent = (total / 300) * 100

        if percent >= 80:
            grade, remark = "A", "Excellent"
        elif percent >= 60:
            grade, remark = "B", "Good"
        else:
            grade, remark = "C", "Needs Improvement"

        students.append({
            "id": student_id,
            "name": request.form["name"],
            "roll": request.form["roll"],
            "class": request.form["class"],
            "maths": maths,
            "science": science,
            "computer": computer,
            "total": total,
            "percentage": round(percent, 2),
            "grade": grade,
            "remark": remark
        })

        save_students(students)
        return redirect(url_for("view_report", student_id=student_id))

    return render_template("add_students.html", show_ai_button=True)


@app.route("/students")
def students_list():
    students = load_students()
    search_name = request.args.get("search")
    selected_class = request.args.get("class")

    classes = sorted(set(s["class"] for s in students))

    if search_name:
        students = [s for s in students if search_name.lower() in s["name"].lower()]
        selected_class = None
    elif selected_class:
        students = [s for s in students if s["class"] == selected_class]

    return render_template(
        "students.html",
        students=students,
        classes=classes,
        selected_class=selected_class,
        search_name=search_name,
        show_ai_button=True
    )


@app.route("/report/<int:student_id>")
def view_report(student_id):
    students = load_students()
    student = next((s for s in students if s["id"] == student_id), None)
    return render_template("report.html", student=student, show_ai_button=True)

@app.route("/ai", methods=["GET", "POST"])
def ai_chat():
    if "chat_history" not in session:
        session["chat_history"] = []

    user_message = None
    ai_response = None

    if request.method == "POST":
        user_message = request.form["message"]

        system_prompt = """
You are CampusAssist AI, a helpful assistant for school teachers.

STYLE RULES:
- Use a warm, encouraging tone
- Start with ONE short friendly introduction sentence (max 15 words)
- Then provide bullet points
- Each bullet point must be on a new line
- Use '-' as bullet symbol
- End with ONE short encouraging closing sentence (max 12 words)
- Do NOT write long paragraphs
"""

        session["chat_history"].append({
            "role": "user",
            "content": user_message
        })

        contents = [{"role": "user", "parts": [{"text": system_prompt}]}]

        for msg in session["chat_history"]:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}]
            })

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )

            raw = response.candidates[0].content.parts[0].text
            raw = raw.replace("•", "-").replace("*", "-")
            raw = raw.replace(". -", ".\n-")

            points = re.split(r"\n-\s*", raw)
            clean = [f"- {p.strip().rstrip('.')}" for p in points if p.strip()]

            ai_response = "\n".join(clean[:8])

            session["chat_history"].append({
                "role": "model",
                "content": ai_response
            })

            session.modified = True

        except Exception as e:
            print("AI ERROR:", e)
            ai_response = "- AI service unavailable\n- Please try again later"

    return render_template(
        "ai_chat.html",
        user_message=user_message,
        ai_response=ai_response,
        show_ai_button=False
    )


@app.route("/attendance/mark", methods=["GET", "POST"])
def mark_attendance():
    students = load_students()
    attendance = load_attendance()
    today = date.today().isoformat()

    selected_class = request.args.get("class")
    classes = sorted(set(s["class"] for s in students))

    if selected_class:
        students = [s for s in students if s["class"] == selected_class]

    if request.method == "POST":
        attendance.setdefault(today, {})
        for s in students:
            status = request.form.get(str(s["id"]))
            if status:
                attendance[today][str(s["id"])] = status
        save_attendance(attendance)
        return redirect(url_for("home"))

    return render_template(
        "mark_attendance.html",
        students=students,
        classes=classes,
        selected_class=selected_class,
        today=today,
        show_ai_button=True
    )

@app.route("/attendance/student/<int:student_id>")
def student_attendance(student_id):
    students = load_students()
    attendance = load_attendance()

    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return "Student not found"

    total = present = 0
    history = []

    for d, records in attendance.items():
        if str(student_id) in records:
            total += 1
            if records[str(student_id)] == "Present":
                present += 1
            history.append({"date": d, "status": records[str(student_id)]})

    percent = round((present / total) * 100, 2) if total else 0

    return render_template(
        "student_attendance.html",
        student=student,
        total_days=total,
        present_days=present,
        absent_days=total - present,
        percentage=percent,
        history=history,
        show_ai_button=True
    )

if __name__ == "__main__":
    app.run(debug=True)
