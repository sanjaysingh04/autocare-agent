from flask import Flask, request, render_template, redirect
import sqlite3
from database import init_db

# ================= SCHEDULER =================
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_followup(phone, hours):
    run_time = datetime.now() + timedelta(hours=hours)
    scheduler.add_job(send_checkin, 'date', run_date=run_time, args=[phone])

# ================= TWILIO =================
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from protocols import PROTOCOL_MAP

ACCOUNT_SID = "ACCOUNT_SID_PLACEHOLDER"
AUTH_TOKEN = "AUTH_TOKEN_PLACEHOLDER"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ================= FLASK INIT =================
app = Flask(__name__)
init_db()

# =========================================================
# 🏆 ROOT → LOGIN
# =========================================================
@app.route("/")
def root():
    return redirect("/login")

# =========================================================
# 🔐 LOGIN
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "employee" and request.form["password"] == "1234":
            return redirect("/home")
        return "Invalid credentials ❌"
    return render_template("login.html")

# =========================================================
# 🧑‍⚕️ CONTROL PANEL
# =========================================================
@app.route("/home")
def doctor_home():
    return render_template("home.html")

# =========================================================
# 📝 REGISTRATION PAGE
# =========================================================
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

# =========================================================
# 💾 HANDLE REGISTRATION
# =========================================================
@app.route("/register", methods=["POST"])
def register_patient():

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]

    phone = "+91" + request.form["phone"]
    department = request.form["department"]

    doctor_name = request.form["doctor_name"]
    doctor_phone = "+91" + request.form["doctor_phone"]

    conn = sqlite3.connect("autocare.db")
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO patients
        (name, age, gender, phone, surgery_type, doctor_name, doctor_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, phone, department, doctor_name, doctor_phone))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "Patient already registered ❌"

    conn.close()

    # 🔥 First autonomous message
    send_checkin(phone)

    return redirect("/home")

# =========================================================
# 📩 TWILIO WEBHOOK — INTELLIGENCE ENGINE
# =========================================================
@app.route("/webhook", methods=["POST"])
def webhook():

    sender = request.form.get("From")
    phone = sender.replace("whatsapp:", "")
    incoming_msg = request.form.get("Body", "").strip().upper()

    resp = MessagingResponse()

    conn = sqlite3.connect("autocare.db")
    cur = conn.cursor()

    # 🔎 Find patient
    cur.execute("SELECT * FROM patients WHERE phone = ?", (phone,))
    patient = cur.fetchone()

    if not patient:
        resp.message("You are not registered in the system.")
        return str(resp)

    # Accept both comma and space
    answers = incoming_msg.replace(",", " ").split()

    if len(answers) != 5:
        resp.message("Reply in format: Y N Y N N")
        return str(resp)

    severe_pain, swelling, fever, mobility, infection = answers

    surgery_type = patient[5]

    # ================= SCORING =================

    if surgery_type == "Orthopedic":

        score = 100
        if severe_pain == "Y": score -= 25
        if swelling == "Y": score -= 20
        if fever == "Y": score -= 15
        if mobility == "N": score -= 30
        if infection == "Y": score -= 25

    elif surgery_type == "Cardiology":

        score = 100
        if severe_pain == "Y": score -= 35
        if swelling == "Y": score -= 20
        if fever == "Y": score -= 10
        if mobility == "Y": score -= 15
        if infection == "Y": score -= 30

    else:
        score = 50

    score = max(score, 0)

    # ================= RISK =================
    if score >= 75:
        risk = "LOW"
    elif score >= 45:
        risk = "MODERATE"
    else:
        risk = "HIGH"

    # ================= FOLLOW-UP =================
    if risk == "HIGH":
        schedule_followup(phone, 8)
    elif risk == "MODERATE":
        schedule_followup(phone, 24)
    else:
        schedule_followup(phone, 48)

    # ================= SAVE =================
    cur.execute("""
        INSERT INTO responses
        (patient_phone, severe_pain, swelling, fever, mobility, infection, score, risk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (phone, severe_pain, swelling, fever, mobility, infection, score, risk))

    conn.commit()
    conn.close()

    # ================= SAFE MESSAGE =================
    if risk == "LOW":
        reply = "✅ Recovery progressing well."
    elif risk == "MODERATE":
        reply = "⚠️ Monitor symptoms and consult doctor."
    else:
        reply = "🚨 Contact doctor immediately."

    resp.message(reply)
    return str(resp)

# =========================================================
# 📊 DASHBOARD
# =========================================================
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("autocare.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT
        p.name,
        p.surgery_type,
        p.phone,
        p.doctor_name,
        p.doctor_phone,
        r.severe_pain,
        r.swelling,
        r.fever,
        r.mobility,
        r.infection,
        r.score,
        r.risk
    FROM responses r
    JOIN patients p ON p.phone = r.patient_phone
    ORDER BY r.timestamp DESC
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)

# =========================================================
# 📤 SEND CHECK-IN
# =========================================================
@app.route("/send_checkin/<phone>")
def send_checkin(phone):

    conn = sqlite3.connect("autocare.db")
    cur = conn.cursor()

    cur.execute("SELECT surgery_type FROM patients WHERE phone = ?", (phone,))
    patient = cur.fetchone()

    if not patient:
        return "Patient not found ❌"

    surgery_type = patient[0]
    questions = PROTOCOL_MAP.get(surgery_type)

    client.messages.create(
        from_='whatsapp:+14155238886',
        to=f'whatsapp:{phone}',
        body=questions
    )

    conn.close()
    return "Check-in sent successfully ✅"

# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)