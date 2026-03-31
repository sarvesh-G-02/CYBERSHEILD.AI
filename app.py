from flask import Flask, render_template, request
import pickle
import re
import numpy as np
import sqlite3
import os

app = Flask(__name__)

# -------- LOAD MODEL (LOCAL VERSION) --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# We load the files directly from your project folder now
try:
    vector = pickle.load(open(os.path.join(BASE_DIR, "vectorizer.pkl"), 'rb'))
    model = pickle.load(open(os.path.join(BASE_DIR, "phishing.pkl"), 'rb'))
except FileNotFoundError:
    print("ERROR: Model files not found! Make sure phishing.pkl and vectorizer.pkl are in the main folder.")

# -------- DATABASE INIT --------
def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            result TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------- YOUR ORIGINAL LOGIC (PRESERVED) --------
def rule_based_check(url):
    url = url.lower()
    score = 0
    if '@' in url: score += 4
    if len(url) > 70: score += 2
    if url.startswith("http://"): score += 2
    if re.match(r'\d+\.\d+\.\d+\.\d+', url): score += 4
    keywords = ["login", "verify", "update", "bank", "secure", "account", "signin", "confirm"]
    if any(word in url for word in keywords): score += 3
    digits = sum(c.isdigit() for c in url)
    if digits > 5: score += 2
    if url.count('-') >= 1: score += 2
    if url.endswith(('.tk', '.xyz', '.info', '.ru', '.cn')): score += 3
    if '%' in url: score += 3
    if url.count('.') >= 4: score += 4

    if score >= 8: return "danger", score
    elif score >= 4: return "suspicious", score
    else: return "safe", score

def extract_features(url):
    url = url.lower()
    return [
        len(url), url.count('.'), 
        1 if '@' in url else 0,
        1 if re.match(r'\d+\.\d+\.\d+\.\d+', url) else 0,
        1 if any(w in url for w in ["login", "verify", "update", "bank"]) else 0,
        url.count('-'), 1 if url.startswith("https") else 0
    ]

# -------- ROUTES --------
@app.route("/", methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    result, result_type, risk = None, None, 0

    if request.method == "POST":
        url = request.form['url']
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        rule_result, rule_score = rule_based_check(url)
        cleaned_url = re.sub(r'^https?://(www\.)?', '', url.lower())

        # ML Prediction
        text_features = vector.transform([cleaned_url])
        custom_features = np.array(extract_features(url)).reshape(1, -1)
        combined_features = np.hstack([text_features.toarray(), custom_features])
        
        predict = model.predict(combined_features)[0]
        ml_score = 6 if predict == 'bad' else 0
        total_score = rule_score + ml_score

        if predict == 'bad' or rule_result == "danger":
            result, result_type = "🚨 Phishing Website (High Risk)", "danger"
        elif rule_result == "suspicious" or total_score >= 6:
            result, result_type = "⚠️ Suspicious Website", "suspicious"
        else:
            result, result_type = "✅ Safe Website", "safe"

        risk = min(total_score * 10, 100)
        c.execute("INSERT INTO history (url, result) VALUES (?, ?)", (url, result))
        conn.commit()

    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10")
    history = c.fetchall()
    conn.close()
    return render_template("index.html", result=result, result_type=result_type, risk=risk, history=history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))