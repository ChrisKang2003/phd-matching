from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "model"))

from classify_discipline import classify_discipline
from rank_professors import rank_professors

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True)

    student_profile = data.get("student_profile", "").strip()
    discipline = data.get("discipline")

    if not student_profile:
        return jsonify({"error": "student_profile is required"}), 400

    if not discipline or discipline == "auto":
        discipline = classify_discipline(student_profile)

    results = rank_professors(
        student_profile=student_profile,
        discipline=discipline,
        top_k=int(data.get("top_k", 5))
    )

    recommendations = []
    for _, row in results.iterrows():
        recommendations.append({
            "professor_name": row.get("professor_name", "Unknown Professor"),
            "discipline": row.get("discipline", discipline),
            "professor_profile": row.get("professor_profile", ""),
            "match_score": float(row.get("match_score", 0.0))
        })

    return jsonify({
        "predicted_discipline": discipline,
        "recommendations": recommendations
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
