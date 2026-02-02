from flask import Flask, render_template, request, redirect, url_for, session
import json
from google import genai
from dotenv import load_dotenv
import os
import re

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("DEBUG → API KEY LOADED =", api_key)

client = genai.Client(api_key=api_key)

app = Flask(__name__)

# 🔐 Secret key for session memory (random)
app.secret_key = "campusassist_ai_secret_928374"

DATA_FILE = "students.json"


# ---------- Helpers ----------

def load_students():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_students(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)


# ---------- Routes ----------

@app.route("/")
def home():
    return render_template("index.html")


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

        student = {
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
        }

        students.append(student)
        save_students(students)

        return redirect(url_for("view_report", student_id=student_id))

    return render_template("add_students.html")


@app.route("/students")
def students_list():
    students = load_students()

    search_name = request.args.get("search")
    selected_class = request.args.get("class")

    classes = sorted(set(s["class"] for s in students))

    if search_name:
        search_name = search_name.lower()
        students = [s for s in students if search_name in s["name"].lower()]
        selected_class = None

    elif selected_class:
        students = [s for s in students if s["class"] == selected_class]

    return render_template(
        "students.html",
        students=students,
        classes=classes,
        selected_class=selected_class,
        search_name=search_name
    )


@app.route("/report/<int:student_id>")
def view_report(student_id):
    students = load_students()
    student = next((s for s in students if s["id"] == student_id), None)
    return render_template("report.html", student=student)


# ---------- AI Chat (WITH MEMORY) ----------

@app.route("/ai", methods=["GET", "POST"])
def ai_chat():
    user_message = None
    ai_response = None

    # 🧠 Initialize memory
    if "chat_history" not in session:
        session["chat_history"] = []

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

        # Add USER message to memory
        session["chat_history"].append({
            "role": "user",
            "content": user_message
        })
        session.modified = True  # 🔒 REQUIRED

        # Build Gemini conversation
        contents = [
            {
                "role": "user",
                "parts": [{"text": system_prompt}]
            }
        ]

        for msg in session["chat_history"]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )

            raw = response.candidates[0].content.parts[0].text.strip()

            # ---------- POST-PROCESSING ----------
            raw = raw.replace("•", "-").replace("*", "-")
            raw = raw.replace(". -", ".\n-")

            points = re.split(r"\n-\s*", raw)

            clean_lines = []
            for p in points:
                p = p.strip()
                if p:
                    clean_lines.append(f"- {p.rstrip('.')}")

            ai_response = "\n".join(clean_lines[:8])

            # Add AI response to memory (IMPORTANT: role = model)
            session["chat_history"].append({
                "role": "model",
                "content": ai_response
            })
            session.modified = True

        except Exception as e:
            print("AI ERROR:", e)
            ai_response = "- AI service is temporarily unavailable\n- Please try again later"

    return render_template(
        "ai_chat.html",
        user_message=user_message,
        ai_response=ai_response
    )

# ---------- Run ----------

if __name__ == "__main__":
    app.run(debug=True)
