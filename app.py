
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

# Allow requests from your GitHub Pages website
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://w74347826-byte.github.io"
        ]
    }
})

DATABASE = os.getenv("DATABASE_PATH", "quiz.db")

QUESTIONS = [
    {
        "id": 1,
        "category": "General Knowledge",
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Venus", "Jupiter"],
        "answer": "Mars"
    },
    {
        "id": 2,
        "category": "General Knowledge",
        "question": "How many days are in a week?",
        "options": ["5", "6", "7", "8"],
        "answer": "7"
    },
    {
        "id": 3,
        "category": "Business",
        "question": "What does KPI stand for?",
        "options": [
            "Key Performance Indicator",
            "Known Product Information",
            "Key Price Index",
            "Knowledge Process Input"
        ],
        "answer": "Key Performance Indicator"
    }
]


def init_db():
    with sqlite3.connect(DATABASE) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                category TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL
            )
        """)


@app.get("/")
def home():
    return jsonify({
        "message": "Quiz Master Python API is running",
        "status": "success"
    })


@app.get("/api/questions")
def get_questions():
    category = request.args.get("category")

    selected = QUESTIONS
    if category:
        selected = [
            q for q in QUESTIONS
            if q["category"].lower() == category.lower()
        ]

    # Never send correct answers to the browser
    safe_questions = [
        {key: value for key, value in q.items()
         if key != "answer"}
        for q in selected
    ]

    return jsonify(safe_questions)


@app.post("/api/submit")
def submit_quiz():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()[:80]
    category = str(data.get("category", "")).strip()[:80]
    answers = data.get("answers", {})

    if not name or not category:
        return jsonify({
            "error": "Name and category are required"
        }), 400

    if not isinstance(answers, dict):
        return jsonify({"error": "Answers must be an object"}), 400

    questions = [
        q for q in QUESTIONS
        if q["category"].lower() == category.lower()
    ]

    if not questions:
        return jsonify({"error": "Unknown category"}), 404

    score = sum(
        1 for q in questions
        if str(answers.get(str(q["id"]), "")) == q["answer"]
    )

    with sqlite3.connect(DATABASE) as con:
        con.execute(
            """INSERT INTO results
               (player_name, category, score, total)
               VALUES (?, ?, ?, ?)""",
            (name, category, score, len(questions))
        )

    return jsonify({
        "message": "Quiz submitted successfully",
        "player": name,
        "category": category,
        "score": score,
        "total": len(questions)
    })


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


init_db()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
  )
  
