import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Search, GraduationCap } from "lucide-react";
import "./style.css";

function App() {
  const [studentProfile, setStudentProfile] = useState(
    "I am interested in natural language processing, recommender systems, and academic search."
  );
  const [discipline, setDiscipline] = useState("auto");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  async function getRecommendations() {
    setLoading(true);
    setResults(null);

    try {
      const response = await fetch("http://localhost:5000/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_profile: studentProfile,
          discipline,
          top_k: 5,
        }),
      });

      const data = await response.json();
      setResults(data);
    } catch (error) {
      setResults({ error: "Could not connect to backend. Make sure Flask is running on port 5000." });
    }

    setLoading(false);
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="badge">AI Professor Recommendation System</p>
          <h1>Rightfit PhD</h1>
          <p className="subtitle">
            Match students with professors based on research compatibility using a fine-tuned MiniLM cross-encoder model.
          </p>
        </div>
        <GraduationCap size={72} />
      </section>

      <section className="panel">
        <h2>Student Profile</h2>
        <textarea
          value={studentProfile}
          onChange={(e) => setStudentProfile(e.target.value)}
        />

        <label>Discipline</label>
        <select value={discipline} onChange={(e) => setDiscipline(e.target.value)}>
          <option value="auto">Auto classify</option>
          <option value="CS & AI">CS & AI</option>
          <option value="Electrical Engineering">Electrical Engineering</option>
          <option value="Bio & Health">Bio & Health</option>
          <option value="Business & Finance">Business & Finance</option>
        </select>

        <button onClick={getRecommendations}>
          <Search size={18} />
          {loading ? "Ranking..." : "Generate Recommendations"}
        </button>
      </section>

      <section className="panel">
        <h2>Recommendations</h2>

        {!results && <p className="muted">No recommendations yet.</p>}

        {results?.error && <p className="error">{results.error}</p>}

        {results?.recommendations && (
          <>
            <p className="muted">Predicted discipline: {results.predicted_discipline}</p>
            <div className="cards">
              {results.recommendations.map((prof, index) => (
                <div className="card" key={index}>
                  <div className="cardHeader">
                    <h3>#{index + 1} {prof.professor_name}</h3>
                    <span>{prof.match_score.toFixed(4)}</span>
                  </div>
                  <p>{prof.discipline}</p>
                  <p>{prof.professor_profile}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
