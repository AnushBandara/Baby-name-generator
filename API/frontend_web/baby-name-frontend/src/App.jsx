import { useState } from "react";

function App() {
  const [letters, setLetters] = useState("");
  const [gender, setGender] = useState("male");
  const [minLength, setMinLength] = useState(3);
  const [maxLength, setMaxLength] = useState(10);
  const [generatedName, setGeneratedName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL = "https://baby-name-api-367079385266.asia-south1.run.app/names/"; // backend URL

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneratedName("");
    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("letters", letters);
      formData.append("gender", gender);
      formData.append("min_length", String(minLength));
      formData.append("max_length", String(maxLength));

      const res = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate name");
      }

      const data = await res.json();
      setGeneratedName(data.name || "");
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-root ${gender}`}>
      <div className="card">
        <h1 className="title">BlossomNames</h1>
        <p className="subtitle">
          Enter starting letters, choose gender, and AI will suggest a name for your cute cute bayby.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Starting letters</label>
            <input
              type="text"
              value={letters}
              onChange={(e) => setLetters(e.target.value)}
              placeholder="e.g. an, jo, el"
              maxLength={10}
              required
            />
          </div>

          <div className="form-group">
            <label>Gender</label>
            <div className="gender-row">
              <button
                type="button"
                className={`gender-btn ${
                  gender === "male" ? "gender-btn-active" : ""
                }`}
                onClick={() => setGender("male")}
              >
                Male
              </button>
              <button
                type="button"
                className={`gender-btn ${
                  gender === "female" ? "gender-btn-active" : ""
                }`}
                onClick={() => setGender("female")}
              >
                Female
              </button>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Min length</label>
              <input
                type="number"
                min={1}
                max={20}
                value={minLength}
                onChange={(e) => setMinLength(Number(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label>Max length</label>
              <input
                type="number"
                min={1}
                max={20}
                value={maxLength}
                onChange={(e) => setMaxLength(Number(e.target.value))}
              />
            </div>
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !letters.trim()}
          >
            {loading ? "Generating..." : "Generate Name"}
          </button>
        </form>

        {error && <p className="error-text">{error}</p>}

        {generatedName && (
          <div className="result-box">
            <p className="result-label">Suggested name</p>
            <p className="result-name">{generatedName}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;