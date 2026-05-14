from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = ROOT / "web" / "frontend" / "dist"

sys.path.append(str(ROOT / "model"))

from classify_discipline import classify_discipline
from rank_professors import rank_professors

app = Flask(__name__, static_folder=str(FRONTEND_DIST), static_url_path="")
CORS(app)


@app.route("/api/health", methods=["GET"])
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


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path and (FRONTEND_DIST / path).exists():
        return send_from_directory(FRONTEND_DIST, path)

    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    if not FRONTEND_DIST.exists():
        print("Frontend build not found.")
        print("Run this first:")
        print("cd web/frontend")
        print("npm install")
        print("npm run build")
    else:
        app.run(debug=True, port=5000)